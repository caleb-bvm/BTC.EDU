import tempfile
from datetime import timedelta
from unittest.mock import patch

import httpx
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from content.access import content_access
from content.models import Chapter, Course, Lesson, LessonResource, Material
from content.publication import publish_course, publish_resource
from creators.models import CreatorProfile
from creators.services import submit
from learning.models import Enrollment
from learning.services import enroll
from media.models import Asset

from .catalog import missing_alternatives, ownership
from .gateway import LNbitsGateway, ProviderInvoice, ProviderStatus, ProviderUnavailable
from .models import (
    CommerceEvent,
    Entitlement,
    EntitlementSource,
    Invoice,
    Offer,
    OfferItem,
    PaymentEvidence,
    Purchase,
)
from .offers import archive_offer, create_offer, review_offer, submit_offer
from .services import (
    ensure_emitted,
    reserve_invoice,
    settle,
    simulate_payment,
)


class FakeGateway:
    def __init__(self):
        self.created = self.simulated = self.closed = 0
        self.paid = False
        self.invoice = None

    def create(self, invoice):
        self.created += 1
        self.invoice = invoice
        return ProviderInvoice(invoice.pk.hex * 2, "lnbc-test-not-real")

    def recover(self, invoice):
        self.invoice = invoice
        return ProviderInvoice(invoice.pk.hex * 2, "lnbc-test-not-real")

    def status(self, invoice):
        return ProviderStatus(self.paid, invoice.amount_sats * 1000, invoice.payment_hash)

    def simulate(self, invoice):
        self.simulated += 1
        self.paid = True

    def close(self):
        self.closed += 1


class CommerceJourneyTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        config = override_settings(MEDIA_ROOT=self.media.name, SECURE_SSL_REDIRECT=False)
        config.enable()
        self.addCleanup(config.disable)
        users = get_user_model().objects
        self.creator = users.create_user("seller@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=self.creator, display_name="Docente", status="approved")
        self.admin = users.create_superuser("review@example.invalid")
        self.student = users.create_user("buyer@example.invalid")
        self.other = users.create_user("other@example.invalid")
        self.course = Course.objects.create(creator=self.creator, title="Curso de pruebas", description="Descripción")
        chapter = Chapter.objects.create(course=self.course, title="Capítulo", status="published")
        self.free = Lesson.objects.create(chapter=chapter, title="Introducción", body="Texto gratuito", status="published", position=1)
        self.lesson = Lesson.objects.create(chapter=chapter, title="Primera práctica", body="Texto comprado original", access_type="paid", status="published", position=2)
        self.second = Lesson.objects.create(chapter=chapter, title="Segunda práctica", body="Otro texto privado", access_type="paid", status="published", position=3)
        asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("ejercicio.txt", b"Material comprado", content_type="text/plain"))
        self.material = Material.objects.create(creator=self.creator, title="Ejercicio", description="Material", access_type="paid", pending_asset=asset)
        self.resource = publish_resource(self.material, self.admin)
        LessonResource.objects.create(lesson=self.lesson, resource=self.resource)
        self.version = publish_course(self.course, self.admin)
        self.records = list(self.version.chapters.first().lessons.select_related("content"))
        self.individual = self.activate(f"lesson:{self.records[1].pk}", "Texto individual", 70)
        self.second_offer = self.activate(f"lesson:{self.records[2].pk}", "Segundo texto", 80)
        self.file_offer = self.activate(f"resource:{self.resource.pk}", "Archivo individual", 30)
        self.bundle = self.activate(f"course:{self.version.pk}", "Curso completo", 150)
        self.gateway = FakeGateway()
        self.client.force_login(self.student)

    def activate(self, target, title, amount):
        offer = create_offer(self.creator, target, title, amount)
        submit_offer(self.creator, offer)
        return review_offer(self.admin, offer, True)

    def invoice(self, offer=None):
        return ensure_emitted(reserve_invoice(self.student, (offer or self.bundle).pk), self.gateway)

    def pay(self, offer=None):
        invoice = self.invoice(offer)
        return settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))

    def lesson_url(self, version=None, record=None):
        version, record = version or self.version, record or self.records[1]
        return reverse("version-lesson", args=[self.course.pk, version.number, record.pk])

    def test_creator_targets_owner_price_and_review(self):
        other = get_user_model().objects.create_user("foreign@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=other, display_name="Otro", status="approved")
        with self.assertRaises(PermissionDenied):
            create_offer(other, f"course:{self.version.pk}", "Ajeno", 100)
        with self.assertRaises(ValidationError):
            create_offer(self.creator, f"course:{self.version.pk}", "Cero", 0)
        with self.assertRaises(PermissionDenied):
            review_offer(self.creator, self.bundle, True)
        self.client.force_login(self.creator)
        response = self.client.post(reverse("creator-offers"), {"target": f"resource:{self.resource.pk}", "title": "Nueva", "amount_sats": 55, "creator": other.pk, "status": "active"})
        self.assertEqual(response.status_code, 302)
        offer = Offer.objects.latest("pk")
        self.assertEqual((offer.creator_id, offer.status), (self.creator.pk, "draft"))

    def test_package_requires_all_individual_alternatives(self):
        archive_offer(self.creator, self.file_offer)
        offer = create_offer(self.creator, f"chapter:{self.records[0].chapter_id}", "Capítulo", 140)
        submit_offer(self.creator, offer)
        with self.assertRaisesMessage(ValidationError, "Ejercicio"):
            review_offer(self.admin, offer, True)
        offer.refresh_from_db()
        self.assertEqual(offer.status, "pending")

    def test_offer_and_invoice_inventory_cannot_change(self):
        self.bundle.amount_sats = 1
        with self.assertRaises(ValidationError):
            self.bundle.save()
        item = self.individual.items.first()
        with self.assertRaises(ValidationError):
            item.delete()
        with self.assertRaises(ValidationError):
            OfferItem.objects.create(offer=self.individual, resource=self.records[2].content)
        invoice = self.invoice()
        invoice.inventory = []
        with self.assertRaises(ValidationError):
            invoice.save()

    def test_pending_invoice_reused_price_is_from_server(self):
        first, second = self.invoice(), self.invoice()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(self.gateway.created, 1)
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            self.client.post(reverse("checkout", args=[self.bundle.pk]), {"amount_sats": 1, "buyer": self.other.pk})
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertEqual(first.amount_sats, 150)
        self.assertEqual(first.buyer_id, self.student.pk)

    def test_changed_price_reuses_original_pending_invoice(self):
        invoice = self.invoice()
        changed = self.activate(f"course:{self.version.pk}", "Precio nuevo", 200)
        reserved = reserve_invoice(self.student, changed.pk)
        self.assertEqual(reserved.pk, invoice.pk)
        self.assertEqual(reserved.amount_sats, 150)
        self.bundle.refresh_from_db()
        self.assertEqual(self.bundle.status, "archived")
        settled = settle(invoice.pk, ProviderStatus(True, 150000, invoice.payment_hash))
        self.assertEqual(settled.status, "paid")

    def test_confirmed_purchase_is_idempotent_and_private(self):
        invoice = self.invoice()
        status = ProviderStatus(True, 150000, invoice.payment_hash)
        settle(invoice.pk, status)
        settle(invoice.pk, status)
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(PaymentEvidence.objects.count(), 1)
        self.assertEqual(Entitlement.objects.count(), 4)
        self.assertEqual(EntitlementSource.objects.count(), 4)
        self.assertEqual(CommerceEvent.objects.filter(kind="paid").count(), 1)
        self.assertTrue(Enrollment.objects.filter(student=self.student, version=self.version).exists())
        self.assertContains(self.client.get(self.lesson_url()), "Texto comprado original")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("invoice-detail", args=[invoice.pk])).status_code, 404)
        self.assertNotContains(self.client.get(self.lesson_url()), "Texto comprado original", status_code=403)

    def test_browser_cannot_claim_paid_and_csrf_is_required(self):
        invoice = self.invoice()
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            self.client.post(reverse("invoice-action", args=[invoice.pk]), {"paid": True, "status": "paid", "payment_hash": invoice.payment_hash})
        self.assertFalse(Purchase.objects.exists())
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        self.assertEqual(client.post(reverse("checkout", args=[self.bundle.pk])).status_code, 403)
        self.assertEqual(client.post(reverse("invoice-action", args=[invoice.pk]), {"action": "simulate"}).status_code, 403)
        self.assertEqual(client.get(reverse("checkout", args=[self.bundle.pk])).status_code, 405)

    def test_simulation_uses_provider_and_repeated_click_does_not_repay(self):
        invoice = self.invoice()
        simulate_payment(self.student, invoice, self.gateway)
        with self.assertRaises(ValidationError):
            simulate_payment(self.student, invoice, self.gateway)
        self.assertEqual(self.gateway.simulated, 1)
        self.assertEqual(Purchase.objects.count(), 1)

    def test_partial_and_full_ownership_block_new_charge(self):
        self.pay(self.individual)
        self.assertEqual(ownership(self.student, self.bundle), "partial")
        self.assertEqual({offer.pk for offer in missing_alternatives(self.student, self.bundle)}, {self.second_offer.pk, self.file_offer.pk})
        with self.assertRaises(ValidationError):
            reserve_invoice(self.student, self.bundle.pk)
        with self.assertRaises(ValidationError):
            reserve_invoice(self.student, self.individual.pk)
        self.assertEqual(ownership(self.student, self.individual), "owned")

    def test_reserved_package_cannot_be_simulated_after_partial_purchase(self):
        invoice = self.invoice()
        self.pay(self.individual)
        with self.assertRaises(ValidationError):
            simulate_payment(self.student, invoice, self.gateway)
        self.assertEqual(self.gateway.simulated, 0)
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertNotContains(response, "Simular pago")
        self.assertContains(response, "Ya adquiriste parte")

    def test_overlapping_paid_invoices_keep_evidence_without_duplicate_rights(self):
        package, individual = self.invoice(), self.invoice(self.individual)
        settle(individual.pk, ProviderStatus(True, individual.amount_sats * 1000, individual.payment_hash))
        settle(package.pk, ProviderStatus(True, package.amount_sats * 1000, package.payment_hash))
        package.refresh_from_db()
        self.assertEqual((package.status, package.incident), ("failed", "overlapping_payment"))
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(PaymentEvidence.objects.count(), 2)
        self.assertEqual(Entitlement.objects.filter(resource__access_type="paid").count(), 1)

    def test_late_payment_is_retained_without_purchase(self):
        invoice = self.invoice()
        settle(invoice.pk, ProviderStatus(True, 150000, invoice.payment_hash), invoice.expires_at + timedelta(seconds=1))
        invoice.refresh_from_db()
        self.assertEqual((invoice.status, invoice.incident), ("expired", "late_payment"))
        self.assertTrue(PaymentEvidence.objects.exists())
        self.assertFalse(Purchase.objects.exists())

    def test_pending_expiration_and_provider_failure_grant_nothing(self):
        invoice = self.invoice()
        settle(invoice.pk, ProviderStatus(False, 150000, invoice.payment_hash), invoice.expires_at)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "expired")
        next_invoice = self.invoice()
        settle(next_invoice.pk, ProviderStatus(False, 150000, next_invoice.payment_hash, True))
        next_invoice.refresh_from_db()
        self.assertEqual(next_invoice.status, "failed")
        self.assertFalse(Entitlement.objects.exists())

    def test_wrong_amount_hash_and_inactive_buyer_never_grant_access(self):
        invoice = self.invoice()
        with self.assertRaises(ValidationError):
            settle(invoice.pk, ProviderStatus(True, 150000, "a" * 64))
        settle(invoice.pk, ProviderStatus(True, 1000, invoice.payment_hash))
        self.assertEqual(PaymentEvidence.objects.get().resolution, "amount_mismatch")
        second = self.invoice(self.individual)
        get_user_model().objects.filter(pk=self.student.pk).update(is_active=False)
        settle(second.pk, ProviderStatus(True, 70000, second.payment_hash))
        self.assertFalse(Entitlement.objects.exists())

    def test_timeout_recovers_same_emission_and_never_recreates(self):
        invoice = reserve_invoice(self.student, self.bundle.pk)
        gateway = FakeGateway()
        with patch.object(gateway, "create", side_effect=ProviderUnavailable("Desconocido")) as create:
            with self.assertRaises(ProviderUnavailable):
                ensure_emitted(invoice, gateway)
            invoice.refresh_from_db()
            self.assertEqual(invoice.issue_state, "unknown")
            ensure_emitted(invoice, gateway)
            self.assertEqual(create.call_count, 1)
        invoice.refresh_from_db()
        self.assertEqual(invoice.issue_state, "ready")
        self.assertEqual(Invoice.objects.count(), 1)

    def test_archived_purchase_and_old_version_survive_new_publication(self):
        self.pay()
        self.lesson.body = "Texto nuevo que no se compró"
        self.lesson.save()
        new = publish_course(self.course, self.admin)
        new_record = new.chapters.first().lessons.get(source_lesson_id=self.lesson.pk)
        self.assertContains(self.client.get(self.lesson_url()), "Texto comprado original")
        self.assertNotContains(self.client.get(self.lesson_url(new, new_record)), "Texto nuevo que no se compró", status_code=403)
        Course.objects.filter(pk=self.course.pk).update(status="archived")
        archive_offer(self.creator, self.bundle)
        self.assertContains(self.client.get(self.lesson_url()), "Texto comprado original")
        self.assertContains(self.client.get(reverse("workspace")), "Versión conservada")
        self.assertNotContains(self.client.get(reverse("courses")), "Curso de pruebas")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.lesson_url()).status_code, 404)

    def test_inscription_preserves_free_lessons_but_never_authorizes_paid(self):
        enroll(self.student, self.version)
        enroll(self.student, self.version)
        self.assertEqual(Enrollment.objects.count(), 1)
        self.assertFalse(content_access(self.student, self.records[1]).allowed)
        Course.objects.filter(pk=self.course.pk).update(status="archived")
        self.assertContains(self.client.get(self.lesson_url(record=self.records[0])), "Texto gratuito")
        self.assertEqual(self.client.get(self.lesson_url()).status_code, 403)

    def test_prepared_review_snapshot_is_never_available_to_buyers(self):
        self.pay()
        submission = submit(self.course, self.creator)
        self.assertEqual(self.client.get(reverse("course-version", args=[self.course.pk, submission.snapshot.number])).status_code, 404)

    def test_bought_resource_opens_reused_attachment_and_archived_file(self):
        self.pay(self.file_offer)
        self.assertFalse(content_access(self.student, self.records[1]).allowed)
        self.pay(self.individual)
        attachment = self.records[1].attachments.first()
        self.assertTrue(content_access(self.student, attachment).allowed)
        file_url = reverse("purchased-resource-file", args=[self.resource.pk, "archivo"])
        Material.objects.filter(pk=self.material.pk).update(status="archived")
        response = self.client.get(file_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"Material comprado")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(file_url).status_code, 404)

    def test_views_offer_price_library_and_secret_absence(self):
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            self.client.post(reverse("checkout", args=[self.bundle.pk]))
            invoice = Invoice.objects.get()
            response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertContains(response, "Simular pago")
        self.assertNotContains(response, invoice.payment_request)
        self.assertNotContains(response, invoice.payment_hash)
        self.assertContains(self.client.get(reverse("courses")), "Desde 70 sats de prueba")
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(reverse("creator-offers")), "Ofertas y precios")
        self.assertEqual(self.client.get(reverse("purchases")).status_code, 302)
        self.client.force_login(self.student)
        self.pay()
        self.assertContains(self.client.get(reverse("workspace")), "Curso de pruebas")
        self.assertContains(self.client.get(reverse("workspace")), "Ejercicio")


