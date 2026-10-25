from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from content.access import content_access
from content.models import Course
from content.publication import publish_course
from learning.models import Notification

from . import tests as fixtures
from .gateway import ProviderStatus
from .membership import (
    check_membership,
    create_membership_payment,
    membership_until,
    settle_membership,
)
from .models import Entitlement, MembershipPayment, MembershipPlan


@override_settings(COMMERCE_PAYMENT_MODE="fake", ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class MembershipFixture(TestCase):
    setUp_commerce = fixtures.CommerceJourneyTests.setUp
    activate = fixtures.CommerceJourneyTests.activate
    lesson_url = fixtures.CommerceJourneyTests.lesson_url
    invoice = fixtures.CommerceJourneyTests.invoice

    def setUp(self):
        self.setUp_commerce()
        self.plan = MembershipPlan.objects.create(name="Membresía mensual", amount_sats=5000, days=30)
        Course.objects.filter(pk=self.course.pk).update(membership=True)

    def join(self, member=None):
        payment = create_membership_payment(member or self.student, self.plan)
        return check_membership(payment, self.gateway, simulate=True)


class MembershipPaymentTests(MembershipFixture):
    def test_paid_period_starts_on_confirmation_and_renewal_continues_it(self):
        self.assertIsNone(membership_until(self.student))
        first = self.join()
        self.assertEqual(first.status, "paid")
        self.assertEqual(first.ends_at - first.starts_at, timedelta(days=30))
        self.assertEqual(membership_until(self.student), first.ends_at)
        self.assertTrue(Notification.objects.filter(recipient=self.student, event_key=f"membership:{first.pk}").exists())
        self.gateway.paid = False
        second = self.join()
        self.assertEqual(second.starts_at, first.ends_at)
        self.assertEqual(membership_until(self.student), first.ends_at + timedelta(days=30))
        self.assertFalse(Entitlement.objects.exists())

    def test_period_ends_and_access_is_only_for_students(self):
        payment = self.join()
        MembershipPayment.objects.filter(pk=payment.pk).update(starts_at=timezone.now() - timedelta(days=31),
                                                                ends_at=timezone.now() - timedelta(days=1))
        self.assertIsNone(membership_until(self.student))
        with self.assertRaises(PermissionDenied):
            create_membership_payment(self.creator, self.plan)

    def test_wrong_amount_or_hash_never_activates_and_confirmation_is_idempotent(self):
        payment = create_membership_payment(self.student, self.plan)
        payment = check_membership(payment, self.gateway)
        payment = settle_membership(payment.pk, ProviderStatus(True, 4999 * 1000, payment.payment_hash))
        self.assertEqual(payment.status, "pending")
        with self.assertRaises(ValidationError):
            settle_membership(payment.pk, ProviderStatus(True, 5000 * 1000, "f" * 64))
        paid = settle_membership(payment.pk, ProviderStatus(True, 5000 * 1000, payment.payment_hash))
        again = settle_membership(payment.pk, ProviderStatus(True, 5000 * 1000, payment.payment_hash))
        self.assertEqual((again.starts_at, again.ends_at), (paid.starts_at, paid.ends_at))

    def test_late_payment_of_an_expired_invoice_still_buys_a_full_period(self):
        payment = check_membership(create_membership_payment(self.student, self.plan), self.gateway)
        MembershipPayment.objects.filter(pk=payment.pk).update(status="expired", expires_at=timezone.now() - timedelta(minutes=1))
        self.gateway.paid = True
        out = StringIO()
        with patch("commerce.membership.LNbitsGateway", return_value=self.gateway):
            call_command("reconcile_payments", stdout=out)
        payment.refresh_from_db()
        self.assertEqual(payment.status, "paid")
        self.assertIn("Pagos de membresía revisados: 1", out.getvalue())

    def test_open_invoice_is_reused_and_plans_keep_their_terms(self):
        first = create_membership_payment(self.student, self.plan)
        self.assertEqual(create_membership_payment(self.student, self.plan).pk, first.pk)
        self.plan.amount_sats = 6000
        with self.assertRaises(ValidationError):
            self.plan.save()
        with self.assertRaises(ValidationError):
            self.plan.delete()
        MembershipPlan.objects.filter(pk=self.plan.pk).update(active=False)
        with self.assertRaises(ValidationError):
            create_membership_payment(self.other, self.plan)


class MembershipAccessTests(MembershipFixture):
    def test_member_opens_paid_lessons_and_materials_of_the_published_version(self):
        lesson, attachment = self.records[1], self.records[1].attachments.get()
        self.assertFalse(content_access(self.student, lesson).allowed)
        self.join()
        self.assertEqual(content_access(self.student, lesson).reason, "membership")
        self.assertTrue(content_access(self.student, attachment).allowed)
        self.assertEqual(content_access(self.student, self.records[0]).reason, "free")
        self.assertFalse(content_access(self.other, lesson).allowed)
        response = self.client.get(self.lesson_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Texto comprado original")

    def test_access_follows_the_course_flag_and_current_version(self):
        self.join()
        Course.objects.filter(pk=self.course.pk).update(membership=False)
        self.assertFalse(content_access(self.student, self.records[1]).allowed)
        Course.objects.filter(pk=self.course.pk).update(membership=True)
        self.course.refresh_from_db()
        publish_course(self.course, self.admin)
        # The previous version is no longer in the catalog, so membership does not open it.
        self.assertFalse(content_access(self.student, self.records[1]).allowed)

    def test_expired_membership_keeps_individual_purchases(self):
        payment = self.join()
        fixtures.CommerceJourneyTests.pay(self, self.individual)
        MembershipPayment.objects.filter(pk=payment.pk).update(starts_at=timezone.now() - timedelta(days=31),
                                                                ends_at=timezone.now() - timedelta(days=1))
        self.assertEqual(content_access(self.student, self.records[1]).reason, "purchase")
        self.assertFalse(content_access(self.student, self.records[2]).allowed)

    def test_course_and_locked_lesson_offer_the_membership(self):
        course_page = self.client.get(reverse("course-version", args=[self.course.pk, self.version.number]))
        self.assertContains(course_page, "Incluido en la membresía")
        self.assertContains(course_page, reverse("membership"))
        lesson_page = self.client.get(self.lesson_url())
        self.assertEqual(lesson_page.status_code, 403)
        self.assertContains(lesson_page, "Incluido en la membresía", status_code=403)
        self.join()
        course_page = self.client.get(reverse("course-version", args=[self.course.pk, self.version.number]))
        self.assertContains(course_page, "Incluido en tu membresía")


class MembershipPageTests(MembershipFixture):
    def test_public_page_lists_plan_and_included_courses(self):
        self.client.logout()
        response = self.client.get(reverse("membership"))
        self.assertContains(response, "Membresía mensual")
        self.assertContains(response, "5000")
        self.assertContains(response, self.version.title)
        self.assertContains(response, f"{reverse('login')}?next=")
        catalog = self.client.get(reverse("courses"), {"acceso": "membresia", "vista": "todos"})
        self.assertContains(catalog, self.version.title)

    def test_student_joins_pays_and_other_accounts_cannot_see_the_payment(self):
        with patch("commerce.membership.LNbitsGateway", return_value=self.gateway):
            response = self.client.post(reverse("membership-join"), {"plan": self.plan.pk})
            payment = MembershipPayment.objects.get()
            self.assertRedirects(response, reverse("membership-payment", args=[payment.pk]), fetch_redirect_response=False)
            detail = self.client.get(reverse("membership-payment", args=[payment.pk]))
            self.assertContains(detail, reverse("membership-payment-status", args=[payment.pk]))
            self.assertEqual(self.client.get(reverse("membership-payment-status", args=[payment.pk])).json()["status"], "pending")
            self.client.post(reverse("membership-payment-action", args=[payment.pk]), {"action": "pay"})
        payment.refresh_from_db()
        self.assertEqual(payment.status, "paid")
        self.assertContains(self.client.get(reverse("membership")), "Activa hasta el")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("membership-payment", args=[payment.pk])).status_code, 404)
