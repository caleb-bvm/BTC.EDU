from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(SECURE_SSL_REDIRECT=False)
class InstallableAppTests(TestCase):
    def test_manifest_and_service_worker_are_root_scoped(self):
        manifest = self.client.get(reverse("pwa-manifest"))
        self.assertEqual(manifest["Content-Type"], "application/manifest+json")
        data = manifest.json()
        self.assertEqual((data["scope"], data["display"]), ("/", "standalone"))
        self.assertIn("512x512", {icon["sizes"] for icon in data["icons"]})
        worker = self.client.get(reverse("pwa-service-worker"))
        self.assertEqual(worker["Service-Worker-Allowed"], "/")
        self.assertIn("javascript", worker["Content-Type"])
        self.assertIn(b"btc-edu-saved", worker.content)
        home = self.client.get(reverse("home"))
        self.assertContains(home, reverse("pwa-manifest"))
        self.assertContains(home, "js/offline.js")

    def test_offline_page_is_cached_without_the_session(self):
        user = get_user_model().objects.create_user("offline@example.invalid", display_name="Persona privada")
        self.client.force_login(user)
        response = self.client.get(reverse("offline"))
        self.assertContains(response, "Sin conexión")
        self.assertNotContains(response, "btc-account-id")
        self.assertNotContains(response, "Persona privada")
