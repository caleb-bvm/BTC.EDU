"""Shared reservations for legacy invoices and grouped orders, without I/O."""
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Invoice


def payment_resources(invoice):
    return {item["resource_id"] for item in invoice.inventory if item.get("paid")}


def needs_reservation(invoice, now=None):
    now = now or timezone.now()
    if invoice.status == "paid":
        return False
    if invoice.issue_state in ("requested", "unknown"):
        return True
    if invoice.incident and invoice.incident not in ("emission_unknown", "provider_failed"):
        return True
    if invoice.status == "pending" and invoice.expires_at > now:
        return True
    # Issued invoices are not safely abandoned until checked after their expiry.
    return bool(invoice.payment_hash and invoice.incident != "provider_failed"
                and (invoice.last_checked_at is None or invoice.last_checked_at < invoice.expires_at))


def overlapping_invoice(actor, resource_ids, exclude=None):
    resources = set(resource_ids)
    if not resources:
        return None
    # Gifts never grant the buyer access, so they do not reserve the buyer's content.
    invoices = Invoice.objects.filter(buyer=actor).exclude(status="paid").exclude(order__gift=True).order_by("created_at", "pk")
    if exclude:
        invoices = invoices.exclude(pk=exclude)
    now = timezone.now()
    return next((invoice for invoice in invoices if needs_reservation(invoice, now) and resources & payment_resources(invoice)), None)


def require_unreserved(actor, resource_ids, exclude=None):
    invoice = overlapping_invoice(actor, resource_ids, exclude)
    if invoice:
        raise ValidationError("Hay un pago pendiente o en revisión para parte de esta selección. Consulta esa factura antes de preparar otro pago.", code="pending_overlap")
