import uuid
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from content.models import ResourceVersion

from .gateway import ProviderStatus, ProviderUnavailable
from .models import Entitlement, Invoice, Offer, PaymentEvidence, Purchase


class ReconciliationTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("reconciliation-creator@example.invalid", account_type="creator")
        self.buyer = users.create_user("reconciliation-buyer@example.invalid")
        self.resource = ResourceVersion.objects.create(resource_key=uuid.uuid4(), number=1, creator=self.creator,
                                                        title="Material", body="Contenido", kind="text", access_type="paid")
        self.offer = Offer.objects.create(creator=self.creator, title="Material", amount_sats=10,
                                          kind="resource", resource=self.resource, logical_key="reconciliation")

    def invoice(self, **fields):
        values = dict(buyer=self.buyer, offer=self.offer, logical_key="reconciliation", title="Material",
                      amount_sats=10, inventory=[{"resource_id": self.resource.pk, "paid": True}],
                      expires_at=timezone.now() + timedelta(minutes=15), issue_state="ready")
        values.update(fields)
        invoice = Invoice.objects.create(**values)
        if invoice.issue_state == "ready":
            Invoice.objects.filter(pk=invoice.pk).update(payment_hash=invoice.pk.hex * 2)
            invoice.refresh_from_db()
        return invoice

    def run_command(self, **options):
        output, errors = StringIO(), StringIO()
        call_command("reconcile_payments", stdout=output, stderr=errors, **options)
        return output.getvalue(), errors.getvalue()

    @staticmethod
    def paid(invoice):
        return ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash)

    @patch("commerce.services.LNbitsGateway")
    def test_one_pass_confirms_without_browser_and_is_idempotent(self, gateway):
        invoice = self.invoice()
        gateway.return_value.status.side_effect = self.paid
        self.run_command()
        self.run_command()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(Entitlement.objects.count(), 1)
        self.assertEqual(PaymentEvidence.objects.count(), 1)
        gateway.return_value.status.assert_called_once()
        self.assertIsNotNone(invoice.last_checked_at)

    @patch("commerce.management.commands.reconcile_payments.time.sleep", side_effect=[None, KeyboardInterrupt])
    @patch("commerce.services.LNbitsGateway")
    def test_watch_recovers_after_provider_outage(self, gateway, sleep):
        invoice = self.invoice()
        gateway.return_value.status.side_effect = [ProviderUnavailable("offline"), self.paid(invoice)]
        output, _ = self.run_command(watch=True, interval=7)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertIn("sin respuesta confirmada: 1", output)
        self.assertIn("Conciliación detenida", output)
        self.assertEqual(sleep.call_count, 2)
        sleep.assert_called_with(7)
        self.assertEqual(gateway.return_value.close.call_count, 2)

    @patch("commerce.services.LNbitsGateway")
    def test_expired_unissued_invoice_does_not_starve_next_batch(self, gateway):
        stale = self.invoice(issue_state="new", expires_at=timezone.now() - timedelta(seconds=1))
        Invoice.objects.filter(pk=stale.pk).update(created_at=timezone.now() - timedelta(minutes=20))
        paid = self.invoice(logical_key="another")
        gateway.return_value.status.side_effect = self.paid
        self.run_command(limit=1)
        self.assertEqual(Purchase.objects.count(), 0)
        self.run_command(limit=1)
        stale.refresh_from_db()
        paid.refresh_from_db()
        self.assertEqual(stale.status, "expired")
        self.assertIsNotNone(stale.last_checked_at)
        self.assertEqual(paid.status, "paid")

    @patch("commerce.services.LNbitsGateway")
    def test_late_payment_is_retained_without_access(self, gateway):
        invoice = self.invoice(expires_at=timezone.now() - timedelta(seconds=1))
        gateway.return_value.status.side_effect = self.paid
        self.run_command()
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "expired")
        self.assertEqual(invoice.evidence.resolution, "late_payment")
        self.assertFalse(Purchase.objects.exists())
        self.assertFalse(Entitlement.objects.exists())
        self.run_command()
        gateway.return_value.status.assert_called_once()

    @patch("commerce.services.LNbitsGateway")
    def test_invalid_confirmation_does_not_block_other_invoices(self, gateway):
        invalid = self.invoice()
        valid = self.invoice(logical_key="another")
        gateway.return_value.status.side_effect = [ProviderStatus(True, 10000, "wrong-hash"), self.paid(valid)]
        output, errors = self.run_command()
        invalid.refresh_from_db()
        valid.refresh_from_db()
        self.assertEqual(invalid.status, "pending")
        self.assertFalse(PaymentEvidence.objects.filter(invoice=invalid).exists())
        self.assertEqual(valid.status, "paid")
        self.assertIn(str(invalid.pk), errors)
        self.assertIn("inválidas: 1", output)

    @patch("commerce.services.LNbitsGateway")
    def test_empty_batch_does_not_contact_provider(self, gateway):
        output, _ = self.run_command()
        gateway.assert_not_called()
        self.assertIn("Facturas conciliadas: 0", output)

    def test_invalid_options_fail_before_processing(self):
        for options in ({"limit": 0}, {"limit": 1001}, {"interval": 0}, {"interval": 3601}):
            with self.subTest(options=options), self.assertRaises(CommandError):
                self.run_command(**options)

    @patch("commerce.management.commands.reconcile_payments.time.sleep", side_effect=KeyboardInterrupt)
    def test_watch_empty_batch_can_be_stopped(self, sleep):
        output, _ = self.run_command(watch=True)
        self.assertIn("Conciliación detenida", output)
        sleep.assert_called_once_with(30)
