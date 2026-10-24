import tempfile
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile
from creators.services import decide, submit
from learning.certificates import issue_certificate
from learning.models import CertificateDraft
from learning.services import enroll, save_progress
from media.models import Asset

from .models import Chapter, Course, Lesson, Material, ResourceVersion, Topic
from .publication import publish_course, publish_resource


@override_settings(SECURE_SSL_REDIRECT=False)
class PublicContentCoherenceTests(TestCase):
    def setUp(self):
        files = tempfile.TemporaryDirectory()
        self.addCleanup(files.cleanup)
        temporary_media = override_settings(MEDIA_ROOT=files.name)
        temporary_media.enable()
        self.addCleanup(temporary_media.disable)
        self.creator = get_user_model().objects.create_user("creator@coherence.invalid", account_type="creator", first_name="Nombre privado", last_name="Apellido privado")
        self.profile = CreatorProfile.objects.create(user=self.creator, display_name="Docente público", status="approved")
        self.admin = get_user_model().objects.create_superuser("admin@coherence.invalid")
        self.original_topic, _ = Topic.objects.get_or_create(slug="bitcoin", defaults={"name": "Bitcoin"})
        self.draft_topic, _ = Topic.objects.get_or_create(slug="lightning", defaults={"name": "Lightning"})
        self.asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("guia.txt", b"Material educativo", content_type="text/plain"))

    def resource(self, topic=None):
        return Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, title="Guía pública", description="Material revisado", topic=topic, pending_asset=self.asset)

    def test_public_creator_identity_is_consistent_while_certificate_keeps_historical_credit(self):
        course = Course.objects.create(creator=self.creator, title="Curso revisado", description="Aprende Bitcoin")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        lesson = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Primera lección", body="Contenido educativo", status="published")
        policy = CertificateDraft.objects.create(course=course, enabled=True)
        policy.required_lessons.set([lesson])
        version = publish_course(course, self.admin)
        student = get_user_model().objects.create_user("student@coherence.invalid")
        enrollment = enroll(student, version)
        save_progress(student, enrollment.pk, version.chapters.get().lessons.get().pk, 0, "complete")
        certificate = issue_certificate(student, enrollment.pk, "Alumno")
        resource = self.resource()
        publish_resource(resource, self.admin)
        self.profile.display_name = "Alias docente actualizado"
        self.profile.save(update_fields=["display_name"])
        for url in (reverse("courses"), reverse("resources"), reverse("course-detail", args=[course.pk]), reverse("resource-detail", args=["materiales", resource.pk]), reverse("creator-public-profile", args=[self.creator.pk])):
            with self.subTest(url=url):
                response = self.client.get(url, {"vista": "todos"} if url in (reverse("courses"), reverse("resources")) else {})
                self.assertContains(response, "Alias docente actualizado")
                self.assertNotContains(response, "Nombre privado")
                self.assertNotContains(response, self.creator.email)
        version.refresh_from_db()
        certificate.refresh_from_db()
        self.assertEqual(version.creator_name, "Docente público")
        self.assertEqual(certificate.creator_name, "Docente público")

    def test_suspended_profile_does_not_fall_back_to_private_creator_name(self):
        resource = self.resource()
        publish_resource(resource, self.admin)
        self.profile.status = "suspended"
        self.profile.save(update_fields=["status"])
        for url in (reverse("resources"), reverse("resource-detail", args=["materiales", resource.pk])):
            response = self.client.get(url, {"vista": "todos"} if url == reverse("resources") else {})
            self.assertContains(response, "Creador de BTC.EDU")
            self.assertNotContains(response, "Nombre privado")

    def test_resource_topic_changes_only_when_the_reviewed_revision_is_published(self):
        resource = self.resource(self.original_topic)
        first_submission = submit(resource, self.creator)
        resource.topic = self.draft_topic
        resource.save(update_fields=["topic"])
        decide(first_submission, self.admin, True)
        first = first_submission.resource_version
        response = self.client.get(reverse("resources"), {"tema": "bitcoin"})
        self.assertContains(response, "Guía pública")
        self.assertEqual(response.context["cards"][0]["item"].topic, self.original_topic)
        self.assertEqual(self.client.get(reverse("resources"), {"tema": "lightning"}).context["result_count"], 0)
        category = self.client.get(reverse("resources"), {"categoria": "bitcoin"})
        counts = {card["slug"]: card["count"] for card in category.context["subcategory_cards"]}
        self.assertEqual(counts["bitcoin"], 1)
        self.assertEqual(counts["lightning"], 0)
        response = self.client.get(reverse("resource-detail", args=["materiales", resource.pk]))
        self.assertEqual(response.context["resource"].topic, self.original_topic)
        second_submission = submit(resource, self.creator)
        decide(second_submission, self.admin, True)
        self.assertEqual(self.client.get(reverse("resources"), {"tema": "bitcoin"}).context["result_count"], 0)
        self.assertContains(self.client.get(reverse("resources"), {"tema": "lightning"}), "Guía pública")
        first.refresh_from_db()
        self.assertEqual(first.topic_id, self.original_topic.pk)
        with self.assertRaises(ProtectedError):
            self.original_topic.delete()

    def test_published_resource_without_topic_does_not_inherit_a_draft_topic(self):
        resource = self.resource()
        revision = publish_resource(resource, self.admin)
        resource.topic = self.draft_topic
        resource.save(update_fields=["topic"])
        response = self.client.get(reverse("resources"), {"vista": "todos"})
        self.assertEqual(response.context["cards"][0]["item"].topic, None)
        self.assertEqual({card["slug"]: card["count"] for card in response.context["category_cards"]}["bitcoin"], 0)
        self.assertEqual(self.client.get(reverse("resources"), {"tema": "lightning"}).context["result_count"], 0)
        revision.refresh_from_db()
        self.assertIsNone(revision.topic_id)


