from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .catalog import available, ownership
from .gateway import LNbitsGateway, ProviderUnavailable
from .models import (
    CommerceEvent,
    Entitlement,
    EntitlementSource,
    Invoice,
    Offer,
    PaymentEvidence,
    Purchase,
)


def require_student(actor):
    if not actor.is_authenticated or not actor.is_active or actor.account_type != "student":
        raise PermissionDenied("Entra con tu cuenta de estudiante.")


def reserve_writer(buyer_id):
    # First statement inside atomic is a write. SQLite serializes competing writers
    # before any business read; select_for_update would not lock SQLite rows.
    get_user_model().objects.filter(pk=buyer_id).update(email=F("email"))


def event(invoice, kind, message):
    CommerceEvent.objects.get_or_create(invoice=invoice, kind=kind, defaults={"message": message})


@transaction.atomic
def reserve_invoice(actor, offer_id, activity_session=None):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    offer = Offer.objects.select_related("creator", "course_version__course", "resource").get(pk=offer_id)
    now = timezone.now()
    for old in Invoice.objects.filter(buyer=actor, logical_key=offer.logical_key, status="pending", expires_at__lte=now):
        Invoice.objects.filter(pk=old.pk, status="pending").update(status="expired")
        event(old, "expired", "La factura venció sin conceder acceso nuevo.")
    if not available(offer):
        raise ValidationError("Esta oferta ya no está disponible.")
    if ownership(actor, offer) != "none":
        raise ValidationError("Ya tienes contenido de esta oferta. Abre lo adquirido o compra únicamente los componentes que faltan.")
    pending = Invoice.objects.filter(buyer=actor, logical_key=offer.logical_key, status="pending").first()
    if pending:
        return pending
    inventory = [{"resource_id": item.resource_id, "title": item.resource.title, "kind": item.resource.kind, "paid": item.resource.access_type == "paid"} for item in offer.items.select_related("resource").order_by("resource_id")]
    invoice = Invoice.objects.create(buyer=actor, offer=offer, logical_key=offer.logical_key, title=offer.title, amount_sats=offer.amount_sats, inventory=inventory, expires_at=now + timedelta(minutes=15))
    event(invoice, "reserved", "Factura reservada por 15 minutos.")
    if activity_session and not actor.is_staff:
        from core.models import ActivityEvent
        ActivityEvent.objects.create(event_key=f"invoice:{invoice.pk}", kind="invoice_created", session_id=activity_session,
                                     actor=actor, creator=offer.creator, offer=offer, invoice=invoice, version=offer.course_version)
    return invoice


@transaction.atomic
def claim_emission(invoice_id):
    Invoice.objects.filter(pk=invoice_id).update(issue_state=F("issue_state"))
    invoice = Invoice.objects.get(pk=invoice_id)
    if invoice.status != "pending" or invoice.expires_at <= timezone.now() or invoice.issue_state != "new":
        return invoice, False
    Invoice.objects.filter(pk=invoice.pk).update(issue_state="requested")
    invoice.issue_state = "requested"
    return invoice, True


def ensure_emitted(invoice, gateway=None):
    own_gateway = gateway is None
    gateway = gateway or LNbitsGateway()
    try:
        invoice, claimed = claim_emission(invoice.pk)
        if claimed:
            try:
                result = gateway.create(invoice)
            except ProviderUnavailable:
                Invoice.objects.filter(pk=invoice.pk, issue_state="requested").update(issue_state="unknown", incident="emission_unknown")
                raise
        elif invoice.issue_state in ("requested", "unknown"):
            result = gateway.recover(invoice)
            if result is None:
                raise ProviderUnavailable("Estamos comprobando la factura. Actualiza su estado para continuar.")
        else:
            return invoice
        Invoice.objects.filter(pk=invoice.pk, payment_hash__isnull=True).update(payment_hash=result.payment_hash, payment_request=result.payment_request, issue_state="ready", incident="")
        invoice.refresh_from_db()
        return invoice
    finally:
        if own_gateway:
            gateway.close()


