"""Server-priced, signed order snapshots; no provider calls inside transactions."""
import hashlib
import json
import uuid
from datetime import timedelta

from django.core import signing
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from .catalog import available, ownership
from .journey import return_lesson
from .models import Cart, Invoice, Offer, Order, OrderLine
from .reservations import overlapping_invoice, require_unreserved
from .services import event, require_student, reserve_writer

MAX_ORDER_LINES = 20
MAX_ORDER_SATS = 2000000
QUOTE_TTL = 900
QUOTE_SALT = "commerce.order.review.v1"


def inventory_for(offer):
    return [{"resource_id": item.resource_id, "title": item.resource.title, "kind": item.resource.kind,
             "paid": item.resource.access_type == "paid"}
            for item in offer.items.select_related("resource").order_by("resource_id")]


def inventory_union(lines):
    units = {}
    for line in lines:
        for item in line["inventory"]:
            if item["resource_id"] in units and units[item["resource_id"]] != item:
                raise ValidationError("La selección contiene revisiones incompatibles.")
            units[item["resource_id"]] = item
    return [units[key] for key in sorted(units)]


def canonical_lines(lines):
    rows = []
    for line in lines:
        row = {"offer_id": line["offer_id"], "creator_id": line["creator_id"], "title": line["title"],
               "amount_sats": line["amount_sats"], "course_version_id": line["course_version"].pk if line["course_version"] else None,
               "logical_key": line["offer"].logical_key, "inventory": line["inventory"],
               "return_lesson_id": line["return_lesson_id"], "cart_item_key": line["cart_item_key"]}
        # Adjustments join the fingerprint only when present, so earlier orders keep theirs.
        if line.get("credit_sats"):
            row["credit_sats"] = line["credit_sats"]
        if line.get("discount_sats"):
            row.update(coupon_id=line["coupon_id"], discount_sats=line["discount_sats"])
        if line.get("path_id"):
            row["path_id"] = line["path_id"]
        rows.append(row)
    return rows


