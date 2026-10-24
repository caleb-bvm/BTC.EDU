from html.parser import HTMLParser

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from creators.models import CreatorProfile


class LoginDestination(HTMLParser):
    def __init__(self, response):
        super().__init__()
        self.destination = None
        self.feed(response.content.decode())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input" and attrs.get("name") == "next" and attrs.get("type") == "hidden":
            self.destination = attrs.get("value", "")


@override_settings(
    SECURE_SSL_REDIRECT=False,
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
    ACCOUNT_THROTTLE_ENABLED=False,
)
class CreatorLoginNavigationTests(TestCase):
    password = "Educator-Return-24713!"

    @classmethod
    def setUpTestData(cls):
        cls.educators = {}
        for status in ("approved", "pending", "suspended", "no-profile"):
            user = get_user_model().objects.create_user(
                f"{status}@login-navigation.invalid", cls.password, account_type="creator",
            )
            if status != "no-profile":
                CreatorProfile.objects.create(user=user, status=status, display_name=status)
            cls.educators[status] = user

    def credentials(self, status, destination):
        return {"username": self.educators[status].email, "password": self.password, "next": destination}

    def test_anonymous_get_keeps_destination_and_approved_post_returns_to_it(self):
        target = reverse("creator-content") + "?tipo=curso"
        page = self.client.get(reverse("creator-login"), {"next": target})
        destination = LoginDestination(page).destination
        self.assertEqual(destination, target)
        response = self.client.post(reverse("creator-login"), self.credentials("approved", destination))
        self.assertRedirects(response, target)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.educators["approved"].pk)

    def test_failed_signin_preserves_safe_destination_for_retry(self):
        target = reverse("creator-files")
        response = self.client.post(reverse("creator-login"), {
            **self.credentials("approved", target), "password": "wrong-password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LoginDestination(response).destination, target)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_unapproved_accounts_return_to_status_after_the_same_get_post_journey(self):
        target = reverse("creator-content") + "?tipo=curso"
        for status in ("pending", "suspended", "no-profile"):
            with self.subTest(status=status):
                self.client.logout()
                page = self.client.get(reverse("creator-login"), {"next": target})
                destination = LoginDestination(page).destination
                self.assertEqual(destination, target)
                response = self.client.post(reverse("creator-login"), self.credentials(status, destination))
                self.assertRedirects(response, reverse("creator-application"))
                self.assertEqual(int(self.client.session["_auth_user_id"]), self.educators[status].pk)
                self.assertEqual(self.client.post(reverse("creator-course-new"), {}).status_code, 403)
                self.educators[status].refresh_from_db()
                if status != "no-profile":
                    self.assertEqual(self.educators[status].creator_profile.status, status)
                else:
                    self.assertFalse(CreatorProfile.objects.filter(user=self.educators[status]).exists())

    def test_unsafe_other_space_and_auth_destinations_are_rejected_on_get_and_post(self):
        for target in (
            "https://outside.invalid/crear/contenido/", "//outside.invalid/crear/contenido/",
            "/\\outside.invalid/crear/contenido/", "javascript:alert(1)",
            "http://testserver/crear/contenido/", "/admin/", reverse("workspace"),
            reverse("creator-login") + "?next=/crear/contenido/", reverse("creator-signup"),
        ):
            with self.subTest(target=target):
                self.client.logout()
                page = self.client.get(reverse("creator-login"), {"next": target})
                self.assertEqual(LoginDestination(page).destination, "")
                response = self.client.post(reverse("creator-login"), self.credentials("approved", target))
                self.assertRedirects(response, reverse("creator-dashboard"))
