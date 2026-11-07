"""Course covers: upload, normalization, review visibility and catalog display."""
import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from content.models import Chapter, Course, Lesson
from content.testing import EDUCATION_FIXTURE
from media.models import Cover, normalize_cover

from .models import CreatorProfile
from .presentation import course_has_changes
from .services import decide, submit


def image_upload(size=(1200, 800), fmt="JPEG", name="portada.jpg", exif=False):
    buffer = BytesIO()
    image = Image.new("RGB", size, (200, 120, 40))
    options = {}
    if exif:
        data = Image.Exif()
        data[0x010F] = "CamaraSecreta"  # Make
        options["exif"] = data
    image.save(buffer, format=fmt, **options)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=f"image/{fmt.lower()}")


class CourseCoverTests(TestCase):
    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name, SECURE_SSL_REDIRECT=False)
        settings.enable()
        self.addCleanup(settings.disable)
        users = get_user_model().objects
        self.owner = users.create_user("cover-owner@example.invalid", account_type="creator")
        self.other = users.create_user("cover-other@example.invalid", account_type="creator")
        self.reviewer = users.create_superuser("cover-review@example.invalid")
        for user in (self.owner, self.other):
            CreatorProfile.objects.create(user=user, display_name="Docente", bio="Enseño.", specialty="Diseño", status="approved")
        self.course = Course.objects.create(creator=self.owner, title="Curso con portada", description="Descripción")
        chapter = Chapter.objects.create(course=self.course, title="Capítulo", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Lección", body="Texto", status="published")
        self.client.force_login(self.owner)

    def fetch(self, url, **headers):
        """Read and close a cover response so Windows releases the file."""
        response = self.client.get(url, **headers)
        if response.streaming:
            b"".join(response.streaming_content)
        response.close()
        return response

    def edit(self, **extra):
        data = {"title": self.course.title, "kind": "course", "description": "Descripción", **extra}
        return self.client.post(reverse("creator-course", args=[self.course.pk]), data)

    def test_upload_is_cropped_to_16_9_webp_without_metadata(self):
        self.assertEqual(self.edit(new_cover=image_upload(exif=True)).status_code, 302)
        self.course.refresh_from_db()
        cover = self.course.cover
        self.assertEqual(cover.creator, self.owner)
        with cover.file.open("rb") as handle, Image.open(handle) as stored:
            self.assertEqual((stored.format, stored.size), ("WEBP", (1600, 900)))
            self.assertNotIn(b"CamaraSecreta", handle.seek(0) or handle.read())
        self.assertTrue(cover.file.name.startswith("covers/"))
        self.assertTrue(course_has_changes(self.course))

    def test_rejects_small_disguised_and_animated_files(self):
        with self.assertRaises(ValidationError):
            normalize_cover(image_upload(size=(640, 360)))
        with self.assertRaises(ValidationError):
            normalize_cover(SimpleUploadedFile("portada.png", b"%PDF-1.4 no es imagen", content_type="image/png"))
        buffer = BytesIO()
        frames = [Image.new("RGB", (900, 500), color) for color in ("red", "blue")]
        frames[0].save(buffer, format="WEBP", save_all=True, append_images=frames[1:])
        with self.assertRaises(ValidationError):
            normalize_cover(SimpleUploadedFile("anim.webp", buffer.getvalue(), content_type="image/webp"))
        response = self.edit(new_cover=image_upload(size=(500, 300)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "800 × 450")
        self.assertFalse(Cover.objects.exists())

    def test_draft_cover_is_private_until_published(self):
        self.edit(new_cover=image_upload())
        self.course.refresh_from_db()
        url = reverse("course-cover", args=[self.course.cover_id])
        owner_view = self.fetch(url)
        self.assertEqual(owner_view.status_code, 200)
        self.assertEqual(owner_view["Cache-Control"], "private, no-store")
        self.client.force_login(self.other)
        self.assertEqual(self.fetch(url).status_code, 404)
        self.client.logout()
        self.assertEqual(self.fetch(url).status_code, 404)

        submission = submit(self.course, self.owner)
        self.assertEqual(submission.course_version.cover_id, self.course.cover_id)
        self.client.force_login(self.reviewer)
        self.assertEqual(self.fetch(url).status_code, 200)
        decide(submission, self.reviewer, True)

        self.client.logout()
        public = self.fetch(url)
        self.assertEqual(public.status_code, 200)
        self.assertEqual(public["Content-Type"], "image/webp")
        self.assertIn("immutable", public["Cache-Control"])
        self.assertEqual(self.fetch(url, HTTP_IF_NONE_MATCH=public["ETag"]).status_code, 304)
        self.assertContains(self.client.get(reverse("course-detail", args=[self.course.pk])), url)
        self.assertContains(self.client.get(reverse("courses"), {"vista": "todos"}), url)

    def test_new_cover_keeps_published_one_until_next_publication(self):
        self.edit(new_cover=image_upload())
        self.course.refresh_from_db()
        first = self.course.cover_id
        decide(submit(self.course, self.owner), self.reviewer, True)
        self.edit(new_cover=image_upload(fmt="PNG", name="otra.png"))
        self.course.refresh_from_db()
        self.assertNotEqual(self.course.cover_id, first)
        self.client.logout()
        page = self.client.get(reverse("course-detail", args=[self.course.pk]))
        self.assertContains(page, reverse("course-cover", args=[first]))
        self.assertEqual(self.fetch(reverse("course-cover", args=[self.course.cover_id])).status_code, 404)

    def test_removing_cover_returns_to_illustration(self):
        self.edit(new_cover=image_upload())
        self.assertEqual(self.edit(remove_cover="on").status_code, 302)
        self.course.refresh_from_db()
        self.assertIsNone(self.course.cover_id)
        self.assertEqual(Cover.objects.count(), 1)
