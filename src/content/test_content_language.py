"""Each course and resource keeps the language its educator writes it in; only the interface is translated."""
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from content.testing import EDUCATION_FIXTURE
from creators.forms import CourseForm
from media.models import Asset

from .languages import CONTENT_LANGUAGES, DEFAULT_CONTENT_LANGUAGE
from .models import (
    Chapter,
    Course,
    Lesson,
    Material,
    PublicationStatus,
    ResourceVersion,
)
from .publication import publish_course, publish_resource


class ContentLanguageTests(TestCase):
    def setUp(self):
        self.creator = get_user_model().objects.create_user("writer@example.invalid")
        self.staff = get_user_model().objects.create_superuser("reviewer@example.invalid", "local-test-password")
        self.course = Course.objects.create(title="Curso em português", creator=self.creator, status=PublicationStatus.PUBLISHED, language="pt")
        chapter = Chapter.objects.create(course=self.course, title="Capítulo", status=PublicationStatus.PUBLISHED)
        self.lesson = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Lição", body="Texto da lição", status=PublicationStatus.PUBLISHED)

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_new_content_defaults_to_spanish(self):
        other = Course.objects.create(title="Curso", creator=self.creator)
        self.assertEqual(other.language, DEFAULT_CONTENT_LANGUAGE)
        with translation.override("en"):
            self.assertIn(("pt", "Portuguese"), [(code, str(name)) for code, name in CONTENT_LANGUAGES])

    def test_publication_freezes_the_course_language_into_its_lessons(self):
        version = publish_course(self.course, self.staff)
        lesson = version.chapters.get().lessons.get()
        self.assertEqual(version.language, "pt")
        self.assertEqual(lesson.content.language, "pt")

    def test_changing_the_language_creates_a_new_lesson_revision(self):
        first = publish_course(self.course, self.staff).chapters.get().lessons.get().content
        self.course.language = "en"
        self.course.save()
        second = publish_course(self.course, self.staff).chapters.get().lessons.get().content
        self.assertNotEqual(first.pk, second.pk)
        self.assertEqual((first.language, second.language), ("pt", "en"))

    def test_resource_publication_keeps_its_language(self):
        with tempfile.TemporaryDirectory() as files, override_settings(MEDIA_ROOT=files):
            asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("guia.txt", b"Guia", content_type="text/plain"))
            material = Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, title="Guia", pending_asset=asset, language="pt")
            revision = publish_resource(material, self.staff)
        self.assertEqual(ResourceVersion.objects.get(pk=revision.pk).language, "pt")

    def test_lesson_and_course_pages_declare_the_content_language(self):
        publish_course(self.course, self.staff)
        lesson = self.client.get(reverse("lesson-detail", args=[self.lesson.pk]))
        self.assertContains(lesson, 'class="reading-copy lesson-body" lang="pt"')
        self.assertContains(self.client.get(reverse("course-detail", args=[self.course.pk])), "<span>Portugués</span>")
        with translation.override("en"):
            course_url = reverse("course-detail", args=[self.course.pk])
        self.assertContains(self.client.get(course_url), "<span>Portuguese</span>")

    def test_reading_copy_has_no_lang_when_it_matches_the_interface(self):
        with translation.override("en"):
            english = render_to_string("content/_reading.html", {"reading_sections": [], "content_language": "en"})
            spanish = render_to_string("content/_reading.html", {"reading_sections": []})
        self.assertNotIn("lang=", english)
        self.assertIn('lang="es"', spanish)

    def test_subtitles_use_the_content_language(self):
        media = {"allowed": True, "kind": "video", "file_url": "/video.mp4", "subtitle_url": "/legendas.vtt", "language": "pt", "title": "Vídeo", "standalone": True}
        html = render_to_string("content/_media.html", {"media": media})
        self.assertIn('srclang="pt" label="Português"', html)

    def test_editor_offers_languages_sorted_by_name_and_rejects_unknown_codes(self):
        form = CourseForm()
        names = [str(name) for _, name in form.fields["language"].choices]
        self.assertEqual(form.fields["language"].initial or form.initial.get("language", DEFAULT_CONTENT_LANGUAGE), DEFAULT_CONTENT_LANGUAGE)
        self.assertLess(names.index("Alemán"), names.index("Árabe"))
        self.assertLess(names.index("Árabe"), names.index("Español"))
        invalid = CourseForm(data={"title": "Curso", "kind": "course", "language": "xx"})
        self.assertFalse(invalid.is_valid())
        self.assertIn("language", invalid.errors)
