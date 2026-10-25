"""Membership: paid periods that open the paid lessons of courses marked for membership."""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max, Min, Q
from django.urls import reverse
from django.utils import timezone

from .gateway import LNbitsGateway
from .lightning import emit_payment
from .models import MembershipPayment, MembershipPlan
from .services import require_student, reserve_writer

MAX_OPEN_PAYMENTS = 3
LATE_PAYMENT_WINDOW = timedelta(days=1)


def membership_until(user):
    """End of the member's continuous access, or None when no paid period covers now."""
    if not user.is_authenticated or not user.is_active or user.account_type != "student":
        return None
    now = timezone.now()
    # Renewals start where the previous period ends, so open periods are contiguous.
    period = MembershipPayment.objects.filter(member=user, status="paid", ends_at__gt=now).aggregate(start=Min("starts_at"), end=Max("ends_at"))
    return period["end"] if period["start"] and period["start"] <= now else None


def course_in_membership(version):
    course = version.course
    return course.membership and course.status == "published" and course.current_version_id == version.pk


def available_plans():
    return MembershipPlan.objects.filter(active=True)


def membership_offer(user, version):
    """What the course and lesson pages show about membership, or None when it does not apply."""
    if not course_in_membership(version):
        return None
    plan = available_plans().first()
    until = membership_until(user)
    if plan is None and until is None:
        return None
    return {"plan": plan, "until": until}


@transaction.atomic
def create_membership_payment(actor, plan):
    require_student(actor)
    reserve_writer(actor.pk)
    plan = available_plans().filter(pk=plan.pk).first()
    if plan is None:
        raise ValidationError("Este plan ya no está disponible.")
    now = timezone.now()
    open_payments = MembershipPayment.objects.filter(member=actor, status="pending", expires_at__gt=now)
    # Pressing the button again reuses the open invoice instead of issuing another one.
    existing = open_payments.filter(plan=plan).first()
    if existing:
        return existing
    if open_payments.count() >= MAX_OPEN_PAYMENTS:
        raise ValidationError("Tienes varios pagos de membresía pendientes. Paga o deja vencer alguno antes de preparar otro.")
    return MembershipPayment.objects.create(member=actor, plan=plan, amount_sats=plan.amount_sats, days=plan.days,
                                            expires_at=now + timedelta(minutes=15))


def emit_membership(payment, gateway):
    return emit_payment(payment, gateway, "Estamos comprobando el pago de tu membresía. Actualiza su estado para continuar.")


def settle_membership(payment_id, provider_status):
    member_id = MembershipPayment.objects.values_list("member_id", flat=True).get(pk=payment_id)
    with transaction.atomic():
        # One writer per member, so two renewals never compute the same period.
        reserve_writer(member_id)
        payment = MembershipPayment.objects.select_related("member").get(pk=payment_id)
        if provider_status.payment_hash != payment.payment_hash:
            raise ValidationError("La confirmación pertenece a otro pago.")
        if payment.status == "paid":
            return payment
        now = timezone.now()
        if provider_status.paid and provider_status.amount_msat == payment.amount_sats * 1000:
            # A payment observed late still buys a full period, counted from its confirmation.
            latest = MembershipPayment.objects.filter(member_id=member_id, status="paid").aggregate(end=Max("ends_at"))["end"]
            starts_at = max(now, latest) if latest else now
            ends_at = starts_at + timedelta(days=payment.days)
            MembershipPayment.objects.filter(pk=payment.pk).exclude(status="paid").update(
                status="paid", paid_at=now, starts_at=starts_at, ends_at=ends_at)
            from learning.support import notify
            notify(payment.member, f"membership:{payment.pk}",
                   f"Tu membresía está activa hasta el {timezone.localtime(ends_at):%d/%m/%Y}.", reverse("membership"))
        elif payment.status == "pending" and payment.expires_at <= now:
            MembershipPayment.objects.filter(pk=payment.pk, status="pending").update(status="expired")
        elif payment.status == "pending" and provider_status.failed:
            MembershipPayment.objects.filter(pk=payment.pk, status="pending").update(status="failed")
        payment.refresh_from_db()
        return payment


def check_membership(payment, gateway=None, simulate=False):
    own_gateway = gateway is None
    gateway = gateway or LNbitsGateway()
    try:
        payment.refresh_from_db()
        if payment.status == "paid":
            return payment
        if payment.status == "pending" and payment.expires_at <= timezone.now() and not payment.payment_hash:
            MembershipPayment.objects.filter(pk=payment.pk, status="pending").update(status="expired")
            payment.refresh_from_db()
            return payment
        if payment.status != "pending" and not payment.payment_hash:
            return payment
        payment = emit_membership(payment, gateway) if payment.status == "pending" else payment
        if not payment.payment_hash:
            return payment
        payment = settle_membership(payment.pk, gateway.status(payment))
        if simulate and payment.status == "pending":
            gateway.simulate(payment)
            payment = settle_membership(payment.pk, gateway.status(payment))
        return payment
    finally:
        if own_gateway:
            gateway.close()


def payments_to_reconcile(limit):
    """Pending payments, and recently expired invoices that may still be paid late."""
    recent = timezone.now() - LATE_PAYMENT_WINDOW
    return list(MembershipPayment.objects.filter(Q(status="pending") | Q(status="expired", payment_hash__isnull=False, expires_at__gt=recent))
                .order_by("created_at", "pk")[:limit])
