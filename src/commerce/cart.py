"""Account and visitor selections; adding an item never grants access."""
from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F

from .catalog import available, ownership
from .journey import return_lesson
from .models import Cart, CartItem, Offer
from .services import require_student, reserve_writer

MAX_ITEMS = 20
GUEST_KEY = "commerce_guest_cart"
PENDING_KEY = "commerce_pending_guest_cart"
UNDO_KEY = "commerce_cart_undo"


def _uuid(value):
    try:
        return UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


def get_cart(request, create=False):
    """A GET can read a selection, but never creates or merges one."""
    if request.user.is_authenticated:
        require_student(request.user)
        if create:
            return Cart.objects.get_or_create(buyer=request.user)[0]
        return Cart.objects.filter(buyer=request.user).first()
    identifier = _uuid(request.session.get(GUEST_KEY))
    cart = Cart.objects.filter(pk=identifier, buyer__isnull=True).first() if identifier else None
    if cart is None and create:
        cart = Cart.objects.create()
        request.session[GUEST_KEY] = str(cart.pk)
    return cart


def cart_summary(request):
    if request.user.is_authenticated and (not request.user.is_active or request.user.account_type != "student"):
        return {"cart_count": 0, "cart": None}
    cart = get_cart(request)
    return {"cart_count": cart.items.count() if cart else 0, "cart": cart}


def _lock_cart(actor, cart):
    if actor.is_authenticated:
        require_student(actor)
        reserve_writer(actor.pk)
        actor.refresh_from_db()
        require_student(actor)
        filters = {"buyer": actor}
    else:
        filters = {"buyer__isnull": True}
    if not Cart.objects.filter(pk=cart.pk, **filters).update(revision=F("revision")):
        raise PermissionDenied
    return Cart.objects.select_for_update().get(pk=cart.pk, **filters)


def _changed(cart):
    Cart.objects.filter(pk=cart.pk).update(revision=F("revision") + 1)
    cart.refresh_from_db()


@transaction.atomic
def add_item(actor, cart, offer_id, return_lesson_id=None, restore=False):
    cart = _lock_cart(actor, cart)
    offer = Offer.objects.select_related("creator", "course_version__course", "resource").get(pk=offer_id)
    chosen = return_lesson(offer, return_lesson_id)
    if return_lesson_id and not chosen:
        raise ValidationError("La lección elegida no forma parte de esta opción de acceso.")
    if not restore:
        if not available(offer):
            raise ValidationError("Esta opción ya no está disponible. Revisa el contenido para elegir una opción actual.")
        if ownership(actor, offer) != "none":
            raise ValidationError("Ya tienes contenido de esta opción. Abre lo adquirido o elige los componentes que faltan.")
    current = cart.items.filter(offer=offer).first()
    if current and current.return_lesson_id == (chosen.pk if chosen else None):
        return current, False
    if not current and cart.items.count() >= MAX_ITEMS:
        raise ValidationError("Tu carrito admite hasta 20 artículos. Retira alguno o guárdalo para después.")
    # A changed origin is a new selection: a late payment must not delete it.
    if current:
        current.delete()
    item = CartItem.objects.create(cart=cart, offer=offer, return_lesson=chosen)
    _changed(cart)
    return item, True


@transaction.atomic
def remove_item(actor, cart, item_id):
    cart = _lock_cart(actor, cart)
    item = cart.items.select_related("offer").filter(pk=item_id).first()
    if item is None:
        raise ValidationError("Este artículo ya no está en tu carrito. Revisa la selección actual.")
    removed = {"cart_id": str(cart.pk), "offer_id": item.offer_id, "return_lesson_id": item.return_lesson_id,
               "title": item.offer.title, "buyer_id": str(actor.pk) if actor.is_authenticated else ""}
    item.delete()
    _changed(cart)
    return removed


def undo_selection(request, cart):
    snapshot = request.session.get(UNDO_KEY)
    buyer_id = str(request.user.pk) if request.user.is_authenticated else ""
    return snapshot if (isinstance(snapshot, dict) and cart and snapshot.get("cart_id") == str(cart.pk)
                        and snapshot.get("buyer_id") == buyer_id) else None


def pending_guest_cart(request):
    pending = request.session.get(PENDING_KEY)
    if not request.user.is_authenticated or not isinstance(pending, dict) or pending.get("buyer_id") != str(request.user.pk):
        return None
    identifier = _uuid(pending.get("id"))
    return Cart.objects.filter(pk=identifier, buyer__isnull=True).first() if identifier else None


@transaction.atomic
def _merge(actor, guest, selected=None):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    if not Cart.objects.filter(pk=guest.pk, buyer__isnull=True).update(revision=F("revision")):
        raise ValidationError("La selección de visitante ya se incorporó o ya no está disponible.")
    guest = Cart.objects.select_for_update().get(pk=guest.pk, buyer__isnull=True)
    own = Cart.objects.select_for_update().filter(buyer=actor).first()
    if own is None and selected is None:
        guest.buyer = actor
        guest.revision += 1
        guest.save(update_fields=("buyer", "revision"))
        return guest, False
    own = own or Cart.objects.create(buyer=actor)
    items = list(guest.items.order_by("created_at", "pk"))
    if selected is not None:
        selected = {_uuid(key) for key in selected}
        if None in selected or not selected or not selected.issubset({item.pk for item in items}):
            raise ValidationError("Elige artículos de tu selección pendiente.")
        items = [item for item in items if item.pk in selected]
    existing = set(own.items.values_list("offer_id", flat=True))
    additional = sum(item.offer_id not in existing for item in items)
    if own.items.count() + additional > MAX_ITEMS:
        return own, True
    for item in items:
        if item.offer_id in existing:
            # Keep the account's previous choice of where to resume.
            item.delete()
        else:
            item.cart = own
            item.save(update_fields=("cart",))
            existing.add(item.offer_id)
    if items:
        _changed(own)
        _changed(guest)
    return own, guest.items.exists()


