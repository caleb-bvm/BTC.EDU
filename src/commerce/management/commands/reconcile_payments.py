from django.core.management.base import BaseCommand
from django.utils import timezone

from commerce.gateway import ProviderUnavailable
from commerce.models import Invoice
from commerce.services import event, reconcile


class Command(BaseCommand):
    help = "Concilia facturas de prueba pendientes y evidencia tardía, sin depender del navegador."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        invoices = Invoice.objects.exclude(status="paid").filter(evidence__isnull=True).order_by("last_checked_at", "created_at")[:max(1, min(options["limit"], 1000))]
        checked = unknown = 0
        for invoice in invoices:
            if invoice.status == "pending" and invoice.expires_at <= timezone.now():
                Invoice.objects.filter(pk=invoice.pk, status="pending").update(status="expired")
                event(invoice, "expired", "La factura venció sin conceder acceso nuevo.")
            try:
                reconcile(invoice)
                checked += 1
            except ProviderUnavailable:
                Invoice.objects.filter(pk=invoice.pk).update(last_checked_at=timezone.now())
                unknown += 1
        self.stdout.write(f"Facturas conciliadas: {checked}; sin respuesta confirmada: {unknown}.")
