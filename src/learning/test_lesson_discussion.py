from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse

from commerce.models import Entitlement
from content.models import Chapter, Course, Lesson, VersionLesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile

from .community import follow_thread, moderate, post_message, report_message
from .lesson_discussion import lesson_url
from .models import CommunityPost, CommunitySubscription, Notification
from .services import enroll


@override_settings(SECURE_SSL_REDIRECT=False)
class LessonDiscussionTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("creator@lesson.invalid", account_type="creator")
        CreatorProfile.objects.create(user=self.creator, display_name="Ana", status="approved")
        self.admin = users.create_superuser("admin@lesson.invalid")
        self.student = users.create_user("student@lesson.invalid", display_name="Lucía")
        self.peer = users.create_user("peer@lesson.invalid", display_name="Luis")
        self.outsider = users.create_user("outsider@lesson.invalid")
        self.course = Course.objects.create(creator=self.creator, title="Curso de conversaciones")
        chapter = Chapter.objects.create(course=self.course, title="Inicio", status="published")
        for position, access_type in enumerate(("free", "free", "paid"), 1):
            Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, position=position, title=f"Lección {position}", body=f"Contenido {position}", access_type=access_type, status="published")
        self.version = publish_course(self.course, self.admin)
        self.lessons = list(VersionLesson.objects.filter(chapter__version=self.version).select_related("content", "chapter__version__course"))
        self.lesson, self.other, self.paid = self.lessons
        enroll(self.student, self.version)
        enroll(self.peer, self.version)
        self.client.force_login(self.student)
        self.url = lesson_url(self.version, self.lesson.pk)

    def post(self, lesson=None, author=None, body="Duda de esta lección"):
        return post_message(author or self.student, self.version, body, uuid4(), lesson_id=(lesson or self.lesson).pk)

    def test_reader_and_community_share_threads_and_return_link(self):
        root = self.post()
        self.assertContains(self.client.get(self.url), root.body)
        self.assertContains(self.client.get(reverse("community-space", args=[self.version.pk])), "Lección 1")
        self.assertContains(self.client.get(reverse("community-thread", args=[root.pk])), self.url + "#lesson-community")
        general = post_message(self.student, self.version, "Tema general", uuid4())
        other = self.post(self.other, body="Duda de otra lección")
        reader = self.client.get(self.url)
        self.assertNotContains(reader, general.body)
        self.assertNotContains(reader, other.body)

    def test_inline_comment_reply_and_idempotent_retries(self):
        key = uuid4()
        payload = {"body": "Pregunta publicada desde el lector", "request_key": key}
        for _ in range(2):
            response = self.client.post(self.url, payload)
            self.assertEqual(response.status_code, 302)
        root = CommunityPost.objects.get(body=payload["body"])
        self.assertEqual(root.lesson_id, self.lesson.pk)
        self.client.force_login(self.creator)
        response = self.client.post(self.url, {"body": "Explicación del creador", "request_key": uuid4(), "parent": root.pk})
        self.assertContains(self.client.get(response.url), "Explicación del creador")
        self.assertContains(self.client.get(self.url), "Creador")
        reply = root.replies.get()
        self.assertEqual(reply.lesson_id, root.lesson_id)
        self.assertEqual(Notification.objects.filter(recipient=self.creator, event_key=f"community-lesson:{root.pk}").count(), 1)
        self.assertEqual(Notification.objects.filter(recipient=self.student, event_key=f"community-reply:{reply.pk}").count(), 1)

    def test_locked_threads_excluded_from_listing_search_counts_and_direct_actions(self):
        root = self.post(self.paid, self.creator, "SECRETO de pago")
        post_message(self.creator, self.version, "RESPUESTA protegida", uuid4(), root.pk)
        space = reverse("community-space", args=[self.version.pk])
        for params in ({}, {"q": "SECRETO"}, {"q": "RESPUESTA"}, {"estado": "seguidas"}):
            response = self.client.get(space, params)
            self.assertNotContains(response, root.body)
            self.assertEqual(response.context["posts"].paginator.count, 0)
        endpoint = reverse("community-thread", args=[root.pk])
        self.assertEqual(self.client.get(endpoint).status_code, 403)
        self.assertEqual(self.client.post(endpoint, {"body": "Respuesta", "request_key": uuid4()}).status_code, 403)
        self.assertEqual(self.client.post(reverse("community-subscription", args=[root.pk]), {"following": "yes"}).status_code, 403)
        self.assertEqual(self.client.post(reverse("community-report", args=[root.pk]), {"reason": "Reporte"}).status_code, 403)
        for action in (lambda: self.post(self.paid), lambda: follow_thread(self.student, root.pk, True), lambda: report_message(self.student, root.pk, "Reporte")):
            with self.assertRaises(PermissionDenied):
                action()
        locked = self.client.get(lesson_url(self.version, self.paid.pk))
        self.assertNotContains(locked, "Conversación de esta lección", status_code=403)
        self.assertEqual(self.client.post(lesson_url(self.version, self.paid.pk), {"body": "Intento", "request_key": uuid4()}).status_code, 403)

    def test_entitlement_unlocks_only_its_lesson_conversation(self):
        root = self.post(self.paid, self.creator)
        Entitlement.objects.create(buyer=self.student, resource=self.paid.content)
        self.assertContains(self.client.get(lesson_url(self.version, self.paid.pk)), root.body)
        self.assertContains(self.client.get(reverse("community-space", args=[self.version.pk])), root.body)
        reply = post_message(self.student, self.version, "Ya tengo acceso", uuid4(), root.pk)
        self.assertEqual(reply.lesson_id, self.paid.pk)

    def test_notifications_recheck_lesson_access_for_subscribers_and_author(self):
        Entitlement.objects.create(buyer=self.student, resource=self.paid.content)
        root = self.post(self.paid)
        Entitlement.objects.create(buyer=self.peer, resource=self.paid.content)
        follow_thread(self.peer, root.pk, True)
        Entitlement._base_manager.filter(buyer__in=[self.student, self.peer], resource=self.paid.content).delete()
        reply = post_message(self.creator, self.version, "Respuesta después de perder acceso", uuid4(), root.pk)
        self.assertFalse(Notification.objects.filter(event_key__startswith=f"community-reply:{reply.pk}").exists())

    def test_scope_cannot_be_forged_between_lessons_or_versions(self):
        root = self.post()
        response = self.client.post(lesson_url(self.version, self.other.pk), {"body": "Cruzar lecciones", "request_key": uuid4(), "parent": root.pk})
        self.assertContains(response, "Selecciona una conversación de esta lección")
        self.assertFalse(root.replies.exists())
        later = publish_course(self.course, self.admin)
        foreign = VersionLesson.objects.filter(chapter__version=later).first()
        with self.assertRaises(ValidationError):
            post_message(self.student, self.version, "Otra versión", uuid4(), lesson_id=foreign.pk)
        with self.assertRaises(ValidationError):
            CommunityPost.objects.create(version=self.version, lesson=foreign, author=self.student, body="Directo", request_key=uuid4())
        with self.assertRaises(ValidationError):
            CommunityPost.objects.create(version=self.version, lesson=self.other, parent=root, author=self.student, body="Directo", request_key=uuid4())
        with self.assertRaises(ValidationError):
            post_message(self.student, self.version, root.body, root.request_key, lesson_id=self.other.pk)

    def test_anonymous_and_unenrolled_readers_see_invitation_without_messages(self):
        root = self.post(body="Comentario solo para inscritos")
        self.client.logout()
        response = self.client.get(self.url)
        self.assertContains(response, "Entrar para participar")
        self.assertNotContains(response, root.body)
        self.assertEqual(self.client.post(self.url, {"body": "No autorizado", "request_key": uuid4()}).status_code, 403)
        self.client.force_login(self.outsider)
        response = self.client.get(self.url)
        self.assertContains(response, "Inscribirme y participar")
        self.assertNotContains(response, root.body)
        self.assertEqual(self.client.post(self.url, {"body": "No inscrito", "request_key": uuid4()}).status_code, 403)

    def test_hidden_closed_and_suspended_states_preserved_in_reader(self):
        root = self.post()
        reply = post_message(self.peer, self.version, "Respuesta a ocultar", uuid4(), root.pk)
        moderate(self.creator, self.version, "hide", "Revisión", reply.pk)
        self.assertNotContains(self.client.get(self.url), reply.body)
        moderate(self.creator, self.version, "close", "Finalizada", root.pk)
        response = self.client.post(self.url, {"body": "Respuesta tardía", "request_key": uuid4(), "parent": root.pk})
        self.assertContains(response, "Esta conversación no admite respuestas")
        moderate(self.creator, self.version, "hide", "Revisión", root.pk)
        self.assertNotContains(self.client.get(self.url), root.body)
        moderate(self.creator, self.version, "suspend", "Conducta", student_id=self.student.pk)
        self.assertContains(self.client.get(self.url), "Tu escritura está suspendida")
        self.assertEqual(self.client.post(self.url, {"body": "No", "request_key": uuid4()}).status_code, 403)

    def test_inline_follow_report_return_to_same_lesson_and_ignore_external_redirect(self):
        root = self.post(author=self.peer)
        response = self.client.post(reverse("community-subscription", args=[root.pk]), {"following": "yes", "lesson_return": self.lesson.pk, "next": "https://evil.invalid"})
        self.assertIn(self.url, response.url)
        self.assertTrue(CommunitySubscription.objects.filter(thread=root, user=self.student).exists())
        response = self.client.post(reverse("community-report", args=[root.pk]), {"reason": "Revisar", "lesson_return": self.lesson.pk})
        self.assertIn(self.url, response.url)
        response = self.client.post(reverse("community-subscription", args=[root.pk]), {"following": "no", "lesson_return": self.other.pk})
        self.assertEqual(response.url, reverse("community-thread", args=[root.pk]))

    def test_forms_csrf_validation_escaping_and_unique_ids(self):
        root = self.post(body='<script>alert("x")</script>')
        self.post(body="Segunda conversación")
        response = self.client.get(self.url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, root.body)
        self.assertNotContains(response, self.student.email)
        from html.parser import HTMLParser
        class IdParser(HTMLParser):
            ids = None
            def handle_starttag(self, tag, attrs):
                self.ids.extend(value for key, value in attrs if key == "id")
        parser = IdParser()
        parser.ids = []
        parser.feed(response.content.decode())
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.student)
        self.assertEqual(csrf_client.post(self.url, {"body": "Sin CSRF", "request_key": uuid4()}).status_code, 403)
        for payload in ({"body": "Texto conservado", "request_key": "invalid"}, {"body": " ", "request_key": uuid4()}):
            response = self.client.post(self.url, payload)
            self.assertTrue(response.context["discussion_form"].errors)
        self.assertEqual(CommunityPost.objects.count(), 2)

    def test_reader_pagination_and_bounded_replies_preserve_reply_target(self):
        first = self.post(body="La primera conversación")
        for i in range(6):
            self.post(body=f"Comentario {i}")
        for i in range(5):
            post_message(self.peer, self.version, f"Respuesta {i}", uuid4(), first.pk)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context["discussion_posts"]), 5)
        self.assertNotContains(response, first.body)
        response = self.client.get(self.url, {"conversaciones": 2})
        self.assertContains(response, first.body)
        self.assertNotContains(response, "Respuesta 0")
        self.assertContains(response, "Respuesta 4")
        self.assertContains(response, "Ver todas las respuestas")
        response = self.client.post(self.url, {"parent": first.pk, "body": "Respuesta desde página 2", "request_key": uuid4()})
        self.assertIn("conversaciones=2", response.url)
        self.assertContains(self.client.get(response.url), "Respuesta desde página 2")

    def test_historical_versions_keep_separate_conversations(self):
        root = self.post()
        later = publish_course(self.course, self.admin)
        self.assertContains(self.client.get(self.url), root.body)
        enroll(self.student, later)
        newer = VersionLesson.objects.filter(chapter__version=later).first()
        self.assertNotContains(self.client.get(lesson_url(later, newer.pk)), root.body)
        Course.objects.filter(pk=self.course.pk).update(status="archived")
        self.assertContains(self.client.get(self.url), root.body)


