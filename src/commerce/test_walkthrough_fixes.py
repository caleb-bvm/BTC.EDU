"""Fixes found in the creator-to-student walkthrough of 5 November 2026."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from content.languages import language_name
from content.models import AccessType, Chapter, Course, Lesson, PublicationStatus
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile

from .offers import create_offer, submit_offer


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class WalkthroughFixTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user("recorrido@example.com", account_type="creator")
        CreatorProfile.objects.create(user=cls.creator, display_name="Ana", status="approved")
        cls.staff = get_user_model().objects.create_superuser("revision@example.com", "local-test-password")
        course = Course.objects.create(creator=cls.creator, title="Primer pago", status=PublicationStatus.PUBLISHED)
        chapter = Chapter.objects.create(course=course, title="Antes de pagar", status=PublicationStatus.PUBLISHED)
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Factura", body="Texto", access_type=AccessType.FREE, status=PublicationStatus.PUBLISHED)
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Pagar", body="Texto", position=2, access_type=AccessType.PAID, status=PublicationStatus.PUBLISHED)
        cls.course = course
        cls.version = publish_course(course, cls.staff)
        paid = cls.version.chapters.get().lessons.get(position=2)
        cls.course_offer = create_offer(cls.creator, f"course:{course.pk}", "Curso completo", 100)
        cls.lesson_offer = create_offer(cls.creator, f"lesson:{paid.pk}", "Lección", 60)

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_student_sign_in_links_to_educator_access(self):
        self.assertContains(self.client.get(reverse("login")), f'href="{reverse("creator-login")}"')

    def test_course_offer_points_to_the_lesson_offer_already_prepared(self):
        self.client.force_login(self.creator)
        url = reverse("creator-offer", args=[self.course_offer.pk])
        draft = self.client.get(url)
        self.assertContains(draft, "Continuar oferta en borrador")
        self.assertContains(draft, reverse("creator-offer", args=[self.lesson_offer.pk]))
        submit_offer(self.creator, self.lesson_offer)
        pending = self.client.get(url)
        self.assertContains(pending, "Oferta en revisión")
        self.assertNotContains(pending, "Preparar esta oferta")

    def test_package_description_names_only_the_formats_included(self):
        self.assertEqual(self.course_offer.included_kinds_label, "Textos")
        with translation.override("en"):
            self.assertEqual(self.course_offer.included_kinds_label, "Texts")

    def test_spanish_language_names_use_common_forms(self):
        with translation.override("es"):
            self.assertEqual(language_name("af"), "Afrikáans")
            self.assertEqual(language_name("pt"), "Portugués")
        with translation.override("en"):
            self.assertEqual(language_name("af"), "Afrikaans")

    def test_course_page_names_the_language_only_when_it_differs(self):
        url = reverse("course-detail", args=[self.course.pk])
        self.assertNotContains(self.client.get(url), "<span>Español</span>")
        with translation.override("en"):
            english_url = reverse("course-detail", args=[self.course.pk])
        self.assertContains(self.client.get(english_url), "<span>Spanish</span>")
