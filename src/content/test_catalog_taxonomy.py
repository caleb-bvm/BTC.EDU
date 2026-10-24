from urllib.parse import parse_qs

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from content.testing import EDUCATION_FIXTURE

from .catalog import UNCATEGORIZED_TOPIC
from .models import (
    Category,
    Chapter,
    Course,
    CourseKind,
    CourseLevel,
    CourseVersion,
    Lesson,
    PublicationStatus,
    Topic,
)


class CatalogHierarchyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user("taxonomy@example.com")
        cls.bitcoin = Category.objects.get(slug="bitcoin")
        cls.technology = Category.objects.get(slug="tecnologia")
        cls.creation = Category.objects.get(slug="creacion")
        cls.security = Topic.objects.get(slug="seguridad")
        cls.lightning = Topic.objects.get(slug="lightning")
        cls.hardware = Topic.objects.get(slug="hardware-pc")
        cls.networks = Topic.objects.get(slug="redes")
        cls.course = Course.objects.create(
            creator=cls.creator, title="Cuida tus llaves", topic=cls.security,
            status=PublicationStatus.PUBLISHED,
        )
        cls.sibling_course = Course.objects.create(
            creator=cls.creator, title="Pagos con Lightning", topic=cls.lightning,
            status=PublicationStatus.PUBLISHED,
        )
        cls.technical_course = Course.objects.create(
            creator=cls.creator, title="Monta tu PC", topic=cls.hardware,
            status=PublicationStatus.PUBLISHED,
        )

    def category_counts(self, response):
        return {card["slug"]: card["count"] for card in response.context["category_cards"]}

    def result_ids(self, response):
        return {card["item"].pk for card in response.context["cards"]}

    def test_parent_counts_aggregate_siblings_and_isolate_sections(self):
        Course.objects.create(
            creator=self.creator, title="Tutorial de redes", topic=self.networks,
            kind=CourseKind.TUTORIAL, status=PublicationStatus.PUBLISHED,
        )
        Course.objects.create(creator=self.creator, title="Hardware en preparación", topic=self.hardware)
        for name, expected in (
            ("courses", {"bitcoin": 2, "tecnologia": 1, "creacion": 0}),
            ("tutorials", {"bitcoin": 0, "tecnologia": 1, "creacion": 0}),
            ("resources", {"bitcoin": 0, "tecnologia": 0, "creacion": 0}),
        ):
            with self.subTest(section=name):
                response = self.client.get(reverse(name))
                self.assertEqual(self.category_counts(response), expected)
                self.assertEqual(response.context["catalog_total"], sum(expected.values()))
        response = self.client.get(reverse("courses"), {"categoria": "bitcoin"})
        self.assertEqual(self.result_ids(response), {self.course.pk, self.sibling_course.pk})
        self.assertEqual(response.context["selected_category"]["slug"], "bitcoin")
        self.assertIsNone(response.context["selected_topic"])

    def test_parent_keeps_empty_subcategories_in_context_and_shows_available_navigation(self):
        response = self.client.get(reverse("courses"), {"categoria": "tecnologia"})
        subcategories = {card["slug"]: card["count"] for card in response.context["subcategory_cards"]}
        self.assertEqual(set(subcategories), set(self.technology.topics.values_list("slug", flat=True)))
        self.assertEqual(subcategories[self.hardware.slug], 1)
        self.assertEqual(subcategories[self.networks.slug], 0)
        self.assertNotContains(response, 'href="/cursos/?categoria=tecnologia&amp;tema=redes"')
        self.assertContains(response, 'href="/cursos/?categoria=tecnologia&amp;tema=hardware-pc"')
        self.assertNotContains(response, self.course.title)

    def test_configured_categories_and_subcategories_remain_visible_without_publications(self):
        Course.objects.all().delete()
        response = self.client.get(reverse("courses"))
        self.assertEqual(self.category_counts(response), {"bitcoin": 0, "tecnologia": 0, "creacion": 0})
        for category in (self.bitcoin, self.technology, self.creation):
            self.assertContains(response, category.name)
        empty_category = self.client.get(reverse("courses"), {"categoria": "tecnologia"})
        self.assertEqual(empty_category.context["result_count"], 0)
        self.assertEqual(len(empty_category.context["subcategory_cards"]), self.technology.topics.count())
        self.assertContains(empty_category, self.hardware.name)

    def test_legacy_topic_links_infer_parent_and_keep_narrow_results(self):
        response = self.client.get(reverse("courses"), {"tema": self.security.slug})
        self.assertEqual(self.result_ids(response), {self.course.pk})
        self.assertEqual(response.context["category_filter"], "bitcoin")
        self.assertEqual(response.context["selected_category"]["slug"], "bitcoin")
        self.assertEqual(response.context["selected_topic"], self.security)
        self.assertFalse(response.context["topic_missing"])

    def test_mismatched_or_unknown_parent_never_exposes_unrelated_results(self):
        for params in (
            {"categoria": "tecnologia", "tema": self.security.slug},
            {"categoria": "bitcoin", "tema": UNCATEGORIZED_TOPIC},
            {"categoria": "desconocida"},
            {"categoria": "desconocida", "tema": self.security.slug},
        ):
            with self.subTest(params=params):
                response = self.client.get(reverse("courses"), params)
                self.assertEqual(response.context["result_count"], 0)
                self.assertTrue(response.context["category_missing"])
                for course in (self.course, self.sibling_course, self.technical_course):
                    self.assertNotContains(response, course.title)

    def test_missing_subcategory_can_clear_back_to_its_valid_parent(self):
        for extra in ({}, {"q": "sin resultados"}):
            with self.subTest(extra=extra):
                response = self.client.get(
                    reverse("courses"), {"categoria": "bitcoin", "tema": "inexistente", **extra},
                )
                self.assertTrue(response.context["topic_missing"])
                self.assertTrue(response.context["show_clear_filters"])
                self.assertEqual(response.context["clear_filters_url"], "/cursos/?categoria=bitcoin")
                self.assertContains(response, 'href="/cursos/?categoria=bitcoin">Limpiar filtros')

    def test_orphan_topics_and_missing_topics_share_fallback_without_losing_legacy_links(self):
        orphan = Topic.objects.create(name="Tema independiente", slug="independiente")
        orphan_course = Course.objects.create(
            creator=self.creator, title="Contenido independiente", topic=orphan,
            status=PublicationStatus.PUBLISHED,
        )
        no_topic = Course.objects.create(
            creator=self.creator, title="Contenido sin tema", status=PublicationStatus.PUBLISHED,
        )
        response = self.client.get(reverse("courses"))
        self.assertEqual(self.category_counts(response)[UNCATEGORIZED_TOPIC], 2)
        response = self.client.get(reverse("courses"), {"categoria": UNCATEGORIZED_TOPIC})
        self.assertEqual(self.result_ids(response), {orphan_course.pk, no_topic.pk})
        legacy = self.client.get(reverse("courses"), {"tema": orphan.slug})
        self.assertEqual(self.result_ids(legacy), {orphan_course.pk})
        self.assertEqual(legacy.context["selected_category"]["slug"], UNCATEGORIZED_TOPIC)
        self.assertEqual(legacy.context["selected_topic"], orphan)
        self.assertFalse(legacy.context["topic_missing"])

    def test_parent_uses_published_version_category_instead_of_pending_edit(self):
        version = CourseVersion.objects.create(
            course=self.course, number=1, title=self.course.title,
            topic=self.security, kind=CourseKind.COURSE, creator_name="Educador",
        )
        Course.objects.filter(pk=self.course.pk).update(current_version=version, topic=self.hardware)
        response = self.client.get(reverse("courses"))
        self.assertEqual(self.category_counts(response), {"bitcoin": 2, "tecnologia": 1, "creacion": 0})
        technology = self.client.get(reverse("courses"), {"categoria": "tecnologia"})
        self.assertEqual(self.result_ids(technology), {self.technical_course.pk})
        bitcoin = self.client.get(reverse("courses"), {"categoria": "bitcoin"})
        self.assertIn(self.course.pk, self.result_ids(bitcoin))

    def test_parent_child_search_access_and_level_survive_pagination_and_htmx(self):
        for number in range(13):
            course = Course.objects.create(
                creator=self.creator, title=f"Guía de redes {number:02}", topic=self.networks,
                level=CourseLevel.BEGINNER, status=PublicationStatus.PUBLISHED,
            )
            chapter = Chapter.objects.create(course=course, title="Pasos", status=PublicationStatus.PUBLISHED)
            Lesson.objects.create(
                **EDUCATION_FIXTURE, chapter=chapter, title="Introducción",
                status=PublicationStatus.PUBLISHED,
            )
        params = {
            "categoria": "tecnologia", "tema": "redes", "q": "Guía de redes",
            "nivel": "beginner", "acceso": "gratis",
        }
        first = self.client.get(reverse("courses"), params, HTTP_HX_REQUEST="true")
        self.assertEqual(first.context["result_count"], 13)
        self.assertEqual(len(first.context["cards"]), 12)
        self.assertNotContains(first, "<html")
        self.assertContains(first, "pagina=2")
        self.assertEqual(parse_qs(first.context["filter_query"]), {key: [value] for key, value in params.items()})
        self.assertContains(first, "volver=%2Fcursos%2F%3Fcategoria%3Dtecnologia%26tema%3Dredes")
        last = self.client.get(reverse("courses"), {**params, "pagina": 2})
        self.assertEqual(len(last.context["cards"]), 1)
        self.assertEqual(last.context["selected_topic"], self.networks)
        self.assertEqual(last.context["selected_category"]["slug"], "tecnologia")

    def test_explore_preserves_section_when_drilling_into_category_and_subcategory(self):
        response = self.client.get(reverse("explore"), {"seccion": "tutoriales", "categoria": "tecnologia"})
        self.assertContains(response, 'href="/explorar/?seccion=tutoriales&amp;categoria=tecnologia&amp;tema=redes"')
        self.assertContains(response, 'href="/explorar/?seccion=tutoriales">← Categorías')
        response = self.client.get(
            reverse("explore"), {"seccion": "tutoriales", "categoria": "tecnologia", "tema": "redes"},
        )
        self.assertEqual(response.context["result_count"], 0)
        self.assertEqual(response.context["selected_topic"], self.networks)
        self.assertFalse(response.context["topic_missing"])
