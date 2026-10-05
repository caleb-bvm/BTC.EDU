"""End-to-end real LNbits API, temporary platform database and fictitious funds."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="commerce-smoke-", dir=ROOT / ".local") as temporary:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(temporary) / "platform.sqlite3")
        import django
        django.setup()
        from demo_commerce import seed
        from django.core.management import call_command
        from django.db import connections
        from django.test import Client, override_settings
        from django.urls import reverse

        from commerce.gateway import LNbitsGateway, ProviderUnavailable
        from commerce.models import Entitlement, Invoice, PaymentEvidence, Purchase
        from commerce.services import (
            ensure_emitted,
            reconcile,
            reserve_invoice,
            simulate_payment,
        )

        with override_settings(MEDIA_ROOT=Path(temporary) / "media", SECURE_SSL_REDIRECT=False, ALLOWED_HOSTS=["testserver", "127.0.0.1"]):
            gateway = None
            try:
                call_command("migrate", verbosity=0)
                data = seed()
                gateway = LNbitsGateway()
                gateway.ensure_fake_wallet()
                invoice = ensure_emitted(reserve_invoice(data.student, data.bundle.pk), gateway)
                assert not gateway.status(invoice).paid
                invoice = simulate_payment(data.student, invoice, gateway)
                invoice = reconcile(invoice, gateway)
                assert invoice.status == "paid" and Purchase.objects.count() == 1 and Entitlement.objects.count() == 4
                client = Client()
                client.force_login(data.student)
                assert client.get(reverse("version-lesson", args=[data.course.pk, data.version.number, data.records[1].pk])).status_code == 200
                assert client.get(reverse("workspace")).status_code == 200
                # A response lost after external creation is recovered by its stored
                # external_id; no second provider emission is attempted.
                unknown = reserve_invoice(data.other, data.individual.pk)
                create = gateway.create
                def lose_response(invoice):
                    create(invoice)
                    raise ProviderUnavailable("Respuesta perdida de forma controlada")
                gateway.create = lose_response
                try:
                    ensure_emitted(unknown, gateway)
                except ProviderUnavailable:
                    pass
                gateway.create = create
                unknown = ensure_emitted(unknown, gateway)
                assert unknown.issue_state == "ready"
                assert gateway.recover(unknown).payment_hash == unknown.payment_hash
                browser_contract = Client(enforce_csrf_checks=True)
                browser_contract.force_login(data.other)
                browser_contract.get(reverse("offer-detail", args=[data.individual.pk]))
                from django.conf import settings
                csrf = browser_contract.cookies[settings.CSRF_COOKIE_NAME].value
                response = browser_contract.post(reverse("invoice-action", args=[unknown.pk]), {"action": "pay", "csrfmiddlewaretoken": csrf})
                assert response.status_code == 302
                unknown.refresh_from_db()
                assert unknown.status == "paid" and Purchase.objects.count() == 2 and PaymentEvidence.objects.count() == 2
                assert Invoice.objects.count() == 2
                assert browser_contract.get(reverse("invoice-detail", args=[unknown.pk])).status_code == 200
                print("OK: LNbits FakeWallet real; factura pendiente -> pagada; derechos, biblioteca e idempotencia comprobados.")
                print("OK: respuesta perdida recuperada por external_id; pago mediante vista autenticada y CSRF, sin segunda factura.")
                print("Base y archivos de plataforma temporales; la base principal permanece intacta.")
            finally:
                if gateway:
                    gateway.close()
                connections.close_all()


if __name__ == "__main__":
    run()
