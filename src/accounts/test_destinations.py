from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class FormDestination(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.links = []
        self.hidden = {}
        self.feed(body)

    def handle_starttag(self, tag, attributes):
        fields = dict(attributes)
        if tag == "a" and "href" in fields:
            self.links.append(fields["href"])
        if tag == "input" and fields.get("type") == "hidden":
            self.hidden[fields.get("name")] = fields.get("value", "")


@override_settings(SECURE_SSL_REDIRECT=False)
class StudentDestinationTests(TestCase):
    def signup_data(self, index=0, **extra):
        return {"email": f"journey{index}@destinations.invalid", "first_name": "Alumno",
                "password1": "Learning-Route-82491!", "password2": "Learning-Route-82491!", **extra}

    def test_offer_survives_login_signup_link_and_registration(self):
        target = "/ofertas/23/?volver=/tutoriales/"
        login = self.client.get(reverse("login"), {"next": target})
        links = FormDestination(login.content.decode()).links
        signup = next(link for link in links if link.startswith(reverse("student-signup")))
        self.assertEqual(parse_qs(urlsplit(signup).query)["next"], [target])
        response = self.client.get(signup)
        next_url = FormDestination(response.content.decode()).hidden["next"]
        self.assertEqual(next_url, target)
        self.assertRedirects(self.client.post(signup, self.signup_data(next=next_url)), target, fetch_redirect_response=False)
        self.assertEqual(get_user_model().objects.get(pk=self.client.session["_auth_user_id"]).account_type, "student")

    def test_registration_errors_and_back_to_login_keep_filters_and_fragment(self):
        target = reverse("explore") + "?tipo=tutoriales&q=Lightning&tema=bitcoin#catalog"
        response = self.client.post(reverse("student-signup"), self.signup_data(password2="different", next=target))
        self.assertEqual(response.status_code, 200)
        parsed = FormDestination(response.content.decode())
        self.assertEqual(parsed.hidden["next"], target)
        login = next(link for link in parsed.links if link.startswith(reverse("login")))
        self.assertEqual(parse_qs(urlsplit(login).query)["next"], [target])
        self.assertFalse(get_user_model().objects.filter(email="journey0@destinations.invalid").exists())

    def test_unsafe_or_other_role_destinations_never_redirect_outside_student_space(self):
        for index, target in enumerate(("https://outside.invalid", "//outside.invalid", "/\\outside.invalid", "/admin/", "/crear/", "javascript:alert(1)", "http://testserver/ofertas/23/")):
            with self.subTest(target=target):
                self.client.logout()
                response = self.client.post(reverse("student-signup"), self.signup_data(index, next=target))
                self.assertRedirects(response, reverse("workspace"))

    def test_post_destination_takes_precedence_over_query_and_default_is_workspace(self):
        response = self.client.post(reverse("student-signup") + "?next=/ofertas/23/", self.signup_data(next="//outside.invalid"))
        self.assertRedirects(response, reverse("workspace"))
        self.client.logout()
        self.assertRedirects(self.client.post(reverse("student-signup"), self.signup_data(1)), reverse("workspace"))

    def test_login_returns_to_exploration_and_people(self):
        user = get_user_model().objects.create_user("login@destinations.invalid", "Learning-Route-82491!")
        for target in (reverse("explore") + "?tipo=tutoriales", reverse("members") + "?q=Bitcoin"):
            with self.subTest(target=target):
                self.client.logout()
                response = self.client.post(reverse("login"), {"username": user.email, "password": "Learning-Route-82491!", "next": target})
                self.assertRedirects(response, target)

    def test_creator_registration_keeps_approval_required(self):
        response = self.client.post(reverse("creator-signup"), self.signup_data(next=reverse("creator-dashboard")))
        self.assertRedirects(response, reverse("creator-application"))
        user = get_user_model().objects.get(pk=self.client.session["_auth_user_id"])
        self.assertEqual(user.account_type, "creator")
        self.assertFalse(user.is_staff)
        self.assertFalse(hasattr(user, "creator_profile"))