def fingerprint_for(lines, gift=False):
    value = {"gift": True, "lines": canonical_lines(lines)} if gift else canonical_lines(lines)
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def quote_selection(actor, selection, cart_revision=0, cart_id=None, coupon_code="", gift=False, path=None):
    from .pricing import (
        bundle_discount,
        coupon_applies,
        coupon_discount,
        find_coupon,
        upgrade_quote,
    )
    lines, conflicts, seen_offers, covered = [], [], set(), set()
    # A path bundle carries its own discount, so it never combines with a coupon.
    coupon, coupon_error = find_coupon(coupon_code, buyer=actor) if path is None else (None, "")
    coupon_used = False
    def conflict(code, message, entry=None, invoice=None):
        entry = entry if isinstance(entry, dict) else None
        conflicts.append({"code": code, "message": message, "offer_id": entry.get("offer_id") if entry else None,
                          "cart_item_key": str(entry.get("cart_item_key")) if entry and entry.get("cart_item_key") else None,
                          "invoice_id": str(invoice.pk) if invoice else None})
    if not selection:
        conflict("empty", "Añade contenido para preparar tu pedido.")
    if len(selection) > MAX_ORDER_LINES:
        conflict("limit", f"Puedes preparar hasta {MAX_ORDER_LINES} contenidos por pedido.")
    student = actor.is_authenticated and actor.is_active and actor.account_type == "student"
    for entry in selection[:MAX_ORDER_LINES]:
        if not isinstance(entry, dict):
            conflict("unavailable", "Revisa el contenido de la selección.")
            continue
        try:
            offer_id = int(entry.get("offer_id"))
            if not 0 < offer_id <= 9223372036854775807:
                raise ValueError
            offer = Offer.objects.select_related("creator", "course_version__course", "resource", "lesson__content").get(pk=offer_id)
        except (ValueError, TypeError, Offer.DoesNotExist):
            conflict("unavailable", "Una oferta de tu selección ya no está disponible.", entry)
            continue
        if offer_id in seen_offers:
            conflict("selection_overlap", "Esta oferta ya está incluida en la selección.", entry)
            continue
        seen_offers.add(offer_id)
        units = inventory_for(offer)
        paid = {item["resource_id"] for item in units if item["paid"]}
        origin = return_lesson(offer, entry.get("return_lesson_id"))
        issues = []
        if not available(offer):
            issues.append("unavailable")
            conflict("unavailable", "Esta oferta cambió o ya no está disponible. Revisa el contenido antes de continuar.", entry)
        # A gift grants nothing to the buyer, so their own access never blocks it.
        state = "none" if gift else ownership(actor, offer)
        upgrade = upgrade_quote(actor, offer) if state == "partial" else None
        amount, credit = offer.amount_sats, 0
        if upgrade:
            units = [item for item in units if item["resource_id"] not in paid or item["resource_id"] in upgrade["missing"]]
            paid, amount, credit = upgrade["missing"], upgrade["amount_sats"], upgrade["credit_sats"]
        elif state != "none":
            issues.append(state if state == "owned" else "partial")
            conflict(state if state == "owned" else "partial", "Ya tienes este contenido." if state == "owned" else "Ya tienes parte del contenido. Elige únicamente lo que falta.", entry)
        if entry.get("return_lesson_id") and not origin:
            issues.append("invalid_origin")
            conflict("invalid_origin", "La lección elegida no forma parte de esta oferta.", entry)
        if not paid:
            issues.append("unavailable")
            conflict("unavailable", "Este contenido no necesita una compra.", entry)
        if paid & covered:
            issues.append("selection_overlap")
            conflict("selection_overlap", "Hay contenido incluido en más de una oferta. Revisa las inclusiones para evitar comprarlo dos veces.", entry)
        if student and not gift:
            reserved = overlapping_invoice(actor, paid)
            if reserved:
                issues.append("pending_overlap")
                conflict("pending_overlap", "Parte de esta selección tiene un pago pendiente o en revisión. Consulta esa factura antes de pagar otra vez.", entry, reserved)
        bundled = path is not None and offer.kind == "course"
        discount = bundle_discount(path.bundle_percent, amount) if bundled else coupon_discount(coupon, amount) if coupon_applies(coupon, offer) else 0
        coupon_used |= bool(discount) and not bundled
        covered |= paid
        key = str(entry.get("cart_item_key")) if entry.get("cart_item_key") else None
        lines.append({"offer": offer, "offer_id": offer.pk, "creator": offer.creator, "creator_id": offer.creator_id,
                      "title": offer.title, "amount_sats": amount - discount, "list_sats": offer.amount_sats,
                      "credit_sats": credit, "coupon": coupon if discount and not bundled else None,
                      "coupon_id": coupon.pk if discount and not bundled else None,
                      "path": path if discount and bundled else None, "path_id": path.pk if discount and bundled else None,
                      "discount_sats": discount, "course_version": offer.course_version,
                      "inventory": units, "return_lesson": origin, "return_lesson_id": origin.pk if origin else None,
                      "cart_item_key": key, "eligible": not issues, "issues": issues})
    if coupon and not coupon_used and not coupon_error:
        coupon_error = "Este cupón no aplica al contenido elegido."
    total = sum(line["amount_sats"] for line in lines)
    if total > MAX_ORDER_SATS or (lines and total <= 0):
        conflict("limit", f"El total debe estar entre 1 y {MAX_ORDER_SATS} sats.")
    fingerprint = fingerprint_for(lines, gift)
    return {"token": "", "fingerprint": fingerprint, "cart_revision": cart_revision, "cart_id": str(cart_id) if cart_id else None,
            "total_sats": total, "request_key": "", "lines": lines, "conflicts": conflicts,
            "coupon": coupon if coupon_used else None, "coupon_code": coupon.code if coupon_used else "",
            "coupon_error": coupon_error, "gift": gift,
            "credit_total_sats": sum(line["credit_sats"] for line in lines),
            "discount_total_sats": sum(line["discount_sats"] for line in lines),
            "can_checkout": bool(lines) and not conflicts}


def sign_quote(actor, quote, mode):
    if quote["can_checkout"] and actor.is_authenticated and actor.is_active and actor.account_type == "student":
        key = str(uuid.uuid4())
        payload = {"buyer_id": actor.pk, "cart_id": quote["cart_id"], "cart_revision": quote["cart_revision"],
                   "fingerprint": quote["fingerprint"], "request_key": key, "mode": mode,
                   "coupon": quote.get("coupon_code", ""), "gift": bool(quote.get("gift")),
                   "selection": [{"offer_id": line["offer_id"], "return_lesson_id": line["return_lesson_id"],
                                  "cart_item_key": line["cart_item_key"]} for line in quote["lines"]]}
        quote.update(token=signing.dumps(payload, salt=QUOTE_SALT, compress=True), request_key=key)
    return quote


def cart_selection(cart):
    return [{"offer_id": item.offer_id, "return_lesson_id": item.return_lesson_id, "cart_item_key": str(item.pk)}
            for item in cart.items.order_by("created_at", "pk")]