@override_settings(COMMERCE_SIMULATION=True, LNBITS_URL="http://127.0.0.1:5000", LNBITS_INVOICE_KEY="invoice-secret", LNBITS_PAYER_KEY="payer-secret", LNBITS_ADMIN_TOKEN="admin-secret")
class GatewayTests(TestCase):
    def test_real_api_payload_and_wallet_detail_validation(self):
        calls = []
        def handler(request):
            calls.append(request)
            if request.url.path == "/admin/api/v1/settings":
                return httpx.Response(200, json={"lnbits_backend_wallet_class": "FakeWallet"})
            if request.method == "POST":
                return httpx.Response(200, json={"payment_hash": "a" * 64, "bolt11": "lnbc-fixture"})
            return httpx.Response(200, json={"paid": True, "details": {"payment_hash": "a" * 64, "amount": 150000}})
        gateway = LNbitsGateway(httpx.MockTransport(handler))
        self.addCleanup(gateway.close)
        invoice = Invoice(amount_sats=150, payment_hash="a" * 64)
        result = gateway.create(invoice)
        invoice.payment_request = result.payment_request
        self.assertTrue(gateway.status(invoice).paid)
        gateway.simulate(invoice)
        self.assertEqual(calls[-1].headers["X-Api-Key"], "payer-secret")
        self.assertEqual(calls[1].headers["X-Api-Key"], "invoice-secret")
        self.assertIn(b'"external_id"', calls[1].content)
        self.assertFalse(any(request.url.host != "127.0.0.1" for request in calls))

    def test_external_providers_and_real_wallets_are_rejected(self):
        with override_settings(LNBITS_URL="https://payments.example.invalid"):
            with self.assertRaises(ProviderUnavailable):
                LNbitsGateway()
        with override_settings(COMMERCE_SIMULATION=False):
            with self.assertRaises(ProviderUnavailable):
                LNbitsGateway()
        gateway = LNbitsGateway(httpx.MockTransport(lambda request: httpx.Response(200, json={"lnbits_backend_wallet_class": "RealWallet"})))
        self.addCleanup(gateway.close)
        with self.assertRaises(ProviderUnavailable):
            gateway.create(Invoice(amount_sats=1))

    def test_timeout_and_status_without_wallet_evidence_are_unknown(self):
        gateway = LNbitsGateway(httpx.MockTransport(lambda request: httpx.Response(200, json={"paid": True})))
        self.addCleanup(gateway.close)
        with self.assertRaises(ProviderUnavailable):
            gateway.status(Invoice(payment_hash="a" * 64))
        def offline(request):
            raise httpx.ReadTimeout("secret URL should never reach user", request=request)
        gateway.client.close()
        gateway.client = httpx.Client(base_url="http://127.0.0.1:5000", transport=httpx.MockTransport(offline))
        with self.assertRaises(ProviderUnavailable) as error:
            gateway.status(Invoice(payment_hash="a" * 64))
        self.assertNotIn("secret URL", str(error.exception))
