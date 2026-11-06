"""The catalog shows a content's language when it differs from the interface and filters by it."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from creators.models import CreatorProfile

from .models import (
    AccessType,
    Chapter,
    Course,
    ExternalReference,
    Lesson,
    PublicationStatus,
    Topic,
    Video,
)
from .testing import EDUCATION_FIXTURE


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class CatalogLanguageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user("idiomas@example.com", account_type="creator")
        CreatorProfile.objects.create(user=cls.creator, display_name="Docente", status="approved")
        cls.topic = Topic.objects.get(slug="lightning")
        cls.spanish = cls.make_course("Canales en español", "es")
        cls.portuguese = cls.make_course("Canais em português", "pt")
        Video.objects.create(creator=cls.creator, title="Vídeo em português", topic=cls.topic, language="pt", status=PublicationStatus.PUBLISHED)
        ExternalReference.objects.create(title="Referencia sin idioma", source_name="Fuente", source_url="https://example.org/docs", topic=cls.topic, status=PublicationStatus.PUBLISHED)

    @classmethod
    def make_course(cls, title, language):
        course = Course.objects.create(creator=cls.creator, title=title, topic=cls.topic, language=language, status=PublicationStatus.PUBLISHED)
        chapter = Chapter.objects.create(course=course, title="Inicio", status=PublicationStatus.PUBLISHED)
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Unidad", body="Texto", access_type=AccessType.FREE, status=PublicationStatus.PUBLISHED)
        return course

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_filter_appears_with_two_languages_and_narrows_the_results(self):
        response = self.client.get(reverse("courses"), {"vista": "todos"})
        filters = response.context["catalog_filters"]
        self.assertTrue(filters["show_language"])
        self.assertEqual([value for value, _ in filters["languages"]], ["es", "pt"])
        self.assertContains(response, 'name="idioma"')
        filtered = self.client.get(reverse("courses"), {"idioma": "pt"})
        titles = [card["item"].title for card in filtered.context["cards"]]
        self.assertEqual(titles, ["Canais em português"])
        self.assertEqual([chip["label"] for chip in filtered.context["active_filter_chips"]], ["Portugués"])

    def test_filter_is_hidden_when_every_result_shares_one_language(self):
        self.portuguese.status = PublicationStatus.DRAFT
        self.portuguese.save()
        response = self.client.get(reverse("courses"), {"vista": "todos"})
        self.assertFalse(response.context["catalog_filters"]["show_language"])
        self.assertNotContains(response, 'name="idioma"')

    def test_unknown_language_is_ignored(self):
        response = self.client.get(reverse("courses"), {"idioma": "xx", "vista": "todos"})
        self.assertEqual(response.context["language_filter"], "")
        self.assertEqual(len(response.context["cards"]), 2)

    def test_resources_filter_by_language_and_leave_out_links_without_one(self):
        response = self.client.get(reverse("resources"), {"idioma": "pt"})
        self.assertEqual([card["item"].title for card in response.context["cards"]], ["Vídeo em português"])

    def test_cards_name_the_language_only_when_it_differs_from_the_interface(self):
        spanish_ui = self.client.get(reverse("courses"), {"vista": "todos"})
        self.assertContains(spanish_ui, "<span>Portugués</span>", count=1)
        self.assertNotContains(spanish_ui, "<span>Español</span>")
        with translation.override("en"):
            url = reverse("courses")
        english_ui = self.client.get(url, {"vista": "todos"})
        self.assertContains(english_ui, "<span>Spanish</span>", count=1)
        self.assertContains(english_ui, "<span>Portuguese</span>", count=1)
