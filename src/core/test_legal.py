"""Terms and refund policy pages required by the consumer protection law."""
from django.core.checks import run_checks
from django.test import override_settings
from django.urls import reverse

from .test_i18n import SpanishAfterEachTest

PROVIDER = {"name": "Ejemplo, S.A. de C.V.", "nit": "0614-000000-000-0", "address": "San Salvador",
            "phone": "+503 0000-0000", "email": "ayuda@example.invalid"}


class LegalPageTests(SpanishAfterEachTest):
    def test_pages_are_public_and_linked_from_the_footer(self):
        home = self.client.get(reverse("home"))
        for name in ("terms", "refund-policy"):
            self.assertContains(home, reverse(name))
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        self.assertContains(self.client.get(reverse("refund-policy")), "Durante 8 días")
        self.assertContains(self.client.get("/en" + reverse("terms")), "Terms and conditions")

    @override_settings(LEGAL_PROVIDER=PROVIDER)
    def test_terms_show_the_seller_identity_when_configured(self):
        response = self.client.get(reverse("terms"))
        self.assertContains(response, "0614-000000-000-0")
        self.assertContains(response, "Defensoría del Consumidor")
        self.assertNotIn("accounts.W003", [issue.id for issue in run_checks(include_deployment_checks=True)])

    @override_settings(LEGAL_PROVIDER={**PROVIDER, "nit": ""})
    def test_missing_identity_is_a_deployment_warning_not_a_page_banner(self):
        self.assertNotContains(self.client.get(reverse("terms")), "NIT")
        self.assertIn("accounts.W003", [issue.id for issue in run_checks(include_deployment_checks=True)])