@transaction.atomic
def settle(invoice_id, provider_status, observed_at=None):
    # Never hold a database transaction while making a provider request.
    Invoice.objects.filter(pk=invoice_id).update(last_checked_at=timezone.now())
    invoice = Invoice.objects.select_related("buyer", "offer__course_version").get(pk=invoice_id)
    now = observed_at or timezone.now()
    if provider_status.payment_hash != invoice.payment_hash:
        raise ValidationError("La confirmación pertenece a otra factura.")
    if invoice.status == "paid":
        return invoice
    if not provider_status.paid:
        if invoice.status == "pending" and invoice.expires_at <= now:
            Invoice.objects.filter(pk=invoice.pk).update(status="expired")
            event(invoice, "expired", "La factura venció sin conceder acceso nuevo.")
        elif invoice.status == "pending" and provider_status.failed:
            Invoice.objects.filter(pk=invoice.pk).update(status="failed", incident="provider_failed")
            event(invoice, "failed", "No se pudo completar el pago.")
        invoice.refresh_from_db()
        return invoice
    if PaymentEvidence.objects.filter(invoice=invoice).exists():
        return invoice
    paid_ids = {item["resource_id"] for item in invoice.inventory if item["paid"]}
    reason = ("amount_mismatch" if provider_status.amount_msat != invoice.amount_sats * 1000
              else "late_payment" if invoice.expires_at <= now or invoice.status == "expired"
              else "closed_invoice" if invoice.status != "pending"
              else "inactive_buyer" if not invoice.buyer.is_active or invoice.buyer.account_type != "student"
              else "overlapping_payment" if Entitlement.objects.filter(buyer=invoice.buyer, resource_id__in=paid_ids).exists()
              else "accepted")
    PaymentEvidence.objects.create(invoice=invoice, payment_hash=invoice.payment_hash, amount_msat=provider_status.amount_msat, observed_at=now, resolution=reason)
    if reason != "accepted":
        Invoice.objects.filter(pk=invoice.pk).update(status="expired" if reason == "late_payment" else "failed", incident=reason)
        event(invoice, "incident", "Pago observado; requiere conciliación administrativa: " + reason)
    else:
        purchase = Purchase.objects.create(invoice=invoice)
        for item in invoice.inventory:
            right, _ = Entitlement.objects.get_or_create(buyer=invoice.buyer, resource_id=item["resource_id"])
            EntitlementSource.objects.create(entitlement=right, purchase=purchase)
        Invoice.objects.filter(pk=invoice.pk).update(status="paid", incident="")
        event(invoice, "paid", "Tu compra está confirmada. El contenido adquirido permanece en tu biblioteca.")
        if invoice.offer.course_version_id:
            from learning.models import Enrollment
            Enrollment.objects.get_or_create(student=invoice.buyer, version=invoice.offer.course_version)
    invoice.refresh_from_db()
    return invoice


def reconcile(invoice, gateway=None):
    expire_invoice(invoice.pk)
    own_gateway = gateway is None
    gateway = gateway or LNbitsGateway()
    try:
        invoice.refresh_from_db()
        if invoice.status == "paid" or PaymentEvidence.objects.filter(invoice=invoice).exists():
            return invoice
        invoice = ensure_emitted(invoice, gateway)
        if not invoice.payment_hash:
            return invoice
        return settle(invoice.pk, gateway.status(invoice))
    finally:
        if own_gateway:
            gateway.close()


@transaction.atomic
def expire_invoice(invoice_id):
    changed = Invoice.objects.filter(pk=invoice_id, status="pending", expires_at__lte=timezone.now()).update(status="expired")
    if changed:
        invoice = Invoice.objects.get(pk=invoice_id)
        event(invoice, "expired", "La factura venció sin conceder acceso nuevo.")


def simulate_payment(actor, invoice, gateway=None):
    require_student(actor)
    invoice.refresh_from_db()
    if invoice.buyer_id != actor.pk:
        raise PermissionDenied
    if invoice.status != "pending" or invoice.expires_at <= timezone.now():
        raise ValidationError("Esta factura ya terminó o venció. Revisa su estado antes de continuar.")
    own_gateway = gateway is None
    gateway = gateway or LNbitsGateway()
    try:
        invoice = ensure_emitted(invoice, gateway)
        # Check first so retries never pay an already successful invoice again.
        invoice = settle(invoice.pk, gateway.status(invoice))
        if invoice.status != "pending":
            return invoice
        paid_ids = {item["resource_id"] for item in invoice.inventory if item["paid"]}
        if Entitlement.objects.filter(buyer=actor, resource_id__in=paid_ids).exists():
            raise ValidationError("Ya adquiriste contenido de esta factura. Abre tu biblioteca o compra solo los componentes que faltan.")
        gateway.simulate(invoice)
        return reconcile(invoice, gateway)
    finally:
        if own_gateway:
            gateway.close()