class LessonDiscussionMigrationTests(TransactionTestCase):
    def test_existing_general_threads_keep_all_values_after_migration(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        previous = [node for node in latest if node[0] != "learning"] + [("learning", "0007_communitysubscription")]
        try:
            executor.migrate(previous)
            apps = executor.loader.project_state(previous).apps
            user = apps.get_model("accounts", "User").objects.create(email="legacy@discussion.invalid", password="!")
            course = apps.get_model("content", "Course").objects.create(creator_id=user.pk, title="Curso conservado")
            version = apps.get_model("content", "CourseVersion").objects.create(course_id=course.pk, number=1, title="Versión conservada")
            posts = apps.get_model("learning", "CommunityPost")
            root = posts.objects.create(version_id=version.pk, author_id=user.pk, body="Tema general anterior", request_key=uuid4(), closed=True)
            posts.objects.create(version_id=version.pk, author_id=user.pk, body="Respuesta anterior", parent_id=root.pk, request_key=uuid4(), hidden=True)
            before = list(posts.objects.order_by("pk").values())
            MigrationExecutor(connection).migrate(latest)
            self.assertEqual(list(CommunityPost.objects.order_by("pk").values(*before[0].keys())), before)
            self.assertFalse(CommunityPost.objects.filter(lesson__isnull=False).exists())
        finally:
            MigrationExecutor(connection).migrate(latest)
