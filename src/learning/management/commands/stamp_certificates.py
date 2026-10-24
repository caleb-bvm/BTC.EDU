from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from learning.models import Certificate, CertificateTimestamp
from learning.timestamps import stamp_certificate, upgrade_record


class Command(BaseCommand):
    help = "Sella en Bitcoin las huellas de certificados con OpenTimestamps y actualiza las pruebas pendientes."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)

    def handle(self, *args, **options):
        if not 1 <= options["limit"] <= 500:
            raise CommandError("--limit debe estar entre 1 y 500.")
        if not settings.CERTIFICATE_TIMESTAMPS:
            raise CommandError("Activa CERTIFICATE_TIMESTAMPS=true para usar los calendarios de OpenTimestamps.")
        pending = Certificate.objects.filter(timestamp__isnull=True, revocation__isnull=True).select_related("enrollment__version").order_by("issued_at")[:options["limit"]]
        stamped = sum(stamp_certificate(certificate) is not None for certificate in list(pending))
        confirmed = 0
        for record in list(CertificateTimestamp.objects.filter(bitcoin_height__isnull=True).order_by("submitted_at")[:options["limit"]]):
            confirmed += upgrade_record(record).bitcoin_height is not None
        self.stdout.write(f"Sellos enviados: {stamped}. Pruebas confirmadas en Bitcoin: {confirmed}.")
