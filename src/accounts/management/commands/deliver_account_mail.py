import time
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import close_old_connections
from django.utils import timezone

from accounts.mail import deliver_mail, models_due
from accounts.models import AccessAttempt, AccountMail


class Command(BaseCommand):
    help = "Entrega correos de cuenta pendientes; --watch reintenta hasta detener con Ctrl+C."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)
        parser.add_argument("--watch", action="store_true")
        parser.add_argument("--interval", type=int, default=30)

    def handle(self, *args, **options):
        if not 1 <= options["limit"] <= 500 or not 1 <= options["interval"] <= 3600:
            raise CommandError("El lote debe estar entre 1 y 500 y la espera entre 1 y 3600 segundos.")
        try:
            while True:
                close_old_connections()
                pending = AccountMail.objects.filter(status__in=("pending", "failed")).filter(models_due(timezone.now())).order_by("created_at", "pk")[:options["limit"]]
                delivered = sum(deliver_mail(pk) for pk in list(pending.values_list("pk", flat=True)))
                # Counters contain only HMAC keys and have a short useful lifetime.
                AccessAttempt.objects.filter(window_started_at__lt=timezone.now() - timedelta(days=2)).delete()
                AccountMail.objects.filter(expires_at__lt=timezone.now()).exclude(body="").update(body="")
                self.stdout.write(f"Correos aceptados por el proveedor: {delivered}.")
                if not options["watch"]:
                    break
                time.sleep(options["interval"])
        except KeyboardInterrupt:
            self.stdout.write("Entrega detenida; puede reanudarse.")
