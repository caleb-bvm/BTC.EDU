"""Refunds paid over Lightning after an administrator approves them.

Access granted only by a refunded purchase ends (see EntitlementQuerySet.active);
the purchase, payment evidence and learning history are kept.
"""
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone

from .bolt11 import normalized, requested_msat
from .gateway import LNbitsGateway, ProviderUnavailable
from .models import Invoice, OrderLine, Refund
from .services import require_student, reserve_writer


def paid_ids(invoice):
    return {item["resource_id"] for item in invoice.inventory if item.get("paid")}


def refund_blocker(invoice, user, now=None):
    """Why this paid invoice cannot be refunded, or an empty string."""
    now = now or timezone.now()
    if invoice.buyer_id != user.pk or invoice.status != "paid" or not hasattr(invoice, "purchase"):
        return "Solo puedes solicitar el reembolso de una compra confirmada."
    if hasattr(invoice, "refund"):
        return "Ya existe una solicitud de reembolso para esta compra."
    if invoice.order_id and invoice.order.gift:
        return "Los regalos no admiten reembolso desde esta página."
    if invoice.purchase.created_at + timedelta(days=settings.COMMERCE_REFUND_DAYS) < now:
        return f"El plazo de reembolso es de {settings.COMMERCE_REFUND_DAYS} días desde la compra."
    from learning.models import Certificate
    versions = {invoice.offer.course_version_id} if invoice.offer_id and invoice.offer.course_version_id else set()
    if invoice.order_id:
        versions |= set(invoice.order.lines.exclude(course_version=None).values_list("course_version_id", flat=True))
    if versions and Certificate.objects.filter(enrollment__student=user, enrollment__version_id__in=versions).exists():
        return "Ya obtuviste un certificado con este contenido."
    bought = paid_ids(invoice)
    # Content credited toward a later package keeps that package price coherent.
    for line in OrderLine.objects.filter(order__buyer=user, credit_sats__gt=0, order__invoice__status="paid",
                                         order__created_at__gt=invoice.created_at).select_related("offer"):
        if bought & set(line.offer.items.values_list("resource_id", flat=True)):
            return "Este contenido se reconoció como crédito en una compra posterior."
    return ""


@transaction.atomic
def request_refund(actor, invoice_id, reason, payment_request):
    require_student(actor)
    reserve_writer(actor.pk)
    invoice = Invoice.objects.select_related("order", "offer", "purchase").get(pk=invoice_id, buyer=actor)
    blocker = refund_blocker(invoice, actor)
    if blocker:
        raise ValidationError(blocker)
    reason = " ".join(str(reason or "").split())
    if not 10 <= len(reason) <= 1000:
        raise ValidationError("Explica el motivo en al menos 10 caracteres.")
    request = normalized(payment_request)
    if requested_msat(request) != invoice.amount_sats * 1000:
        raise ValidationError(f"Pega una factura Lightning de tu wallet por exactamente {invoice.amount_sats} sats.")
    refund = Refund.objects.create(invoice=invoice, buyer=actor, amount_sats=invoice.amount_sats, reason=reason, payment_request=request)
    return refund


def require_reviewer(actor):
    if not actor.is_authenticated or not actor.is_active or not actor.is_staff or not actor.has_perm("commerce.decide_refund"):
        raise PermissionDenied


@transaction.atomic
def claim_refund(actor, refund_id, note):
    require_reviewer(actor)
    Refund.objects.filter(pk=refund_id).update(status=F("status"))
    refund = Refund.objects.get(pk=refund_id)
    if refund.status != "requested":
        raise ValidationError("La solicitud ya fue revisada.")
    Refund.objects.filter(pk=refund.pk).update(status="paying", decided_by=actor, decided_at=timezone.now(), decision_note=note[:500])
    refund.refresh_from_db()
    return refund


@transaction.atomic
def finish_refund(refund_id, payment_hash):
    Refund.objects.filter(pk=refund_id, status="paying").update(status="refunded", payment_hash=payment_hash, refunded_at=timezone.now())
    refund = Refund.objects.select_related("buyer").get(pk=refund_id)
    from learning.support import notify
    notify(refund.buyer, f"refund:{refund.pk}", f"Reembolsamos {refund.amount_sats} sats a tu wallet.", reverse("invoice-detail", args=[refund.invoice_id]))
    return refund


def approve_refund(actor, refund, note="", gateway=None):
    require_reviewer(actor)
    if not settings.LNBITS_REFUND_KEY:
        raise ValidationError("Los reembolsos por Lightning no están configurados en este entorno.")
    refund = claim_refund(actor, refund.pk, " ".join(str(note or "").split()))
    own_gateway = gateway is None
    try:
        gateway = gateway or LNbitsGateway()
        payment_hash = gateway.pay(refund.payment_request)
    except ProviderUnavailable:
        # The outcome is unknown: keep access until someone reconciles the payment.
        Refund.objects.filter(pk=refund.pk, status="paying").update(status="review")
        refund.refresh_from_db()
        return refund
    finally:
        if own_gateway and gateway is not None:
            gateway.close()
    return finish_refund(refund.pk, payment_hash)


@transaction.atomic
def reject_refund(actor, refund, note):
    require_reviewer(actor)
    note = " ".join(str(note or "").split())
    if not note:
        raise ValidationError("Explica al estudiante por qué no procede el reembolso.")
    if not Refund.objects.filter(pk=refund.pk, status__in=("requested", "review")).update(
            status="rejected", decided_by=actor, decided_at=timezone.now(), decision_note=note[:500]):
        raise ValidationError("La solicitud ya fue revisada.")
    refund.refresh_from_db()
    from learning.support import notify
    notify(refund.buyer, f"refund-rejected:{refund.pk}", "Revisamos tu solicitud de reembolso.", reverse("invoice-detail", args=[refund.invoice_id]))
    return refund


@transaction.atomic
def confirm_reviewed_refund(actor, refund, payment_hash):
    """Close a refund whose payment an administrator confirmed in the wallet."""
    require_reviewer(actor)
    if refund.status != "review" or not payment_hash or len(payment_hash) != 64:
        raise ValidationError("Indica el hash del pago confirmado en la wallet.")
    Refund.objects.filter(pk=refund.pk, status="review").update(status="paying")
    return finish_refund(refund.pk, payment_hash.lower())