def merge_guest_cart(request):
    """Called only by the completed student-login/registration flow."""
    if not request.user.is_authenticated:
        return []
    if request.user.account_type != "student" or not request.user.is_active:
        request.session.pop(GUEST_KEY, None)
        request.session.pop(PENDING_KEY, None)
        request.session.pop(UNDO_KEY, None)
        return []
    identifier = _uuid(request.session.pop(GUEST_KEY, None))
    guest = Cart.objects.filter(pk=identifier, buyer__isnull=True).first() if identifier else pending_guest_cart(request)
    if not guest:
        return []
    try:
        _, pending = _merge(request.user, guest)
    except (ValidationError, PermissionDenied):
        # Authentication must still finish; keep this visitor choice private.
        request.session[PENDING_KEY] = {"id": str(guest.pk), "buyer_id": str(request.user.pk)}
        return ["Tu selección de visitante se conserva en esta sesión. Puedes revisarla desde el carrito."]
    request.session.pop(UNDO_KEY, None)
    if pending:
        request.session[PENDING_KEY] = {"id": str(guest.pk), "buyer_id": str(request.user.pk)}
        return ["Tu carrito ya tiene varios artículos. La selección de visitante se conserva en esta sesión para que elijas cuáles incorporar."]
    request.session.pop(PENDING_KEY, None)
    return []


def merge_pending_selection(request, selected):
    guest = pending_guest_cart(request)
    if not guest:
        raise ValidationError("No hay una selección de visitante pendiente para esta cuenta.")
    _, pending = _merge(request.user, guest, selected)
    if pending and all(guest.items.filter(pk=key).exists() for key in selected if _uuid(key)):
        raise ValidationError("No hay espacio para esa selección. Tu carrito admite hasta 20 artículos; retira alguno antes de incorporar más.")
    if not pending:
        request.session.pop(PENDING_KEY, None)
    return pending


def ordered_items(cart):
    return cart.items.select_related("offer__creator__creator_profile", "offer__course_version__course", "offer__course_version__topic",
                                     "offer__resource", "offer__lesson__content", "offer__chapter", "return_lesson__content").order_by("created_at", "pk")


def replacement_offer(offer):
    active = Offer.objects.filter(status="active").exclude(pk=offer.pk).select_related("creator", "course_version__course", "resource")
    candidates = active.filter(logical_key=offer.logical_key)
    if offer.kind == "course" and offer.course_version_id:
        candidates = active.filter(kind="course", course_version_id=offer.course_version.course.current_version_id)
    elif offer.kind == "resource" and offer.resource_id:
        candidates = active.filter(kind="resource", resource__resource_key=offer.resource.resource_key)
    return next((candidate for candidate in candidates if available(candidate)), None)


def decorate_quote(user, quote):
    """Labels and routes enrich server-authoritative quotes without changing prices."""
    from django.urls import reverse

    from .catalog import missing_alternatives
    from .journey import destination, offer_url, public_destination
    conflicts = quote.get("conflicts", [])
    quote["eligible_total_sats"] = sum(line["amount_sats"] for line in quote.get("lines", []) if line["eligible"])
    for line in quote.get("lines", []):
        offer = line["offer"]
        line["scope"] = ("Tutorial completo" if offer.course_version and offer.course_version.kind == "tutorial" else "Curso completo") if offer.kind == "course" else "Capítulo completo" if offer.kind == "chapter" else "Texto de la lección" if offer.kind == "lesson" else offer.resource.get_kind_display() if offer.resource else "Recurso"
        line["creator_name"] = getattr(getattr(offer.creator, "creator_profile", None), "display_name", "") or "Educador"
        line["content_url"] = public_destination(offer)
        line["issues_display"] = [item for item in conflicts if item.get("offer_id") == offer.pk]
        line["details_url"] = offer_url(offer, line.get("return_lesson")) if available(offer) else ""
        line["save_kind"] = "curso" if offer.course_version_id else "recurso"
        line["save_label"] = ("Guardar tutorial para después" if offer.course_version.kind == "tutorial" else "Guardar curso para después") if offer.course_version_id else "Guardar para después"
        if "owned" in line.get("issues", []):
            line["owned_destination"] = destination(user, offer, line.get("return_lesson"))
        if "partial" in line.get("issues", []):
            line["alternatives"] = [{"title": alternative.title, "price": alternative.amount_sats, "url": offer_url(alternative)}
                                    for alternative in missing_alternatives(user, offer)]
        if "unavailable" in line.get("issues", []):
            replacement = replacement_offer(offer)
            if replacement:
                line["replacement"] = {"title": replacement.title, "price": replacement.amount_sats, "url": offer_url(replacement)}
        for issue in line["issues_display"]:
            if issue.get("invoice_id") and user.is_authenticated:
                issue["invoice_url"] = reverse("invoice-detail", args=[issue["invoice_id"]])
    return quote
