import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from commerce.gateway import ProviderStatus
from commerce.models import Cart, CartItem, Invoice
from commerce.offers import create_offer, review_offer, submit_offer
from commerce.orders import quote_order, reserve_order
from commerce.services import settle
from content.models import Material
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile
from creators.services import decide, submit
from media.models import Asset
from scripts.demo_commerce import seed

from .analytics import dashboard_data


@override_settings(SECURE_SSL_REDIRECT=False)
class OrderAnalyticsTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        config = override_settings(MEDIA_ROOT=self.media.name)
        config.enable()
        self.addCleanup(config.disable)
        self.data = seed()
        self.other_creator = get_user_model().objects.create_user("otra@ventas.invalid", account_type="creator", first_name="Otra")
        CreatorProfile.objects.create(user=self.other_creator, status="approved", display_name="Otra educadora")
        asset = Asset.objects.create(creator=self.other_creator, file=SimpleUploadedFile("otra-guia.txt", b"Una actividad independiente.", content_type="text/plain"))
        material = Material.objects.create(creator=self.other_creator, title="Actividad de la otra educadora", description="Una guía para resolver una práctica.", access_type="paid", pending_asset=asset, **EDUCATION_FIXTURE)
        decide(submit(material, self.other_creator), self.data.reviewer, True)
        material.refresh_from_db()
        offer = create_offer(self.other_creator, f"resource:{material.revision_id}", "Material de otra educadora", 40)
        submit_offer(self.other_creator, offer)
        self.other_offer = review_offer(self.data.reviewer, offer, True)
        self.cart = Cart.objects.create(buyer=self.data.student)
        for offer in (self.data.individual, self.data.second, self.other_offer):
            CartItem.objects.create(cart=self.cart, offer=offer)

    def buy(self, marker="c"):
        invoice = reserve_order(self.data.student, self.cart, quote_order(self.data.student, self.cart)["token"])
        Invoice.objects.filter(pk=invoice.pk).update(payment_hash=marker * 64, issue_state="ready")
        settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, marker * 64))
        return invoice

    def stats(self, creator=None):
        today = timezone.localdate()
        return dashboard_data(today, today, creator)

    def test_order_counts_once_and_each_educator_receives_only_own_amount(self):
        self.buy()
        first, second, whole = self.stats(self.data.creator), self.stats(self.other_creator), self.stats()
        self.assertEqual((first["invoice_count"], first["paid_count"], first["volume"], first["sold_count"]), (1, 1, 150, 2))
        self.assertEqual((second["invoice_count"], second["paid_count"], second["volume"], second["sold_count"]), (1, 1, 40, 1))
        self.assertEqual((whole["paid_count"], whole["volume"], whole["sold_count"]), (1, 190, 3))
        self.assertEqual(first["repeat_purchase"]["numerator"], 0)
        self.assertEqual(second["recent_invoices"][0].metric_title, self.other_offer.title)
        self.assertEqual(second["recent_invoices"][0].metric_amount_sats, 40)
        self.client.force_login(self.other_creator)
        page = self.client.get(reverse("creator-analytics"))
        self.assertContains(page, self.other_offer.title)
        self.assertNotContains(page, self.data.individual.title)
        self.assertNotContains(page, "190 sats")

    def test_repeat_purchase_requires_another_confirmed_order(self):
        self.buy()
        self.cart.refresh_from_db()
        CartItem.objects.create(cart=self.cart, offer=self.data.file_offer)
        self.buy("d")
        self.assertEqual(self.stats(self.data.creator)["repeat_purchase"]["numerator"], 1)
        self.assertEqual(self.stats(self.other_creator)["repeat_purchase"]["numerator"], 0)

    def test_order_confirmation_opens_each_acquired_line_and_protects_other_accounts(self):
        invoice = self.buy()
        self.client.force_login(self.data.student)
        page = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertContains(page, "Listo para aprender")
        self.assertContains(page, self.data.individual.title)
        self.assertContains(page, self.other_offer.title)
        self.assertContains(page, "Abrir recurso")
        self.assertContains(page, f"factura={invoice.pk}")
        self.client.force_login(self.data.other)
        self.assertEqual(self.client.get(reverse("invoice-detail", args=[invoice.pk])).status_code, 404)