def quote_order(actor, cart, coupon_code=""):
    require_student(actor)
    cart = Cart.objects.get(pk=cart.pk)
    if cart.buyer_id != actor.pk:
        raise PermissionDenied
    return sign_quote(actor, quote_selection(actor, cart_selection(cart), cart.revision, cart.pk, coupon_code=coupon_code), "cart")


def quote_direct_order(actor, offer_id, return_lesson_id=None, coupon_code="", gift=False):
    quote = quote_selection(actor, [{"offer_id": offer_id, "return_lesson_id": return_lesson_id}], coupon_code=coupon_code, gift=gift)
    return sign_quote(actor, quote, "direct")


def load_quote(actor, token, request_key, mode):
    try:
        payload = signing.loads(token, salt=QUOTE_SALT)
        key = uuid.UUID(payload["request_key"])
        if request_key is not None and uuid.UUID(str(request_key)) != key:
            raise ValueError
    except (signing.BadSignature, KeyError, ValueError, TypeError):
        raise ValidationError("La revisión de compra no es válida. Revisa tu selección para continuar.") from None
    if payload.get("buyer_id") != actor.pk or payload.get("mode") != mode:
        raise PermissionDenied
    existing = Order.objects.filter(buyer=actor, request_key=key).first()
    if existing:
        if existing.fingerprint != payload.get("fingerprint") or str(existing.cart_id or "") != (payload.get("cart_id") or ""):
            raise ValidationError("La solicitud corresponde a otra selección.")
        return payload, existing.invoice
    try:
        signing.loads(token, salt=QUOTE_SALT, max_age=QUOTE_TTL)
    except signing.SignatureExpired:
        raise ValidationError("La revisión de compra venció. Revisa el precio y el contenido para continuar.") from None
    return payload, None


def create_reserved_order(actor, quote, key, cart=None, activity_session=None, gift_message="", title=""):
    if not quote["can_checkout"]:
        raise ValidationError([item["message"] for item in quote["conflicts"]])
    inventory = inventory_union(quote["lines"])
    gift = bool(quote.get("gift"))
    if not gift:
        require_unreserved(actor, {item["resource_id"] for item in inventory if item["paid"]})
    line_count = len(quote["lines"])
    label = "Regalo" if gift else "Pedido"
    order = Order.objects.create(buyer=actor, title=title[:200] or f"{label} · {line_count} artículo{'s' if line_count != 1 else ''}",
                                 amount_sats=quote["total_sats"], inventory=inventory, cart=cart, cart_revision=quote["cart_revision"],
                                 fingerprint=quote["fingerprint"], request_key=key, gift=gift,
                                 gift_message=" ".join(str(gift_message or "").split())[:280] if gift else "")
    for position, line in enumerate(quote["lines"], 1):
        OrderLine.objects.create(order=order, offer=line["offer"], creator=line["creator"], title=line["title"],
                                 amount_sats=line["amount_sats"], inventory=line["inventory"], logical_key=line["offer"].logical_key,
                                 course_version=line["course_version"], return_lesson=line["return_lesson"], cart_item_key=line["cart_item_key"], position=position,
                                 credit_sats=line.get("credit_sats", 0), coupon=line.get("coupon"), discount_sats=line.get("discount_sats", 0),
                                 path=line.get("path"))
    Order._base_manager.filter(pk=order.pk).update(sealed=True)
    order.sealed = True
    invoice = Invoice.objects.create(buyer=actor, order=order, title=order.title, amount_sats=order.amount_sats,
                                     inventory=inventory, logical_key=f"order:{order.pk}", expires_at=timezone.now() + timedelta(minutes=15))
    event(invoice, "reserved", "Factura del pedido reservada por 15 minutos.")
    if activity_session and not actor.is_staff:
        from core.models import ActivityEvent
        for line in quote["lines"]:
            ActivityEvent.objects.create(event_key=f"invoice:{invoice.pk}:offer:{line['offer_id']}", kind="invoice_created",
                                         session_id=activity_session, actor=actor, creator=line["creator"], offer=line["offer"],
                                         invoice=invoice, version=line["course_version"])
    return invoice


