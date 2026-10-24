from html.parser import HTMLParser
from tempfile import TemporaryDirectory
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.html import escape

from creators.models import CreatorProfile
from media.models import Asset

from .catalog import UNCATEGORIZED_TOPIC
from .models import (
    AccessType,
    Chapter,
    Course,
    CourseKind,
    CourseLevel,
    ExternalReference,
    Lesson,
    Material,
    PublicationStatus,
    Topic,
    Video,
)
from .publication import publish_course, publish_resource
from .testing import EDUCATION_FIXTURE


class FilterMarkup(HTMLParser):
    def __init__(self, response):
        super().__init__()
        self.fields = []
        self.details = []
        self.current_select = None
        self.feed(response.content.decode())

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag in ("input", "select"):
            self.fields.append(attributes)
            if tag == "select":
                attributes["options"] = []
                self.current_select = attributes
        elif tag == "option" and self.current_select is not None:
            self.current_select["options"].append(attributes)
        elif tag == "details" and "catalog-refinements" in attributes.get("class", "").split():
            self.details.append(attributes)

    def handle_endtag(self, tag):
        if tag == "select":
            self.current_select = None

    def named(self, name):
        return [field for field in self.fields if field.get("name") == name]


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class AdaptiveCatalogFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user("filters@example.com", account_type="creator")
        cls.admin = get_user_model().objects.create_superuser("filters-admin@example.com")
        CreatorProfile.objects.create(user=cls.creator, display_name="Docente de tecnología", status="approved")
        cls.security = Topic.objects.get(slug="seguridad")
        cls.lightning = Topic.objects.get(slug="lightning")
        cls.hardware = Topic.objects.get(slug="hardware-pc")
        cls.networks = Topic.objects.get(slug="redes")
        cls.photography = Topic.objects.get(slug="fotografia")
        cls.free_course = cls.make_course("Guía de llaves", cls.security, CourseLevel.BEGINNER)
        cls.paid_course = cls.make_course("Guía de canales", cls.lightning, CourseLevel.ADVANCED, access=(AccessType.PAID,))
        cls.mixed_course = cls.make_course("Guía de hardware", cls.hardware, CourseLevel.INTERMEDIATE, access=(AccessType.FREE, AccessType.PAID))
        cls.tutorial = cls.make_course("Tutorial de redes", cls.networks, CourseLevel.BEGINNER, kind=CourseKind.TUTORIAL)
        cls.video = Video.objects.create(creator=cls.creator, title="Video de hardware", topic=cls.hardware, status=PublicationStatus.PUBLISHED)
        cls.material = Material.objects.create(creator=cls.creator, title="Material de redes", topic=cls.networks, access_type=AccessType.PAID, status=PublicationStatus.PUBLISHED)
        cls.reference = ExternalReference.objects.create(title="Referencia de llaves", source_name="Fuente", source_url="https://example.org/docs", topic=cls.security, status=PublicationStatus.PUBLISHED)
        cls.make_course("Curso todavía privado", cls.photography, CourseLevel.ADVANCED, status=PublicationStatus.DRAFT)

    @classmethod
    def make_course(cls, title, topic, level, *, access=(AccessType.FREE,), kind=CourseKind.COURSE, status=PublicationStatus.PUBLISHED, creator=None):
        course = Course.objects.create(creator=creator or cls.creator, title=title, topic=topic, level=level, kind=kind, status=status)
        chapter = Chapter.objects.create(course=course, title="Inicio", status=PublicationStatus.PUBLISHED)
        for position, access_type in enumerate(access, 1):
            Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, position=position, title=f"Unidad {position}", body="Contenido público", access_type=access_type, status=PublicationStatus.PUBLISHED)
        return course

    def facets(self, response):
        self.assertEqual(response.status_code, 200)
        return response.context["catalog_filters"]

    def values(self, entries):
        return {entry[0] for entry in entries}

    def topic_values(self, facets):
        return {topic["value"] for group in facets["topic_groups"] for topic in group["topics"]}

    def assert_hidden_context(self, markup, name, value):
        fields = markup.named(name)
        self.assertEqual(len(fields), 1)
        self.assertEqual(fields[0].get("type"), "hidden")
        self.assertEqual(fields[0].get("value"), value)

    def test_global_course_options_use_available_publications_instead_of_all_configured_taxonomy(self):
        response = self.client.get(reverse("courses"), {"vista": "todos"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 3)
        self.assertEqual({entry["value"] for entry in facets["categories"]}, {"bitcoin", "tecnologia"})
        self.assertEqual(self.topic_values(facets), {"seguridad", "lightning", "hardware-pc"})
        self.assertEqual(self.values(facets["levels"]), {"beginner", "intermediate", "advanced"})
        self.assertEqual(self.values(facets["access"]), {"gratis", "pago"})
        self.assertEqual(self.values(facets["formats"]), {"cursos"})
        self.assertFalse(facets["show_format"])
        self.assertNotContains(response, 'id="catalog-type"')

    def test_one_available_choice_needs_only_search_without_advanced_controls(self):
        response = self.client.get(reverse("tutorials"), {"vista": "todos"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 1)
        for flag in ("show_category", "show_topic", "show_level", "show_access", "show_format", "has_controls"):
            self.assertFalse(facets[flag], flag)
        markup = FilterMarkup(response)
        self.assertEqual(markup.details, [])
        self.assertIn("tutorial", markup.named("q")[0]["placeholder"].lower())
        self.assertContains(response, self.tutorial.title)

    def test_parent_navigation_preserves_context_without_duplicate_category_or_topic_selects(self):
        response = self.client.get(reverse("courses"), {"categoria": "bitcoin"})
        facets = self.facets(response)
        self.assertFalse(facets["show_category"])
        self.assertFalse(facets["show_topic"])
        self.assertEqual(facets["active_count"], 0)
        self.assertTrue(facets["show_level"])
        self.assertTrue(facets["show_access"])
        markup = FilterMarkup(response)
        self.assert_hidden_context(markup, "categoria", "bitcoin")
        self.assertFalse(any("options" in field for field in markup.named("tema")))
        self.assertContains(response, 'aria-label="Subcategorías de Bitcoin"')
        self.assertTrue(markup.details)

    def test_child_context_stays_hidden_when_only_one_choice_is_available(self):
        response = self.client.get(reverse("courses"), {"categoria": "bitcoin", "tema": "seguridad"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 1)
        self.assertFalse(facets["has_controls"])
        self.assertEqual(facets["active_count"], 0)
        markup = FilterMarkup(response)
        self.assert_hidden_context(markup, "categoria", "bitcoin")
        self.assert_hidden_context(markup, "tema", "seguridad")
        self.assertEqual(markup.details, [])
        self.assertIn(self.security.name.lower(), markup.named("q")[0]["placeholder"].lower())

    def test_search_defines_available_facets_without_becoming_an_advanced_filter(self):
        response = self.client.get(reverse("courses"), {"q": "llaves"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 1)
        self.assertEqual(self.values(facets["levels"]), {"beginner"})
        self.assertEqual({entry["value"] for entry in facets["categories"]}, {"bitcoin"})
        self.assertEqual(self.topic_values(facets), {"seguridad"})
        self.assertEqual(facets["active_count"], 0)
        self.assertTrue(facets["has_refinements"])
        self.assertFalse(facets["has_controls"])
        self.assertEqual(FilterMarkup(response).details, [])
        self.assertNotContains(response, self.mixed_course.title)
        self.assertNotContains(response, self.paid_course.title)

    def test_level_and_access_do_not_remove_other_available_options(self):
        response = self.client.get(reverse("courses"), {"nivel": "beginner", "acceso": "gratis"})
        facets = self.facets(response)
        self.assertEqual(response.context["result_count"], 1)
        self.assertEqual(facets["scope_count"], 3)
        self.assertEqual(self.values(facets["levels"]), {"beginner", "intermediate", "advanced"})
        self.assertEqual(self.values(facets["access"]), {"gratis", "pago"})
        self.assertEqual(facets["active_count"], 2)
        self.assertTrue(FilterMarkup(response).details)

    def test_resource_formats_and_access_are_public_and_stable_before_refinements(self):
        response = self.client.get(reverse("resources"), {"tipo": "materiales", "acceso": "pago"})
        facets = self.facets(response)
        self.assertEqual(response.context["result_count"], 1)
        self.assertEqual(facets["scope_count"], 3)
        self.assertEqual(self.values(facets["formats"]), {"videos", "materiales", "referencias"})
        self.assertEqual(self.values(facets["access"]), {"gratis", "pago"})
        self.assertFalse(facets["show_level"])
        self.assertFalse(FilterMarkup(response).named("nivel"))
        self.assertEqual(facets["active_count"], 2)

    def test_selected_unavailable_refinements_remain_visible_and_clearable(self):
        response = self.client.get(reverse("courses"), {"categoria": "bitcoin", "tema": "seguridad", "nivel": "advanced", "acceso": "pago"})
        facets = self.facets(response)
        self.assertEqual(response.context["result_count"], 0)
        self.assertEqual(facets["scope_count"], 1)
        self.assertEqual(self.values(facets["levels"]), {"beginner", "advanced"})
        self.assertEqual(self.values(facets["access"]), {"gratis", "pago"})
        self.assertTrue(facets["show_level"])
        self.assertTrue(facets["show_access"])
        self.assertEqual(response.context["clear_filters_url"], "/cursos/?categoria=bitcoin&tema=seguridad")
        markup = FilterMarkup(response)
        for name, value in (("nivel", "advanced"), ("acceso", "pago")):
            self.assertTrue(any(option.get("value") == value and "selected" in option for option in markup.named(name)[0]["options"]))
        self.assertTrue(markup.details)
        chips = {chip["label"]: parse_qs(urlsplit(chip["url"]).query) for chip in response.context["active_filter_chips"]}
        context = {"categoria": ["bitcoin"], "tema": ["seguridad"], "vista": ["todos"]}
        self.assertEqual(chips["Avanzado"], {**context, "acceso": ["pago"]})
        self.assertEqual(chips["Con contenido de pago"], {**context, "nivel": ["advanced"]})
        self.assertContains(response, 'aria-label="Quitar filtro: Avanzado"')

    def test_unavailable_format_after_search_is_kept_as_an_active_option(self):
        response = self.client.get(reverse("resources"), {"q": "Video de hardware", "tipo": "materiales"})
        facets = self.facets(response)
        self.assertEqual(response.context["result_count"], 0)
        self.assertEqual(facets["scope_count"], 1)
        self.assertEqual(self.values(facets["formats"]), {"videos", "materiales"})
        self.assertTrue(facets["show_format"])
        self.assertEqual(facets["active_count"], 1)

    def test_empty_category_keeps_search_and_context_without_empty_filter_controls(self):
        response = self.client.get(reverse("courses"), {"categoria": "creacion"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 0)
        self.assertFalse(facets["has_controls"])
        self.assertEqual(facets["categories"], [{"value": "creacion", "label": "Creación"}])
        self.assertFalse(facets["show_category"])
        self.assertEqual(facets["topic_groups"], [])
        markup = FilterMarkup(response)
        self.assert_hidden_context(markup, "categoria", "creacion")
        self.assertEqual(markup.details, [])
        self.assertIn("creación", markup.named("q")[0]["placeholder"].lower())

    def test_course_facets_use_published_snapshot_instead_of_pending_edits(self):
        course = self.make_course("Versión visible", self.security, CourseLevel.BEGINNER)
        publish_course(course, self.admin)
        Course.objects.filter(pk=course.pk).update(title="METADATO_PRIVADO", topic=self.hardware, level=CourseLevel.ADVANCED, kind=CourseKind.TUTORIAL)
        course.chapters.first().lessons.update(access_type=AccessType.PAID)
        response = self.client.get(reverse("courses"), {"q": "Versión visible"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 1)
        self.assertEqual(self.values(facets["levels"]), {"beginner"})
        self.assertEqual(self.values(facets["access"]), {"gratis"})
        self.assertEqual(self.values(facets["formats"]), {"cursos"})
        self.assertEqual(self.topic_values(facets), {"seguridad"})
        self.assertEqual({entry["value"] for entry in facets["categories"]}, {"bitcoin"})
        self.assertNotContains(response, "METADATO_PRIVADO")

    def test_resource_facets_use_reviewed_revision_topic_access_and_title(self):
        with TemporaryDirectory() as directory, self.settings(MEDIA_ROOT=directory):
            asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("facetas.txt", b"Contenido de prueba", content_type="text/plain"))
            resource = Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, title="Revisión visible", topic=self.hardware, access_type=AccessType.PAID, pending_asset=asset)
            publish_resource(resource, self.admin)
        Material.objects.filter(pk=resource.pk).update(title="OTRO_METADATO_PRIVADO", topic=self.photography, access_type=AccessType.FREE)
        response = self.client.get(reverse("resources"), {"q": "Revisión visible"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 1)
        self.assertEqual(self.values(facets["access"]), {"pago"})
        self.assertEqual(self.topic_values(facets), {"hardware-pc"})
        self.assertEqual({entry["value"] for entry in facets["categories"]}, {"tecnologia"})
        self.assertNotContains(response, "OTRO_METADATO_PRIVADO")

    def test_selector_keeps_relevant_filters_and_native_form_submission(self):
        response = self.client.get(reverse("course-selector"), {"categoria": "bitcoin", "tema": "seguridad"})
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 1)
        self.assertTrue(facets["show_category"])
        self.assertTrue(facets["show_topic"])
        self.assertTrue(FilterMarkup(response).named("categoria")[0].get("options"))
        self.assertNotContains(response, f'hx-get="{reverse("course-selector")}"')
        self.assertContains(response, self.free_course.title)
        self.assertNotContains(response, self.paid_course.title)

    def test_creator_metadata_excludes_other_creators_and_external_references(self):
        other = get_user_model().objects.create_user("other-filters@example.com", account_type="creator")
        self.make_course("Curso ajeno", self.photography, CourseLevel.BEGINNER, creator=other)
        response = self.client.get(reverse("creator-public-profile", args=[self.creator.pk]))
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 6)
        self.assertEqual(self.values(facets["formats"]), {"cursos", "tutoriales", "videos", "materiales"})
        self.assertEqual({entry["value"] for entry in facets["categories"]}, {"bitcoin", "tecnologia"})
        self.assertNotContains(response, "Curso ajeno")
        self.assertNotContains(response, self.reference.title)

    def test_legacy_topic_link_and_htmx_keep_search_context_and_return_destination(self):
        params = {"seccion": "cursos", "tema": "seguridad", "q": "llaves", "acceso": "gratis"}
        response = self.client.get(reverse("explore"), params, HTTP_HX_REQUEST="true")
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 1)
        self.assertEqual(parse_qs(response.context["filter_query"]), {key: [value] for key, value in params.items()})
        markup = FilterMarkup(response)
        self.assert_hidden_context(markup, "categoria", "bitcoin")
        self.assert_hidden_context(markup, "tema", "seguridad")
        self.assert_hidden_context(markup, "seccion", "cursos")
        self.assertNotContains(response, "<html")
        self.assertContains(response, "volver=%2Fexplorar%2F%3Fseccion%3Dcursos%26tema%3Dseguridad")

    def test_facet_scope_is_calculated_before_pagination(self):
        for number in range(13):
            self.make_course(f"Redes {number:02}", self.networks, CourseLevel.BEGINNER)
        params = {"categoria": "tecnologia", "tema": "redes", "q": "Redes", "pagina": 2}
        response = self.client.get(reverse("courses"), params)
        facets = self.facets(response)
        self.assertEqual(facets["scope_count"], 13)
        self.assertEqual(response.context["result_count"], 13)
        self.assertEqual(len(response.context["cards"]), 1)
        self.assertEqual(parse_qs(response.context["filter_query"]), {key: [str(value)] for key, value in params.items() if key != "pagina"})
        self.assert_hidden_context(FilterMarkup(response), "tema", "redes")

    def test_all_subcategories_link_preserves_search_and_other_refinements(self):
        refinements = {
            "categoria": "bitcoin", "q": "llaves", "nivel": "beginner",
            "acceso": "gratis", "tipo": "cursos",
        }
        response = self.client.get(reverse("courses"), {
            **refinements, "tema": "seguridad", "pagina": 2, "curso": self.free_course.pk,
        })
        url = response.context["all_subcategories_url"]
        self.assertEqual(urlsplit(url).path, reverse("courses"))
        self.assertEqual(parse_qs(urlsplit(url).query), {key: [value] for key, value in refinements.items()})
        self.assertContains(response, f'href="{escape(url)}">Todas')

    def test_uncategorized_scope_keeps_choice_for_publications_without_a_topic(self):
        orphan = Topic.objects.create(name="Tema independiente", slug="tema-independiente")
        orphan_course = self.make_course("Curso independiente", orphan, CourseLevel.BEGINNER)
        unassigned_course = self.make_course("Curso sin subcategoría", None, CourseLevel.BEGINNER)
        response = self.client.get(reverse("courses"), {"categoria": UNCATEGORIZED_TOPIC})
        self.assertEqual({card["item"].pk for card in response.context["cards"]}, {orphan_course.pk, unassigned_course.pk})
        unassigned_card = next(card for card in response.context["subcategory_cards"] if card["slug"] == UNCATEGORIZED_TOPIC)
        self.assertEqual(unassigned_card["count"], 1)
        self.assertEqual(parse_qs(urlsplit(unassigned_card["url"]).query), {"categoria": [UNCATEGORIZED_TOPIC], "tema": [UNCATEGORIZED_TOPIC]})
        self.assertContains(response, f'href="{escape(unassigned_card["url"])}">Sin subcategoría')

        legacy = self.client.get(reverse("courses"), {"tema": UNCATEGORIZED_TOPIC})
        self.assertEqual([card["item"].pk for card in legacy.context["cards"]], [unassigned_course.pk])
        self.assertNotContains(legacy, orphan_course.title)
        self.assertContains(legacy, "<h2>Sin subcategoría</h2>", html=True)
        self.assertContains(legacy, "Cambiar subcategoría")
        self.assertContains(legacy, 'class="category-parent-link"')
        selected = next(card for card in legacy.context["subcategory_cards"] if card["slug"] == UNCATEGORIZED_TOPIC)
        self.assertContains(legacy, f'href="{escape(selected["url"])}" aria-current="page">Sin subcategoría')
        self.assert_hidden_context(FilterMarkup(legacy), "tema", UNCATEGORIZED_TOPIC)
