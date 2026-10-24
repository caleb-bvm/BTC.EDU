from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile

from . import tests as fixtures
from .gateway import ProviderStatus, ProviderUnavailable
from .journey import invoice_destination
from .models import Entitlement, Invoice, Purchase
from .offers import archive_offer, create_offer
from .services import ensure_emitted, reserve_invoice, settle


@override_settings(COMMERCE_PAYMENT_MODE="fake", ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class PurchaseExperienceTests(TestCase):
    # Reuse the actual publication/purchase fixture, not pre-granted permissions.
    setUp = fixtures.CommerceJourneyTests.setUp
    activate = fixtures.CommerceJourneyTests.activate
    invoice = fixtures.CommerceJourneyTests.invoice
    pay = fixtures.CommerceJourneyTests.pay
    lesson_url = fixtures.CommerceJourneyTests.lesson_url

    def test_locked_lesson_prioritizes_only_options_that_unlock_it(self):
        chapter = self.activate(f"chapter:{self.records[1].chapter_id}", "Capítulo completo", 120)
        response = self.client.get(self.lesson_url())
        self.assertEqual(response.status_code, 403)
        self.assertEqual([offer.pk for offer in response.context["offers"]], [self.individual.pk, chapter.pk, self.bundle.pk])
        self.assertContains(response, f'?leccion={self.records[1].pk}', status_code=403)
        self.assertContains(response, "Esta lección", status_code=403)
        self.assertContains(response, "Este capítulo", status_code=403)
        self.assertContains(response, "Todo el curso", status_code=403)
        self.assertNotContains(response, reverse("offer-detail", args=[self.second_offer.pk]), status_code=403)
        self.assertNotContains(response, reverse("offer-detail", args=[self.file_offer.pk]), status_code=403)
        self.assertFalse(Entitlement.objects.exists())

    def test_partial_packages_leave_only_eligible_missing_lesson(self):
        self.pay(self.second_offer)
        response = self.client.get(self.lesson_url())
        self.assertEqual([offer.pk for offer in response.context["offers"]], [self.individual.pk, self.bundle.pk])
        self.assertEqual(response.context["offers"][1].upgrade["amount_sats"], 70)
        review = self.client.get(reverse("offer-detail", args=[self.bundle.pk]), {"leccion": self.records[1].pk})
        self.assertEqual(review.context["ownership"], "partial")
        self.assertEqual(review.context["upgrade"]["credit_sats"], 80)
        self.assertContains(review, reverse("direct-checkout", args=[self.bundle.pk]))
        alternative = next(offer for offer in review.context["alternatives"] if offer.pk == self.individual.pk)
        self.assertEqual(alternative.purchase_url, reverse("offer-detail", args=[self.individual.pk]) + f"?leccion={self.records[1].pk}")
        self.assertNotContains(review, reverse("checkout", args=[self.bundle.pk]))

    def test_selected_lesson_survives_checkout_payment_and_purchase_history(self):
        url = reverse("offer-detail", args=[self.bundle.pk])
        review = self.client.get(url, {"leccion": self.records[1].pk})
        self.assertEqual(review.context["selected_lesson"].pk, self.records[1].pk)
        self.assertContains(review, 'name="leccion"')
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            self.client.post(reverse("checkout", args=[self.bundle.pk]), {"leccion": self.records[1].pk})
            invoice = Invoice.objects.get()
            pending = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertEqual(invoice.return_lesson_id, self.records[1].pk)
        self.assertEqual(pending.context["return_to_content"], self.lesson_url())
        self.assertFalse(Purchase.objects.exists())
        settle(invoice.pk, ProviderStatus(True, 150000, invoice.payment_hash))
        confirmed = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertEqual(confirmed.context["destination"], self.lesson_url())
        self.assertEqual(confirmed.context["destination_label"], "Abrir lección")
        self.assertContains(confirmed, f'href="{self.lesson_url()}"')
        history = self.client.get(reverse("purchases"), {"estado": "paid"})
        self.assertContains(history, f'href="{self.lesson_url()}"')

    def test_individual_lesson_and_resource_have_direct_defaults(self):
        individual = self.pay(self.individual)
        self.assertEqual(invoice_destination(individual, self.student)["url"], self.lesson_url())
        resource = self.pay(self.file_offer)
        self.assertEqual(invoice_destination(resource, self.student)["url"], reverse("purchased-resource", args=[self.resource.pk]))

    def test_unrelated_and_arbitrary_return_values_never_choose_destinations(self):
        url = reverse("offer-detail", args=[self.individual.pk])
        for value in (self.records[2].pk, "https://example.invalid/steal", "//example.invalid", "-1"):
            with self.subTest(value=value):
                review = self.client.get(url, {"leccion": value, "next": "https://example.invalid/steal"})
                self.assertIsNone(review.context["selected_lesson"])
                self.assertNotContains(review, "example.invalid")
                with self.assertRaises(ValidationError):
                    reserve_invoice(self.student, self.individual.pk, return_lesson_id=value)
                rejected = self.client.post(reverse("checkout", args=[self.individual.pk]), {"leccion": value})
                self.assertRedirects(rejected, url, fetch_redirect_response=False)
        self.assertFalse(Invoice.objects.exists())
        self.assertFalse(Entitlement.objects.exists())

    def test_pending_reuse_keeps_price_but_tracks_latest_valid_lesson(self):
        first = reserve_invoice(self.student, self.bundle.pk, return_lesson_id=self.records[1].pk)
        reused = reserve_invoice(self.student, self.bundle.pk, return_lesson_id=self.records[2].pk)
        self.assertEqual(first.pk, reused.pk)
        self.assertEqual(reused.return_lesson_id, self.records[2].pk)
        self.assertEqual(reused.amount_sats, 150)
        self.assertEqual(Invoice.objects.count(), 1)
        no_new_intent = reserve_invoice(self.student, self.bundle.pk)
        self.assertEqual(no_new_intent.return_lesson_id, self.records[2].pk)

    def test_expired_retry_preserves_intent_and_reviews_current_price(self):
        invoice = ensure_emitted(reserve_invoice(self.student, self.bundle.pk, return_lesson_id=self.records[1].pk), self.gateway)
        Invoice.objects.filter(pk=invoice.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
        replacement = self.activate(f"course:{self.version.pk}", "Nueva oferta", 180)
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
            expected = reverse("offer-detail", args=[replacement.pk]) + f"?leccion={self.records[1].pk}"
            self.assertEqual(response.context["retry_url"], expected)
            self.assertContains(response, "Esta factura venció")
            self.client.post(reverse("checkout", args=[replacement.pk]), {"leccion": self.records[1].pk})
        invoice.refresh_from_db()
        self.assertEqual((invoice.status, invoice.amount_sats), ("expired", 150))
        current = Invoice.objects.get(status="pending")
        self.assertEqual((current.return_lesson_id, current.amount_sats), (self.records[1].pk, 180))
        self.assertFalse(Entitlement.objects.exists())

    def test_authentication_and_email_verification_keep_valid_intent(self):
        purchase_url = reverse("offer-detail", args=[self.bundle.pk]) + f"?leccion={self.records[1].pk}"
        self.client.logout()
        response = self.client.get(purchase_url)
        signin_url = response.context["navigation_signin_url"]
        self.assertEqual(urlsplit(signin_url).path, reverse("login"))
        self.assertEqual(parse_qs(urlsplit(signin_url).query)["next"], [purchase_url])
        self.assertContains(response, f'href="{signin_url}"')
        review_url = reverse("direct-checkout", args=[self.bundle.pk]) + f"?leccion={self.records[1].pk}"
        review = self.client.get(review_url)
        self.assertEqual(parse_qs(urlsplit(review.context["signin_url"]).query)["next"], [review_url])
        self.assertFalse(Invoice.objects.exists())
        self.client.force_login(self.student)
        with override_settings(ACCOUNT_REQUIRE_VERIFIED_EMAIL=True):
            response = self.client.post(reverse("checkout", args=[self.bundle.pk]), {"leccion": self.records[1].pk})
        self.assertRedirects(response, reverse("student-account-security"), fetch_redirect_response=False)
        self.assertEqual(self.client.session["account_verify_destination"], purchase_url)
        self.assertFalse(Invoice.objects.exists())

    def test_historical_purchase_returns_to_original_version_after_publication(self):
        invoice = ensure_emitted(reserve_invoice(self.student, self.bundle.pk, return_lesson_id=self.records[1].pk), self.gateway)
        settle(invoice.pk, ProviderStatus(True, 150000, invoice.payment_hash))
        self.lesson.body = "Nueva revisión no adquirida"
        self.lesson.save()
        publish_course(self.course, self.admin)
        Course.objects.filter(pk=self.course.pk).update(status="archived")
        archive_offer(self.creator, self.bundle)
        response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertEqual(response.context["destination"], self.lesson_url())
        self.assertContains(self.client.get(response.context["destination"]), "Texto comprado original")

    def test_destination_rechecks_permission_and_forged_lesson_membership(self):
        invoice = self.pay(self.individual)
        Invoice.objects.filter(pk=invoice.pk).update(return_lesson=self.records[2])
        invoice.refresh_from_db()
        self.assertNotEqual(invoice_destination(invoice, self.student)["url"], self.lesson_url(record=self.records[2]))
        Course.objects.filter(pk=self.course.pk).update(status="draft")
        invoice = Invoice.objects.get(pk=invoice.pk)
        self.assertEqual(invoice_destination(invoice, self.student)["url"], reverse("workspace"))

    def test_purchase_filters_are_private_and_expired_pending_is_closed(self):
        paid = self.pay(self.individual)
        pending = self.invoice(self.second_offer)
        expired = self.invoice(self.file_offer)
        Invoice.objects.filter(pk=expired.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
        with patch("commerce.services.LNbitsGateway") as gateway:
            for state, expected in (("paid", {paid.pk}), ("pending", {pending.pk}), ("closed", {expired.pk})):
                response = self.client.get(reverse("purchases"), {"estado": state})
                self.assertEqual({invoice.pk for invoice in response.context["invoices"]}, expected)
            gateway.assert_not_called()
        self.client.force_login(self.other)
        self.assertFalse(list(self.client.get(reverse("purchases")).context["invoices"]))

    def test_provider_error_is_actionable_and_does_not_expose_environment(self):
        invoice = self.invoice()
        with patch("commerce.views.reconcile", side_effect=ProviderUnavailable("regtest wallet secret")):
            response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertContains(response, "Usa Actualizar estado")
        self.assertNotContains(response, "regtest")
        self.assertNotContains(response, "wallet secret")
        self.assertFalse(Entitlement.objects.exists())

    def test_expiration_is_visible_even_when_provider_is_unavailable(self):
        invoice = self.invoice()
        Invoice.objects.filter(pk=invoice.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
        with patch("commerce.services.LNbitsGateway", side_effect=ProviderUnavailable("offline")):
            response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertEqual(response.context["invoice"].status, "expired")
        self.assertFalse(response.context["can_pay"])
        self.assertContains(response, "Actualizar estado del pago")
        self.assertNotContains(response, 'name="action" value="pay"')
        self.assertFalse(Entitlement.objects.exists())

    def test_failed_provider_can_retry_but_paid_incident_requests_help(self):
        invoice = self.invoice()
        settle(invoice.pk, ProviderStatus(False, 150000, invoice.payment_hash, True))
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertContains(response, "Revisar selección y continuar")
        self.assertEqual(response.context["retry_url"], reverse("offer-detail", args=[self.bundle.pk]))
        Invoice.objects.filter(pk=invoice.pk).update(incident="amount_mismatch")
        with patch("commerce.views.reconcile", return_value=Invoice.objects.get(pk=invoice.pk)):
            response = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertContains(response, reverse("student-account-support"))
        self.assertNotContains(response, "Revisar selección y continuar")
        self.assertEqual(response.context["retry_url"], "")

    def test_creator_course_context_is_owned_scoped_and_preserved_in_form(self):
        self.client.force_login(self.creator)
        response = self.client.get(reverse("creator-offers"), {"curso": self.course.pk, "objetivo": f"lesson:{self.records[1].pk}"})
        self.assertEqual(response.context["selected_course"], self.course)
        self.assertEqual(response.context["form"].initial["target"], f"lesson:{self.records[1].pk}")
        self.assertContains(response, "data-dirty-form")
        self.assertContains(response, 'name="curso"')
        other = get_user_model().objects.create_user("other.teacher@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=other, display_name="Otro docente", status="approved")
        foreign = Course.objects.create(creator=other, title="Otro curso")
        self.assertEqual(self.client.get(reverse("creator-offers"), {"curso": foreign.pk}).status_code, 404)
        self.assertEqual(self.client.get(reverse("creator-offers"), {"curso": "invalid"}).status_code, 404)
        forged = self.client.post(reverse("creator-offers") + f"?curso={self.course.pk}", {"target": "course:999999", "title": "No permitido", "amount_sats": 25})
        self.assertEqual(forged.status_code, 200)
        self.assertTrue(forged.context["form"].errors)

    def test_package_dependency_links_select_exact_individual_targets(self):
        archive_offer(self.creator, self.file_offer)
        package = create_offer(self.creator, f"chapter:{self.records[1].chapter_id}", "Capítulo nuevo", 130)
        self.client.force_login(self.creator)
        response = self.client.get(reverse("creator-offer", args=[package.pk]))
        dependencies = response.context["dependencies"]
        self.assertEqual(len(dependencies), 1)
        url = reverse("creator-offers") + "?" + urlencode({"objetivo": f"resource:{self.resource.pk}", "curso": self.course.pk})
        self.assertEqual(dependencies[0]["url"], url)
        selected = self.client.get(url)
        self.assertEqual(selected.context["form"].initial["target"], f"resource:{self.resource.pk}")

    def test_free_course_has_no_paid_target_and_explains_next_step(self):
        course = Course.objects.create(creator=self.creator, title="Curso gratuito", description="Descripción")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Gratis", body="Lección abierta", status="published")
        publish_course(course, self.admin)
        self.client.force_login(self.creator)
        response = self.client.get(reverse("creator-offers"), {"curso": course.pk})
        self.assertFalse(response.context["has_targets"])
        self.assertContains(response, "todavía no tiene una publicación de pago")
        self.assertNotContains(response, "data-dirty-form")

    def test_paginated_purchase_history_keeps_filter_and_user_scope(self):
        for index in range(21):
            Invoice.objects.create(buyer=self.student, offer=self.bundle, logical_key=f"closed:{index}", title=f"Factura anterior {index}",
                                   amount_sats=150, inventory=[], status="failed", expires_at=timezone.now())
        response = self.client.get(reverse("purchases"), {"estado": "closed"})
        self.assertEqual(response.context["invoices"].paginator.count, 21)
        self.assertContains(response, "?estado=closed&amp;pagina=2")
        second = self.client.get(reverse("purchases"), {"estado": "closed", "pagina": 2})
        self.assertEqual(len(second.context["invoices"]), 1)
        self.assertContains(second, "?estado=closed&amp;pagina=1")

    def test_standalone_resource_offer_context_is_exact_and_owned(self):
        self.client.force_login(self.creator)
        url = reverse("creator-offers") + "?" + urlencode({"recurso": self.material.pk, "tipo": "material"})
        response = self.client.get(url)
        self.assertEqual(response.context["selected_resource"], self.material)
        self.assertEqual(response.context["form"].initial["target"], f"resource:{self.resource.pk}")
        self.assertEqual({offer.pk for offer in response.context["offers"]}, {self.file_offer.pk})
        self.assertContains(response, reverse("creator-resource", args=["materiales", self.material.pk]))
        self.assertContains(response, 'name="recurso"')
        forged = self.client.post(url, {"target": f"lesson:{self.records[1].pk}", "title": "Wrong unit", "amount_sats": 10})
        self.assertTrue(forged.context["form"].errors)
        other = get_user_model().objects.create_user("resource.teacher@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=other, display_name="Otro docente", status="approved")
        self.client.force_login(other)
        self.assertEqual(self.client.get(url).status_code, 404)
