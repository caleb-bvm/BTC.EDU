import tempfile

from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from commerce.gateway import ProviderStatus
from commerce.models import Invoice
from commerce.services import reserve_invoice, settle
from content.models import Course
from content.publication import publish_course
from scripts.demo_commerce import seed

from .models import Enrollment, LessonProgress
from .services import StaleProgress, enroll, save_progress


class LearningJourneyTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        config = override_settings(MEDIA_ROOT=self.media.name, SECURE_SSL_REDIRECT=False)
        config.enable()
        self.addCleanup(config.disable)
        self.data = seed()
        self.client.force_login(self.data.student)
        self.enrollment = enroll(self.data.student, self.data.version)

    def buy(self):
        invoice = reserve_invoice(self.data.student, self.data.bundle.pk)
        Invoice.objects.filter(pk=invoice.pk).update(payment_hash="f" * 64, issue_state="ready")
        settle(invoice.pk, ProviderStatus(True, 150000, "f" * 64))

    def save(self, record=None, revision=0, action="complete", client=None):
        return (client or self.client).post(reverse("progress-update", args=[self.enrollment.pk]), {"lesson": (record or self.data.records[0]).pk, "revision": revision, "action": action}, HTTP_ACCEPT="application/json")

    def test_opening_and_completion_are_separate_and_resume_persists(self):
        self.buy()
        response = self.save(action="position")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LessonProgress.objects.exists())
        response = self.save(revision=1)
        self.assertEqual(response.json()["completed"], 1)
        self.client.logout()
        self.client.force_login(self.data.student)
        library = self.client.get(reverse("workspace"))
        self.assertContains(library, "1 de 3 lecciones completadas")
        self.assertContains(library, "Continuar")
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.last_lesson_id, self.data.records[0].pk)

    def test_locked_paid_lesson_cannot_be_completed_or_used_as_resume_point(self):
        response = self.save(record=self.data.records[1])
        self.assertEqual(response.status_code, 403)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.revision, 0)
        self.assertIsNone(self.enrollment.last_lesson_id)
        self.assertFalse(LessonProgress.objects.exists())
        self.save(record=self.data.records[0])
        self.assertContains(self.client.get(reverse("workspace")), "Ver acceso")

    def test_stale_save_does_not_overwrite_last_lesson_or_completion(self):
        self.buy()
        first = self.save()
        second = self.save(record=self.data.records[1], revision=first.json()["revision"])
        stale = self.save(action="incomplete", revision=0)
        self.assertEqual(stale.status_code, 409)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.last_lesson_id, self.data.records[1].pk)
        self.assertEqual(self.enrollment.revision, second.json()["revision"])
        self.assertEqual(LessonProgress.objects.count(), 2)

    def test_complete_retry_is_unique_and_unmark_is_explicit(self):
        self.save()
        self.save(revision=1)
        self.assertEqual(LessonProgress.objects.count(), 1)
        self.save(revision=2, action="position")
        self.assertEqual(LessonProgress.objects.count(), 1)
        response = self.save(revision=3, action="incomplete")
        self.assertEqual(response.json()["completed"], 0)
        self.assertFalse(LessonProgress.objects.exists())

    def test_other_account_creator_and_missing_csrf_cannot_write_progress(self):
        self.client.force_login(self.data.other)
        self.assertEqual(self.save().status_code, 404)
        self.client.force_login(self.data.creator)
        self.assertEqual(self.save().status_code, 302)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.data.student)
        self.assertEqual(self.save(client=client).status_code, 403)
        self.assertEqual(self.client.get(reverse("progress-update", args=[self.enrollment.pk])).status_code, 302)
        self.assertFalse(LessonProgress.objects.exists())

    def test_course_update_does_not_move_enrollment_or_copy_progress(self):
        self.save()
        self.data.lesson.body = "Nueva versión independiente"
        self.data.lesson.save()
        new = publish_course(self.data.course, self.data.reviewer)
        new_record = new.chapters.first().lessons.get(source_lesson_id=self.data.free.pk)
        with self.assertRaises(PermissionDenied):
            save_progress(self.data.student, self.enrollment.pk, new_record.pk, 1, "complete")
        second = enroll(self.data.student, new)
        self.assertEqual(second.revision, 0)
        self.assertFalse(second.completed_lessons.exists())
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.version_id, self.data.version.pk)
        self.assertEqual(self.enrollment.completed_lessons.count(), 1)

    def test_archived_enrolled_free_course_keeps_progress_and_private_access(self):
        self.save()
        Course.objects.filter(pk=self.data.course.pk).update(status="archived")
        url = reverse("version-lesson", args=[self.data.course.pk, self.data.version.number, self.data.records[0].pk])
        self.assertContains(self.client.get(url), "Esta lección está completada")
        self.assertContains(self.client.get(reverse("workspace")), "Versión conservada")
        self.client.force_login(self.data.other)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_invalid_payload_and_plain_form_have_honest_outcomes(self):
        endpoint = reverse("progress-update", args=[self.enrollment.pk])
        self.assertEqual(self.client.post(endpoint, {"revision": "bad"}, HTTP_ACCEPT="application/json").status_code, 400)
        self.assertEqual(self.client.post(endpoint, {"revision": 0, "lesson": self.data.records[0].pk, "action": "invented"}, HTTP_ACCEPT="application/json").status_code, 400)
        response = self.client.post(endpoint, {"revision": 0, "lesson": self.data.records[0].pk, "action": "complete"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("lecciones", response.url)
        self.assertContains(self.client.get(response.url), "Esta lección está completada")

    def test_all_completed_reports_full_progress_without_counting_materials(self):
        self.buy()
        for revision, record in enumerate(self.data.records):
            self.assertEqual(self.save(record, revision).status_code, 200)
        self.assertEqual(LessonProgress.objects.count(), 3)
        self.assertContains(self.client.get(reverse("workspace")), "100%")
        self.assertContains(self.client.get(reverse("workspace")), "Repasar")

    def test_direct_service_rejects_stale_revision(self):
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "position")
        with self.assertRaises(StaleProgress):
            save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "complete")
        self.assertEqual(Enrollment.objects.get(pk=self.enrollment.pk).revision, 1)
