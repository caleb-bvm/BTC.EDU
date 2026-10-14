from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile

from .community import access, moderate, post_message, report_message
from .models import (
    CommunityDecision,
    CommunityPost,
    CommunityReport,
    Enrollment,
    Notification,
)
from .services import enroll


@override_settings(SECURE_SSL_REDIRECT=False)
class CommunityTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("creator@community.invalid", account_type="creator", first_name="Ana")
        CreatorProfile.objects.create(user=self.creator, display_name="Ana", status="approved")
        self.admin = users.create_superuser("admin@community.invalid")
        self.student = users.create_user("student@community.invalid", first_name="Lucía")
        self.peer = users.create_user("peer@community.invalid", first_name="Luis")
        self.outsider = users.create_user("other@community.invalid")
        self.course = Course.objects.create(creator=self.creator, title="Comunidad", description="Aprendemos juntos")
        chapter = Chapter.objects.create(course=self.course, title="Inicio", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Lección", body="Texto", status="published")
        self.version = publish_course(self.course, self.admin)
        enroll(self.student, self.version)
        enroll(self.peer, self.version)
        self.client.force_login(self.student)

    def post(self, body="Una pregunta"):
        return post_message(self.student, self.version, body, uuid4())

    def test_access_requires_same_version_enrollment(self):
        with self.assertRaises(PermissionDenied):
            access(self.outsider, self.version)
        later = publish_course(self.course, self.admin)
        with self.assertRaises(PermissionDenied):
            access(self.student, later)
        self.assertEqual(self.client.get(reverse("community-space", args=[later.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse("community-space", args=[self.version.pk])).status_code, 200)

    def test_retired_version_remains_available(self):
        self.course.status = "archived"
        self.course.save()
        access(self.student, self.version)
        self.assertEqual(self.client.get(reverse("community-spaces")).status_code, 200)

    def test_idempotent_post_and_changed_payload_rejected(self):
        key = uuid4()
        post = post_message(self.student, self.version, "Hola", key)
        self.assertEqual(post_message(self.student, self.version, "Hola", key).pk, post.pk)
        with self.assertRaises(ValidationError):
            post_message(self.student, self.version, "Otro", key)
        self.assertEqual(CommunityPost.objects.count(), 1)

    def test_replies_only_to_open_root_in_same_version(self):
        root = self.post()
        reply = post_message(self.peer, self.version, "Respuesta", uuid4(), root.pk)
        with self.assertRaises(ValidationError):
            post_message(self.student, self.version, "Anidada", uuid4(), reply.pk)
        moderate(self.creator, self.version, "close", "Tema resuelto", root.pk)
        with self.assertRaises(ValidationError):
            post_message(self.peer, self.version, "Tarde", uuid4(), root.pk)
        moderate(self.creator, self.version, "open", "Continuar", root.pk)
        post_message(self.peer, self.version, "Ahora", uuid4(), root.pk)

    def test_hidden_thread_and_replies_never_leak(self):
        root = self.post("Contenido privado ocultado")
        post_message(self.peer, self.version, "Respuesta oculta", uuid4(), root.pk)
        moderate(self.creator, self.version, "hide", "Incumple normas", root.pk)
        self.assertEqual(self.client.get(reverse("community-thread", args=[root.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("community-space", args=[self.version.pk])), root.body)
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(reverse("community-thread", args=[root.pk])), root.body)
        moderate(self.creator, self.version, "show", "Revisado", root.pk)
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse("community-thread", args=[root.pk])), root.body)

    def test_hidden_reply_not_rendered_for_students(self):
        root = self.post()
        reply = post_message(self.peer, self.version, "Ocultar respuesta específica", uuid4(), root.pk)
        moderate(self.creator, self.version, "hide", "Revisión", reply.pk)
        self.assertNotContains(self.client.get(reverse("community-thread", args=[root.pk])), reply.body)

    def test_reports_idempotent_and_resolved_with_audit(self):
        root = self.post()
        report = report_message(self.peer, root.pk, "Spam")
        self.assertEqual(report_message(self.peer, root.pk, "Reintento").pk, report.pk)
        moderate(self.creator, self.version, "dismiss", "No incumple", root.pk)
        report.refresh_from_db()
        self.assertTrue(report.resolved)
        self.assertEqual(CommunityDecision.objects.get().reason, "No incumple")
        self.assertEqual(CommunityReport.objects.count(), 1)

    def test_suspension_preserves_reading_and_learning_and_is_reversible(self):
        root = self.post()
        moderate(self.creator, self.version, "suspend", "Conducta", student_id=self.student.pk)
        access(self.student, self.version)
        with self.assertRaises(PermissionDenied):
            self.post("Bloqueada")
        self.assertEqual(self.client.get(reverse("community-thread", args=[root.pk])).status_code, 200)
        self.assertTrue(Enrollment.objects.filter(student=self.student, version=self.version).exists())
        moderate(self.creator, self.version, "restore", "Revisión favorable", student_id=self.student.pk)
        self.post("Restablecida")
        self.assertEqual(CommunityDecision.objects.count(), 2)

    def test_moderation_ownership_and_staff_permission(self):
        root = self.post()
        with self.assertRaises(PermissionDenied):
            moderate(self.peer, self.version, "hide", "No autorizado", root.pk)
        staff = get_user_model().objects.create_user("staff@community.invalid", is_staff=True)
        with self.assertRaises(PermissionDenied):
            moderate(staff, self.version, "hide", "Sin permiso", root.pk)
        staff.user_permissions.add(Permission.objects.get(codename="moderate_community"))
        moderate(staff, self.version, "hide", "Administración", root.pk)
        another = get_user_model().objects.create_user("creator2@community.invalid", account_type="creator")
        CreatorProfile.objects.create(user=another, display_name="Otro", status="approved")
        with self.assertRaises(PermissionDenied):
            moderate(another, self.version, "show", "Ajeno", root.pk)

    def test_no_reason_no_change_and_repeated_decisions_no_duplicate(self):
        root = self.post()
        with self.assertRaises(ValidationError):
            moderate(self.creator, self.version, "hide", " ", root.pk)
        moderate(self.creator, self.version, "hide", "Motivo", root.pk)
        moderate(self.creator, self.version, "hide", "Reintento", root.pk)
        self.assertEqual(CommunityDecision.objects.count(), 1)
        root.refresh_from_db()
        self.assertTrue(root.hidden)
        with self.assertRaises(ValidationError):
            root.save()

    def test_html_escaping_and_email_privacy(self):
        root = self.post('<script>alert("x")</script>')
        response = self.client.get(reverse("community-thread", args=[root.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, root.body)
        self.assertNotContains(response, self.student.email)

    def test_csrf_and_get_cannot_mutate(self):
        root = self.post()
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.creator)
        url = reverse("community-decision", args=[self.version.pk])
        self.assertEqual(csrf_client.post(url, {"action": "hide", "post": root.pk, "reason": "Motivo"}).status_code, 403)
        self.assertEqual(self.client.get(url).status_code, 405)
        root.refresh_from_db()
        self.assertFalse(root.hidden)

    def test_rate_limit_and_pagination(self):
        for index in range(30):
            self.post(f"Mensaje {index}")
        with self.assertRaises(ValidationError):
            self.post("Exceso")
        response = self.client.get(reverse("community-space", args=[self.version.pk]))
        self.assertEqual(len(response.context["posts"]), 20)
        self.assertTrue(response.context["posts"].has_next())

    def test_full_form_journey_and_report_queue_privacy(self):
        url = reverse("community-space", args=[self.version.pk])
        response = self.client.post(url, {"body": "Tema de prueba", "request_key": uuid4()})
        self.assertEqual(response.status_code, 302)
        root = CommunityPost.objects.get()
        self.client.post(reverse("community-report", args=[root.pk]), {"reason": "Revisar contenido"})
        queue = reverse("community-moderation", args=[self.version.pk])
        self.assertEqual(self.client.get(queue).status_code, 403)
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(queue), "Revisar contenido")
        self.client.post(reverse("community-decision", args=[self.version.pk]), {"action": "hide", "post": root.pk, "reason": "Ocultado por revisión"})
        self.assertContains(self.client.get(queue), "Ocultado por revisión")

    def test_internal_notifications_unique_on_retries(self):
        root = self.post()
        key = uuid4()
        reply = post_message(self.creator, self.version, "Respuesta", key, root.pk)
        post_message(self.creator, self.version, "Respuesta", key, root.pk)
        report = report_message(self.peer, root.pk, "Revisar")
        report_message(self.peer, root.pk, "Reintento")
        self.assertEqual(Notification.objects.filter(event_key=f"community-reply:{reply.pk}", recipient=self.student).count(), 1)
        self.assertEqual(Notification.objects.filter(event_key=f"community-report:{report.pk}", recipient=self.creator).count(), 1)

    def test_inactive_and_unapproved_accounts_denied(self):
        self.student.is_active = False
        self.student.save()
        with self.assertRaises(PermissionDenied):
            self.post()
        CreatorProfile.objects.filter(user=self.creator).update(status="suspended")
        with self.assertRaises(PermissionDenied):
            moderate(self.creator, self.version, "suspend", "Motivo", student_id=self.peer.pk)

    def test_cross_version_target_and_unenrolled_suspension_denied(self):
        root = self.post()
        later = publish_course(self.course, self.admin)
        with self.assertRaises(ValidationError):
            moderate(self.creator, later, "hide", "Otra versión", root.pk)
        with self.assertRaises(ValidationError):
            moderate(self.creator, self.version, "suspend", "No inscrito", student_id=self.outsider.pk)
        self.assertEqual(CommunityDecision.objects.count(), 0)

    def test_hidden_report_and_malformed_message_rejected(self):
        root = self.post()
        moderate(self.creator, self.version, "hide", "Ocultar", root.pk)
        with self.assertRaises(ValidationError):
            report_message(self.peer, root.pk, "Oculto")
        for body, key in ((" ", uuid4()), ("x" * 2001, uuid4()), ("Hola", "invalid")):
            with self.assertRaises(ValidationError):
                post_message(self.student, self.version, body, key)

    def test_follow_is_idempotent_and_unfollow_stops_peer_notifications(self):
        from .community import follow_thread
        from .models import CommunitySubscription
        root = self.post()
        follow_thread(self.peer, root.pk, True)
        follow_thread(self.peer, root.pk, True)
        self.assertEqual(CommunitySubscription.objects.count(), 1)
        key = uuid4()
        reply = post_message(self.creator, self.version, "Primera respuesta", key, root.pk)
        post_message(self.creator, self.version, "Primera respuesta", key, root.pk)
        self.assertEqual(Notification.objects.filter(recipient=self.peer, event_key=f"community-reply:{reply.pk}:{self.peer.pk}").count(), 1)
        follow_thread(self.peer, root.pk, False)
        follow_thread(self.peer, root.pk, False)
        post_message(self.creator, self.version, "Otra respuesta", uuid4(), root.pk)
        self.assertEqual(Notification.objects.filter(recipient=self.peer).count(), 1)

    def test_follow_does_not_grant_access_or_allow_hidden_threads(self):
        from .community import follow_thread
        root = self.post()
        with self.assertRaises(PermissionDenied):
            follow_thread(self.outsider, root.pk, True)
        moderate(self.creator, self.version, "hide", "Privacidad", root.pk)
        with self.assertRaises(PermissionDenied):
            follow_thread(self.peer, root.pk, True)

    def test_follow_notifications_recheck_current_access_and_exclude_sender(self):
        from .community import follow_thread
        root = self.post()
        follow_thread(self.peer, root.pk, True)
        follow_thread(self.creator, root.pk, True)
        self.peer.is_active = False
        self.peer.save()
        post_message(self.creator, self.version, "Una respuesta", uuid4(), root.pk)
        self.assertFalse(Notification.objects.filter(recipient=self.peer).exists())
        self.assertFalse(Notification.objects.filter(recipient=self.creator).exists())
        self.assertEqual(Notification.objects.filter(recipient=self.student).count(), 1)

    def test_follow_endpoint_is_post_only_csrf_protected_and_validated(self):
        root = self.post()
        url = reverse("community-subscription", args=[root.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {"following": "wrong"}).status_code, 400)
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.student)
        self.assertEqual(secure.post(url, {"following": "yes"}).status_code, 403)
        self.assertEqual(self.client.post(url, {"following": "yes"}).status_code, 302)

    def test_search_filters_counts_and_order_do_not_expose_hidden_activity(self):
        root = self.post("Micropagos educativos")
        later = self.post("Otra conversación")
        reply = post_message(self.peer, self.version, "Texto secreto", uuid4(), root.pk)
        moderate(self.creator, self.version, "hide", "Ocultar respuesta", reply.pk)
        url = reverse("community-space", args=[self.version.pk])
        response = self.client.get(url, {"q": "Micropagos", "estado": "sin-respuesta"})
        self.assertEqual([p.pk for p in response.context["posts"]], [root.pk])
        self.assertEqual(response.context["posts"][0].reply_count, 0)
        self.assertEqual(response.context["posts"][0].last_activity, root.created_at)
        self.assertNotContains(response, "Texto secreto")
        self.assertEqual(len(self.client.get(url, {"q": "Texto secreto"}).context["posts"]), 0)
        moderate(self.creator, self.version, "show", "Restablecer", reply.pk)
        self.assertEqual([p.pk for p in self.client.get(url, {"q": "Texto secreto"}).context["posts"]], [root.pk])
        response = self.client.get(url)
        self.assertEqual([p.pk for p in response.context["posts"]], [root.pk, later.pk])
        self.assertEqual(response.context["posts"][0].reply_count, 1)
        self.assertEqual([p.pk for p in self.client.get(url, {"orden": "recientes"}).context["posts"]], [later.pk, root.pk])
        self.assertEqual([p.pk for p in self.client.get(url, {"estado": "sin-respuesta"}).context["posts"]], [later.pk])

    def test_hidden_roots_and_other_versions_never_appear_in_search(self):
        root = self.post("Reservado")
        moderate(self.creator, self.version, "hide", "Ocultar", root.pk)
        later = publish_course(self.course, self.admin)
        post_message(self.creator, later, "Reservado nuevo", uuid4())
        response = self.client.get(reverse("community-space", args=[self.version.pk]), {"q": "Reservado"})
        self.assertEqual(len(response.context["posts"]), 0)

    def test_community_uses_alias_and_links_only_shared_profiles(self):
        self.student.display_name = "Aprendiz"
        self.student.save()
        root = self.post()
        url = reverse("community-thread", args=[root.pk])
        response = self.client.get(url)
        self.assertContains(response, "Aprendiz")
        self.assertNotContains(response, self.student.email)
        self.assertNotContains(response, self.student.first_name)
        self.assertNotContains(response, reverse("member-profile", args=[self.student.pk]))
        self.student.profile_public = True
        self.student.save()
        self.assertContains(self.client.get(url), reverse("member-profile", args=[self.student.pk]))

    def test_followed_filter_counts_distinct_replies(self):
        from .community import follow_thread
        root = self.post()
        follow_thread(self.peer, root.pk, True)
        follow_thread(self.creator, root.pk, True)
        post_message(self.creator, self.version, "Respuesta", uuid4(), root.pk)
        response = self.client.get(reverse("community-space", args=[self.version.pk]), {"estado": "seguidas"})
        self.assertEqual(len(response.context["posts"]), 1)
        self.assertEqual(response.context["posts"][0].reply_count, 1)
        self.client.force_login(self.peer)
        self.assertContains(self.client.get(reverse("community-thread", args=[root.pk])), "Dejar de seguir")
