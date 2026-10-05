import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from content.models import (
    Chapter,
    Course,
    Lesson,
    LessonResource,
    Material,
    PublicationStatus,
)
from content.publication import publish_course, publish_resource
from media.models import Asset

from .models import CreatorProfile, Submission
from .services import decide, submit


class CreatorJourneyTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.media.name, SECURE_SSL_REDIRECT=False)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        users = get_user_model().objects
        self.owner = users.create_user("creator@example.invalid", account_type="creator")
        self.other = users.create_user("other@example.invalid", account_type="creator")
        self.reviewer = users.create_superuser("review@example.invalid")
        for user in (self.owner, self.other):
            CreatorProfile.objects.create(user=user, display_name="Docente", bio="Aprendo y enseño.", specialty="Tecnología", status="approved")
        self.course = Course.objects.create(creator=self.owner, title="Curso original", description="Descripción para alumnos")
        self.chapter = Chapter.objects.create(course=self.course, title="Capítulo", status="published")
        self.lesson = Lesson.objects.create(chapter=self.chapter, title="Lección", body="Texto original secreto", status="published")
        self.client.force_login(self.owner)

    def material(self, owner=None):
        owner = owner or self.owner
        asset = Asset.objects.create(creator=owner, file=SimpleUploadedFile("guia.txt", b"Guia privada", content_type="text/plain"))
        return Material.objects.create(creator=owner, title="Guía", description="Práctica", pending_asset=asset)

    def test_application_requires_login_and_cannot_self_approve(self):
        student = get_user_model().objects.create_user("student@example.invalid", account_type="creator")
        self.client.logout()
        self.assertEqual(self.client.get(reverse("creator-application")).status_code, 302)
        self.client.force_login(student)
        response = self.client.post(reverse("creator-application"), {"display_name": "Ana", "bio": "Enseño", "specialty": "Código", "accept_rights": "on", "status": "approved", "user": self.owner.pk})
        self.assertEqual(response.status_code, 302)
        profile = CreatorProfile.objects.get(user=student)
        self.assertEqual(profile.status, "pending")
        self.assertEqual(self.client.get(reverse("creator-dashboard")).status_code, 403)
        self.assertEqual(self.client.get(reverse("creator-public-profile", args=[student.pk])).status_code, 404)

    def test_suspension_disables_tools_and_cannot_be_reset_from_form(self):
        CreatorProfile.objects.filter(user=self.owner).update(status="suspended")
        self.assertEqual(self.client.get(reverse("creator-dashboard")).status_code, 403)
        self.assertEqual(self.client.post(reverse("creator-application"), {"display_name": "Reset"}).status_code, 403)
        self.assertEqual(CreatorProfile.objects.get(user=self.owner).status, "suspended")
        with self.assertRaises(PermissionDenied):
            submit(self.course, self.owner)

    def test_owner_is_assigned_by_server_and_status_is_not_editable(self):
        response = self.client.post(reverse("creator-course-new"), {"title": "Tutorial", "kind": "tutorial", "description": "Guía", "creator": self.other.pk, "status": "published"})
        self.assertEqual(response.status_code, 302)
        item = Course.objects.get(title="Tutorial")
        self.assertEqual(item.creator_id, self.owner.pk)
        self.assertEqual(item.status, "draft")

    def test_foreign_content_is_denied_on_get_and_post(self):
        self.client.force_login(self.other)
        paths = [reverse("creator-course", args=[self.course.pk]), reverse("creator-chapter", args=[self.course.pk, self.chapter.pk]), reverse("creator-lesson", args=[self.chapter.pk, self.lesson.pk]), reverse("creator-course-preview", args=[self.course.pk]), reverse("creator-send", args=["cursos", self.course.pk])]
        for path in paths:
            self.assertIn(self.client.get(path).status_code, (404, 405))
            self.assertIn(self.client.post(path, {"title": "Intruso"}).status_code, (404, 405))
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Curso original")

    def test_submission_freezes_text_but_does_not_publish(self):
        submission = submit(self.course, self.owner)
        self.course.refresh_from_db()
        self.assertIsNone(self.course.current_version_id)
        self.assertEqual(self.course.status, "draft")
        self.lesson.body = "Texto nuevo del borrador"
        self.lesson.save()
        self.course.title = "Título nuevo"
        self.course.save()
        response = self.client.get(reverse("creator-review", args=[submission.pk]))
        self.assertContains(response, "Texto original secreto")
        self.assertNotContains(response, "Texto nuevo del borrador")
        decide(submission, self.reviewer, True)
        self.course.refresh_from_db()
        self.assertEqual(self.course.current_version.title, "Curso original")
        self.assertEqual(self.course.title, "Título nuevo")
        self.assertEqual(self.course.current_version.chapters.first().lessons.first().content.body, "Texto original secreto")

    def test_submitted_version_and_text_are_hidden_from_visitors(self):
        submission = submit(self.course, self.owner)
        anonymous = Client()
        self.assertEqual(anonymous.get(reverse("course-version", args=[self.course.pk, submission.course_version.number])).status_code, 404)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("creator-review", args=[submission.pk])).status_code, 403)

    def test_duplicate_submit_withdraw_and_resubmit(self):
        first = submit(self.course, self.owner)
        with self.assertRaises(ValidationError):
            submit(self.course, self.owner)
        response = self.client.post(reverse("creator-withdraw", args=[first.pk]))
        self.assertEqual(response.status_code, 302)
        second = submit(self.course, self.owner)
        self.assertNotEqual(first.course_version_id, second.course_version_id)
        with self.assertRaises(ValidationError):
            decide(first, self.reviewer, True)
        first.refresh_from_db()
        self.assertEqual(first.status, "withdrawn")

    def test_rejection_requires_feedback_and_allows_new_submission(self):
        first = submit(self.course, self.owner)
        with self.assertRaises(ValidationError):
            decide(first, self.reviewer, False)
        decide(first, self.reviewer, False, "Añade una explicación.")
        first.refresh_from_db()
        self.assertEqual(first.feedback, "Añade una explicación.")
        self.assertIsNone(Course.objects.get(pk=self.course.pk).current_version_id)
        self.assertEqual(submit(self.course, self.owner).status, "pending")

    def test_owner_cannot_approve_and_staff_requires_explicit_permissions(self):
        submission = submit(self.course, self.owner)
        with self.assertRaises(PermissionDenied):
            decide(submission, self.owner, True)
        self.assertEqual(self.client.post(reverse("creator-review", args=[submission.pk]), {"decision": "approve"}).status_code, 403)
        staff = get_user_model().objects.create_user("staff@example.invalid", is_staff=True)
        with self.assertRaises(PermissionDenied):
            decide(submission, staff, True)
        staff.user_permissions.add(Permission.objects.get(codename="change_submission"))
        staff = get_user_model().objects.get(pk=staff.pk)
        with self.assertRaises(PermissionDenied):
            decide(submission, staff, True)

    def test_decision_cannot_repeat_or_reverse(self):
        submission = submit(self.course, self.owner)
        decide(submission, self.reviewer, True)
        with self.assertRaises(ValidationError):
            decide(submission, self.reviewer, False, "Cambio de opinión")
        submission.refresh_from_db()
        self.assertEqual(submission.status, "approved")
        self.assertEqual(self.course.versions.count(), 1)

    def test_new_draft_and_submission_keep_previous_publication(self):
        old = publish_course(self.course, self.reviewer)
        response = self.client.post(reverse("creator-lesson", args=[self.chapter.pk, self.lesson.pk]), {"title": "Nueva lección", "position": 1, "body": "Contenido nuevo", "access_type": "free", "status": "published"})
        self.assertEqual(response.status_code, 302)
        submission = submit(self.course, self.owner)
        self.course.refresh_from_db()
        self.assertEqual(self.course.current_version_id, old.pk)
        public = Client().get(reverse("course-detail", args=[self.course.pk]))
        self.assertContains(public, "Lección")
        self.assertNotContains(public, "Nueva lección")
        decide(submission, self.reviewer, True)
        self.assertEqual(old.chapters.first().lessons.first().content.body, "Texto original secreto")

    def test_invalid_course_submission_rolls_back(self):
        self.lesson.body = ""
        self.lesson.save()
        with self.assertRaises(ValidationError):
            submit(self.course, self.owner)
        self.assertEqual(self.course.versions.count(), 0)
        self.assertEqual(Submission.objects.count(), 0)

    def test_review_cannot_replace_a_newer_admin_publication(self):
        submission = submit(self.course, self.owner)
        newer = publish_course(self.course, self.reviewer)
        with self.assertRaises(ValidationError):
            decide(submission, self.reviewer, True)
        self.course.refresh_from_db()
        submission.refresh_from_db()
        self.assertEqual(self.course.current_version_id, newer.pk)
        self.assertEqual(submission.status, "pending")

    def test_resource_submission_freezes_file_and_delivery_is_scoped(self):
        material = self.material()
        first_asset = material.pending_asset
        submission = submit(material, self.owner)
        material.pending_asset = self.material().pending_asset
        material.title = "Otra guía"
        material.save()
        decide(submission, self.reviewer, True)
        material.refresh_from_db()
        self.assertEqual(material.revision.asset_id, first_asset.pk)
        url = reverse("creator-review-file", args=[submission.pk, first_asset.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response.close()
        response = self.client.head(url)
        self.assertEqual(response.status_code, 200)
        response.close()
        self.client.force_login(self.reviewer)
        response = self.client.get(url, HTTP_RANGE="bytes=0-3")
        self.assertEqual(response.status_code, 206)
        response.close()
        unrelated = self.material().pending_asset
        self.assertEqual(self.client.get(reverse("creator-review-file", args=[submission.pk, unrelated.pk])).status_code, 404)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.get(reverse("creator-file", args=[first_asset.pk])).status_code, 404)

    def test_upload_validation_and_owner_enforcement(self):
        response = self.client.post(reverse("creator-files"), {"file": SimpleUploadedFile("not-safe.html", b"<script>alert(1)</script>", content_type="text/html"), "creator": self.other.pk})
        self.assertContains(response, "Formato no admitido")
        self.assertEqual(Asset.objects.count(), 0)
        response = self.client.post(reverse("creator-files"), {"file": SimpleUploadedFile("apuntes.txt", b"Texto valido", content_type="text/plain"), "creator": self.other.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Asset.objects.get().creator_id, self.owner.pk)

    def test_foreign_asset_and_revision_cannot_be_selected(self):
        foreign = self.material(self.other)
        response = self.client.post(reverse("creator-resource-new", args=["materiales"]), {"title": "Robo", "description": "Prueba", "access_type": "free", "pending_asset": foreign.pending_asset_id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Material.objects.filter(title="Robo").exists())
        revision = publish_resource(foreign, self.reviewer)
        response = self.client.post(reverse("creator-lesson", args=[self.chapter.pk, self.lesson.pk]), {"title": "Lección", "position": 1, "body": "Texto", "access_type": "free", "status": "published", "resources": [revision.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LessonResource.objects.count(), 0)

    def test_attach_approved_resource_and_course_review_file(self):
        material = self.material()
        revision = publish_resource(material, self.reviewer)
        response = self.client.post(reverse("creator-lesson", args=[self.chapter.pk, self.lesson.pk]), {"title": "Lección", "position": 1, "body": "Texto", "access_type": "free", "status": "published", "resources": [revision.pk]})
        self.assertEqual(response.status_code, 302)
        submission = submit(self.course, self.owner)
        self.client.force_login(self.reviewer)
        self.assertContains(self.client.get(reverse("creator-review", args=[submission.pk])), "guia.txt")
        response = self.client.get(reverse("creator-review-file", args=[submission.pk, material.pending_asset_id]))
        self.assertEqual(response.status_code, 200)
        response.close()

    def test_position_conflict_shows_error_without_losing_text(self):
        response = self.client.post(reverse("creator-lesson-new", args=[self.chapter.pk]), {"title": "Conservar este título", "position": 1, "body": "Conservar este texto", "access_type": "free", "status": "published"})
        self.assertContains(response, "Este orden ya lo ocupa")
        self.assertContains(response, "Conservar este texto")
        self.assertEqual(self.chapter.lessons.count(), 1)

    def test_preview_pages_and_public_profile_do_not_leak_email(self):
        self.assertContains(self.client.get(reverse("creator-course-preview", args=[self.course.pk])), "Texto original secreto")
        material = self.material()
        self.assertEqual(self.client.get(reverse("creator-resource-preview", args=["materiales", material.pk])).status_code, 200)
        response = Client().get(reverse("creator-public-profile", args=[self.owner.pk]))
        self.assertContains(response, "Docente")
        self.assertNotContains(response, self.owner.email)

    def test_empty_post_shows_required_fields(self):
        response = self.client.post(reverse("creator-course-new"), {})
        self.assertContains(response, "Este campo es obligatorio")

    def test_ajax_save_preserves_success_message_for_destination(self):
        response = self.client.post(reverse("creator-course-new"), {"title": "AJAX", "kind": "course", "description": "Curso nuevo"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertContains(self.client.get(response.json()["redirect"]), "Información guardada")

    def test_csrf_and_post_only_submission(self):
        secure_client = Client(enforce_csrf_checks=True)
        secure_client.force_login(self.owner)
        url = reverse("creator-send", args=["cursos", self.course.pk])
        self.assertEqual(secure_client.get(url).status_code, 405)
        self.assertEqual(secure_client.post(url).status_code, 403)

    def test_legacy_publication_must_be_frozen_before_edit(self):
        Course.objects.filter(pk=self.course.pk).update(status=PublicationStatus.PUBLISHED)
        response = self.client.post(reverse("creator-course", args=[self.course.pk]), {"title": "No publicar sin revisión", "kind": "course"})
        self.assertEqual(response.status_code, 403)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Curso original")
