from datetime import timedelta

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


class InvoiceJourneyMigrationTests(TransactionTestCase):
    def test_grouped_order_migration_preserves_legacy_paid_purchase_and_rights(self):
        executor = MigrationExecutor(connection)
        previous = [node for node in executor.loader.graph.leaf_nodes() if node[0] != "commerce"] + [("commerce", "0003_invoice_return_lesson")]
        executor.migrate(previous)
        old = executor.loader.project_state(previous).apps
        try:
            user = old.get_model("accounts", "User").objects.create(email="orders-migration@example.invalid", account_type="student")
            resource = old.get_model("content", "ResourceVersion").objects.create(creator_id=user.pk, kind="text", title="Revisión histórica", access_type="paid", body="Texto conservado")
            offer = old.get_model("commerce", "Offer").objects.create(creator_id=user.pk, title="Compra histórica", amount_sats=75, kind="resource", logical_key="migration:paid", resource_id=resource.pk)
            old.get_model("commerce", "OfferItem").objects.create(offer_id=offer.pk, resource_id=resource.pk)
            inventory = [{"resource_id": resource.pk, "title": resource.title, "kind": "text", "paid": True}]
            invoice = old.get_model("commerce", "Invoice").objects.create(buyer_id=user.pk, offer_id=offer.pk, title=offer.title, logical_key=offer.logical_key,
                amount_sats=75, inventory=inventory, payment_hash="d" * 64, issue_state="ready", status="paid", expires_at=timezone.now() + timedelta(minutes=15))
            purchase = old.get_model("commerce", "Purchase").objects.create(invoice_id=invoice.pk)
            right = old.get_model("commerce", "Entitlement").objects.create(buyer_id=user.pk, resource_id=resource.pk)
            old.get_model("commerce", "EntitlementSource").objects.create(entitlement_id=right.pk, purchase_id=purchase.pk)
            old.get_model("commerce", "PaymentEvidence").objects.create(invoice_id=invoice.pk, payment_hash=invoice.payment_hash, amount_msat=75000, observed_at=timezone.now(), resolution="accepted")
            before = {name: list(old.get_model("commerce", name).objects.values().order_by("pk"))
                      for name in ("Invoice", "Offer", "OfferItem", "Purchase", "Entitlement", "EntitlementSource", "PaymentEvidence")}
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
            current = executor.loader.project_state(executor.loader.graph.leaf_nodes()).apps
            for name, rows in before.items():
                fields = list(rows[0])
                self.assertEqual(list(current.get_model("commerce", name).objects.values(*fields).order_by("pk")), rows)
            self.assertIsNone(current.get_model("commerce", "Invoice").objects.get(pk=invoice.pk).order_id)
            for name in ("Cart", "CartItem", "Order", "OrderLine"):
                self.assertFalse(current.get_model("commerce", name).objects.exists())
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_key_check")
                self.assertEqual(cursor.fetchall(), [])
                cursor.execute("PRAGMA integrity_check")
                self.assertEqual(cursor.fetchone(), ("ok",))
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())

    def test_existing_invoice_keeps_snapshot_and_nullable_destination(self):
        executor = MigrationExecutor(connection)
        previous = [node for node in executor.loader.graph.leaf_nodes() if node[0] != "commerce"] + [("commerce", "0002_remove_invoice_one_pending_invoice_per_offer_and_more")]
        executor.migrate(previous)
        old = executor.loader.project_state(previous).apps
        user = old.get_model("accounts", "User").objects.create(email="migration@example.invalid", account_type="student")
        offer = old.get_model("commerce", "Offer").objects.create(creator_id=user.pk, title="Oferta conservada", amount_sats=75, kind="course", logical_key="migration:original")
        inventory = [{"resource_id": 12, "title": "Contenido conservado", "kind": "text", "paid": True}]
        invoice = old.get_model("commerce", "Invoice").objects.create(buyer_id=user.pk, offer_id=offer.pk, title=offer.title, logical_key=offer.logical_key,
                                                                         amount_sats=75, inventory=inventory, expires_at=timezone.now() + timedelta(minutes=15))
        try:
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
            from .models import Invoice
            migrated = Invoice.objects.get(pk=invoice.pk)
            self.assertIsNone(migrated.return_lesson_id)
            self.assertEqual((migrated.title, migrated.amount_sats, migrated.inventory, migrated.status), ("Oferta conservada", 75, inventory, "pending"))
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
