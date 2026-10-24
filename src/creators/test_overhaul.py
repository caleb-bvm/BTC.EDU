import tempfile
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from content.models import Chapter, Course, Lesson, Material
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from core.models import ActivityEvent
from learning.assessment_services import save_attempt, start_attempt
from learning.models import (
    CertificateDraft,
    Enrollment,
    ExtraQuizAttempt,
    LessonProgress,
    QuizAttempt,
    QuizDraft,
)
from learning.services import enroll
from learning.support import post_question, reply_question
from media.models import Asset

from .models import CreatorProfile
from .services import decide, submit


@override_settings(SECURE_SSL_REDIRECT=False)
class CreatorOverhaulTests(TestCase):
    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        users = get_user_model().objects
        self.creator = users.create_user("teacher@overhaul.invalid", account_type="creator")
        self.other = users.create_user("other@overhaul.invalid", account_type="creator")
        self.student = users.create_user("student@overhaul.invalid")
        self.reviewer = users.create_superuser("reviewer@overhaul.invalid")
        for creator in (self.creator, self.other):
            CreatorProfile.objects.create(user=creator, display_name="Educador", status="approved")
        self.course = Course.objects.create(creator=self.creator, title="Curso de práctica", description="Descripción")
        self.chapter = Chapter.objects.create(course=self.course, title="Primer capítulo", status="published")
        self.lesson = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=self.chapter, title="Lección gratuita", body="CONTENIDO_GRATUITO", status="published")
        self.second = Lesson.objects.create(**EDUCATION_FIXTURE, chapter=self.chapter, title="Lección con precio", body="CONTENIDO_PAGADO", status="published", access_type="paid", position=2)
        self.quiz = QuizDraft.objects.create(lesson=self.lesson, title="Comprobar práctica", questions=[{"prompt": "Elige A", "multiple": False, "options": ["A", "B"], "correct": [0], "explanation": "EXPLICACION_CORRECTA"}])
        self.policy = CertificateDraft.objects.create(course=self.course, enabled=True)
        self.policy.required_lessons.add(self.lesson)
        self.client.force_login(self.creator)

    def publication(self):
        version = publish_course(self.course, self.reviewer)
        return version, version.chapters.first().lessons.get(source_lesson_id=self.lesson.pk)

    def test_latest_question_message_drives_dashboard_and_filtered_inbox(self):
        version, lesson = self.publication()
        enroll(self.student, version)
        question = post_question(self.student, lesson.pk, "Una duda", uuid4())
        reply_question(self.creator, question.pk, "Respuesta", uuid4())
        self.assertEqual(self.client.get(reverse("creator-dashboard")).context["unanswered_count"], 0)
        reply_question(self.student, question.pk, "Una aclaración más", uuid4())
        dashboard = self.client.get(reverse("creator-dashboard"))
        inbox = self.client.get(reverse("creator-questions"), {"estado": "pending", "curso": self.course.pk})
        self.assertEqual(dashboard.context["unanswered_count"], 1)
        self.assertEqual(inbox.context["questions"].paginator.count, 1)
        self.assertEqual(inbox.context["questions"][0].pk, question.pk)
        self.assertEqual(self.client.get(reverse("creator-questions"), {"estado": "replied"}).context["questions"].paginator.count, 0)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("creator-dashboard")).context["unanswered_count"], 0)
        self.assertEqual(self.client.get(reverse("creator-questions"), {"curso": self.course.pk}).context["questions"].paginator.count, 0)

    def test_content_distinguishes_publication_from_changed_draft_and_current_review(self):
        version, _ = self.publication()
        published = self.client.get(reverse("creator-content"), {"estado": "published"})
        self.assertEqual(published.context["cards"].paginator.count, 1)
        self.assertFalse(published.context["cards"][0]["changed"])
        self.lesson.body = "BORRADOR_NUEVO"
        self.lesson.save()
        draft = self.client.get(reverse("creator-content"), {"estado": "draft"})
        self.assertEqual(draft.context["cards"].paginator.count, 1)
        self.assertEqual(draft.context["cards"][0]["snapshot"].pk, version.pk)
        submission = submit(self.course, self.creator)
        self.assertEqual(self.client.get(reverse("creator-content"), {"estado": "review"}).context["cards"].paginator.count, 1)
        decide(submission, self.reviewer, False, "Revisar ejemplo")
        self.assertEqual(self.client.get(reverse("creator-dashboard")).context["changes_count"], 1)
        replacement = submit(self.course, self.creator)
        self.assertEqual(self.client.get(reverse("creator-dashboard")).context["changes_count"], 0)
        self.assertEqual(replacement.status, "pending")
        self.course.refresh_from_db()
        self.assertEqual(self.course.current_version_id, version.pk)
        self.assertEqual(version.chapters.first().lessons.get(source_lesson_id=self.lesson.pk).content.body, "CONTENIDO_GRATUITO")

    def test_quiz_and_certificate_draft_changes_appear_in_content_state(self):
        self.publication()
        self.quiz.pass_mark = 80
        self.quiz.save()
        cards = self.client.get(reverse("creator-content"), {"estado": "draft"}).context["cards"]
        self.assertEqual(cards.paginator.count, 1)
        self.quiz.pass_mark = 70
        self.quiz.save()
        self.policy.required_lessons.add(self.second)
        self.assertEqual(self.client.get(reverse("creator-content"), {"estado": "draft"}).context["cards"].paginator.count, 1)

    def test_publication_requirements_link_to_actual_blocked_lesson(self):
        self.lesson.body = ""
        self.lesson.save()
        response = self.client.get(reverse("creator-course", args=[self.course.pk]), {"seccion": "publicacion"})
        self.assertFalse(response.context["ready_to_send"])
        missing = [check for check in response.context["requirements"] if not check["ready"]]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["url"], reverse("creator-lesson", args=[self.chapter.pk, self.lesson.pk]))
        self.assertContains(response, "Completar lección")
        self.assertNotContains(response, 'id="id_body"')

    def test_reorder_uses_buttons_and_preserves_published_lesson_order(self):
        version, frozen = self.publication()
        url = reverse("creator-reorder", args=["lecciones", self.second.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {"direction": "up"}).status_code, 302)
        self.lesson.refresh_from_db()
        self.second.refresh_from_db()
        self.assertEqual((self.lesson.position, self.second.position), (2, 1))
        self.assertEqual(frozen.position, 1)
        self.assertEqual(version.chapters.first().lessons.first().source_lesson_id, self.lesson.pk)
        self.assertEqual(self.client.post(url, {"direction": "invalid"}).status_code, 400)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url, {"direction": "down"}).status_code, 404)

    def test_resource_upload_is_contextual_owned_and_validated(self):
        back = reverse("creator-lesson", args=[self.chapter.pk, self.lesson.pk])
        response = self.client.post(reverse("creator-resource-new", args=["materiales"]), {**EDUCATION_FIXTURE, "title": "Guía de estudio", "description": "Material", "access_type": "free", "new_file": SimpleUploadedFile("guia.txt", b"Guia privada", content_type="text/plain"), "volver": back})
        self.assertEqual(response.status_code, 302)
        item = Material.objects.get(title="Guía de estudio")
        self.assertEqual(item.pending_asset.creator_id, self.creator.pk)
        self.assertIsNone(item.revision_id)
        editor = self.client.get(response.url)
        self.assertContains(editor, back)
        self.assertTrue(editor.context["ready_to_send"])
        invalid = self.client.post(reverse("creator-resource-new", args=["videos"]), {**EDUCATION_FIXTURE, "title": "Video", "access_type": "free", "new_file": SimpleUploadedFile("guia.txt", b"No es un video", content_type="text/plain")})
        self.assertContains(invalid, "El formato del archivo no corresponde")
        self.assertEqual(Asset.objects.count(), 1)

    def test_file_library_return_rejects_external_destination(self):
        response = self.client.post(reverse("creator-files") + "?volver=https%3A%2F%2Fexample.invalid", {"file": SimpleUploadedFile("a.txt", b"Notas", content_type="text/plain")})
        self.assertRedirects(response, reverse("creator-files"))
        back = reverse("creator-lesson", args=[self.chapter.pk, self.lesson.pk])
        response = self.client.post(reverse("creator-files"), {"file": SimpleUploadedFile("b.txt", b"Otras notas", content_type="text/plain"), "volver": back})
        self.assertRedirects(response, back)

    def test_student_draft_preview_checks_access_without_learning_or_telemetry(self):
        included = self.client.get(reverse("creator-course-preview", args=[self.course.pk]))
        self.assertContains(included, "CONTENIDO_PAGADO")
        blocked = self.client.get(reverse("creator-course-preview", args=[self.course.pk]), {"acceso": "sin-compra"})
        self.assertNotContains(blocked, "CONTENIDO_PAGADO")
        self.assertContains(blocked, "CONTENIDO_GRATUITO")
        self.assertContains(included, reverse("creator-quiz-preview", args=[self.lesson.pk]))
        self.assertFalse(Enrollment.objects.exists())
        self.assertFalse(LessonProgress.objects.exists())
        self.assertFalse(QuizAttempt.objects.exists())
        self.assertFalse(ActivityEvent.objects.exists())

    def test_quiz_preview_uses_feedback_rule_and_never_creates_attempt(self):
        self.quiz.feedback = "passed"
        self.quiz.save()
        url = reverse("creator-quiz-preview", args=[self.lesson.pk])
        failed = self.client.post(url, {"question_0": "1", "revision": 0})
        self.assertEqual(failed.context["score"], 0)
        self.assertNotContains(failed, "EXPLICACION_CORRECTA")
        passed = self.client.post(url, {"question_0": "0", "revision": 0})
        self.assertEqual(passed.context["score"], 100)
        self.assertContains(passed, "EXPLICACION_CORRECTA")
        self.assertFalse(QuizAttempt.objects.exists())
        self.assertFalse(Enrollment.objects.exists())
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_results_scope_and_filters_preserve_private_students(self):
        version, lesson = self.publication()
        enrollment = enroll(self.student, version)
        first = start_attempt(self.student, enrollment.pk, lesson.quiz.pk)
        save_attempt(self.student, first.pk, {"0": [0]}, 0, submit=True)
        passed = self.client.get(reverse("creator-results"), {"estado": "passed"})
        self.assertEqual(passed.context["attempts"].paginator.count, 1)
        failed = self.client.get(reverse("creator-quiz-results", args=[self.course.pk]), {"estado": "failed", "version": version.number})
        self.assertEqual(failed.context["attempts"].paginator.count, 0)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("creator-results")).context["attempts"].paginator.count, 0)
        self.assertEqual(self.client.get(reverse("creator-quiz-results", args=[self.course.pk])).status_code, 404)

    def test_ajax_grant_errors_preserve_attempts_and_valid_retry_is_idempotent(self):
        version, lesson = self.publication()
        enrollment = enroll(self.student, version)
        attempt = start_attempt(self.student, enrollment.pk, lesson.quiz.pk)
        url = reverse("creator-quiz-grant", args=[attempt.pk])
        ajax = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        for data, error in (
            ({"allowance": lesson.quiz.max_attempts, "reason": " "}, "Indica un motivo"),
            ({"allowance": "inválido", "reason": "Revisar la práctica"}, "La solicitud no es válida"),
            ({"allowance": lesson.quiz.max_attempts, "reason": "Revisar la práctica"}, "agotado los disponibles"),
        ):
            response = self.client.post(url, data, **ajax)
            self.assertEqual(response.status_code, 400)
            self.assertIn(error, " ".join(response.json()["errors"]))
            self.assertNotIn("redirect", response.json())
            self.assertFalse(ExtraQuizAttempt.objects.exists())
            self.assertEqual(QuizAttempt.objects.count(), 1)
            enrollment.refresh_from_db()
            self.assertEqual(enrollment.revision, 0)
            self.assertEqual(enrollment.version_id, version.pk)
            self.assertFalse(LessonProgress.objects.exists())
        save_attempt(self.student, attempt.pk, {"0": [1]}, 0, submit=True)
        for _ in range(lesson.quiz.max_attempts - 1):
            current = start_attempt(self.student, enrollment.pk, lesson.quiz.pk)
            save_attempt(self.student, current.pk, {"0": [1]}, 0, submit=True)
        data = {"allowance": lesson.quiz.max_attempts, "reason": "Revisar la práctica"}
        for _ in range(2):
            response = self.client.post(url, data, **ajax)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"redirect": reverse("creator-quiz-results", args=[self.course.pk])})
        self.assertEqual(ExtraQuizAttempt.objects.count(), 1)
        self.assertEqual(QuizAttempt.objects.count(), lesson.quiz.max_attempts)
        attempt.refresh_from_db()
        self.assertEqual(attempt.answers, {"0": [1]})
        self.assertFalse(attempt.passed)
        self.assertFalse(LessonProgress.objects.exists())
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url, data, **ajax).status_code, 404)
        self.assertEqual(ExtraQuizAttempt.objects.count(), 1)