@transaction.atomic
def reserve_order(actor, cart, token, request_key=None, activity_session=None):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    payload, existing = load_quote(actor, token, request_key, "cart")
    if str(cart.pk) != payload.get("cart_id"):
        raise ValidationError("La solicitud corresponde a otro carrito.")
    if existing:
        return existing
    cart = Cart.objects.get(pk=cart.pk)
    if cart.buyer_id != actor.pk:
        raise PermissionDenied
    if cart.revision != payload.get("cart_revision"):
        raise ValidationError("Tu carrito cambió. Revisa la selección actual antes de pagar.")
    quote = quote_selection(actor, cart_selection(cart), cart.revision, cart.pk, coupon_code=payload.get("coupon", ""))
    if quote["fingerprint"] != payload.get("fingerprint"):
        raise ValidationError("Tu selección, precio o destino cambió. Revísala antes de pagar.")
    return create_reserved_order(actor, quote, uuid.UUID(payload["request_key"]), cart, activity_session)


@transaction.atomic
def reserve_direct_order(actor, offer_id, return_lesson_id=None, request_key=None, token=None, activity_session=None, gift_message=""):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    try:
        offer_id = int(offer_id)
        return_lesson_id = int(return_lesson_id) if return_lesson_id else None
        if not 0 < offer_id <= 9223372036854775807 or (return_lesson_id is not None and not 0 < return_lesson_id <= 9223372036854775807):
            raise ValueError
    except (ValueError, TypeError):
        raise ValidationError("El contenido o la lección elegida no es válido.") from None
    if token:
        payload, existing = load_quote(actor, token, request_key, "direct")
        selection = [{"offer_id": int(offer_id), "return_lesson_id": int(return_lesson_id) if return_lesson_id else None, "cart_item_key": None}]
        if selection != payload.get("selection"):
            raise ValidationError("La solicitud corresponde a otro contenido.")
        if existing:
            return existing
        key = uuid.UUID(payload["request_key"])
    else:
        try:
            key = uuid.UUID(str(request_key)) if request_key else uuid.uuid4()
        except ValueError:
            raise ValidationError("La solicitud de compra no es válida.") from None
        existing = Order.objects.filter(buyer=actor, request_key=key).first()
        if existing:
            line = existing.lines.first()
            if existing.lines.count() != 1 or line.offer_id != int(offer_id) or line.return_lesson_id != (int(return_lesson_id) if return_lesson_id else None):
                raise ValidationError("La solicitud corresponde a otro contenido.")
            return existing.invoice
        payload = None
    quote = quote_selection(actor, [{"offer_id": offer_id, "return_lesson_id": return_lesson_id}],
                            coupon_code=payload.get("coupon", "") if payload else "", gift=bool(payload and payload.get("gift")))
    if payload and quote["fingerprint"] != payload.get("fingerprint"):
        raise ValidationError("El contenido o su precio cambió. Revisa la compra antes de pagar.")
    return create_reserved_order(actor, quote, key, activity_session=activity_session, gift_message=gift_message)


def order_snapshot_valid(invoice):
    try:
        return _order_snapshot_valid(invoice)
    except (ValidationError, KeyError, TypeError, ValueError):
        return False


def _order_snapshot_valid(invoice):
    order = invoice.order
    lines = list(order.lines.select_related("offer", "course_version"))
    values = [{"inventory": line.inventory} for line in lines]
    if not order.sealed or order.buyer_id != invoice.buyer_id or not lines:
        return False
    if sum(line.amount_sats for line in lines) != order.amount_sats or invoice.amount_sats != order.amount_sats:
        return False
    if [line.position for line in lines] != list(range(1, len(lines) + 1)):
        return False
    if inventory_union(values) != order.inventory or invoice.inventory != order.inventory:
        return False
    paid = set()
    reconstructed = []
    for line in lines:
        current = {item["resource_id"] for item in line.inventory if item["paid"]}
        full = inventory_for(line.offer)
        # A credited line keeps a subset of the frozen offer inventory, item by item.
        same_inventory = (all(item in full for item in line.inventory) and len(line.inventory) < len(full)) if line.credit_sats else line.inventory == full
        if (paid & current or not current or line.creator_id != line.offer.creator_id
                or line.amount_sats + line.credit_sats + line.discount_sats != line.offer.amount_sats
                or line.course_version_id != line.offer.course_version_id or line.logical_key != line.offer.logical_key or not same_inventory):
            return False
        paid |= current
        reconstructed.append({"offer": line.offer, "offer_id": line.offer_id, "creator_id": line.creator_id,
                              "title": line.title, "amount_sats": line.amount_sats, "course_version": line.course_version,
                              "inventory": line.inventory, "return_lesson_id": line.return_lesson_id,
                              "cart_item_key": str(line.cart_item_key) if line.cart_item_key else None,
                              "credit_sats": line.credit_sats, "coupon_id": line.coupon_id, "discount_sats": line.discount_sats,
                              "path_id": line.path_id})
    return fingerprint_for(reconstructed, order.gift) == order.fingerprint
