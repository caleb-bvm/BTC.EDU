import io
import tempfile
import uuid
import zipfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.export import account_data
from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile
from creators.services import submit

from .bookmarks import save_item
from .collections import change_collection, organize_item
from .models import (
    Notification,
    PracticeDelivery,
    PracticeDraft,
    PracticeIntake,
    PracticeReview,
    SavedCollection,
    SavedItem,
    VersionPractice,
)
from .practices import (
    review_delivery,
    save_practice,
    set_intake,
    submit_delivery,
    validate_attachment,
)
from .services import enroll


@override_settings(SECURE_SSL_REDIRECT=False)
class CollectionsPracticesTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        settings = override_settings(MEDIA_ROOT=self.media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        users = get_user_model().objects
        self.student = users.create_user("student@practice.invalid")
        self.other = users.create_user("other@practice.invalid")
        self.creator = users.create_user("creator@practice.invalid", account_type="creator")
        self.other_creator = users.create_user("othercreator@practice.invalid", account_type="creator")
        self.admin = users.create_superuser("admin@practice.invalid")
        for actor in (self.creator, self.other_creator):
            CreatorProfile.objects.create(user=actor, display_name="Educador", status="approved")
        self.course = Course.objects.create(creator=self.creator, title="Mi curso", description="Descripción")
        self.chapter = Chapter.objects.create(course=self.course, title="Inicio", status="published")
        self.lesson = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=self.chapter, title="Proyecto", body="Lección", status="published")
        self.draft = PracticeDraft.objects.create(lesson=self.lesson, title="Mi práctica", instructions="INSTRUCCION_PRIVADA", criteria=["Resultado correcto", "Explica cómo probarlo"], review_days=3)
        self.version = publish_course(self.course, self.admin)
        self.practice = self.version.chapters.first().lessons.first().practice
        self.enrollment = enroll(self.student, self.version)
        self.client.force_login(self.student)

    def delivery(self, **changes):
        values = dict(actor=self.student, practice_id=self.practice.pk, body="Mi solución", project_url="https://example.org/proyecto", attachment=None, request_key=uuid.uuid4(), previous_id=0)
        values.update(changes)
        return submit_delivery(**values)

    def saved(self):
        save_item(self.student, "curso", self.version.pk, "save")
        return SavedItem.objects.get(student=self.student)

    def test_collections_are_named_unique_private_and_multiple(self):
        item = self.saved()
        first = change_collection(self.student, "create", "  Para   estudiar ")
        second = change_collection(self.student, "create", "Mi proyecto")
        organize_item(self.student, item.pk, [str(first.pk), str(second.pk)])
        self.assertEqual(item.collections.count(), 2)
        with self.assertRaises(ValidationError):
            change_collection(self.student, "create", "PARA ESTUDIAR")
        other = change_collection(self.other, "create", "Repasar")
        for actor, item_id, ids in [(self.student, item.pk, [other.pk]), (self.other, item.pk, [])]:
            with self.assertRaises(PermissionDenied):
                organize_item(actor, item_id, ids)
        with self.assertRaises(PermissionDenied):
            change_collection(self.other, "delete", pk=first.pk)
        self.assertEqual(item.collections.count(), 2)
        change_collection(self.student, "rename", "Repasar", first.pk)
        change_collection(self.student, "delete", pk=first.pk)
        self.assertTrue(SavedItem.objects.filter(pk=item.pk).exists())
        self.assertEqual(item.collections.count(), 1)

    def test_collection_filter_forms_and_unassigned(self):
        item = self.saved()
        collection = change_collection(self.student, "create", "Mi proyecto")
        base = reverse("workspace") + "?seccion=guardados"
        self.assertContains(self.client.get(base + "&coleccion=sin-coleccion"), item.title)
        organize_item(self.student, item.pk, [collection.pk])
        page = self.client.get(base + f"&coleccion={collection.pk}")
        self.assertContains(page, "Guardar organización")
        self.assertContains(page, 'name="collections"')
        self.assertEqual(list(page.context["saved_items"]), [item])
        self.assertFalse(self.client.get(base + "&coleccion=sin-coleccion").context["saved_items"])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(base + f"&coleccion={collection.pk}").status_code, 404)
        self.assertEqual(self.client.post(reverse("bookmark-organize", args=[item.pk]), {"collections": []}).status_code, 403)

    def test_collection_endpoints_and_safe_redirects(self):
        item = self.saved()
        response = self.client.post(reverse("collection-create"), {"action": "create", "name": "Repasar"})
        collection = SavedCollection.objects.get(student=self.student)
        self.assertRedirects(response, reverse("workspace") + f"?seccion=guardados&coleccion={collection.pk}")
        response = self.client.post(reverse("bookmark-organize", args=[item.pk]), {"collections": [collection.pk], "next": "https://evil.invalid/"})
        self.assertRedirects(response, reverse("workspace") + "?seccion=guardados")
        self.assertEqual(self.client.get(reverse("collection-change", args=[collection.pk])).status_code, 405)

    def test_version_freezes_practice_and_editorial_review_shows_it(self):
        self.draft.instructions = "Nuevo borrador"
        self.draft.save()
        self.practice.refresh_from_db()
        self.assertEqual(self.practice.instructions, "INSTRUCCION_PRIVADA")
        with self.assertRaises(ValidationError):
            VersionPractice.objects.filter(pk=self.practice.pk).update(instructions="Cambiar")
        with self.assertRaises(ValidationError):
            self.practice.delete()
        submission = submit(self.course, self.creator)
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(reverse("creator-review", args=[submission.pk])), "Nuevo borrador")
        self.assertContains(self.client.get(reverse("creator-review", args=[submission.pk])), "Resultado correcto")

    def test_editor_revision_and_publication_disable_preserves_previous(self):
        values = dict(title="Proyecto", instructions="Entrega un diseño", criteria=["Diseño comprobable"], review_days=5, enabled=False)
        saved = save_practice(self.creator, self.lesson.pk, values, 0)
        self.assertEqual(saved.revision, 1)
        with self.assertRaises(ValidationError):
            save_practice(self.creator, self.lesson.pk, values, 0)
        with self.assertRaises(PermissionDenied):
            save_practice(self.other_creator, self.lesson.pk, values, 1)
        new_version = publish_course(self.course, self.admin)
        self.assertFalse(VersionPractice.objects.filter(lesson__chapter__version=new_version).exists())
        self.assertTrue(VersionPractice.objects.filter(pk=self.practice.pk).exists())

    def test_complete_delivery_changes_resubmission_acceptance_and_notices(self):
        first = self.delivery()
        self.assertEqual(first.state, "pending")
        self.assertEqual(first.due_at - first.submitted_at, timedelta(days=3))
        self.assertTrue(Notification.objects.filter(recipient=self.creator, event_key=f"practice-delivery:{first.pk}").exists())
        with self.assertRaises(ValidationError):
            self.delivery(previous_id=first.pk)
        review = review_delivery(self.creator, first.pk, "changes", "Explica los pasos de prueba.", [0])
        self.assertTrue(Notification.objects.filter(recipient=self.student, event_key=f"practice-review:{review.pk}").exists())
        second = self.delivery(body="Solución corregida", previous_id=first.pk)
        review_delivery(self.creator, second.pk, "accepted", "Cumple los criterios.", [0, 1])
        with self.assertRaises(ValidationError):
            self.delivery(previous_id=second.pk)
        self.assertEqual(self.practice.deliveries.count(), 2)
        response = self.client.get(reverse("student-practice", args=[self.practice.pk]))
        for text in ("Práctica aprobada", "Solución corregida", "Explica los pasos", "Mi solución"):
            self.assertContains(response, text)

    def test_review_requires_owner_feedback_all_criteria_and_is_immutable(self):
        delivery = self.delivery()
        with self.assertRaises(PermissionDenied):
            review_delivery(self.other_creator, delivery.pk, "accepted", "Bien", [0, 1])
        for outcome, feedback, criteria in [("accepted", "Bien", [0]), ("changes", "", []), ("changes", "Falta", [10])]:
            with self.assertRaises(ValidationError):
                review_delivery(self.creator, delivery.pk, outcome, feedback, criteria)
        review = review_delivery(self.creator, delivery.pk, "changes", "Corrige", [])
        self.assertEqual(review_delivery(self.creator, delivery.pk, "changes", "Corrige", []).pk, review.pk)
        with self.assertRaises(ValidationError):
            review_delivery(self.creator, delivery.pk, "accepted", "Bien", [0, 1])
        with self.assertRaises(ValidationError):
            PracticeReview.objects.filter(pk=review.pk).update(feedback="Cambio")

    def test_delivery_retries_and_stale_forms_do_not_duplicate(self):
        key = uuid.uuid4()
        delivery = self.delivery(request_key=key)
        self.assertEqual(self.delivery(request_key=key).pk, delivery.pk)
        with self.assertRaises(ValidationError):
            self.delivery(request_key=key, body="Otro contenido")
        review_delivery(self.creator, delivery.pk, "changes", "Corrige", [])
        with self.assertRaises(ValidationError):
            self.delivery(previous_id=0)
        self.assertEqual(PracticeDelivery.objects.count(), 1)

    def test_private_attachment_download_and_no_storage_path_in_html(self):
        delivery = self.delivery(attachment=SimpleUploadedFile("solución.txt", b"resultado", content_type="text/plain"))
        url = reverse("practice-attachment", args=[delivery.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"resultado")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("no-store", response["Cache-Control"])
        page = self.client.get(reverse("student-practice", args=[self.practice.pk]))
        self.assertNotContains(page, delivery.attachment.name)
        for actor, expected in [(self.other, 403), (self.other_creator, 403), (self.creator, 200)]:
            self.client.force_login(actor)
            file_response = self.client.get(url)
            self.assertEqual(file_response.status_code, expected)
            file_response.close()
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_invalid_uploads_rejected_before_storage(self):
        for upload in [SimpleUploadedFile("x.html", b"<script>alert(1)</script>"), SimpleUploadedFile("fake.pdf", b"not pdf"), SimpleUploadedFile("binary.txt", b"\x00"), SimpleUploadedFile("empty.txt", b"")]:
            with self.assertRaises(ValidationError):
                self.delivery(attachment=upload)
        upload = SimpleUploadedFile("huge.txt", b"ok")
        upload.size = 10 * 1024 * 1024 + 1
        with self.assertRaises(ValidationError):
            validate_attachment(upload)
        self.assertEqual(list(Path(self.media.name).rglob("*")), [])

    def test_rollback_removes_uploaded_file(self):
        with patch("learning.practices.notify", side_effect=RuntimeError("Notification failed")):
            with self.assertRaises(RuntimeError):
                self.delivery(attachment=SimpleUploadedFile("solution.txt", b"resultado"))
        self.assertFalse(PracticeDelivery.objects.exists())
        self.assertFalse(any(p.is_file() for p in Path(self.media.name).rglob("*")))

    def test_pause_and_reopen_reception_with_pending_reviews_kept(self):
        first = self.delivery()
        set_intake(self.creator, self.practice.pk, False, 0)
        review_delivery(self.creator, first.pk, "changes", "Corrige", [])
        with self.assertRaises(ValidationError):
            self.delivery(previous_id=first.pk)
        response = self.client.get(reverse("student-practice", args=[self.practice.pk]))
        self.assertContains(response, "ha pausado la recepción")
        with self.assertRaises(ValidationError):
            set_intake(self.creator, self.practice.pk, True, 0)
        set_intake(self.creator, self.practice.pk, True, 1)
        self.assertEqual(self.delivery(previous_id=first.pk).number, 2)

    def test_non_enrolled_or_inactive_cannot_submit_and_paid_access_is_required(self):
        with self.assertRaises(PermissionDenied):
            self.delivery(actor=self.other)
        get_user_model().objects.filter(pk=self.student.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied):
            self.delivery()
        get_user_model().objects.filter(pk=self.student.pk).update(is_active=True)
        self.student.refresh_from_db()
        self.lesson.access_type = "paid"
        self.lesson.save()
        version = publish_course(self.course, self.admin)
        practice = version.chapters.first().lessons.first().practice
        enroll(self.student, version)
        with self.assertRaises(PermissionDenied):
            self.delivery(practice_id=practice.pk)
        self.assertNotContains(self.client.get(reverse("student-practice", args=[practice.pk])), "INSTRUCCION_PRIVADA")

    def test_pages_render_role_navigation_and_inbox_is_private(self):
        first = self.delivery()
        for name, args in [("student-practices", []), ("student-practice", [self.practice.pk])]:
            response = self.client.get(reverse(name, args=args))
            self.assertEqual(response.status_code, 200)
        self.assertContains(self.client.get(reverse("version-lesson", args=[self.course.pk, self.version.number, self.practice.lesson_id])), "Ver práctica y entregas")
        self.client.force_login(self.creator)
        for name, args in [("creator-practices", []), ("creator-practice-delivery", [first.pk]), ("creator-practice", [self.lesson.pk]), ("creator-dashboard", []), ("creator-course", [self.course.pk])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200)
        self.client.force_login(self.other_creator)
        self.assertNotContains(self.client.get(reverse("creator-practices")), self.practice.title)
        self.assertEqual(self.client.get(reverse("creator-practice-delivery", args=[first.pk])).status_code, 404)

    def test_post_delivery_and_review_forms_escape_text_and_notify(self):
        response = self.client.post(reverse("student-practice", args=[self.practice.pk]), {"body": "<script>unsafe()</script>", "project_url": "", "request_key": uuid.uuid4(), "previous_id": 0, "attachment": SimpleUploadedFile("solution.txt", b"OK")})
        self.assertEqual(response.status_code, 302)
        delivery = PracticeDelivery.objects.get()
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(reverse("creator-practice-delivery", args=[delivery.pk])), "&lt;script&gt;unsafe()&lt;/script&gt;")
        self.assertRedirects(self.client.post(reverse("creator-practice-delivery", args=[delivery.pk]), {"met_criteria": ["0", "1"], "outcome": "accepted", "feedback": "Buen resultado"}), reverse("creator-practice-delivery", args=[delivery.pk]))
        self.assertEqual(PracticeReview.objects.get().outcome, "accepted")

    def test_service_rejects_dangerous_links_empty_deliveries_and_bad_keys(self):
        for changes in [{"project_url": "javascript:alert(1)"}, {"body": "", "project_url": ""}, {"request_key": "invalid"}]:
            with self.assertRaises(ValidationError):
                self.delivery(**changes)
        self.assertFalse(PracticeDelivery.objects.exists())

    def test_account_export_includes_collections_deliveries_and_feedback(self):
        item = self.saved()
        collection = change_collection(self.student, "create", "Repasar")
        organize_item(self.student, item.pk, [collection.pk])
        delivery = self.delivery()
        review_delivery(self.creator, delivery.pk, "changes", "Corrige", [])
        data = account_data(self.student)
        self.assertEqual(data["saved_collections"][0]["name"], "Repasar")
        self.assertEqual(data["practice_deliveries"][0]["body"], "Mi solución")
        self.assertEqual(data["practice_reviews"][0]["feedback"], "Corrige")

    def test_zip_and_image_uploads_are_validated_without_extracting(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("project/readme.txt", "Mi proyecto")
        self.assertEqual(validate_attachment(SimpleUploadedFile("project.zip", buffer.getvalue())), "project.zip")
        from PIL import Image
        buffer = io.BytesIO()
        Image.new("RGB", (2, 2), "white").save(buffer, format="PNG")
        self.assertEqual(validate_attachment(SimpleUploadedFile("result.png", buffer.getvalue())), "result.png")
        for name, data in [("fake.zip", b"ZIP"), ("fake.png", b"PNG"), ("bad\nname.txt", b"OK")]:
            with self.assertRaises(ValidationError):
                validate_attachment(SimpleUploadedFile(name, data))

    def test_file_retry_checks_content_and_allows_long_original_names(self):
        key = uuid.uuid4()
        filename = "a" * 150 + ".txt"
        first = self.delivery(request_key=key, attachment=SimpleUploadedFile(filename, b"primera"))
        self.assertEqual(first.attachment_name, filename)
        repeated = self.delivery(request_key=key, attachment=SimpleUploadedFile(filename, b"primera"))
        self.assertEqual(first.pk, repeated.pk)
        with self.assertRaises(ValidationError):
            self.delivery(request_key=key, attachment=SimpleUploadedFile(filename, b"segunda"))
        self.assertEqual(len([path for path in Path(self.media.name).rglob("*") if path.is_file()]), 1)

    def test_suspended_educator_cannot_review_or_change_reception(self):
        delivery = self.delivery()
        CreatorProfile.objects.filter(user=self.creator).update(status="suspended")
        with self.assertRaises(PermissionDenied):
            review_delivery(self.creator, delivery.pk, "changes", "Corrige", [])
        with self.assertRaises(PermissionDenied):
            set_intake(self.creator, self.practice.pk, False, 0)
        self.assertFalse(PracticeReview.objects.exists())
        self.assertFalse(PracticeIntake.objects.exists())

    def test_form_errors_preserve_text_and_do_not_write_a_delivery(self):
        response = self.client.post(reverse("student-practice", args=[self.practice.pk]), {"body": "Mi trabajo conservado", "previous_id": 0, "request_key": uuid.uuid4(), "attachment": SimpleUploadedFile("fake.pdf", b"Not a PDF")})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi trabajo conservado")
        self.assertContains(response, "PDF, ZIP, TXT")
        self.assertFalse(PracticeDelivery.objects.exists())
        self.client.force_login(self.creator)
        response = self.client.post(reverse("creator-practice", args=[self.lesson.pk]), {"enabled": True, "title": "Mi título", "instructions": "Mi instrucción", "criteria_text": "Resultado", "review_days": 3, "revision": 0})
        self.assertEqual(response.status_code, 302)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.criteria, ["Resultado"])
        self.assertContains(self.client.get(reverse("creator-course", args=[self.course.pk]) + "?seccion=evaluaciones"), reverse("creator-practice", args=[self.lesson.pk]))

    def test_pause_endpoint_and_inbox_exclude_other_educators(self):
        self.delivery()
        self.client.force_login(self.other_creator)
        url = reverse("creator-practice-intake", args=[self.practice.pk])
        self.assertEqual(self.client.post(url, {"action": "pause", "revision": 0}).status_code, 404)
        self.client.force_login(self.creator)
        self.assertRedirects(self.client.post(url, {"action": "pause", "revision": 0}), reverse("creator-practices"))
        self.assertFalse(PracticeIntake.objects.get(practice=self.practice).accepting)

    def test_cross_account_form_and_csrf_protection(self):
        response = self.client.post(reverse("student-practice", args=[self.practice.pk]), {"account_id": self.other.pk, "body": "No guardar", "request_key": uuid.uuid4(), "previous_id": 0})
        self.assertEqual(response.status_code, 403)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.student)
        self.assertEqual(csrf_client.post(reverse("collection-create"), {"action": "create", "name": "Repasar"}).status_code, 403)
        self.assertFalse(PracticeDelivery.objects.exists())

