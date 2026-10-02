from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import DatabaseError, IntegrityError, transaction
from django.test import Client, TestCase


class FoundationTests(TestCase):
    def test_public_pages_and_health(self):
        for url in ("/", "/explorar/", "/para-creadores/", "/cuenta/entrar/", "/health/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_private_workspace_requires_login(self):
        self.assertRedirects(self.client.get("/mi-espacio/"), "/cuenta/entrar/?next=/mi-espacio/", fetch_redirect_response=False)
        self.assertEqual(self.client.get("/admin/").status_code, 302)

    def test_health_handles_database_unavailability(self):
        with patch("core.views.connection.cursor", side_effect=DatabaseError):
            response = self.client.get("/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})

    def test_email_account_and_external_redirect_rejection(self):
        user = get_user_model().objects.create_user("Alumno@Example.com", "prueba-segura-2026")
        self.assertEqual(user.email, "alumno@example.com")
        response = self.client.post("/cuenta/entrar/?next=https://example.org", {"username": user.email, "password": "prueba-segura-2026"})
        self.assertRedirects(response, "/mi-espacio/")
        self.assertEqual(self.client.get("/admin/").status_code, 302)

    def test_duplicate_email_is_case_insensitive(self):
        get_user_model().objects.create_user("alumno@example.com", "prueba-segura-2026")
        with self.assertRaises(IntegrityError), transaction.atomic():
            get_user_model().objects.create_user("ALUMNO@EXAMPLE.COM", "otra-clave-segura")

    def test_login_requires_csrf_and_logout_requires_post(self):
        secure_client = Client(enforce_csrf_checks=True)
        self.assertEqual(secure_client.post("/cuenta/entrar/", {}).status_code, 403)
        self.assertEqual(self.client.get("/cuenta/salir/").status_code, 405)

    def test_htmx_filter_returns_only_empty_catalog(self):
        response = self.client.get("/explorar/?tipo=videos", HTTP_HX_REQUEST="true")
        self.assertContains(response, "Todavía no hay videos")
        self.assertNotContains(response, "<html")
