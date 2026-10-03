import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from media.models import Asset

from .models import (
    AccessType,
    Chapter,
    Course,
    CourseVersion,
    Lesson,
    LessonResource,
    Material,
    PublicationStatus,
    ResourceVersion,
    Topic,
    VersionAttachment,
    VersionChapter,
    VersionLesson,
    Video,
)
from .publication import publish_course, publish_resource


class VersionMediaTests(TestCase):
    def setUp(self):
        self.files = tempfile.TemporaryDirectory()
        self.addCleanup(self.files.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.files.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.creator = get_user_model().objects.create_user("writer@example.invalid")
        self.other = get_user_model().objects.create_user("other@example.invalid")
        self.staff = get_user_model().objects.create_superuser("reviewer@example.invalid", "local-test-password")
        self.course = Course.objects.create(title="Título publicado", creator=self.creator, status=PublicationStatus.PUBLISHED)
        self.chapter = Chapter.objects.create(course=self.course, title="Capítulo", status=PublicationStatus.PUBLISHED)
        self.lesson = Lesson.objects.create(chapter=self.chapter, title="Lección", body="Texto inicial", status=PublicationStatus.PUBLISHED)

    def asset(self, name="guide.txt", data=b"Material original", creator=None, mime="text/plain"):
        return Asset.objects.create(creator=creator or self.creator, file=SimpleUploadedFile(name, data, content_type=mime))

    def material(self, access=AccessType.FREE):
        resource = Material.objects.create(creator=self.creator, title="Material publicado", pending_asset=self.asset(), access_type=access)
        revision = publish_resource(resource, self.staff)
        resource.refresh_from_db()
        return resource, revision

    def video(self):
        data = (Path(__file__).resolve().parent.parent / "media/fixtures/white.mp4").read_bytes()
        asset = self.asset("clip.mp4", data, mime="video/mp4")
        captions = self.asset("captions.vtt", b"WEBVTT\n\n00:00.000 --> 00:01.000\nEjemplo\n", mime="text/vtt")
        resource = Video.objects.create(creator=self.creator, title="Video", pending_asset=asset, pending_subtitles=captions, transcript="Transcripción de prueba")
        revision = publish_resource(resource, self.staff)
        resource.refresh_from_db()
        return resource, revision

    def file_url(self, resource, part="archivo"):
        return reverse("resource-file", args=["videos" if isinstance(resource, Video) else "materiales", resource.pk, resource.revision.number, part])

    def bytes(self, response):
        value = b"".join(response.streaming_content) if response.streaming else response.content
        response.close()
        return value

    def test_version_freezes_catalogue_body_topic_and_composition(self):
        version = publish_course(self.course, self.staff)
        self.course.title = "Borrador distinto"
        self.course.kind = "tutorial"
        self.course.topic = Topic.objects.create(name="Nuevo tema", slug="nuevo")
        self.course.save()
        self.lesson.body = "NO PUBLICADO"
        self.lesson.access_type = AccessType.PAID
        self.lesson.save()
        catalog = self.client.get(reverse("courses"))
        self.assertContains(catalog, "Título publicado")
        self.assertNotContains(catalog, "Borrador distinto")
        self.assertEqual(self.client.get(reverse("courses") + "?tema=nuevo").context["result_count"], 0)
        response = self.client.get(reverse("lesson-content", args=[self.lesson.pk]))
        self.assertEqual(response.json()["body"], "Texto inicial")
        self.assertEqual(response.json()["version"], version.number)
        self.assertContains(self.client.get(reverse("course-detail", args=[self.course.pk])), "Versión 1")

    def test_new_version_retains_old_text_and_reuses_unchanged_revisions(self):
        first = publish_course(self.course, self.staff)
        second = publish_course(self.course, self.staff)
        self.assertEqual(ResourceVersion.objects.filter(kind="text").count(), 1)
        self.lesson.body = "Texto corregido"
        self.lesson.save()
        third = publish_course(self.course, self.staff)
        self.assertEqual([first.number, second.number, third.number], [1, 2, 3])
        self.assertEqual(first.chapters.get().lessons.get().content.body, "Texto inicial")
        self.assertEqual(ResourceVersion.objects.filter(kind="text").count(), 2)

    def test_immutable_records_and_historical_composition_cannot_be_extended_or_deleted(self):
        first = publish_course(self.course, self.staff)
        publish_course(self.course, self.staff)
        first.title = "Overwrite"
        with self.assertRaises(ValidationError):
            first.save()
        with self.assertRaises(ValidationError):
            CourseVersion.objects.filter(pk=first.pk).update(title="Overwrite")
        with self.assertRaises(ValidationError):
            VersionChapter.objects.create(version=first, title="Extra", position=2)
        with self.assertRaises(ValidationError):
            first.delete()
        with self.assertRaises(ProtectedError):
            self.course.delete()

    def test_publication_is_reviewed_atomic_and_rejects_incompatible_attachments(self):
        with self.assertRaises(PermissionDenied):
            publish_course(self.course, self.creator)
        resource, revision = self.material()
        LessonResource.objects.create(lesson=self.lesson, resource=revision)
        # A second lesson lacks content. No partially published version survives.
        Lesson.objects.create(chapter=self.chapter, title="Vacía", position=2, status=PublicationStatus.PUBLISHED)
        with self.assertRaises(ValidationError):
            publish_course(self.course, self.staff)
        self.assertEqual(CourseVersion.objects.count(), 0)
        self.assertEqual(VersionLesson.objects.count(), 0)
        foreign = self.asset(creator=self.other)
        resource.pending_asset = foreign
        resource.save()
        with self.assertRaises(ValidationError):
            publish_resource(resource, self.staff)
        self.assertEqual(ResourceVersion.objects.filter(resource_key=revision.resource_key).count(), 1)

    def test_legacy_lesson_link_survives_deleting_authoring_lesson(self):
        publish_course(self.course, self.staff)
        lesson_id = self.lesson.pk
        self.lesson.delete()
        self.assertContains(self.client.get(reverse("lesson-detail", args=[lesson_id])), "Texto inicial")
        self.assertEqual(self.client.get(reverse("lesson-content", args=[lesson_id])).json()["body"], "Texto inicial")

    def test_old_versions_are_retained_for_owner_and_hidden_from_unrelated_users(self):
        first = publish_course(self.course, self.staff)
        publish_course(self.course, self.staff)
        url = reverse("course-version", args=[self.course.pk, first.number])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(self.creator)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_missing_unpublished_lesson_does_not_fall_back_to_mutable_text(self):
        publish_course(self.course, self.staff)
        extra = Lesson.objects.create(chapter=self.chapter, title="Nueva", body="Texto no publicado", position=2, status=PublicationStatus.PUBLISHED)
        self.assertEqual(self.client.get(reverse("lesson-detail", args=[extra.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("lesson-content", args=[extra.pk])).status_code, 404)

    def test_material_download_is_private_and_owner_can_inspect_paid_file(self):
        resource, _ = self.material()
        response = self.client.get(self.file_url(resource))
        self.assertEqual(self.bytes(response), b"Material original")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("private", response["Cache-Control"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        resource.access_type = AccessType.PAID
        resource.save()
        publish_resource(resource, self.staff)
        resource.refresh_from_db()
        self.assertEqual(self.client.get(self.file_url(resource)).status_code, 403)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.file_url(resource)).status_code, 403)
        self.client.force_login(self.creator)
        self.assertEqual(self.bytes(self.client.get(self.file_url(resource))), b"Material original")

    def test_video_ranges_head_suffix_and_invalid_ranges(self):
        resource, _ = self.video()
        url = self.file_url(resource)
        full = self.bytes(self.client.get(url))
        response = self.client.get(url, HTTP_RANGE="bytes=4-7")
        self.assertEqual(response.status_code, 206)
        self.assertEqual(self.bytes(response), b"ftyp")
        self.assertEqual(response["Content-Range"], f"bytes 4-7/{len(full)}")
        self.assertEqual(response["Content-Length"], "4")
        self.assertEqual(self.bytes(self.client.get(url, HTTP_RANGE="bytes=-7")), full[-7:])
        self.assertEqual(self.bytes(self.client.get(url, HTTP_RANGE="bytes=8-")), full[8:])
        head = self.client.head(url, HTTP_RANGE="bytes=4-7")
        self.assertEqual(head.status_code, 206)
        self.assertEqual(head.content, b"")
        self.assertEqual(head["Content-Length"], "4")
        for value in (f"bytes={len(full)}-", "bytes=7-4", "bytes=-0", "bytes=0-1,3-4", "bad", "bytes=-"):
            response = self.client.get(url, HTTP_RANGE=value)
            self.assertEqual(response.status_code, 416, value)
            self.assertEqual(response["Content-Range"], f"bytes */{len(full)}")
        self.assertEqual(self.client.post(url).status_code, 405)

    def test_if_range_and_conditional_requests_still_require_permission(self):
        resource, _ = self.video()
        url = self.file_url(resource)
        head = self.client.head(url)
        etag = head["ETag"]
        self.assertEqual(self.client.get(url, HTTP_IF_NONE_MATCH=etag).status_code, 304)
        response = self.client.get(url, HTTP_RANGE="bytes=0-2", HTTP_IF_RANGE='"different"')
        self.assertEqual(response.status_code, 200)
        self.bytes(response)
        resource.status = PublicationStatus.DRAFT
        resource.save()
        self.assertEqual(self.client.get(url, HTTP_IF_NONE_MATCH=etag).status_code, 404)

    def test_reused_attachment_keeps_original_file_after_resource_replacement(self):
        resource, revision = self.material()
        LessonResource.objects.create(lesson=self.lesson, resource=revision)
        version = publish_course(self.course, self.staff)
        attachment = VersionAttachment.objects.get(lesson__chapter__version=version)
        resource.pending_asset = self.asset("replacement.txt", b"Material nuevo")
        resource.save()
        publish_resource(resource, self.staff)
        url = reverse("attachment-file", args=[attachment.pk, "archivo"])
        self.assertEqual(self.bytes(self.client.get(url)), b"Material original")
        resource.refresh_from_db()
        self.assertEqual(self.bytes(self.client.get(self.file_url(resource))), b"Material nuevo")
        self.assertTrue(Path(revision.asset.file.path).exists())

    def test_each_attachment_checks_lesson_and_its_own_access(self):
        resource, revision = self.material(access=AccessType.PAID)
        LessonResource.objects.create(lesson=self.lesson, resource=revision)
        version = publish_course(self.course, self.staff)
        attachment = VersionAttachment.objects.get(lesson__chapter__version=version)
        url = reverse("attachment-file", args=[attachment.pk, "archivo"])
        self.assertEqual(self.client.get(url).status_code, 403)
        lesson_url = reverse("version-lesson", args=[self.course.pk, version.number, attachment.lesson_id])
        self.assertContains(self.client.get(lesson_url), "Texto inicial")
        self.assertNotContains(self.client.get(lesson_url), url)
        self.client.force_login(self.creator)
        self.assertEqual(self.bytes(self.client.get(url)), b"Material original")
        self.client.logout()
        self.lesson.access_type = AccessType.PAID
        self.lesson.save()
        new_version = publish_course(self.course, self.staff)
        new_attachment = VersionAttachment.objects.get(lesson__chapter__version=new_version)
        response = self.client.get(reverse("version-lesson", args=[self.course.pk, new_version.number, new_attachment.lesson_id]))
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, "Texto inicial", status_code=403)
        self.assertEqual(self.client.get(reverse("attachment-file", args=[new_attachment.pk, "archivo"])).status_code, 403)

    def test_video_and_captions_render_only_with_access(self):
        resource, _ = self.video()
        detail = reverse("resource-detail", args=["videos", resource.pk])
        response = self.client.get(detail)
        self.assertContains(response, "<video")
        self.assertContains(response, "Transcripción de prueba")
        self.assertEqual(self.bytes(self.client.get(self.file_url(resource, "subtitulos")))[:6], b"WEBVTT")
        resource.access_type = AccessType.PAID
        resource.save()
        publish_resource(resource, self.staff)
        resource.refresh_from_db()
        response = self.client.get(detail)
        self.assertNotContains(response, "<video")
        self.assertNotContains(response, "Transcripción de prueba")
        self.assertEqual(self.client.get(self.file_url(resource, "subtitulos")).status_code, 403)

    def test_missing_file_is_a_useful_incident_without_disclosing_path(self):
        resource, revision = self.material()
        Path(revision.asset.file.path).unlink()
        response = self.client.get(self.file_url(resource))
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, self.files.name, status_code=404)
        self.assertContains(self.client.get(reverse("resource-detail", args=["materiales", resource.pk])), "El archivo no está disponible")

    def test_file_validation_rejects_spoofing_empty_invalid_text_and_excess_size(self):
        for name, data, mime in (("file.mp4", b"fake", "video/mp4"), ("guide.pdf", b"not pdf", "application/pdf"), ("file.html", b"<script>", "text/html"), ("file.txt", b"\x00binary", "text/plain"), ("file.txt", b"\xff", "text/plain"), ("empty.txt", b"", "text/plain"), ("sub.vtt", b"fake", "text/vtt"), ("file.txt", b"text", "application/pdf")):
            with self.subTest(name=name, data=data), self.assertRaises(ValidationError):
                self.asset(name, data, mime=mime)
        with override_settings(CONTENT_MAX_UPLOAD_BYTES=3), self.assertRaises(ValidationError):
            self.asset()
        self.assertEqual(Asset.objects.count(), 0)

    def test_asset_names_urls_and_overwrites_cannot_open_public_storage(self):
        asset = self.asset("../../guide.txt")
        self.assertEqual(asset.original_name, "guide.txt")
        self.assertNotIn("guide", asset.file.name)
        with self.assertRaises(ValueError):
            _ = asset.file.url
        asset.file = SimpleUploadedFile("new.txt", b"replaced", content_type="text/plain")
        with self.assertRaises(ValidationError):
            asset.save()
        self.assertEqual(self.client.get("/media/" + asset.file.name).status_code, 404)

    def test_admin_upload_and_publication_actions(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("admin:media_asset_add"), {"creator": self.creator.pk, "file": SimpleUploadedFile("guide.txt", b"admin upload", content_type="text/plain"), "_save": "Guardar"})
        self.assertEqual(response.status_code, 302)
        asset = Asset.objects.get()
        resource = Material.objects.create(title="Adjunto", creator=self.creator, pending_asset=asset)
        response = self.client.post(reverse("admin:content_material_changelist"), {"action": "publish_revision", "_selected_action": resource.pk, "index": 0})
        self.assertEqual(response.status_code, 302)
        resource.refresh_from_db()
        self.assertIsNotNone(resource.revision)
        self.client.post(reverse("admin:content_course_changelist"), {"action": "publish_version", "_selected_action": self.course.pk, "index": 0})
        self.course.refresh_from_db()
        self.assertIsNotNone(self.course.current_version)

    def test_public_resource_metadata_and_access_remain_frozen_until_republished(self):
        resource, revision = self.material(access=AccessType.PAID)
        resource.title = "Borrador pendiente"
        resource.access_type = AccessType.FREE
        resource.save()
        response = self.client.get(reverse("resource-detail", args=["materiales", resource.pk]))
        self.assertContains(response, "Material publicado")
        self.assertNotContains(response, "Borrador pendiente")
        self.assertEqual(self.client.get(self.file_url(resource)).status_code, 403)
        self.assertEqual(self.client.get(reverse("resources") + "?acceso=gratis").context["result_count"], 0)
        self.assertEqual(revision.access_type, AccessType.PAID)

    def test_real_mp4_fixture_and_pdf_can_be_loaded(self):
        data = (Path(__file__).resolve().parent.parent / "media/fixtures/white.mp4").read_bytes()
        clip = self.asset("white.mp4", data, mime="video/mp4")
        self.assertEqual(clip.mime_type, "video/mp4")
        pdf = self.asset("guide.pdf", b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n", mime="application/pdf")
        self.assertEqual(pdf.kind, "material")
        with self.assertRaises(ValidationError):
            self.asset("truncated.mp4", data[:-20], mime="video/mp4")

    def test_admin_rejects_invalid_upload_without_writing_a_file(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse("admin:media_asset_add"), {"creator": self.creator.pk, "file": SimpleUploadedFile("fake.mp4", b"not video", content_type="video/mp4"), "_save": "Guardar"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formato no admitido")
        self.assertEqual(Asset.objects.count(), 0)

    def test_changing_authoring_rows_cannot_reset_published_pointers(self):
        stale_course = Course.objects.get(pk=self.course.pk)
        version = publish_course(self.course, self.staff)
        stale_course.title = "Edición local"
        stale_course.save()
        self.assertEqual(Course.objects.get(pk=self.course.pk).current_version_id, version.pk)
        material, _ = self.material()
        stale_resource = Material.objects.get(pk=material.pk)
        newest = publish_resource(material, self.staff)
        stale_resource.title = "Borrador"
        stale_resource.save()
        self.assertEqual(Material.objects.get(pk=material.pk).revision_id, newest.pk)


class ResourceKeyMigrationTests(TransactionTestCase):
    def test_existing_records_receive_distinct_keys_and_keep_their_content(self):
        old = [("content", "0002_topic_course_estimated_minutes_course_kind_and_more"), ("media", "0001_initial")]
        latest = MigrationExecutor(connection).loader.graph.leaf_nodes()
        executor = MigrationExecutor(connection)
        executor.migrate(old)
        try:
            apps = executor.loader.project_state(old).apps
            user = apps.get_model("accounts", "User").objects.create(email="migration@example.invalid", password="!")
            course = apps.get_model("content", "Course").objects.create(title="Conservar", creator=user)
            chapter = apps.get_model("content", "Chapter").objects.create(course=course, title="Capítulo")
            for position in range(1, 4):
                apps.get_model("content", "Lesson").objects.create(chapter=chapter, title=str(position), body="Conservar texto", position=position)
            for name in ("Video", "Material"):
                for index in range(2):
                    apps.get_model("content", name).objects.create(creator=user, title=str(index))
            MigrationExecutor(connection).migrate(latest)
            self.assertEqual(Lesson.objects.values("resource_key").distinct().count(), 3)
            self.assertEqual(Video.objects.values("resource_key").distinct().count(), 2)
            self.assertEqual(Material.objects.values("resource_key").distinct().count(), 2)
            self.assertEqual(Lesson.objects.filter(body="Conservar texto").count(), 3)
            self.assertEqual(Asset.objects.count(), 0)
        finally:
            MigrationExecutor(connection).migrate(latest)
