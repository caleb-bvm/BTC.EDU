from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import (
    AccessType,
    Chapter,
    Course,
    CourseKind,
    CourseLevel,
    ExternalReference,
    Lesson,
    PublicationStatus,
    Topic,
)


class AcademyDiscoveryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user("editor@example.com", first_name="Ana")
        cls.topic = Topic.objects.create(name="Seguridad", slug="seguridad")
        cls.course = Course.objects.create(creator=cls.creator, title="Seguridad desde cero", topic=cls.topic, level=CourseLevel.BEGINNER, estimated_minutes=45, status=PublicationStatus.PUBLISHED)
        cls.tutorial = Course.objects.create(creator=cls.creator, title="Configura una wallet", kind=CourseKind.TUTORIAL, topic=cls.topic, level=CourseLevel.INTERMEDIATE, status=PublicationStatus.PUBLISHED)
        for course in (cls.course, cls.tutorial):
            chapter = Chapter.objects.create(course=course, title="Pasos", status=PublicationStatus.PUBLISHED)
            Lesson.objects.create(chapter=chapter, title="Inicio", body="CUERPO QUE NO ES METADATO", status=PublicationStatus.PUBLISHED)
        cls.reference = ExternalReference.objects.create(title="Documentación de prueba", source_name="Fuente de prueba", source_url="https://example.org/docs", topic=cls.topic, status=PublicationStatus.PUBLISHED)

    def test_sections_keep_courses_tutorials_and_external_references_separate(self):
        for name, visible, hidden in (
            ("courses", self.course.title, (self.tutorial.title, self.reference.title)),
            ("tutorials", self.tutorial.title, (self.course.title, self.reference.title)),
            ("resources", self.reference.title, (self.course.title, self.tutorial.title)),
        ):
            response = self.client.get(reverse(name))
            self.assertContains(response, visible)
            for title in hidden:
                self.assertNotContains(response, title)
            self.assertNotContains(response, "CUERPO QUE NO ES METADATO")
            self.assertNotContains(response, self.creator.email)

    def test_topic_level_search_and_access_are_combinable(self):
        url = reverse("courses")
        self.assertContains(self.client.get(url, {"tema": "seguridad", "nivel": "beginner", "q": "cero", "acceso": "gratis"}), self.course.title)
        self.assertNotContains(self.client.get(url, {"nivel": "advanced"}), self.course.title)
        self.assertNotContains(self.client.get(url, {"tema": "desconocido"}), self.course.title)
        self.assertContains(self.client.get(url, {"nivel": "invalido", "tipo": "videos"}), self.course.title)

    def test_selector_never_reuses_a_selection_outside_the_filtered_set(self):
        another = Course.objects.create(creator=self.creator, title="Curso ajeno al filtro", level=CourseLevel.ADVANCED, status=PublicationStatus.PUBLISHED)
        response = self.client.get(reverse("course-selector"), {"nivel": "beginner", "curso": another.pk})
        self.assertEqual(response.context["selected"]["item"], self.course)
        self.assertNotContains(response, another.title)
        response = self.client.get(reverse("course-selector"), {"nivel": "advanced", "q": "sin resultados", "curso": self.course.pk})
        self.assertIsNone(response.context["selected"])

    def test_selector_and_catalog_use_the_same_mixed_access_summary(self):
        chapter = self.course.chapters.first()
        Lesson.objects.create(chapter=chapter, position=2, title="Contenido extra", body="PAGO PRIVADO", access_type=AccessType.PAID, status=PublicationStatus.PUBLISHED)
        for name in ("courses", "course-selector"):
            response = self.client.get(reverse(name))
            self.assertContains(response, "Gratis + lecciones de pago")
            self.assertNotContains(response, "PAGO PRIVADO")

    def test_pagination_limits_topic_groups_and_handles_invalid_page(self):
        Course.objects.bulk_create([Course(creator=self.creator, title=f"Curso {number:02}", topic=self.topic, status=PublicationStatus.PUBLISHED) for number in range(15)])
        first = self.client.get(reverse("courses"))
        self.assertEqual(len(first.context["cards"]), 12)
        self.assertEqual(sum(len(cards) for _, cards in first.context["groups"]), 12)
        last = self.client.get(reverse("courses"), {"pagina": "999"})
        self.assertEqual(len(last.context["cards"]), 4)
        self.assertEqual(last.context["result_count"], 16)

    def test_external_reference_has_safe_explicit_destination_and_hides_drafts(self):
        response = self.client.get(reverse("reference-detail", args=[self.reference.pk]))
        self.assertContains(response, 'href="https://example.org/docs"')
        self.assertContains(response, "FUERA DE BTC.EDU")
        self.assertNotContains(self.client.get(reverse("resources"), {"acceso": "gratis"}), self.reference.title)
        self.reference.status = PublicationStatus.DRAFT
        self.reference.save()
        self.assertEqual(self.client.get(reverse("reference-detail", args=[self.reference.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("resources")), self.reference.title)
        self.reference.status = PublicationStatus.PUBLISHED
        self.reference.source_url = "javascript:alert(1)"
        with self.assertRaises(ValidationError):
            self.reference.full_clean()
        self.reference.save()
        self.assertEqual(self.client.get(reverse("reference-detail", args=[self.reference.pk])).status_code, 404)

    def test_htmx_returns_only_catalog_and_discovery_rejects_post(self):
        for name in ("courses", "tutorials", "resources"):
            response = self.client.get(reverse(name), HTTP_HX_REQUEST="true")
            self.assertContains(response, 'id="catalog"')
            self.assertNotContains(response, "<html")
            self.assertEqual(self.client.post(reverse(name)).status_code, 405)
        self.assertEqual(self.client.post(reverse("course-selector")).status_code, 405)

    def test_return_context_keeps_filters_and_never_links_to_external_destination(self):
        response = self.client.get(reverse("courses"), {"tema": "seguridad", "nivel": "beginner"})
        self.assertContains(response, "volver=%2Fcursos%2F%3Ftema%3Dseguridad%26nivel%3Dbeginner")
        detail_url = reverse("course-detail", args=[self.course.pk])
        response = self.client.get(detail_url, {"volver": "/cursos/?tema=seguridad&nivel=beginner"})
        self.assertContains(response, 'href="/cursos/?tema=seguridad&amp;nivel=beginner"')
        for unsafe in ("https://example.org", "//example.org", "javascript:alert(1)", "/\\example.org"):
            response = self.client.get(detail_url, {"volver": unsafe})
            self.assertEqual(response.context["return_to"], "/cursos/")
