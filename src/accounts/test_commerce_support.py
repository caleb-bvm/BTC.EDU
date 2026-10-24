import tempfile
from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from commerce.models import Entitlement, Invoice, Offer, Order
from content.models import Material
from content.publication import publish_resource
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile
from media.models import Asset

from .models import AccountSupportRequest, SupportEvent
from .support import review_support


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_SEND_EMAIL=False,
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CommerceSupportTests(TestCase):
    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        users = get_user_model().objects
        self.student = users.create_user("buyer@context-support.invalid")
        self.other = users.create_user("other@context-support.invalid")
        self.creator = users.create_user("author@context-support.invalid", account_type="creator")
        self.admin = users.create_superuser("admin@context-support.invalid")
        CreatorProfile.objects.create(user=self.creator, display_name="Educador", status="approved")
        asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("guia.txt", b"Material privado"))
        item = Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, title="Guía adquirida", description="Material", access_type="paid", pending_asset=asset)
        self.resource = publish_resource(item, self.admin)
        offer = Offer.objects.create(creator=self.creator, title="Oferta de guía", amount_sats=150, kind="resource", resource=self.resource, logical_key=f"resource:{self.resource.pk}")
        self.invoice = Invoice.objects.create(buyer=self.student, offer=offer, title="Compra comprobada", amount_sats=150, inventory=[self.resource.pk], expires_at=timezone.now() + timedelta(minutes=15))
        self.second = Invoice.objects.create(buyer=self.student, offer=offer, title="Otra referencia comprobada", amount_sats=150, inventory=[self.resource.pk], expires_at=timezone.now() + timedelta(minutes=15), logical_key="second-reference")
        Entitlement.objects.create(buyer=self.student, resource=self.resource)
        self.client.force_login(self.student)
        self.url = reverse("student-account-support")

    def test_owned_reference_is_read_only_and_unowned_context_reveals_nothing(self):
        page = self.client.get(self.url, {"factura": self.invoice.pk})
        self.assertContains(page, self.invoice.title)
        self.assertContains(page, f'name="factura" value="{self.invoice.pk}"')
        self.assertFalse(AccountSupportRequest.objects.exists())
        self.client.force_login(self.other)
        denied = self.client.get(self.url, {"factura": self.invoice.pk})
        self.assertEqual(denied.status_code, 404)
        self.assertNotContains(denied, self.invoice.title, status_code=404)
        self.assertNotContains(denied, self.student.email, status_code=404)
        self.assertEqual(self.client.get(self.url, {"recurso": self.resource.pk}).status_code, 404)
        self.assertEqual(self.client.get(self.url, {"factura": "malformed"}).status_code, 404)
        self.assertFalse(AccountSupportRequest.objects.exists())

    def test_context_is_derived_by_server_and_valid_retry_creates_one_request(self):
        key = uuid4()
        data = {"factura": self.invoice.pk, "kind": "other", "body": "Conserva mi consulta.", "request_key": key,
                "title": "REFERENCIA_FALSA", "buyer": self.other.pk}
        for _ in range(2):
            self.assertEqual(self.client.post(self.url, data).status_code, 302)
        item = AccountSupportRequest.objects.get()
        self.assertEqual(item.user_id, self.student.pk)
        self.assertIn(str(self.invoice.pk), item.body)
        self.assertIn(self.invoice.title, item.body)
        self.assertTrue(item.body.endswith("Conserva mi consulta."))
        self.assertNotIn("REFERENCIA_FALSA", item.body)
        self.assertEqual(SupportEvent.objects.count(), 1)
        changed = self.client.post(self.url, {**data, "factura": self.second.pk})
        self.assertContains(changed, "Este envío ya fue utilizado")
        item.refresh_from_db()
        self.assertNotIn(self.second.title, item.body)
        self.assertEqual(AccountSupportRequest.objects.count(), 1)

    def test_foreign_post_is_denied_and_invalid_body_keeps_verified_context(self):
        data = {"factura": self.invoice.pk, "kind": "other", "body": "", "request_key": uuid4()}
        invalid = self.client.post(self.url, data)
        self.assertContains(invalid, self.invoice.title)
        self.assertContains(invalid, f'name="factura" value="{self.invoice.pk}"')
        self.assertFalse(AccountSupportRequest.objects.exists())
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.url, {**data, "body": "Consulta"}).status_code, 404)
        self.assertFalse(AccountSupportRequest.objects.exists())

    def test_resource_context_stays_private_and_cannot_be_reviewed_by_educator(self):
        key = uuid4()
        response = self.client.post(self.url, {"recurso": self.resource.pk, "kind": "other", "body": "No abre el archivo.", "request_key": key})
        self.assertEqual(response.status_code, 302)
        item = AccountSupportRequest.objects.get()
        self.assertIn("Recurso adquirido", item.body)
        self.assertIn(self.resource.title, item.body)
        with self.assertRaises(PermissionDenied):
            review_support(item, self.creator, "resolved", "No autorizado")
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(self.url), self.resource.title)
        self.assertNotContains(self.client.get(self.url), "No abre el archivo.")

    def test_body_limit_accounts_for_immutable_context_prefix(self):
        page = self.client.get(self.url, {"factura": self.invoice.pk})
        limit = page.context["form"].fields["body"].max_length
        self.assertLess(limit, 2000)
        response = self.client.post(self.url, {"factura": self.invoice.pk, "kind": "other", "body": "A" * (limit + 1), "request_key": uuid4()})
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(AccountSupportRequest.objects.exists())

    def test_order_reference_comes_from_owned_invoice_relationship(self):
        order = Order.objects.create(buyer=self.student, title="Pedido propio", amount_sats=150, inventory=[self.resource.pk], fingerprint="a" * 64)
        invoice = Invoice.objects.create(buyer=self.student, order=order, title=order.title, amount_sats=150, inventory=order.inventory,
                                         expires_at=timezone.now() + timedelta(minutes=15), logical_key=f"order:{order.pk}")
        response = self.client.post(self.url, {"factura": invoice.pk, "kind": "other", "body": "Consulta del pedido.", "request_key": uuid4(), "pedido": str(uuid4())})
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"Pedido: {order.pk}", AccountSupportRequest.objects.get().body)
        foreign = Order.objects.create(buyer=self.other, title="PEDIDO_AJENO", amount_sats=150, inventory=[self.resource.pk], fingerprint="b" * 64)
        inconsistent = Invoice.objects.create(buyer=self.student, order=foreign, title="Referencia incoherente", amount_sats=150, inventory=foreign.inventory,
                                              expires_at=timezone.now() + timedelta(minutes=15), logical_key=f"order:{foreign.pk}")
        denied = self.client.get(self.url, {"factura": inconsistent.pk})
        self.assertEqual(denied.status_code, 404)
        self.assertNotContains(denied, "PEDIDO_AJENO", status_code=404)
