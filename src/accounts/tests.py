import re

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from creators.models import CreatorProfile


@override_settings(SECURE_SSL_REDIRECT=False, EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class IndependentAccountTests(TestCase):
    def setUp(self):
        self.email = "same@example.invalid"
        self.student_password = "Student-pass-38271!"
        self.creator_password = "Creator-pass-92486!"
        users = get_user_model().objects
        self.student = users.create_user(self.email, self.student_password)
        self.creator = users.create_user(self.email, self.creator_password, account_type="creator")
        CreatorProfile.objects.create(user=self.creator, display_name="Nombre del creador", bio="Perfil docente", specialty="Tecnología", status="approved")
        self.admin = users.create_superuser(self.email, "Admin-pass-64295!")

    def credentials(self, password):
        return {"username": self.email.upper(), "password": password}

    def test_same_email_is_three_independent_accounts(self):
        self.assertEqual(get_user_model().objects.filter(email=self.email).count(), 3)
        self.assertNotEqual(self.creator.pk, self.student.pk)
        self.assertIsNone(authenticate(username=self.email, password=self.creator_password, account_type="student"))
        self.assertEqual(authenticate(username=self.email, password=self.creator_password, account_type="creator"), self.creator)
        with self.assertRaises(IntegrityError), transaction.atomic():
            get_user_model().objects.create_user(self.email.upper(), "Other-pass-75931!", account_type="creator")

    def test_credentials_are_scoped_to_login(self):
        response = self.client.post(reverse("creator-login"), self.credentials(self.student_password))
        self.assertContains(response, "No pudimos iniciar sesión")
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post(reverse("login"), self.credentials(self.creator_password))
        self.assertContains(response, "No pudimos iniciar sesión")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_creator_login_goes_to_studio_student_to_workspace(self):
        self.assertRedirects(self.client.post(reverse("creator-login"), self.credentials(self.creator_password)), reverse("creator-dashboard"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.creator.pk)
        self.assertRedirects(self.client.post(reverse("login"), self.credentials(self.student_password)), reverse("workspace"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.student.pk)

    def test_pending_creator_can_sign_in_but_only_to_application(self):
        CreatorProfile.objects.filter(user=self.creator).update(status="pending")
        response = self.client.post(reverse("creator-login") + "?next=/crear/cursos/nuevo/", self.credentials(self.creator_password))
        self.assertRedirects(response, reverse("creator-application"))
        self.assertEqual(self.client.get(reverse("creator-dashboard")).status_code, 403)

    def test_suspended_and_inactive_cannot_login(self):
        CreatorProfile.objects.filter(user=self.creator).update(status="suspended")
        self.assertContains(self.client.post(reverse("creator-login"), self.credentials(self.creator_password)), "No pudimos iniciar sesión")
        get_user_model().objects.filter(pk=self.student.pk).update(is_active=False)
        self.assertContains(self.client.post(reverse("login"), self.credentials(self.student_password)), "No pudimos iniciar sesión")

    def test_wrong_session_redirects_to_correct_login_without_mutating_profile(self):
        self.client.force_login(self.student)
        for name in ("creator-dashboard", "creator-application", "creator-files"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse("creator-login")))
        self.client.post(reverse("creator-application"), {"display_name": "Student cannot apply"})
        self.assertFalse(CreatorProfile.objects.filter(user=self.student).exists())
        self.client.force_login(self.creator)
        self.assertRedirects(self.client.get(reverse("workspace")), reverse("login") + "?next=/mi-espacio/", fetch_redirect_response=False)

    def test_creator_studio_has_own_navigation(self):
        self.client.force_login(self.creator)
        response = self.client.get(reverse("creator-dashboard"))
        self.assertContains(response, "CUENTA DE CREADOR")
        self.assertNotContains(response, "Mi aprendizaje")
        self.assertNotContains(response, "Selector")
        self.client.force_login(self.student)
        response = self.client.get(reverse("workspace"))
        self.assertNotContains(response, "Estudio de creador")

    def test_student_profile_edits_do_not_modify_creator(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("student-profile"), {"first_name": "Nombre del estudiante", "last_name": "Alumno", "account_type": "creator", "email": "changed@example.invalid"})
        self.assertRedirects(response, reverse("student-profile"))
        self.student.refresh_from_db()
        self.creator.refresh_from_db()
        self.assertEqual(self.student.first_name, "Nombre del estudiante")
        self.assertEqual(self.student.account_type, "student")
        self.assertEqual(self.student.email, self.email)
        self.assertEqual(self.creator.creator_profile.display_name, "Nombre del creador")
        self.assertEqual(self.creator.first_name, "")
        self.client.force_login(self.creator)
        self.assertEqual(self.client.post(reverse("student-profile"), {"first_name": "No"}).status_code, 302)

    def test_safe_redirect_keeps_creator_destination_only(self):
        for next_url in ("https://example.org", "//example.org", "/mi-espacio/"):
            self.client.logout()
            response = self.client.post(reverse("creator-login") + "?next=" + next_url, self.credentials(self.creator_password))
            self.assertRedirects(response, reverse("creator-dashboard"))
        response = self.client.post(reverse("creator-login") + "?next=/crear/archivos/", self.credentials(self.creator_password))
        self.assertRedirects(response, reverse("creator-files"))
        response = self.client.post(reverse("login") + "?next=/crear/", self.credentials(self.student_password))
        self.assertRedirects(response, reverse("workspace"))

    def test_registration_sets_account_type_and_cannot_self_approve(self):
        data = {"email": "NEW@example.invalid", "first_name": "Persona", "password1": "New-pass-16358!", "password2": "New-pass-16358!", "account_type": "admin", "is_staff": True, "is_superuser": True, "status": "approved"}
        response = self.client.post(reverse("creator-signup"), data)
        self.assertRedirects(response, reverse("creator-application"))
        creator = get_user_model().objects.get(email="new@example.invalid", account_type="creator")
        self.assertFalse(creator.is_staff)
        self.assertFalse(creator.is_superuser)
        self.assertFalse(CreatorProfile.objects.filter(user=creator).exists())
        response = self.client.post(reverse("student-signup"), data)
        self.assertRedirects(response, reverse("workspace"))
        student = get_user_model().objects.get(email="new@example.invalid", account_type="student")
        self.assertNotEqual(student.pk, creator.pk)
        self.assertFalse(student.is_staff)

    def test_duplicate_registration_and_weak_password_do_not_create_user(self):
        initial = get_user_model().objects.count()
        response = self.client.post(reverse("creator-signup"), {"email": self.email.upper(), "first_name": "Nombre", "password1": "123", "password2": "123"})
        self.assertContains(response, "Ya existe una cuenta")
        self.assertEqual(get_user_model().objects.count(), initial)
        response = self.client.post(reverse("creator-signup"), {"email": "fresh@example.invalid", "first_name": "Nombre", "password1": "123", "password2": "123"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(email="fresh@example.invalid").exists())

    def test_recovery_sends_only_for_selected_account(self):
        self.client.post(reverse("creator-password-reset"), {"email": self.email})
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("cuenta de creador", mail.outbox[0].body)
        self.assertIn("/crear/recuperar/", mail.outbox[0].body)
        self.client.post(reverse("student-password-reset"), {"email": self.email})
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("cuenta de estudiante", mail.outbox[1].body)
        self.assertIn("/cuenta/recuperar/", mail.outbox[1].body)

    def test_reset_changes_only_creator_and_token_cannot_be_reused(self):
        self.client.post(reverse("creator-password-reset"), {"email": self.email})
        path = re.search(r"http://testserver(/crear/recuperar/\S+)", mail.outbox[0].body).group(1)
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)
        confirm = response.url
        self.assertRedirects(self.client.post(confirm, {"new_password1": "Changed-pass-23571!", "new_password2": "Changed-pass-23571!"}), reverse("creator-password-reset-complete"))
        self.creator.refresh_from_db()
        self.student.refresh_from_db()
        self.assertTrue(self.creator.check_password("Changed-pass-23571!"))
        self.assertTrue(self.student.check_password(self.student_password))
        self.assertContains(self.client.get(path), "Este enlace venció")

    def test_creator_token_does_not_work_on_student_reset(self):
        uid = urlsafe_base64_encode(force_bytes(self.creator.pk))
        token = default_token_generator.make_token(self.creator)
        response = self.client.get(reverse("student-password-reset-confirm", args=[uid, token]))
        self.assertContains(response, "Este enlace venció")

    def test_unknown_recovery_has_same_response_and_no_email(self):
        self.assertRedirects(self.client.post(reverse("creator-password-reset"), {"email": "missing@example.invalid"}), reverse("creator-password-reset-done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_admin_auth_is_separate(self):
        self.assertEqual(self.client.post("/admin/login/?next=/admin/", self.credentials(self.creator_password)).status_code, 200)
        response = self.client.post("/admin/login/?next=/admin/", self.credentials("Admin-pass-64295!"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.admin.pk)

    def test_creator_login_registration_and_logout_require_csrf(self):
        secure = Client(enforce_csrf_checks=True)
        for name in ("creator-login", "creator-signup", "student-signup", "creator-password-reset"):
            self.assertEqual(secure.post(reverse(name), {}).status_code, 403)
        self.assertEqual(self.client.get(reverse("creator-logout")).status_code, 405)
        self.client.force_login(self.creator)
        self.assertRedirects(self.client.post(reverse("creator-logout")), reverse("creator-login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_of_other_space_preserves_current_account(self):
        self.client.force_login(self.student)
        self.client.post(reverse("creator-logout"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.student.pk)
        self.client.force_login(self.creator)
        self.client.post(reverse("logout"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.creator.pk)


class AccountSeparationMigrationTests(TransactionTestCase):
    def test_existing_identity_ids_and_content_survive_separation(self):
        latest = MigrationExecutor(connection).loader.graph.leaf_nodes()
        old = [("accounts", "0001_initial"), ("creators", "0001_initial")]
        executor = MigrationExecutor(connection)
        executor.migrate(old)
        try:
            apps = executor.loader.project_state(old).apps
            User = apps.get_model("accounts", "User")
            student = User.objects.create(email="old-student@example.invalid", password="!")
            creator = User.objects.create(email="old-creator@example.invalid", password="!")
            admin = User.objects.create(email="old-admin@example.invalid", password="!", is_staff=True)
            apps.get_model("creators", "CreatorProfile").objects.create(user=creator, display_name="Conservar perfil", bio="Conservar", specialty="Contenido", status="approved")
            course = apps.get_model("content", "Course").objects.create(creator=creator, title="Conservar curso")
            ids = (student.pk, creator.pk, admin.pk, course.pk)
            MigrationExecutor(connection).migrate(latest)
            User = get_user_model()
            self.assertEqual(User.objects.get(pk=ids[0]).account_type, "student")
            self.assertEqual(User.objects.get(pk=ids[1]).account_type, "creator")
            self.assertEqual(User.objects.get(pk=ids[2]).account_type, "admin")
            self.assertEqual(CreatorProfile.objects.get(user_id=ids[1]).display_name, "Conservar perfil")
            from content.models import Course
            self.assertEqual(Course.objects.get(pk=ids[3]).creator_id, ids[1])
        finally:
            MigrationExecutor(connection).migrate(latest)
