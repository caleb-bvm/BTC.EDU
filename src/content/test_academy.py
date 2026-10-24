from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from content.testing import EDUCATION_FIXTURE
from media.models import Asset

from .catalog import UNCATEGORIZED_TOPIC
from .models import (
    AccessType,
    Category,
    Chapter,
    Course,
    CourseKind,
    CourseLevel,
    CourseVersion,
    ExternalReference,
    Lesson,
    Material,
    PublicationStatus,
    ResourceVersion,
    Topic,
    Video,
)


class AcademyDiscoveryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user("editor@example.com", first_name="Ana")
        cls.bitcoin = Category.objects.get(slug="bitcoin")
        cls.topic, _ = Topic.objects.get_or_create(slug="seguridad", defaults={"name": "Seguridad"})
        cls.topic.category = cls.bitcoin
        cls.topic.save()
        cls.course = Course.objects.create(creator=cls.creator, title="Seguridad desde cero", topic=cls.topic, level=CourseLevel.BEGINNER, estimated_minutes=45, status=PublicationStatus.PUBLISHED)
        cls.tutorial = Course.objects.create(creator=cls.creator, title="Configura una wallet", kind=CourseKind.TUTORIAL, topic=cls.topic, level=CourseLevel.INTERMEDIATE, status=PublicationStatus.PUBLISHED)
        for course in (cls.course, cls.tutorial):
            chapter = Chapter.objects.create(course=course, title="Pasos", status=PublicationStatus.PUBLISHED)
            Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Inicio", body="CUERPO QUE NO ES METADATO", status=PublicationStatus.PUBLISHED)
        cls.reference = ExternalReference.objects.create(title="Documentación de prueba", source_name="Fuente de prueba", source_url="https://example.org/docs", topic=cls.topic, status=PublicationStatus.PUBLISHED)

    def test_sections_keep_courses_tutorials_and_external_references_separate(self):
        for name, visible, hidden in (
            ("courses", self.course.title, (self.tutorial.title, self.reference.title)),
            ("tutorials", self.tutorial.title, (self.course.title, self.reference.title)),
            ("resources", self.reference.title, (self.course.title, self.tutorial.title)),
        ):
            response = self.client.get(reverse(name))
            self.assertTrue(response.context["show_categories"])
            self.assertContains(response, "Elige una categoría")
            self.assertNotContains(response, visible)
            response = self.client.get(reverse(name), {"vista": "todos"})
            label = {"courses": "Cursos", "tutorials": "Tutoriales", "resources": "Recursos"}[name]
            self.assertContains(response, f"<h1>{label}</h1>", html=True)
            self.assertContains(response, f"<title>{label} · BTC.EDU</title>", html=True)
            self.assertNotContains(response, 'aria-label="Tipos de contenido"')
            self.assertEqual(response.context["catalog_url"], reverse(name))
            self.assertContains(response, "Comparar cursos" if name == "courses" else label)
            if name != "courses":
                self.assertNotContains(response, "Comparar cursos")
            self.assertContains(response, visible)
            for title in hidden:
                self.assertNotContains(response, title)
            self.assertNotContains(response, "CUERPO QUE NO ES METADATO")
            self.assertNotContains(response, self.creator.email)
        empty = self.client.get(reverse("explore"), {"seccion": "recursos", "q": "sin coincidencias"})
        self.assertContains(empty, f'href="{reverse("explore")}?seccion=recursos&amp;vista=todos">Ver todo el catálogo')
        self.assertContains(empty, f'href="{reverse("explore")}?seccion=recursos&amp;vista=todos">Limpiar filtros')

    def test_topic_level_search_and_access_are_combinable(self):
        url = reverse("courses")
        self.assertContains(self.client.get(url, {"tema": "seguridad", "nivel": "beginner", "q": "cero", "acceso": "gratis"}), self.course.title)
        self.assertNotContains(self.client.get(url, {"nivel": "advanced"}), self.course.title)
        self.assertNotContains(self.client.get(url, {"tema": "desconocido"}), self.course.title)
        self.assertContains(self.client.get(url, {"vista": "todos", "nivel": "invalido", "tipo": "videos"}), self.course.title)

    def test_selector_never_reuses_a_selection_outside_the_filtered_set(self):
        another = Course.objects.create(creator=self.creator, title="Curso ajeno al filtro", level=CourseLevel.ADVANCED, status=PublicationStatus.PUBLISHED)
        response = self.client.get(reverse("course-selector"), {"nivel": "beginner", "curso": another.pk})
        self.assertIsNone(response.context["selected"])
        self.assertContains(response, "Elige un curso de la lista.")
        self.assertNotContains(response, another.title)
        response = self.client.get(reverse("course-selector"), {"nivel": "advanced", "q": "sin resultados", "curso": self.course.pk})
        self.assertIsNone(response.context["selected"])

    def test_selector_and_catalog_use_the_same_mixed_access_summary(self):
        chapter = self.course.chapters.first()
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, position=2, title="Contenido extra", body="PAGO PRIVADO", access_type=AccessType.PAID, status=PublicationStatus.PUBLISHED)
        for name in ("courses", "course-selector"):
            response = self.client.get(reverse(name), {"curso": self.course.pk} if name == "course-selector" else {"vista": "todos"})
            self.assertContains(response, "Gratis + lecciones de pago")
            self.assertNotContains(response, "PAGO PRIVADO")

    def test_pagination_limits_topic_groups_and_handles_invalid_page(self):
        Course.objects.bulk_create([Course(creator=self.creator, title=f"Curso {number:02}", topic=self.topic, status=PublicationStatus.PUBLISHED) for number in range(15)])
        first = self.client.get(reverse("courses"), {"vista": "todos"})
        self.assertEqual(len(first.context["cards"]), 12)
        self.assertEqual(sum(len(cards) for _, cards in first.context["groups"]), 12)
        last = self.client.get(reverse("courses"), {"pagina": "999"})
        self.assertEqual(len(last.context["cards"]), 4)
        self.assertEqual(last.context["result_count"], 16)

    def test_category_cards_count_all_publications_before_pagination(self):
        Course.objects.bulk_create([Course(creator=self.creator, title=f"Curso {number:02}", topic=self.topic, status=PublicationStatus.PUBLISHED) for number in range(15)])
        Course.objects.create(creator=self.creator, title="Borrador oculto", topic=self.topic)
        Topic.objects.create(name="Vacía", slug="vacia")
        # Extra lessons must not multiply the number of courses.
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=self.course.chapters.first(), position=2, title="Otra lección", status=PublicationStatus.PUBLISHED)
        response = self.client.get(reverse("courses"))
        self.assertEqual(response.context["catalog_total"], 16)
        self.assertEqual({card["slug"]: card["count"] for card in response.context["category_cards"]}, {"bitcoin": 16, "tecnologia": 0, "creacion": 0})
        self.assertContains(response, "16 cursos")
        self.assertNotContains(response, "Vacía")
        self.assertEqual(response.context["all_cards"], [])
        self.assertContains(response, 'href="/cursos/?categoria=bitcoin"')
        self.assertContains(response, 'src="/static/images/categories/bitcoin.svg"')
        self.assertContains(response, 'href="/cursos/?vista=todos"')

    def test_home_starts_with_the_same_category_cards(self):
        response = self.client.get("/")
        self.assertTrue(response.context["show_categories"])
        self.assertEqual({card["slug"]: card["count"] for card in response.context["category_cards"]}["bitcoin"], 1)
        self.assertContains(response, 'href="/explorar/?seccion=cursos&amp;categoria=bitcoin"')
        self.assertNotContains(response, self.course.title)
        self.assertNotContains(response, self.tutorial.title)

    def test_category_counts_respect_published_course_version_topic_and_kind(self):
        draft_topic = Topic.objects.create(name="Cambio sin publicar", slug="borrador")
        version = CourseVersion.objects.create(course=self.course, number=1, title=self.course.title, kind=CourseKind.COURSE, topic=self.topic, creator_name="Ana")
        Course.objects.filter(pk=self.course.pk).update(current_version=version, topic=draft_topic, kind=CourseKind.TUTORIAL)
        for name, count in (("courses", 1), ("tutorials", 1)):
            response = self.client.get(reverse(name))
            self.assertEqual({card["slug"]: card["count"] for card in response.context["category_cards"]}, {"bitcoin": count, "tecnologia": 0, "creacion": 0})
            self.assertNotContains(response, draft_topic.name)

    def test_resource_categories_combine_formats_and_skip_unpublished_items(self):
        for model in (Video, Material):
            model.objects.create(creator=self.creator, title=model.__name__, topic=self.topic, status=PublicationStatus.PUBLISHED)
            model.objects.create(creator=self.creator, title="Sin publicar", topic=self.topic)
        response = self.client.get(reverse("resources"))
        self.assertEqual({card["slug"]: card["count"] for card in response.context["category_cards"]}["bitcoin"], 3)
        self.assertContains(response, "3 recursos")
        filtered = self.client.get(reverse("resources"), {"tema": self.topic.slug, "tipo": "videos"})
        self.assertEqual(filtered.context["result_count"], 1)
        self.assertEqual(filtered.context["cards"][0]["kind"], "Video")

    def test_resource_category_uses_revision_topic_instead_of_draft(self):
        draft_topic = Topic.objects.create(name="Tema sin publicar", slug="pendiente")
        material = Material.objects.create(creator=self.creator, title="Material publicado", topic=draft_topic, status=PublicationStatus.PUBLISHED)
        with TemporaryDirectory() as directory, self.settings(MEDIA_ROOT=directory):
            asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("categorias.txt", b"Contenido de prueba", content_type="text/plain"))
            revision = ResourceVersion.objects.create(creator=self.creator, resource_key=material.resource_key, kind="material", title=material.title, topic=self.topic, access_type=AccessType.FREE, asset=asset)
        Material.objects.filter(pk=material.pk).update(revision=revision)
        response = self.client.get(reverse("resources"))
        self.assertEqual({card["slug"]: card["count"] for card in response.context["category_cards"]}, {"bitcoin": 2, "tecnologia": 0, "creacion": 0})
        self.assertNotContains(response, draft_topic.name)

    def test_uncategorized_publications_remain_discoverable(self):
        course = Course.objects.create(creator=self.creator, title="Sin categoría", status=PublicationStatus.PUBLISHED)
        response = self.client.get(reverse("courses"))
        self.assertEqual(response.context["category_cards"][-1]["slug"], UNCATEGORIZED_TOPIC)
        response = self.client.get(reverse("courses"), {"tema": UNCATEGORIZED_TOPIC})
        self.assertEqual([card["item"].pk for card in response.context["cards"]], [course.pk])
        self.assertEqual(response.context["selected_category"]["name"], "Por descubrir")
        self.assertFalse(response.context["topic_missing"])

    def test_empty_sections_keep_the_configured_categories_without_other_sections_counts(self):
        self.reference.delete()
        response = self.client.get(reverse("resources"))
        self.assertEqual({card["slug"]: card["count"] for card in response.context["category_cards"]}, {"bitcoin": 0, "tecnologia": 0, "creacion": 0})
        self.assertEqual(response.context["catalog_total"], 0)
        self.assertContains(response, "0 recursos")
        self.assertNotContains(response, self.course.title)
        self.assertNotContains(response, self.tutorial.title)

    def test_search_htmx_and_legacy_links_preserve_category_navigation(self):
        response = self.client.get(reverse("explore"), {"seccion": "tutoriales"})
        self.assertContains(response, 'href="/explorar/?seccion=tutoriales&amp;categoria=bitcoin"')
        response = self.client.get(reverse("explore"), {"seccion": "tutoriales", "tema": "seguridad", "q": "wallet"}, HTTP_HX_REQUEST="true")
        self.assertFalse(response.context["show_categories"])
        self.assertContains(response, self.tutorial.title)
        self.assertContains(response, 'href="/explorar/?seccion=tutoriales&amp;tema=seguridad">Limpiar filtros')
        self.assertContains(response, 'href="/explorar/?seccion=tutoriales">← Categorías')
        self.assertNotContains(response, "<html")
        search = self.client.get(reverse("courses"), {"q": "cero"})
        self.assertFalse(search.context["show_categories"])
        self.assertContains(search, self.course.title)

    def test_new_categories_use_default_artwork_and_accept_editorial_description(self):
        category = Category.objects.create(name="Matemáticas", slug="matematicas", description="Números y problemas cotidianos.")
        topic = Topic.objects.create(name="Álgebra", slug="algebra", category=category)
        Course.objects.filter(pk=self.course.pk).update(topic=topic)
        response = self.client.get(reverse("courses"))
        self.assertContains(response, 'src="/static/images/categories/general.svg"')
        self.assertContains(response, category.description)
        category.artwork = "desarrollo"
        category.save()
        self.assertContains(self.client.get(reverse("courses")), 'src="/static/images/categories/desarrollo.svg"')

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
