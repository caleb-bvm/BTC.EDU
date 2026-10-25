"""Issue invoices for Lightning payments that are not content orders (tips, memberships)."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .gateway import ProviderUnavailable


@transaction.atomic
def claim_emission(model, pk):
    # Writing first serializes concurrent requests before the state is read.
    model.objects.filter(pk=pk).update(issue_state=F("issue_state"))
    payment = model.objects.get(pk=pk)
    if payment.status != "pending" or payment.expires_at <= timezone.now() or payment.issue_state != "new":
        return payment, False
    claimed = model.objects.filter(pk=pk, issue_state="new").update(issue_state="requested")
    payment.refresh_from_db()
    return payment, bool(claimed)


def emit_payment(payment, gateway, pending_message):
    """Request the invoice once; an unknown outcome is recovered, never issued again."""
    model = type(payment)
    payment, claimed = claim_emission(model, payment.pk)
    if claimed:
        try:
            result = gateway.create(payment)
        except ProviderUnavailable:
            model.objects.filter(pk=payment.pk, issue_state="requested").update(issue_state="unknown")
            raise
    elif payment.issue_state in ("requested", "unknown"):
        result = gateway.recover(payment)
        if result is None:
            raise ProviderUnavailable(pending_message)
    else:
        return payment
    model.objects.filter(pk=payment.pk, payment_hash__isnull=True).update(
        payment_hash=result.payment_hash, payment_request=result.payment_request, issue_state="ready")
    payment.refresh_from_db()
    return payment
