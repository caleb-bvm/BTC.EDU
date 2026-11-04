from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import translation

from accounts.destinations import student_destination
from core.content_translation import translate_content, without_language_prefix
from core.translation_files import read_po


class SpanishAfterEachTest(TestCase):
    """English requests leave their language active in the test thread; later tests expect Spanish."""

    def tearDown(self):
        translation.activate(settings.LANGUAGE_CODE)


class BilingualSiteTests(SpanishAfterEachTest):
    def test_spanish_stays_unprefixed_and_english_lives_under_en(self):
        spanish = self.client.get("/")
        english = self.client.get("/en/")
        self.assertContains(spanish, '<html lang="es">')
        self.assertContains(spanish, "Aprende a tu ritmo")
        self.assertContains(english, '<html lang="en">')
        self.assertContains(english, "Learn at your own pace")
        self.assertNotContains(english, "Saltar al contenido")

    def test_switch_and_alternates_point_to_the_same_page_without_the_query(self):
        response = self.client.get("/en/cursos/?q=marcador-de-prueba")
        self.assertContains(response, 'href="/cursos/" hreflang="es" lang="es"')
        self.assertContains(response, '<link rel="alternate" hreflang="en" href="http://testserver/en/cursos/">')
        self.assertNotContains(response, 'hreflang="es" href="http://testserver/cursos/?')

    def test_urls_follow_the_active_language(self):
        with translation.override("en"):
            self.assertEqual(reverse("courses"), "/en/cursos/")
        with translation.override("es"):
            self.assertEqual(reverse("courses"), "/cursos/")
        self.assertEqual(reverse("pwa-manifest"), "/manifest.webmanifest")

    def test_login_redirect_keeps_the_language(self):
        response = self.client.get("/en/mi-espacio/")
        self.assertRedirects(response, "/en/cuenta/entrar/?next=/en/mi-espacio/", fetch_redirect_response=False)

    def test_student_destinations_accept_the_english_prefix(self):
        request = RequestFactory().get("/")
        self.assertEqual(without_language_prefix("/en/cursos/"), "/cursos/")
        self.assertEqual(student_destination(request, "/en/cursos/4/"), "/en/cursos/4/")
        self.assertEqual(student_destination(request, "/en/administracion/estadisticas/"), "")


class ContentTranslationTests(SpanishAfterEachTest):
    def test_catalog_text_is_translated_and_other_text_is_kept(self):
        title = "Bitcoin desde cero: unidades, red y transacciones"
        with translation.override("en"):
            self.assertEqual(translate_content(title), "Bitcoin from scratch: units, network and transactions")
            self.assertEqual(translate_content("Texto propio de un educador"), "Texto propio de un educador")
        with translation.override("es"):
            self.assertEqual(translate_content(title), title)

    def test_joined_paragraphs_are_translated_one_by_one(self):
        from content.course_catalog import SUPPORT
        text = "Bitcoin y Lightning\n\n" + SUPPORT
        with translation.override("en"):
            first, second = translate_content(text).split("\n\n")
        self.assertEqual(first, "Bitcoin and Lightning")
        self.assertTrue(second.startswith("Self-paced study"))

    def test_lesson_bodies_are_marked_as_spanish_in_english_pages(self):
        from django.template.loader import render_to_string
        with translation.override("en"):
            html = render_to_string("content/_reading.html", {"reading_sections": []})
        self.assertIn('lang="es"', html)
        with translation.override("es"):
            self.assertNotIn('lang="es"', render_to_string("content/_reading.html", {"reading_sections": []}))


class CatalogFileTests(TestCase):
    def test_catalogs_are_complete_and_keep_their_placeholders(self):
        output = StringIO()
        call_command("translations", "status", stdout=output)
        for domain in ("django", "content"):
            _header, entries = read_po(settings.BASE_DIR / "locale" / "en" / "LC_MESSAGES" / f"{domain}.po")
            self.assertTrue(entries)
            self.assertEqual([entry.msgid for entry in entries if not entry.translated], [])

    def test_compiled_catalogs_match_the_po_files(self):
        import tempfile
        from pathlib import Path

        from core.translation_files import write_mo
        for domain in ("django", "content"):
            po = settings.BASE_DIR / "locale" / "en" / "LC_MESSAGES" / f"{domain}.po"
            header, entries = read_po(po)
            with tempfile.TemporaryDirectory() as folder:
                fresh = Path(folder) / "fresh.mo"
                write_mo(fresh, header, entries)
                self.assertEqual(fresh.read_bytes(), po.with_suffix(".mo").read_bytes(), f"Run «manage.py translations compile» ({domain}).")