class ResourceTopicMigrationTests(TransactionTestCase):
    def test_migration_captures_current_classification_without_inventing_older_topics(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        # Descendants (including lesson discussions) also require the new field.
        descendants = set(executor.loader.graph.backwards_plan(("content", "0005_resourceversion_topic")))
        previous = [node for node in latest if node[0] != "content" and node not in descendants] + [
            ("content", "0004_courseversion_published_at_alter_chapter_status_and_more"),
        ]
        try:
            executor.migrate(previous)
            apps = executor.loader.project_state(previous).apps
            user = apps.get_model("accounts", "User").objects.create(email="legacy@topic.invalid", password="!")
            topic = apps.get_model("content", "Topic").objects.create(name="Tema observado", slug="observado")
            asset = apps.get_model("media", "Asset").objects.create(creator_id=user.pk, file="legacy-guide.txt", kind="material", mime_type="text/plain", size=7, sha256="a" * 64, original_name="guide.txt")
            revisions = apps.get_model("content", "ResourceVersion")
            key = uuid4()
            old = revisions.objects.create(resource_key=key, number=1, creator_id=user.pk, kind="material", title="Anterior", access_type="paid", asset_id=asset.pk)
            current = revisions.objects.create(resource_key=key, number=2, creator_id=user.pk, kind="material", title="Actual", access_type="paid", asset_id=asset.pk)
            apps.get_model("content", "Material").objects.create(creator_id=user.pk, title="Borrador", resource_key=key, topic_id=topic.pk, revision_id=current.pk)
            original_values = list(revisions.objects.order_by("pk").values())
            MigrationExecutor(connection).migrate(latest)
            self.assertIsNone(ResourceVersion.objects.get(pk=old.pk).topic_id)
            self.assertEqual(ResourceVersion.objects.get(pk=current.pk).topic_id, topic.pk)
            fields = tuple(original_values[0])
            self.assertEqual(list(ResourceVersion.objects.order_by("pk").values(*fields)), original_values)
        finally:
            MigrationExecutor(connection).migrate(latest)
