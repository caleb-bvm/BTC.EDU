import time

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import close_old_connections
from django.utils import timezone

from commerce.gateway import ProviderUnavailable
from commerce.models import Invoice
from commerce.services import reconcile


class Command(BaseCommand):
    help = "Concilia facturas y evidencia tardía; --watch repite la consulta sin depender del navegador."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--watch", action="store_true", help="Repetir hasta detener con Ctrl+C.")
        parser.add_argument("--interval", type=int, default=30, help="Segundos de espera entre lotes (1–3600).")

    def handle(self, *args, **options):
        if not 1 <= options["limit"] <= 1000:
            raise CommandError("--limit debe estar entre 1 y 1000.")
        if not 1 <= options["interval"] <= 3600:
            raise CommandError("--interval debe estar entre 1 y 3600 segundos.")
        try:
            while True:
                close_old_connections()
                self.reconcile_batch(options["limit"])
                if not options["watch"]:
                    break
                close_old_connections()
                time.sleep(options["interval"])
        except KeyboardInterrupt:
            self.stdout.write("Conciliación detenida. Puede reanudarse con el mismo comando.")
        finally:
            close_old_connections()

    def reconcile_batch(self, limit):
        # Materialize before writing so each batch has a stable, bounded inventory.
        invoices = list(Invoice.objects.exclude(status="paid").filter(evidence__isnull=True)
                        .order_by("last_checked_at", "created_at", "pk")[:limit])
        checked = unknown = invalid = 0
        for invoice in invoices:
            try:
                reconcile(invoice)
                checked += 1
            except ProviderUnavailable:
                unknown += 1
            except ValidationError:
                invalid += 1
                self.stderr.write(f"Factura {invoice.pk}: confirmación inválida; requiere revisión.")
            finally:
                # Also rotate invoices with no hash or a failed provider request.
                # Otherwise a full batch of never-issued invoices can starve payments.
                Invoice.objects.filter(pk=invoice.pk).update(last_checked_at=timezone.now())
        stamp = timezone.localtime().isoformat(timespec="seconds")
        self.stdout.write(f"{stamp} · Facturas conciliadas: {checked}; sin respuesta confirmada: {unknown}; inválidas: {invalid}.")
        self.stdout.flush()
