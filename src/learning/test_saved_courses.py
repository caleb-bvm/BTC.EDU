from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from commerce.models import Entitlement
from content.models import Chapter, Course, ExternalReference, Lesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile
from creators.services import submit

from .bookmarks import bookmark_context, save_item
from .models import Enrollment, SavedItem
from .services import enroll


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_SEND_EMAIL=False,
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class SavedCourseTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.student = users.create_user("student@saved-courses.invalid")
        self.other = users.create_user("other@saved-courses.invalid")
        self.creator = users.create_user("creator@saved-courses.invalid", account_type="creator")
        self.admin = users.create_superuser("admin@saved-courses.invalid")
        CreatorProfile.objects.create(user=self.creator, display_name="Educador", status="approved")
        self.course = Course.objects.create(creator=self.creator, title="Curso para guardar", description="Un recorrido")
        chapter = Chapter.objects.create(course=self.course, title="Inicio", status="published")
        self.lesson = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Unidad con precio", body="CONTENIDO_PROTEGIDO", access_type="paid", status="published")
        self.version = publish_course(self.course, self.admin)
        self.record = self.version.chapters.first().lessons.first()
        self.client.force_login(self.student)

    def test_saved_course_is_idempotent_and_does_not_enroll_or_unlock(self):
        first = save_item(self.student, "curso", self.version.pk, "save")
        second = save_item(self.student, "curso", self.version.pk, "save")
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.course_version_id, self.version.pk)
        self.assertFalse(Enrollment.objects.exists())
        self.assertFalse(Entitlement.objects.exists())
        from accounts.export import account_data
        self.assertEqual(account_data(self.student)["saved_items"][0]["course_version_id"], self.version.pk)
        lesson_url = reverse("version-lesson", args=[self.course.pk, self.version.number, self.record.pk])
        self.assertEqual(self.client.get(lesson_url).status_code, 403)
        self.assertNotContains(self.client.get(lesson_url), "CONTENIDO_PROTEGIDO", status_code=403)
        self.assertRedirects(self.client.get(reverse("bookmark-open", args=[first.pk])), reverse("course-version", args=[self.course.pk, self.version.number]))

    def test_tutorial_alias_and_course_share_one_version_reference(self):
        self.course.kind = "tutorial"
        self.course.title = "Tutorial para guardar"
        self.course.save()
        version = publish_course(self.course, self.admin)
        first = save_item(self.student, "tutorial", version.pk, "save")
        self.assertEqual(save_item(self.student, "curso", version.pk, "save").pk, first.pk)
        context = bookmark_context(self.student, course_version=version)
        self.assertEqual(context["bookmark_kind"], "tutorial")
        page = self.client.get(reverse("course-version", args=[self.course.pk, version.number]))
        self.assertContains(page, reverse("bookmark-toggle", args=["tutorial", version.pk]))
        self.assertContains(self.client.get(reverse("workspace"), {"seccion": "guardados"}), "Abrir tutorial")

    def test_snapshot_does_not_follow_new_publication_and_old_access_is_guarded(self):
        saved = save_item(self.student, "curso", self.version.pk, "save")
        self.course.title = "Nueva publicación"
        self.course.save()
        publish_course(self.course, self.admin)
        unavailable = self.client.get(reverse("bookmark-open", args=[saved.pk]))
        self.assertContains(unavailable, "ya no está disponible")
        saved.refresh_from_db()
        self.assertEqual(saved.title, "Curso para guardar")
        self.assertEqual(saved.course_version_id, self.version.pk)
        Entitlement.objects.create(buyer=self.student, resource=self.record.content)
        self.assertRedirects(self.client.get(reverse("bookmark-open", args=[saved.pk])), reverse("course-version", args=[self.course.pk, self.version.number]))
        self.assertEqual(save_item(self.student, "curso", self.version.pk, "save").pk, saved.pk)
        save_item(self.student, "curso", self.version.pk, "remove")
        self.assertFalse(SavedItem.objects.exists())
        self.assertTrue(Entitlement.objects.filter(buyer=self.student, resource=self.record.content).exists())

    def test_historical_enrollment_allows_metadata_without_creating_paid_rights(self):
        enrollment = enroll(self.student, self.version)
        self.course.title = "Versión nueva"
        self.course.save()
        publish_course(self.course, self.admin)
        saved = save_item(self.student, "curso", self.version.pk, "save")
        self.assertEqual(saved.title, "Curso para guardar")
        self.assertTrue(Enrollment.objects.filter(pk=enrollment.pk).exists())
        self.assertFalse(Entitlement.objects.exists())

    def test_unpublished_version_wrong_accounts_and_foreign_saved_rows_are_denied(self):
        pending = submit(self.course, self.creator).course_version
        for actor, version in ((self.student, pending), (self.creator, self.version), (AnonymousUser(), self.version)):
            with self.assertRaises(PermissionDenied):
                save_item(actor, "curso", version.pk, "save")
        self.assertFalse(bookmark_context(AnonymousUser(), course_version=self.version)["is_saved"])
        saved = save_item(self.student, "curso", self.version.pk, "save")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("bookmark-open", args=[saved.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("workspace"), {"seccion": "guardados"}), saved.title)

    def test_single_target_and_unique_saved_course_constraints(self):
        reference = ExternalReference.objects.create(title="Fuente", source_name="Documentación", source_url="https://example.invalid/source", status="published")
        with self.assertRaises(IntegrityError), transaction.atomic():
            SavedItem.objects.create(student=self.student, title="Inválido")
        with self.assertRaises(IntegrityError), transaction.atomic():
            SavedItem.objects.create(student=self.student, title="Inválido", course_version=self.version, reference=reference)
        save_item(self.student, "curso", self.version.pk, "save")
        with self.assertRaises(IntegrityError), transaction.atomic():
            SavedItem.objects.create(student=self.student, title="Duplicado", course_version=self.version)

    def test_saved_filters_and_removal_preserve_context_and_owner(self):
        save_item(self.student, "curso", self.version.pk, "save")
        reference = ExternalReference.objects.create(title="Referencia", source_name="Documentación", source_url="https://example.invalid/source", status="published")
        save_item(self.student, "referencia", reference.pk, "save")
        page = self.client.get(reverse("workspace"), {"seccion": "guardados", "guardados_tipo": "cursos", "guardados_q": "Curso"})
        self.assertEqual(page.context["saved_items"].paginator.count, 1)
        self.assertContains(page, "Abrir curso")
        self.assertNotContains(page, "<h3>Referencia</h3>")
        course_url = reverse("course-version", args=[self.course.pk, self.version.number])
        response = self.client.post(reverse("bookmark-toggle", args=["curso", self.version.pk]), {"action": "remove", "next": course_url})
        self.assertRedirects(response, course_url)
        self.assertEqual(SavedItem.objects.count(), 1)
