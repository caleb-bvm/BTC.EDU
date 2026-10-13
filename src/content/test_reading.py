from django.template.loader import render_to_string
from django.test import SimpleTestCase

from .reading import reading_sections


class ReadingSectionsTests(SimpleTestCase):
    def test_editorial_practice_solution_and_reference_keep_all_text(self):
        body = "Una explicación.\n\nOtro párrafo.\n\nPráctica\nHaz el ejercicio.\n\nSolución y comprobación\nCompara el resultado.\n\nPara profundizar\nhttps://example.com/"
        sections = reading_sections(body)
        self.assertEqual([item["kind"] for item in sections], ["text", "text", "practice", "solution", "reference"])
        html = render_to_string("content/_reading.html", {"reading_sections": sections})
        self.assertIn('<details class="reading-solution">', html)
        self.assertNotIn('class="reading-solution" open', html)
        self.assertIn("Compara el resultado.", html)

    def test_plain_text_and_html_are_preserved_as_escaped_reading(self):
        body = 'Texto\nuna línea\n\n<script>alert("test")</script>\n\nPráctica\n<img src=x onerror=alert(1)>'
        html = render_to_string("content/_reading.html", {"reading_sections": reading_sections(body)})
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("una línea", html)

    def test_empty_protected_content_never_becomes_a_section(self):
        self.assertEqual(reading_sections(None), [])
