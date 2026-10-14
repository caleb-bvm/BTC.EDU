import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from commerce.offers import create_offer, review_offer, submit_offer
from creators.forms import LessonForm, MaterialForm
from creators.models import CreatorProfile
from creators.services import decide, submit
from media.models import Asset

from .education import EDUCATION_FIELDS
from .models import Chapter, Course, Lesson, Material, ResourceVersion
from .publication import publish_course, publish_resource
from .testing import EDUCATION_FIXTURE


@override_settings(SECURE_SSL_REDIRECT=False)
class EducationalUnitTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("units@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=self.creator, status="approved", display_name="Docente")
        self.reviewer = users.create_superuser("unit-review@example.invalid")
        self.course = Course.objects.create(creator=self.creator, title="Curso", description="Un recorrido educativo")
        self.chapter = Chapter.objects.create(course=self.course, title="Capítulo", status="published")
        self.lesson = Lesson.objects.create(chapter=self.chapter, title="Unidad", body="SOLUCION_PRIVADA_917", access_type="paid", status="published", **EDUCATION_FIXTURE)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        settings = override_settings(MEDIA_ROOT=self.temporary.name)
        settings.enable()
        self.addCleanup(settings.disable)

    def material(self):
        asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("ejercicio.txt", b"ARCHIVO_PRIVADO", content_type="text/plain"))
        return Material.objects.create(creator=self.creator, title="Material", description="Actividad", pending_asset=asset, transcript="TRANSCRIPCION_PRIVADA_917", access_type="paid", **EDUCATION_FIXTURE)

    def test_incomplete_draft_saves_but_all_publication_paths_reject_it(self):
        self.lesson.learning_outcome = " "
        self.lesson.save()
        with self.assertRaisesMessage(ValidationError, "qué aprenderá"):
            submit(self.course, self.creator)
        with self.assertRaises(ValidationError):
            publish_course(self.course, self.reviewer)
        self.assertFalse(self.course.versions.exists())
        resource = self.material()
        resource.public_preview = ""
        resource.save()
        for action in (lambda: submit(resource, self.creator), lambda: publish_resource(resource, self.reviewer)):
            with self.assertRaisesMessage(ValidationError, "muestra pública"):
                action()
        self.assertFalse(ResourceVersion.objects.exists())

    def test_invalid_activity_cannot_be_published_through_service(self):
        self.lesson.activity_kind = "invented"
        self.lesson.save()
        with self.assertRaisesMessage(ValidationError, "tipo de actividad válido"):
            publish_course(self.course, self.reviewer)

    def test_review_and_publication_use_submitted_educational_information(self):
        submission = submit(self.course, self.creator)
        self.lesson.learning_outcome = "OBJETIVO_POSTERIOR_917"
        self.lesson.public_preview = "MUESTRA_POSTERIOR_917"
        self.lesson.save()
        self.client.force_login(self.reviewer)
        response = self.client.get(reverse("creator-review", args=[submission.pk]))
        self.assertContains(response, EDUCATION_FIXTURE["learning_outcome"])
        self.assertNotContains(response, "OBJETIVO_POSTERIOR_917")
        decide(submission, self.reviewer, True)
        stored = submission.course_version.chapters.first().lessons.first()
        response = Client().get(reverse("version-lesson", args=[self.course.pk, submission.course_version.number, stored.pk]))
        self.assertContains(response, EDUCATION_FIXTURE["public_preview"], status_code=403)
        self.assertNotContains(response, "MUESTRA_POSTERIOR_917", status_code=403)
        self.assertNotContains(response, self.lesson.body, status_code=403)

    def test_each_profile_change_creates_revision_and_keeps_previous_purchase_metadata(self):
        version = publish_course(self.course, self.reviewer)
        initial = version.chapters.first().lessons.first().content
        for field in EDUCATION_FIELDS:
            setattr(self.lesson, field, "design" if field == "activity_kind" else f"Nuevo {field}")
            self.lesson.save()
            newest = publish_course(self.course, self.reviewer).chapters.first().lessons.first().content
            self.assertNotEqual(initial.pk, newest.pk)
            initial.refresh_from_db()
            self.assertEqual(getattr(initial, field), EDUCATION_FIXTURE[field])
        newest_version = publish_course(self.course, self.reviewer)
        self.assertEqual(newest.pk, newest_version.chapters.first().lessons.first().content_id)

    def test_paid_offer_shows_public_sample_without_body_and_escapes_markup(self):
        self.lesson.public_preview = '<script>alert("sample")</script> MUESTRA_PUBLICA_917'
        self.lesson.save()
        version = publish_course(self.course, self.reviewer)
        stored = version.chapters.first().lessons.first()
        offer = create_offer(self.creator, f"lesson:{stored.pk}", "Unidad", 50)
        submit_offer(self.creator, offer)
        review_offer(self.reviewer, offer, True)
        response = Client().get(reverse("offer-detail", args=[offer.pk]))
        self.assertContains(response, "MUESTRA_PUBLICA_917")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("sample")</script>')
        self.assertNotContains(response, self.lesson.body)

    def test_resource_public_profile_uses_revision_and_never_draft_or_transcript(self):
        resource = self.material()
        revision = publish_resource(resource, self.reviewer)
        resource.learning_outcome = "BORRADOR_RECURSO_917"
        resource.public_preview = "BORRADOR_MUESTRA_917"
        resource.save()
        response = Client().get(reverse("resource-detail", args=["materiales", resource.pk]))
        self.assertContains(response, revision.learning_outcome)
        self.assertContains(response, revision.public_preview)
        self.assertNotContains(response, "BORRADOR_RECURSO_917")
        self.assertNotContains(response, "BORRADOR_MUESTRA_917")
        self.assertNotContains(response, resource.transcript)
        self.assertNotContains(response, "ARCHIVO_PRIVADO")

    def test_authoring_forms_allow_empty_profile_until_submission(self):
        form = LessonForm({"title": "Borrador", "body": "Texto", "access_type": "free", "position": 2, "status": "draft"}, instance=Lesson(chapter=self.chapter), actor=self.creator)
        self.assertTrue(form.is_valid(), form.errors)
        draft = form.save()
        self.assertEqual(draft.learning_outcome, "")
        resource_form = MaterialForm(instance=self.material(), actor=self.creator)
        for field in EDUCATION_FIELDS:
            self.assertIn(field, form.fields)
            self.assertIn(field, resource_form.fields)
            self.assertFalse(form.fields[field].required)

    def test_legacy_profile_renders_without_invented_information(self):
        resource = self.material()
        revision = publish_resource(resource, self.reviewer)
        ResourceVersion._base_manager.filter(pk=revision.pk).update(**{field: "" for field in EDUCATION_FIELDS})
        response = Client().get(reverse("resource-detail", args=["materiales", resource.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Sobre esta unidad")
        resource.public_preview = "BORRADOR_NO_PUBLICADO_917"
        resource.revision = None
        # Rows predating version publication cannot expose new draft metadata.
        Material._base_manager.filter(pk=resource.pk).update(revision=None)
        response = Client().get(reverse("resource-detail", args=["materiales", resource.pk]))
        self.assertNotContains(response, "BORRADOR_NO_PUBLICADO_917")


class EducationMigrationTests(TransactionTestCase):
    def test_additive_migration_preserves_rows_and_leaves_historical_profiles_empty(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        previous = [node for node in latest if node[0] != "content"] + [("content", "0005_resourceversion_topic")]
        try:
            executor.migrate(previous)
            apps = executor.loader.project_state(previous).apps
            user = apps.get_model("accounts", "User").objects.create(email="old-unit@example.invalid", password="!")
            course = apps.get_model("content", "Course").objects.create(creator_id=user.pk, title="Histórico")
            chapter = apps.get_model("content", "Chapter").objects.create(course_id=course.pk, title="Capítulo")
            lesson = apps.get_model("content", "Lesson").objects.create(chapter_id=chapter.pk, title="Unidad anterior", body="Texto anterior")
            revision = apps.get_model("content", "ResourceVersion").objects.create(creator_id=user.pk, title="Revisión anterior", kind="text", access_type="paid", body="Privado anterior")
            old_lesson = apps.get_model("content", "Lesson").objects.values().get(pk=lesson.pk)
            old_revision = apps.get_model("content", "ResourceVersion").objects.values().get(pk=revision.pk)
            executor = MigrationExecutor(connection)
            executor.migrate(latest)
            self.assertEqual(Lesson.objects.values(*old_lesson).get(pk=lesson.pk), old_lesson)
            self.assertEqual(ResourceVersion.objects.values(*old_revision).get(pk=revision.pk), old_revision)
            self.assertEqual({field: getattr(ResourceVersion.objects.get(pk=revision.pk), field) for field in EDUCATION_FIELDS}, dict.fromkeys(EDUCATION_FIELDS, ""))
        finally:
            MigrationExecutor(connection).migrate(latest)
