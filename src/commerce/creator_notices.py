"""Tell educators about sales and refunds of their content, without the student's identity."""
from django.urls import reverse
from django.utils.translation import gettext


def creator_shares(invoice):
    """Each educator in an invoice with their own titles and amount in sats."""
    if invoice.offer_id:
        return [(invoice.offer.creator, invoice.title, invoice.amount_sats)]
    shares = {}
    for line in invoice.order.lines.select_related("creator").order_by("pk"):
        creator, titles, amount = shares.get(line.creator_id, (line.creator, [], 0))
        shares[line.creator_id] = (creator, [*titles, line.title], amount + line.amount_sats)
    return [(creator, ", ".join(titles), amount) for creator, titles, amount in shares.values()]


def notify_creators(invoice, key, message):
    """Send one notice per educator; ``message`` receives title and amount_sats."""
    if invoice is None:
        # Membership periods belong to the platform plan, not to one educator.
        return
    from learning.support import notify
    url = reverse("creator-analytics")
    for creator, title, amount in creator_shares(invoice):
        notify(creator, f"{key}:{creator.pk}", message % {"title": title, "amount_sats": amount}, url)


def sale(invoice):
    notify_creators(invoice, f"sale:{invoice.pk}", gettext("Vendiste «%(title)s» por %(amount_sats)s sats."))


def refund_requested(refund):
    notify_creators(refund.invoice, f"refund-requested:{refund.pk}",
                    gettext("Se solicitó el reembolso de «%(title)s» (%(amount_sats)s sats)."))


def refund_resolved(refund):
    message = (gettext("Reembolsamos «%(title)s» (%(amount_sats)s sats).") if refund.status == "refunded"
               else gettext("Rechazamos el reembolso de «%(title)s»."))
    notify_creators(refund.invoice, f"refund-resolved:{refund.pk}", message)
