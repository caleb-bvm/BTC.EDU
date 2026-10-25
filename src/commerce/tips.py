"""Tips to educators: Lightning payments that grant no content."""
from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Count, Sum
from django.urls import reverse
from django.utils import timezone

from .gateway import LNbitsGateway
from .lightning import emit_payment
from .models import Tip
from .services import require_student, reserve_writer

TIP_PRESETS = (100, 500, 1000, 5000)
TIP_MIN, TIP_MAX = 10, 100000
MAX_OPEN_TIPS = 5


def tip_recipient(user):
    from creators.models import CreatorProfile
    return (user.is_active and user.account_type == "creator"
            and CreatorProfile.objects.filter(user=user, status="approved").exists())


@transaction.atomic
def create_tip(actor, creator, amount, message="", lesson=None):
    require_student(actor)
    reserve_writer(actor.pk)
    if not tip_recipient(creator) or creator.pk == actor.pk:
        raise PermissionDenied("Este educador no puede recibir propinas ahora.")
    if type(amount) is not int or not TIP_MIN <= amount <= TIP_MAX:
        raise ValidationError(f"Elige un importe entre {TIP_MIN} y {TIP_MAX} sats.")
    if lesson is not None and lesson.chapter.version.course.creator_id != creator.pk:
        raise ValidationError("La lección no pertenece a este educador.")
    now = timezone.now()
    open_tips = Tip.objects.filter(sender=actor, status="pending", expires_at__gt=now)
    if open_tips.count() >= MAX_OPEN_TIPS:
        raise ValidationError("Tienes varias propinas pendientes. Paga o deja vencer alguna antes de preparar otra.")
    return Tip.objects.create(sender=actor, creator=creator, amount_sats=amount, message=" ".join(str(message or "").split())[:280],
                              lesson=lesson, version=lesson.chapter.version if lesson else None, expires_at=now + timedelta(minutes=15))


def emit_tip(tip, gateway):
    return emit_payment(tip, gateway, "Estamos comprobando la propina. Actualiza su estado para continuar.")


@transaction.atomic
def settle_tip(tip_id, provider_status):
    tip = Tip.objects.select_related("sender", "creator").get(pk=tip_id)
    if provider_status.payment_hash != tip.payment_hash:
        raise ValidationError("La confirmación pertenece a otro pago.")
    if tip.status == "paid":
        return tip
    now = timezone.now()
    # A tip grants no access, so a payment observed late is still the educator's.
    if provider_status.paid and provider_status.amount_msat == tip.amount_sats * 1000:
        Tip.objects.filter(pk=tip.pk).exclude(status="paid").update(status="paid", paid_at=now)
        from learning.support import notify
        notify(tip.creator, f"tip:{tip.pk}", f"Recibiste una propina de {tip.amount_sats} sats.", reverse("creator-tips"))
    elif tip.status == "pending" and tip.expires_at <= now:
        Tip.objects.filter(pk=tip.pk, status="pending").update(status="expired")
    elif tip.status == "pending" and provider_status.failed:
        Tip.objects.filter(pk=tip.pk, status="pending").update(status="failed")
    tip.refresh_from_db()
    return tip


def check_tip(tip, gateway=None, simulate=False):
    own_gateway = gateway is None
    gateway = gateway or LNbitsGateway()
    try:
        tip.refresh_from_db()
        if tip.status == "paid":
            return tip
        if tip.status == "pending" and tip.expires_at <= timezone.now() and not tip.payment_hash:
            Tip.objects.filter(pk=tip.pk, status="pending").update(status="expired")
            tip.refresh_from_db()
            return tip
        tip = emit_tip(tip, gateway)
        if not tip.payment_hash:
            return tip
        tip = settle_tip(tip.pk, gateway.status(tip))
        if simulate and tip.status == "pending":
            gateway.simulate(tip)
            tip = settle_tip(tip.pk, gateway.status(tip))
        return tip
    finally:
        if own_gateway:
            gateway.close()


def creator_tip_summary(creator):
    paid = Tip.objects.filter(creator=creator, status="paid")
    totals = paid.aggregate(count=Count("pk"), sats=Sum("amount_sats"))
    return {"count": totals["count"] or 0, "sats": totals["sats"] or 0,
            "recent": paid.select_related("sender", "lesson__content", "version").order_by("-paid_at", "-pk")}
