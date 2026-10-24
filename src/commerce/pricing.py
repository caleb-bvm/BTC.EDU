"""Server-side price adjustments: credit for earlier purchases and educator coupons."""
from django.db.models import Q
from django.utils import timezone

from .catalog import owned_ids
from .models import Coupon, Invoice, OrderLine

COUPON_STATES = ("pending", "paid")


def paid_units(offer):
    return set(offer.items.filter(resource__access_type="paid").values_list("resource_id", flat=True))


def upgrade_credit(user, offer):
    """Sats this buyer already paid for parts of a course or chapter package.

    Only purchases whose paid content sits entirely inside the package count,
    so a credit is never shared with content outside it. A completed package
    has nothing left to credit, which makes the credit single-use.
    """
    if offer.kind not in ("course", "chapter") or not user.is_authenticated or user.account_type != "student":
        return 0
    package = paid_units(offer)
    owned = owned_ids(user, package)
    if not owned or owned == package:
        return 0
    credit = 0
    invoices = (Invoice.objects.filter(buyer=user, status="paid").exclude(order__gift=True)
                .exclude(refund__status="refunded").select_related("order").prefetch_related("order__lines"))
    for invoice in invoices:
        parts = [(line.inventory, line.amount_sats) for line in invoice.order.lines.all()] if invoice.order_id else [(invoice.inventory, invoice.amount_sats)]
        for inventory, amount in parts:
            bought = {item["resource_id"] for item in inventory if item.get("paid")}
            if bought and bought <= package:
                credit += amount
    return credit


def upgrade_quote(user, offer):
    """The remaining price to complete a package, never below one sat."""
    credit = upgrade_credit(user, offer)
    if not credit:
        return None
    applied = min(credit, offer.amount_sats - 1)
    package = paid_units(offer)
    return {"credit_sats": applied, "amount_sats": offer.amount_sats - applied,
            "missing": package - owned_ids(user, package)} if applied else None


def annotate_upgrades(user, offers):
    for offer in offers:
        offer.upgrade = upgrade_quote(user, offer) if offer.kind in ("course", "chapter") else None
    return offers


def normalize_code(value):
    return "".join(str(value or "").split()).upper()[:24]


def coupon_uses(coupon, exclude_buyer=None):
    lines = OrderLine.objects.filter(coupon=coupon, order__invoice__status__in=COUPON_STATES)
    if exclude_buyer is not None:
        lines = lines.exclude(order__buyer=exclude_buyer)
    return lines.values("order_id").distinct().count()


def find_coupon(code, buyer=None, now=None):
    """Return (coupon, error); an unusable code never blocks buying without it."""
    code = normalize_code(code)
    if not code:
        return None, ""
    now = now or timezone.now()
    coupon = Coupon.objects.select_related("creator", "course").filter(code=code).first()
    if coupon is None or not coupon.active or not coupon.creator.is_active:
        return None, "Este cupón no existe o ya no está activo."
    if coupon.starts_at > now:
        return None, "Este cupón todavía no está disponible."
    if coupon.expires_at <= now:
        return None, "Este cupón venció."
    if buyer is not None and buyer.is_authenticated and OrderLine.objects.filter(
            coupon=coupon, order__buyer=buyer, order__invoice__status="paid").exists():
        return None, "Ya usaste este cupón en una compra anterior."
    if coupon_uses(coupon, exclude_buyer=buyer if buyer is not None and buyer.is_authenticated else None) >= coupon.max_uses:
        return None, "Este cupón ya alcanzó su límite de usos."
    return coupon, ""


def coupon_applies(coupon, offer):
    if coupon is None or coupon.creator_id != offer.creator_id:
        return False
    if coupon.course_id is None:
        return True
    return bool(offer.course_version_id and offer.course_version.course_id == coupon.course_id)


def coupon_discount(coupon, base_sats):
    """Discount on the price left after credit; the line always charges at least one sat."""
    if base_sats <= 1:
        return 0
    value = base_sats * coupon.percent_off // 100 if coupon.percent_off else coupon.amount_off_sats
    return max(0, min(value, base_sats - 1))


def creator_coupons(creator):
    return Coupon.objects.filter(creator=creator).select_related("course").order_by("-created_at", "-pk")


def coupon_rows(creator):
    rows = []
    now = timezone.now()
    for coupon in creator_coupons(creator):
        uses = coupon_uses(coupon)
        state = ("Desactivado" if not coupon.active else "Programado" if coupon.starts_at > now
                 else "Vencido" if coupon.expires_at <= now else "Agotado" if uses >= coupon.max_uses else "Activo")
        rows.append({"coupon": coupon, "uses": uses, "state": state})
    return rows


def coupon_scope_choices(creator):
    from content.models import Course
    courses = Course.objects.filter(creator=creator).filter(Q(status="published") | Q(current_version__isnull=False)).order_by("title")
    return [("", "Todo mi contenido")] + [(str(course.pk), course.title) for course in courses]
