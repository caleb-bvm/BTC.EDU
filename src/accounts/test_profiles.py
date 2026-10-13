from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from creators.models import CreatorProfile


@override_settings(SECURE_SSL_REDIRECT=False)
class MemberProfileTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.student = users.create_user("private@profiles.invalid", first_name="Nombre privado", display_name="Luna", bio="Presentación privada", interests="Lightning")
        self.other = users.create_user("other@profiles.invalid")
        self.creator = users.create_user("creator@profiles.invalid", account_type="creator")
        CreatorProfile.objects.create(user=self.creator, display_name="Docente", bio="Educación", specialty="Bitcoin", status="approved")
        self.client.force_login(self.student)

    def test_private_default_only_owner_can_view(self):
        url = reverse("member-profile", args=[self.student.pk])
        self.assertContains(self.client.get(url), "Presentación privada")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_shared_profile_never_exposes_private_identity(self):
        self.student.profile_public = True
        self.student.save()
        self.client.logout()
        response = self.client.get(reverse("member-profile", args=[self.student.pk]))
        self.assertContains(response, "Luna")
        self.assertNotContains(response, self.student.email)
        self.assertNotContains(response, self.student.first_name)
        self.student.profile_public = False
        self.student.save()
        self.assertEqual(self.client.get(reverse("member-profile", args=[self.student.pk])).status_code, 404)

    def test_directory_filters_only_shared_and_approved_profiles(self):
        response = self.client.get(reverse("members"))
        self.assertContains(response, "Docente")
        self.assertNotContains(response, "Presentación privada")
        self.student.profile_public = True
        self.student.save()
        response = self.client.get(reverse("members"), {"q": "Lightning", "tipo": "student"})
        self.assertContains(response, "Luna")
        self.assertNotContains(response, "Docente")
        self.assertNotContains(response, self.student.email)
        profile = self.creator.creator_profile
        profile.status = "suspended"
        profile.save()
        self.assertNotContains(self.client.get(reverse("members")), "Docente")
        self.assertEqual(self.client.get(reverse("member-profile", args=[self.creator.pk])).status_code, 404)

    def test_creator_profile_keeps_canonical_url_and_public_identity(self):
        self.assertRedirects(self.client.get(reverse("member-profile", args=[self.creator.pk])), reverse("creator-public-profile", args=[self.creator.pk]))
        self.assertEqual(self.creator.public_name, "Docente")
        self.assertEqual(self.creator.profile_initials, "D")

    def test_profile_edit_cannot_change_role_or_other_account(self):
        response = self.client.post(reverse("student-profile"), {"first_name": "Nombre", "display_name": "Alias", "profile_public": "on", "bio": "Hola", "account_type": "creator", "email": "changed@invalid.test", "pk": self.other.pk})
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.other.refresh_from_db()
        self.assertTrue(self.student.profile_public)
        self.assertEqual(self.student.account_type, "student")
        self.assertEqual(self.student.email, "private@profiles.invalid")
        self.assertEqual(self.other.display_name, "")

    def test_share_requires_alias_and_rejects_unsafe_url(self):
        response = self.client.post(reverse("student-profile"), {"profile_public": "on", "display_name": "", "website": "javascript:alert(1)"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("display_name", response.context["form"].errors)
        self.assertIn("website", response.context["form"].errors)

    def test_edit_requires_csrf_and_directory_requires_login(self):
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.student)
        self.assertEqual(secure.post(reverse("student-profile"), {}).status_code, 403)
        self.client.logout()
        self.assertEqual(self.client.get(reverse("members")).status_code, 302)

    def test_inactive_and_admin_profiles_are_unavailable(self):
        admin = get_user_model().objects.create_superuser("admin@profiles.invalid")
        self.assertEqual(self.client.get(reverse("member-profile", args=[admin.pk])).status_code, 404)
        self.other.is_active = False
        self.other.profile_public = True
        self.other.save()
        self.assertEqual(self.client.get(reverse("member-profile", args=[self.other.pk])).status_code, 404)

    def test_public_bio_is_escaped(self):
        self.student.bio = '<script>alert("x")</script>'
        self.student.profile_public = True
        self.student.save()
        response = self.client.get(reverse("member-profile", args=[self.student.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("x")</script>')
