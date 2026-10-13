import uuid
from datetime import timedelta
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from creators.application_service import review_application
from creators.models import CreatorApplicationEvent, CreatorProfile
from learning.models import Notification
from learning.support import notify

from .account_forms import PhotoForm
from .mail import deliver_mail
from .models import (
    AccountEmailAction,
    AccountMail,
    AccountSession,
    AccountSupportRequest,
)
from .security import (
    action_token,
    close_account,
    confirm_action,
    request_email_action,
    resolve_action,
)
from .support import review_support
from .throttling import AccessThrottled, allow


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_SEND_EMAIL=False,
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class AccountServiceTests(TestCase):
    def setUp(self):
        self.media = TemporaryDirectory(prefix="btc-edu-test-photos-")
        self.settings_override = override_settings(MEDIA_ROOT=self.media.name)
        self.settings_override.enable()
        self.addCleanup(self.media.cleanup)
        self.addCleanup(self.settings_override.disable)
        users = get_user_model().objects
        self.password = "Learning-service-92481!"
        self.student = users.create_user("same@service.invalid", self.password, display_name="Luna")
        self.creator = users.create_user("same@service.invalid", "Creator-service-18429!", account_type="creator")
        self.other = users.create_user("other@service.invalid", self.password, display_name="Sol")
        self.admin = users.create_superuser("review@service.invalid", self.password)
        self.profile = CreatorProfile.objects.create(user=self.creator, display_name="Docente", bio="Experiencia", specialty="Bitcoin", status="pending")
        self.request = RequestFactory().get("/cuenta/ajustes/")
        self.client.force_login(self.student)

    @staticmethod
    def image(name="portrait.jpg", size=(300, 220), color="red"):
        stream = BytesIO()
        image = Image.new("RGB", size, color)
        exif = Image.Exif()
        exif[315] = "Private author metadata"
        image.save(stream, "JPEG", exif=exif)
        return SimpleUploadedFile(name, stream.getvalue(), content_type="image/jpeg")

    def test_settings_pages_render_for_their_own_account(self):
        for suffix in ("", "-photo", "-security", "-password", "-email", "-preferences", "-sessions", "-support", "-export", "-close", "-switch"):
            with self.subTest(suffix=suffix):
                self.assertEqual(self.client.get(reverse("student-account" + suffix)).status_code, 200)
                self.assertEqual(self.client.get(reverse("creator-account" + suffix)).status_code, 302)
        self.client.force_login(self.creator)
        self.assertEqual(self.client.get(reverse("creator-account")).status_code, 200)

    def test_photo_is_normalized_and_metadata_removed(self):
        response = self.client.post(reverse("student-account-photo"), {"photo": self.image(), "crop_x": 100, "crop_y": 0, "zoom": "1.4"})
        self.assertRedirects(response, reverse("student-account-photo"))
        self.student.refresh_from_db()
        with self.student.avatar.storage.open(self.student.avatar.name, "rb") as file, Image.open(file) as image:
            self.assertEqual(image.size, (384, 384))
            self.assertEqual(image.format, "WEBP")
            self.assertNotIn("exif", image.info)
            self.assertNotIn("Private author metadata", str(image.info))
        self.assertNotIn("portrait", self.student.avatar.name)
        self.creator.refresh_from_db()
        self.assertFalse(self.creator.avatar)

    def test_replacing_and_removing_photo_delete_only_old_file(self):
        self.client.post(reverse("student-account-photo"), {"photo": self.image()})
        self.student.refresh_from_db()
        previous, storage = self.student.avatar.name, self.student.avatar.storage
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("student-account-photo"), {"photo": self.image(color="blue")})
        self.student.refresh_from_db()
        self.assertFalse(storage.exists(previous))
        self.assertTrue(storage.exists(self.student.avatar.name))
        previous = self.student.avatar.name
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(reverse("student-account-photo"), {"remove_photo": "on"})
        self.student.refresh_from_db()
        self.assertFalse(self.student.avatar)
        self.assertFalse(storage.exists(previous))

    def test_fake_image_oversize_and_invalid_crop_are_rejected(self):
        form = PhotoForm({"zoom": 4}, {"photo": self.image()})
        self.assertFalse(form.is_valid())
        fake = SimpleUploadedFile("fake.jpg", b"<svg onload='alert(1)'></svg>", content_type="image/jpeg")
        self.assertFalse(PhotoForm({}, {"photo": fake}).is_valid())
        large = SimpleUploadedFile("large.png", b"x" * (3 * 1024 * 1024 + 1), content_type="image/png")
        self.assertFalse(PhotoForm({}, {"photo": large}).is_valid())
        self.assertFalse(PhotoForm({}, {"photo": self.image(size=(40, 40))}).is_valid())

    def test_avatar_visibility_tracks_profile_privacy(self):
        self.client.post(reverse("student-account-photo"), {"photo": self.image()})
        self.student.refresh_from_db()
        url = self.student.avatar_url
        owner = self.client.get(url)
        self.assertEqual(owner.status_code, 200)
        owner.close()
        anonymous = Client()
        self.assertEqual(anonymous.get(url).status_code, 404)
        self.student.profile_public = True
        self.student.save(update_fields=("profile_public",))
        public = anonymous.get(url)
        try:
            self.assertEqual(public.status_code, 200)
            self.assertIn("private", public["Cache-Control"])
            self.assertIn("no-store", public["Cache-Control"])
        finally:
            public.close()
        self.student.profile_public = False
        self.student.save(update_fields=("profile_public",))
        self.assertEqual(anonymous.get(url).status_code, 404)

    def test_csrf_and_stale_identity_protect_photo(self):
        secured = Client(enforce_csrf_checks=True)
        secured.force_login(self.student)
        self.assertEqual(secured.post(reverse("student-account-photo"), {"photo": self.image()}).status_code, 403)
        response = self.client.post(reverse("student-account-photo"), {"account_id": self.other.pk, "photo": self.image()})
        self.assertEqual(response.status_code, 403)
        self.student.refresh_from_db()
        self.assertFalse(self.student.avatar)

    def test_private_photo_visible_only_in_authorized_visible_conversation(self):
        from content.models import Course, CourseVersion
        from learning.models import CommunityPost, Enrollment
        self.client.post(reverse("student-account-photo"), {"photo": self.image()})
        self.student.refresh_from_db()
        course = Course.objects.create(creator=self.creator, title="Curso", status="published")
        version = CourseVersion.objects.create(course=course, number=1, title="Curso", kind="course", creator_name="Docente", sealed=True, published_at=timezone.now())
        post = CommunityPost.objects.create(version=version, author=self.student, body="Hola", request_key=uuid.uuid4())
        viewer = Client()
        viewer.force_login(self.other)
        self.assertEqual(viewer.get(self.student.avatar_url).status_code, 404)
        Enrollment.objects.create(student=self.other, version=version)
        response = viewer.get(self.student.avatar_url)
        try:
            self.assertEqual(response.status_code, 200)
        finally:
            response.close()
        CommunityPost._base_manager.filter(pk=post.pk).update(hidden=True)
        self.assertEqual(viewer.get(self.student.avatar_url).status_code, 404)

    def test_creator_photo_public_only_while_approved(self):
        self.client.force_login(self.creator)
        self.client.post(reverse("creator-account-photo"), {"photo": self.image()})
        self.creator.refresh_from_db()
        visitor = Client()
        self.assertEqual(visitor.get(self.creator.avatar_url).status_code, 404)
        review_application(self.profile, self.admin, "approved", "")
        response = visitor.get(self.creator.avatar_url)
        try:
            self.assertEqual(response.status_code, 200)
        finally:
            response.close()
        review_application(self.profile, self.admin, "suspended", "Revisar perfil")
        self.assertEqual(visitor.get(self.creator.avatar_url).status_code, 404)

    def test_password_change_keeps_this_session_and_other_identity(self):
        other_browser = Client()
        other_browser.force_login(self.student)
        other_browser.get(reverse("student-account"))
        response = self.client.post(reverse("student-account-password"), {"old_password": self.password, "new_password1": "New-student-access-37281!", "new_password2": "New-student-access-37281!"})
        self.assertRedirects(response, reverse("student-account-security"))
        self.assertEqual(other_browser.get(reverse("student-account")).status_code, 302)
        self.creator.refresh_from_db()
        self.assertTrue(self.creator.check_password("Creator-service-18429!"))

    def test_wrong_password_does_not_change_email(self):
        response = self.client.post(reverse("student-account-email"), {"password": "wrong", "email": "new@service.invalid"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(AccountEmailAction.objects.exists())

    def test_verification_requires_post_and_token_is_single_use(self):
        action = request_email_action(self.request, self.student, "verify")
        url = reverse("account-email-confirm", args=[action_token(action)])
        visitor = Client()
        self.assertEqual(visitor.get(url).status_code, 200)
        self.student.refresh_from_db()
        self.assertIsNone(self.student.email_verified_at)
        self.assertContains(visitor.post(url), "Correo confirmado")
        self.student.refresh_from_db()
        self.assertIsNotNone(self.student.email_verified_at)
        with self.assertRaises(ValidationError):
            resolve_action(action_token(action))
        self.creator.refresh_from_db()
        self.assertIsNone(self.creator.email_verified_at)

    def test_expired_resend_and_password_change_invalidate_tokens(self):
        old = request_email_action(self.request, self.student, "verify")
        new = request_email_action(self.request, self.student, "verify")
        with self.assertRaises(ValidationError):
            resolve_action(action_token(old))
        AccountEmailAction.objects.filter(pk=new.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
        with self.assertRaises(ValidationError):
            resolve_action(action_token(new))
        another = request_email_action(self.request, self.student, "verify")
        self.student.set_password("Different-password-34782!")
        self.student.save(update_fields=("password",))
        with self.assertRaises(ValidationError):
            resolve_action(action_token(another))

    def test_email_change_requires_both_buxes_and_preserves_id(self):
        browser = Client()
        browser.force_login(self.student)
        original_id = self.student.pk
        action = request_email_action(self.request, self.student, "change", "new@service.invalid")
        _, done = confirm_action(action_token(action))
        self.assertFalse(done)
        self.student.refresh_from_db()
        self.assertEqual(self.student.email, "same@service.invalid")
        _, done = confirm_action(action_token(action, "old"))
        self.assertTrue(done)
        self.student.refresh_from_db()
        self.assertEqual(self.student.pk, original_id)
        self.assertEqual(self.student.email, "new@service.invalid")
        self.assertEqual(browser.get(reverse("student-account")).status_code, 302)
        self.creator.refresh_from_db()
        self.assertEqual(self.creator.email, "same@service.invalid")

    def test_email_collision_at_confirmation_preserves_original_identity(self):
        action = request_email_action(self.request, self.student, "change", "occupied@service.invalid")
        confirm_action(action_token(action, "old"))
        get_user_model().objects.create_user("occupied@service.invalid", self.password)
        with self.assertRaises(ValidationError):
            confirm_action(action_token(action))
        self.student.refresh_from_db()
        self.assertEqual(self.student.email, "same@service.invalid")

    def test_confirm_link_does_not_bypass_csrf(self):
        action = request_email_action(self.request, self.student, "verify")
        visitor = Client(enforce_csrf_checks=True)
        url = reverse("account-email-confirm", args=[action_token(action)])
        visitor.get(url)
        self.assertEqual(visitor.post(url).status_code, 403)
        self.student.refresh_from_db()
        self.assertIsNone(self.student.email_verified_at)

    def test_ajax_photo_success_preserves_flash_and_error_preserves_form(self):
        response = self.client.post(reverse("student-account-photo"), {"photo": self.image()}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.json()["redirect"], reverse("student-account-photo"))
        self.assertContains(self.client.get(response.json()["redirect"]), "Foto de perfil actualizada")
        response = self.client.post(reverse("student-account-photo"), {"photo": self.image(size=(20, 20))}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertContains(response, "account-errors")

    def test_stale_application_revision_preserves_admin_decision(self):
        from creators.application_service import save_application
        review_application(self.profile, self.admin, "approved", "")
        with self.assertRaises(ValidationError):
            save_application(self.creator, {"display_name": "Otro", "bio": "Texto", "specialty": "Bitcoin", "website": ""}, expected_revision=0)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, "Docente")

    def test_mail_failure_is_retryable_without_exposing_links(self):
        action = request_email_action(self.request, self.student, "verify")
        queued = AccountMail.objects.get(action=action)
        with patch("accounts.mail.send_mail", side_effect=OSError("offline")):
            self.assertFalse(deliver_mail(queued.pk))
        queued.refresh_from_db()
        self.assertEqual(queued.status, "failed")
        AccountMail.objects.filter(pk=queued.pk).update(next_attempt_at=timezone.now() - timedelta(seconds=1))
        self.assertTrue(deliver_mail(queued.pk))
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(deliver_mail(queued.pk))

    def test_superseded_mail_is_not_delivered(self):
        old = request_email_action(self.request, self.student, "verify")
        request_email_action(self.request, self.student, "verify")
        queued = AccountMail.objects.get(action=old)
        self.assertFalse(deliver_mail(queued.pk))
        queued.refresh_from_db()
        self.assertEqual(queued.status, "cancelled")
        self.assertEqual(queued.body, "")

    def test_creator_decisions_notify_once_and_history_is_retained(self):
        review_application(self.profile, self.admin, "changes", "Completa tu experiencia.")
        review_application(self.profile, self.admin, "changes", "Completa tu experiencia.")
        self.assertEqual(CreatorApplicationEvent.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.creator).count(), 1)
        review_application(self.profile, self.admin, "approved", "")
        self.assertEqual(CreatorApplicationEvent.objects.count(), 2)
        self.assertEqual(Notification.objects.filter(recipient=self.creator).count(), 2)
        with self.assertRaises(ValidationError):
            review_application(self.profile, self.admin, "suspended", "")

    def test_suspended_creator_can_see_reason_but_not_tools(self):
        review_application(self.profile, self.admin, "suspended", "Revisar autoría.")
        self.client.logout()
        response = self.client.post(reverse("creator-login"), {"username": self.creator.email, "password": "Creator-service-18429!"})
        self.assertRedirects(response, reverse("creator-application"))
        self.assertContains(self.client.get(reverse("creator-application")), "Revisar autoría.")
        self.assertEqual(self.client.post(reverse("creator-course-new"), {"title": "Blocked"}).status_code, 403)
        self.assertRedirects(self.client.get(reverse("creator-dashboard")), reverse("creator-application"))
        self.assertEqual(self.client.get(reverse("creator-account-support")).status_code, 200)

    def test_support_and_appeal_are_private_and_idempotent(self):
        review_application(self.profile, self.admin, "suspended", "Motivo de revisión")
        self.client.force_login(self.creator)
        data = {"kind": "appeal", "body": "Solicito revisar mi suspensión.", "request_key": str(uuid.uuid4())}
        self.assertRedirects(self.client.post(reverse("creator-account-support"), data), reverse("creator-account-support"))
        self.client.post(reverse("creator-account-support"), data)
        self.assertEqual(AccountSupportRequest.objects.count(), 1)
        item = AccountSupportRequest.objects.get()
        review_support(item, self.admin, "resolved", "Revisamos la solicitud; consulta tu perfil.")
        self.assertEqual(item.history.count(), 2)
        self.client.force_login(self.student)
        self.assertNotContains(self.client.get(reverse("student-account-support")), "Solicito revisar mi suspensión.")

    def test_preferences_skip_optional_notices_but_keep_decisions(self):
        self.student.notify_questions = False
        self.student.notify_community = False
        self.student.save(update_fields=("notify_questions", "notify_community"))
        notify(self.student, "question:999", "Pregunta", "/")
        notify(self.student, "community-reply:999", "Comunidad", "/")
        notify(self.student, "community-decision:999", "Decisión", "/")
        self.assertEqual(Notification.objects.filter(recipient=self.student).count(), 1)
        notice = Notification.objects.get(recipient=self.student)
        self.assertEqual(notice.category, "service")

    def test_read_all_does_not_change_other_users_notices(self):
        own = notify(self.student, "account:1", "Cuenta", "/")
        other = notify(self.other, "account:2", "Cuenta", "/")
        self.client.post(reverse("notifications-read-all"))
        own.refresh_from_db()
        other.refresh_from_db()
        self.assertIsNotNone(own.read_at)
        self.assertIsNone(other.read_at)

    def test_export_excludes_password_tokens_and_other_identity(self):
        response = self.client.post(reverse("student-account-export"), {"password": self.password})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["account"]["id"], self.student.pk)
        self.assertNotIn("password", data["account"])
        self.assertNotIn("session_key", response.content.decode())
        self.assertNotIn("Creator-service", response.content.decode())

    def test_close_and_restore_keep_id_and_do_not_restore_admin_disable(self):
        original_id = self.student.pk
        close_account(self.student)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)
        action = request_email_action(self.request, self.student, "restore")
        user, done = confirm_action(action_token(action), "Restored-student-43817!")
        self.assertTrue(done)
        self.assertEqual(user.pk, original_id)
        self.assertTrue(user.is_active)
        self.assertIsNone(user.closed_at)
        self.other.is_active = False
        self.other.save(update_fields=("is_active",))
        self.client.logout()
        self.client.post(reverse("account-restore"), {"email": self.other.email, "account_type": "student"})
        self.assertFalse(AccountEmailAction.objects.filter(user=self.other).exists())

    def test_access_limits_are_scoped_to_account_type(self):
        for _ in range(12):
            allow(self.request, "student", "login", "same@service.invalid")
        with self.assertRaises(AccessThrottled):
            allow(self.request, "student", "login", "same@service.invalid")
        allow(self.request, "creator", "login", "same@service.invalid")

    def test_session_revoke_rejects_other_account_and_malformed_id(self):
        visitor = Client()
        visitor.force_login(self.other)
        visitor.get(reverse("student-account"))
        foreign = AccountSession.objects.get(user=self.other)
        self.assertEqual(self.client.post(reverse("student-account-sessions"), {"session": foreign.pk}).status_code, 404)
        self.assertEqual(self.client.post(reverse("student-account-sessions"), {"session": "malformed"}).status_code, 404)

    @override_settings(ACCOUNT_REQUIRE_VERIFIED_EMAIL=True)
    def test_public_operation_requires_verified_profile_and_creator_approval(self):
        self.student.profile_public = True
        self.student.save(update_fields=("profile_public",))
        self.assertFalse(self.student.has_public_profile)
        self.assertEqual(Client().get(reverse("member-profile", args=[self.student.pk])).status_code, 404)
        with self.assertRaises(ValidationError):
            review_application(self.profile, self.admin, "approved", "")
        action = request_email_action(self.request, self.creator, "verify")
        confirm_action(action_token(action))
        review_application(self.profile, self.admin, "approved", "")
        self.creator.refresh_from_db()
        self.assertTrue(self.creator.has_public_profile)

    def test_verification_retains_safe_learning_destination(self):
        action = request_email_action(self.request, self.student, "verify", destination="/explorar/?tipo=tutoriales")
        response = self.client.post(reverse("account-email-confirm", args=[action_token(action)]))
        self.assertContains(response, 'href="/explorar/?tipo=tutoriales"')
        unsafe = request_email_action(self.request, self.student, "verify", destination="https://outside.invalid/")
        self.assertEqual(unsafe.destination, "")

    def test_audit_events_cannot_be_rewritten(self):
        from .models import AccountEvent
        event = AccountEvent.objects.create(user=self.student, kind="photo_updated")
        event.detail = "Rewritten"
        with self.assertRaises(ValidationError):
            event.save()
        with self.assertRaises(ValidationError):
            AccountEvent.objects.filter(pk=event.pk).delete()
