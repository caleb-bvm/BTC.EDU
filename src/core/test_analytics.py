import tempfile
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from commerce.gateway import ProviderStatus
from commerce.models import Invoice
from commerce.services import reserve_invoice, settle
from creators.models import CreatorProfile
from learning.services import enroll, save_progress
from learning.support import post_question, reply_question
from scripts.demo_commerce import seed

from .analytics import dashboard_data, ratio
from .models import ActivityEvent


@override_settings(SECURE_SSL_REDIRECT=False)
class AnalyticsTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        config = override_settings(MEDIA_ROOT=self.media.name)
        config.enable()
        self.addCleanup(config.disable)
        self.data = seed()
        self.today = timezone.localdate()
        self.client.force_login(self.data.student)

    def buy(self, session=None):
        invoice = reserve_invoice(self.data.student, self.data.bundle.pk, activity_session=session)
        Invoice.objects.filter(pk=invoice.pk).update(payment_hash="d" * 64, issue_state="ready")
        settle(invoice.pk, ProviderStatus(True, 150000, "d" * 64))
        return invoice

    def stats(self, creator=None):
        return dashboard_data(self.today, self.today, creator)

    def test_empty_ratios_and_invalid_dates(self):
        self.assertIsNone(ratio(0, 0)["percent"])
        self.client.force_login(self.data.creator)
        self.assertContains(self.client.get(reverse("creator-analytics")), "Sin datos")
        self.assertContains(self.client.get(reverse("creator-analytics")), f'value="{self.today:%Y-%m-%d}"')
        self.assertEqual(self.client.get(reverse("creator-analytics"), {"start": "bad", "end": "bad"}).status_code, 400)
        self.assertEqual(self.client.get(reverse("creator-analytics"), {"start": "2026-10-10", "end": "2026-01-01"}).status_code, 400)

    def test_payment_cohort_counts_bundle_once_and_ignores_repeated_confirmation(self):
        session = uuid4()
        invoice = self.buy(session)
        settle(invoice.pk, ProviderStatus(True, 150000, "d" * 64))
        stats = self.stats(self.data.creator)
        self.assertEqual((stats["invoice_count"], stats["paid_count"], stats["volume"]), (1, 1, 150))
        self.assertEqual(stats["payment_completion"]["percent"], 100)
        self.assertGreater(stats["opening"]["denominator"], 1)
        self.assertEqual(ActivityEvent.objects.filter(kind="invoice_created").count(), 1)

    def test_views_deduplicate_session_offer_and_reused_invoice_has_one_source(self):
        url = reverse("offer-detail", args=[self.data.bundle.pk])
        self.client.get(url)
        self.client.get(url)
        session = self.client.session["activity_session"]
        invoice = reserve_invoice(self.data.student, self.data.bundle.pk, activity_session=session)
        self.assertEqual(reserve_invoice(self.data.student, self.data.bundle.pk, activity_session=uuid4()).pk, invoice.pk)
        stats = self.stats(self.data.creator)
        self.assertEqual(stats["request_conversion"], {"numerator": 1, "denominator": 1, "percent": 100.0})
        self.assertEqual(ActivityEvent.objects.filter(kind="invoice_created").count(), 1)

    def test_permission_open_is_deduplicated_and_denied_content_not_counted(self):
        lesson = self.data.records[1]
        url = reverse("version-lesson", args=[self.data.course.pk, self.data.version.number, lesson.pk])
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertFalse(ActivityEvent.objects.filter(kind="purchased_content_opened").exists())
        self.buy()
        self.client.get(url)
        self.client.get(url)
        stats = self.stats()
        self.assertEqual(stats["opening"]["numerator"], 1)
        self.assertEqual(ActivityEvent.objects.filter(kind="purchased_content_opened").count(), 2)

    def test_library_return_requires_later_different_session(self):
        session = uuid4()
        invoice = self.buy(session)
        with patch("django.utils.timezone.now", return_value=invoice.created_at):
            ActivityEvent.objects.create(kind="library_viewed", actor=self.data.student, session_id=uuid4())
        self.assertEqual(self.stats(self.data.creator)["library_return"]["numerator"], 0)
        ActivityEvent.objects.create(kind="library_viewed", actor=self.data.student, session_id=session)
        self.assertEqual(self.stats(self.data.creator)["library_return"]["numerator"], 0)
        ActivityEvent.objects.create(kind="library_viewed", actor=self.data.student, session_id=uuid4())
        self.assertEqual(self.stats(self.data.creator)["library_return"]["numerator"], 1)

    def test_creator_scope_and_admin_permissions(self):
        self.buy()
        creator = get_user_model().objects.create_user("isolated@metrics.invalid", account_type="creator")
        CreatorProfile.objects.create(user=creator, status="approved", display_name="Otro")
        self.assertEqual(self.stats(creator)["volume"], 0)
        self.client.force_login(creator)
        page = self.client.get(reverse("creator-analytics"))
        self.assertNotContains(page, self.data.course.title)
        self.assertEqual(self.client.get(reverse("admin-analytics")).status_code, 302)
        self.client.force_login(self.data.reviewer)
        self.assertContains(self.client.get(reverse("admin-analytics")), "150 sats")
        self.assertContains(self.client.get(reverse("admin:index")), "Consultar actividad")
        self.client.force_login(self.data.student)
        self.assertEqual(self.client.get(reverse("creator-analytics")).status_code, 302)
        staff = get_user_model().objects.create_user("staff@metrics.invalid", account_type="admin", is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse("admin-analytics")).status_code, 403)

    def test_administrator_and_creator_views_do_not_record_customer_activity(self):
        self.client.force_login(self.data.reviewer)
        self.client.get(reverse("offer-detail", args=[self.data.bundle.pk]))
        self.client.force_login(self.data.creator)
        self.client.get(reverse("course-version", args=[self.data.course.pk, self.data.version.number]))
        self.assertFalse(ActivityEvent.objects.exists())

    def test_date_boundary_uses_el_salvador_calendar(self):
        invoice = self.buy()
        midnight = timezone.make_aware(timezone.datetime.combine(self.today, timezone.datetime.min.time()))
        Invoice.objects.filter(pk=invoice.pk).update(created_at=midnight - timedelta(seconds=1))
        self.assertEqual(self.stats()["invoice_count"], 0)
        Invoice.objects.filter(pk=invoice.pk).update(created_at=midnight)
        self.assertEqual(self.stats()["invoice_count"], 1)

    def test_completion_and_answer_time_use_actual_records(self):
        enrollment = enroll(self.data.student, self.data.version)
        self.buy()
        for index, lesson in enumerate(self.data.records):
            save_progress(self.data.student, enrollment.pk, lesson.pk, index, "complete")
        question = post_question(self.data.student, self.data.records[0].pk, "Pregunta", uuid4())
        reply_question(self.data.creator, question.pk, "Respuesta", uuid4())
        stats = self.stats()
        self.assertEqual(stats["course_completion"]["percent"], 100)
        self.assertEqual((stats["answered_count"], stats["question_count"]), (1, 1))
        self.assertIsNotNone(stats["answer_hours"])

    def test_telemetry_failure_does_not_block_content(self):
        from django.db import OperationalError
        # Patch the wrapper rather than the database transaction, keeping tests usable.
        with patch("core.telemetry.ActivityEvent.objects.create", side_effect=OperationalError("Unavailable")):
            with self.assertLogs("core.telemetry", level="WARNING"):
                self.assertEqual(Client().get(reverse("offer-detail", args=[self.data.bundle.pk])).status_code, 200)
