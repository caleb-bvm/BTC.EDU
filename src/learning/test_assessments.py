from copy import deepcopy
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from creators.models import CreatorProfile
from creators.services import decide, submit

from .assessment_services import grant_attempt, save_attempt, start_attempt
from .models import (
    ExtraQuizAttempt,
    LessonProgress,
    QuizAttempt,
    QuizDraft,
    VersionQuiz,
)
from .quizzes import validate_questions
from .services import enroll, save_progress

QUESTIONS = [
    {"prompt": "¿Quién confirma el pago?", "multiple": False, "options": ["El servidor", "El navegador"], "correct": [0], "explanation": "CLAVE_PRIVADA_UNICA: el servidor consulta el proveedor."},
    {"prompt": "¿Qué se conserva?", "multiple": True, "options": ["Precio", "Versión", "La contraseña pública"], "correct": [0, 1], "explanation": "EXPLICACION_RESERVADA: precio y versión permanecen."},
]


@override_settings(SECURE_SSL_REDIRECT=False)
class AssessmentTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("creator@quiz.invalid", account_type="creator")
        self.reviewer = users.create_superuser("review@quiz.invalid")
        self.student = users.create_user("student@quiz.invalid")
        self.other = users.create_user("other@quiz.invalid")
        CreatorProfile.objects.create(user=self.creator, display_name="Docente", status="approved")
        self.course = Course.objects.create(creator=self.creator, title="Evaluaciones", description="Curso de prueba")
        self.chapter = Chapter.objects.create(course=self.course, title="Inicio", status="published")
        self.lesson = Lesson.objects.create(chapter=self.chapter, title="Verificar", body="Contenido gratuito", status="published")
        self.draft = QuizDraft.objects.create(lesson=self.lesson, title="Prueba", questions=deepcopy(QUESTIONS), max_attempts=2)
        self.version = publish_course(self.course, self.reviewer)
        self.record = self.version.chapters.first().lessons.first()
        self.quiz = self.record.quiz
        self.enrollment = enroll(self.student, self.version)
        self.client.force_login(self.student)

    def start(self):
        return start_attempt(self.student, self.enrollment.pk, self.quiz.pk)

    def finish(self, answers=None, attempt=None):
        attempt = attempt or self.start()
        return save_attempt(self.student, attempt.pk, answers or {"0": [0], "1": [0, 1]}, attempt.revision, submit=True)

    def editor_payload(self, **changes):
        data = {"enabled": "on", "title": "Nueva evaluación", "pass_mark": "70", "max_attempts": "2", "wait_minutes": "0", "required": "on", "feedback": "passed", "revision": "0", "questions-TOTAL_FORMS": "2", "questions-INITIAL_FORMS": "2"}
        for index, question in enumerate(QUESTIONS):
            prefix = f"questions-{index}-"
            data.update({prefix + "prompt": question["prompt"], prefix + "options": "\n".join(question["options"]), prefix + "correct": ",".join(str(value + 1) for value in question["correct"]), prefix + "explanation": question["explanation"]})
            if question["multiple"]:
                data[prefix + "multiple"] = "on"
        data.update(changes)
        return data

    def test_publication_freezes_quiz_and_reviewer_sees_exact_answers(self):
        submission = submit(self.course, self.creator)
        self.draft.questions = [{**QUESTIONS[0], "correct": [1]}]
        self.draft.pass_mark = 90
        self.draft.save()
        self.client.force_login(self.reviewer)
        review = self.client.get(reverse("creator-review", args=[submission.pk]))
        self.assertContains(review, "CLAVE_PRIVADA_UNICA")
        self.assertContains(review, "Nota mínima 70")
        decide(submission, self.reviewer, True)
        self.assertEqual(submission.course_version.chapters.first().lessons.first().quiz.questions, QUESTIONS)
        new = publish_course(self.course, self.reviewer)
        self.assertEqual(new.chapters.first().lessons.first().quiz.pass_mark, 90)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.questions, QUESTIONS)
        self.assertEqual(self.quiz.pass_mark, 70)

    def test_frozen_quiz_cannot_be_mutated_or_added_after_sealing(self):
        self.quiz.title = "Cambio"
        with self.assertRaises(ValidationError):
            self.quiz.save()
        with self.assertRaises(ValidationError):
            VersionQuiz.objects.filter(pk=self.quiz.pk).update(pass_mark=0)
        with self.assertRaises(ValidationError):
            self.quiz.delete()
        with self.assertRaises(ValidationError):
            VersionQuiz(lesson=self.record, title="Otra", questions=QUESTIONS).full_clean()

    def test_malformed_answer_keys_rejected_before_publication(self):
        bad_cases = [[], [{**QUESTIONS[0], "correct": [3]}], [{**QUESTIONS[0], "correct": [0, 1]}], [{**QUESTIONS[0], "multiple": "true"}], [{**QUESTIONS[0], "options": ["igual", "igual"]}]]
        for questions in bad_cases:
            with self.subTest(questions=questions), self.assertRaises(ValidationError):
                validate_questions(questions)
        self.draft.questions = []
        self.draft.save()
        count = self.course.versions.count()
        with self.assertRaises(ValidationError):
            publish_course(self.course, self.reviewer)
        self.assertEqual(self.course.versions.count(), count)

    def test_start_is_idempotent_and_open_attempt_resumes_without_consuming_more(self):
        first, second = self.start(), self.start()
        self.assertEqual(first.pk, second.pk)
        saved = save_attempt(self.student, first.pk, {"0": [0]}, 0)
        self.assertIsNone(saved.submitted_at)
        self.client.logout()
        self.client.force_login(self.student)
        response = self.client.get(reverse("quiz-attempt", args=[first.pk]))
        self.assertEqual(response.context["form"]["question_0"].value(), "0")
        self.assertEqual(QuizAttempt.objects.count(), 1)

    def test_multiple_choice_is_exact_and_submission_ignores_client_score(self):
        attempt = self.start()
        response = self.client.post(reverse("quiz-attempt", args=[attempt.pk]), {"revision": 0, "question_0": "0", "question_1": ["0"], "score": 100, "passed": "true", "action": "submit"})
        self.assertEqual(response.status_code, 302)
        attempt.refresh_from_db()
        self.assertEqual(attempt.correct_count, 1)
        self.assertEqual(attempt.score, 50)
        self.assertFalse(attempt.passed)
        self.assertEqual(self.finish().score, 100)

    def test_grade_rounding_cannot_turn_failure_into_pass(self):
        self.draft.questions = [deepcopy(QUESTIONS[0]) for _ in range(6)]
        self.draft.pass_mark = 84
        self.draft.save()
        version = publish_course(self.course, self.reviewer)
        quiz = version.chapters.first().lessons.first().quiz
        enrollment = enroll(self.student, version)
        attempt = start_attempt(self.student, enrollment.pk, quiz.pk)
        result = save_attempt(self.student, attempt.pk, {str(i): [0] if i < 5 else [1] for i in range(6)}, 0, submit=True)
        self.assertEqual(str(result.score), "83.33")
        self.assertFalse(result.passed)

    def test_missing_invalid_duplicate_and_unknown_answers_do_not_close_attempt(self):
        attempt = self.start()
        for answers in ({"0": [0]}, {"0": [2], "1": [0, 1]}, {"0": [0, 0], "1": [0]}, {"0": [True], "1": [0]}, {"0": [0], "1": [0], "999": [0]}, {"0": [0, 1], "1": [0]}):
            with self.subTest(answers=answers), self.assertRaises(ValidationError):
                save_attempt(self.student, attempt.pk, answers, 0, submit=True)
        attempt.refresh_from_db()
        self.assertIsNone(attempt.submitted_at)
        self.assertEqual(attempt.revision, 0)

    def test_stale_answers_do_not_overwrite_and_repeated_submission_preserves_result(self):
        attempt = self.start()
        saved = save_attempt(self.student, attempt.pk, {"0": [0]}, 0)
        with self.assertRaises(ValidationError):
            save_attempt(self.student, attempt.pk, {"0": [1]}, 0)
        result = self.finish(attempt=saved)
        retried = save_attempt(self.student, attempt.pk, {"0": [1], "1": [2]}, 0, submit=True)
        self.assertEqual(retried.answers, result.answers)
        self.assertEqual(retried.score, 100)
        with self.assertRaises(ValidationError):
            save_attempt(self.student, attempt.pk, {}, result.revision)

    def test_wait_limit_and_recorded_extra_attempt(self):
        self.draft.wait_minutes = 60
        self.draft.max_attempts = 1
        self.draft.save()
        version = publish_course(self.course, self.reviewer)
        quiz = version.chapters.first().lessons.first().quiz
        enrollment = enroll(self.student, version)
        attempt = start_attempt(self.student, enrollment.pk, quiz.pk)
        save_attempt(self.student, attempt.pk, {"0": [1], "1": [2]}, 0, submit=True)
        with self.assertRaises(ValidationError):
            start_attempt(self.student, enrollment.pk, quiz.pk)
        with self.assertRaises(ValidationError):
            grant_attempt(self.creator, enrollment.pk, quiz.pk, 1, " ")
        grant = grant_attempt(self.creator, enrollment.pk, quiz.pk, 1, "La conexión interrumpió el ejercicio")
        self.assertEqual(grant_attempt(self.creator, enrollment.pk, quiz.pk, 1, "Solicitud repetida").pk, grant.pk)
        self.assertEqual(ExtraQuizAttempt.objects.count(), 1)
        with self.assertRaises(ValidationError):
            start_attempt(self.student, enrollment.pk, quiz.pk)
        QuizAttempt.objects.filter(pk=attempt.pk).update(submitted_at=timezone.now() - timedelta(minutes=61))
        self.assertEqual(start_attempt(self.student, enrollment.pk, quiz.pk).number, 2)

    def test_required_quiz_blocks_completion_but_not_reading_or_position(self):
        save_progress(self.student, self.enrollment.pk, self.record.pk, 0, "position")
        with self.assertRaises(ValidationError):
            save_progress(self.student, self.enrollment.pk, self.record.pk, 1, "complete")
        self.assertFalse(LessonProgress.objects.exists())
        self.finish()
        save_progress(self.student, self.enrollment.pk, self.record.pk, 1, "complete")
        self.assertTrue(LessonProgress.objects.exists())
        # A later failure does not revoke an earlier approval.
        self.finish({"0": [1], "1": [2]})
        save_progress(self.student, self.enrollment.pk, self.record.pk, 2, "complete")
        self.assertEqual(LessonProgress.objects.count(), 1)

    def test_optional_quiz_does_not_block_completion_and_disabling_only_affects_new_version(self):
        self.draft.required = False
        self.draft.save()
        version = publish_course(self.course, self.reviewer)
        enrollment = enroll(self.student, version)
        record = version.chapters.first().lessons.first()
        save_progress(self.student, enrollment.pk, record.pk, 0, "complete")
        self.draft.enabled = False
        self.draft.save()
        newest = publish_course(self.course, self.reviewer)
        self.assertFalse(VersionQuiz.objects.filter(lesson__chapter__version=newest).exists())
        self.assertTrue(VersionQuiz.objects.filter(pk=self.quiz.pk).exists())

    def test_answer_keys_do_not_leak_before_submission_or_when_feedback_requires_pass(self):
        self.client.get(reverse("quiz-detail", args=[self.quiz.pk]))
        attempt = self.start()
        url = reverse("quiz-attempt", args=[attempt.pk])
        self.assertNotContains(self.client.get(url), "CLAVE_PRIVADA_UNICA")
        self.assertContains(self.client.get(url), "¿Quién confirma el pago?")
        self.draft.feedback = "passed"
        self.draft.save()
        version = publish_course(self.course, self.reviewer)
        quiz = version.chapters.first().lessons.first().quiz
        enrollment = enroll(self.student, version)
        hidden = start_attempt(self.student, enrollment.pk, quiz.pk)
        save_attempt(self.student, hidden.pk, {"0": [1], "1": [2]}, 0, submit=True)
        response = self.client.get(reverse("quiz-attempt", args=[hidden.pk]))
        self.assertNotContains(response, "CLAVE_PRIVADA_UNICA")
        self.assertNotContains(response, "EXPLICACION_RESERVADA")
        success = start_attempt(self.student, enrollment.pk, quiz.pk)
        save_attempt(self.student, success.pk, {"0": [0], "1": [0, 1]}, 0, submit=True)
        self.assertContains(self.client.get(reverse("quiz-attempt", args=[success.pk])), "CLAVE_PRIVADA_UNICA")

    def test_permissions_require_student_enrollment_and_lesson_access(self):
        attempt = self.start()
        with self.assertRaises(PermissionDenied):
            start_attempt(self.other, self.enrollment.pk, self.quiz.pk)
        with self.assertRaises(PermissionDenied):
            save_attempt(self.other, attempt.pk, {}, 0)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("quiz-attempt", args=[attempt.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("quiz-detail", args=[self.quiz.pk])).status_code, 404)
        with self.assertRaises(PermissionDenied):
            start_attempt(self.creator, self.enrollment.pk, self.quiz.pk)
        self.lesson.access_type = "paid"
        self.lesson.save()
        version = publish_course(self.course, self.reviewer)
        enrollment = enroll(self.student, version)
        quiz = version.chapters.first().lessons.first().quiz
        with self.assertRaises(PermissionDenied):
            start_attempt(self.student, enrollment.pk, quiz.pk)

    def test_historical_attempts_survive_update_and_archiving(self):
        attempt = self.finish()
        self.draft.pass_mark = 100
        self.draft.questions = [deepcopy(QUESTIONS[1])]
        self.draft.save()
        new = publish_course(self.course, self.reviewer)
        Course.objects.filter(pk=self.course.pk).update(status="archived")
        response = self.client.get(reverse("quiz-attempt", args=[attempt.pk]))
        self.assertContains(response, "Evaluación aprobada")
        self.assertContains(response, "CLAVE_PRIVADA_UNICA")
        other_quiz = new.chapters.first().lessons.first().quiz
        with self.assertRaises(PermissionDenied):
            start_attempt(self.student, self.enrollment.pk, other_quiz.pk)

    def test_editor_saves_draft_without_mutating_published_quiz_and_detects_stale_form(self):
        self.client.force_login(self.creator)
        url = reverse("creator-quiz", args=[self.lesson.pk])
        self.assertEqual(self.client.post(url, self.editor_payload()).status_code, 302)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.feedback, "passed")
        self.assertEqual(self.draft.revision, 1)
        self.assertEqual(self.quiz.feedback, "submitted")
        stale = self.client.post(url, self.editor_payload(title="No sobrescribir"))
        self.assertContains(stale, "borrador más reciente")
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.title, "Nueva evaluación")

    def test_editor_validation_and_question_limits_preserve_existing_draft(self):
        self.client.force_login(self.creator)
        url = reverse("creator-quiz", args=[self.lesson.pk])
        for changes in ({"questions-0-correct": "99"}, {"questions-TOTAL_FORMS": "999"}, {"pass_mark": "101"}, {"max_attempts": "0"}, {"questions-0-options": "Igual\nIgual"}, {"questions-0-DELETE": "on", "questions-1-DELETE": "on"}):
            with self.subTest(changes=changes):
                response = self.client.post(url, self.editor_payload(**changes))
                self.assertEqual(response.status_code, 200)
                self.draft.refresh_from_db()
                self.assertEqual(self.draft.revision, 0)
                self.assertEqual(self.draft.questions, QUESTIONS)

    def test_creator_editor_and_results_are_private_and_grants_are_audited(self):
        attempt = self.finish({"0": [1], "1": [2]})
        self.finish({"0": [1], "1": [2]})
        self.client.force_login(self.creator)
        results = self.client.get(reverse("creator-quiz-results", args=[self.course.pk]))
        self.assertContains(results, "student@quiz.invalid")
        response = self.client.post(reverse("creator-quiz-grant", args=[attempt.pk]), {"allowance": 2, "reason": "Revisión acordada con el alumno"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExtraQuizAttempt.objects.get().granted_by, self.creator)
        other_creator = get_user_model().objects.create_user("another@quiz.invalid", account_type="creator")
        CreatorProfile.objects.create(user=other_creator, display_name="Otro", status="approved")
        self.client.force_login(other_creator)
        self.assertEqual(self.client.get(reverse("creator-quiz", args=[self.lesson.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("creator-quiz-results", args=[self.course.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("creator-quiz-grant", args=[attempt.pk]), {"allowance": 3, "reason": "Ajeno"}).status_code, 404)

    def test_post_requires_csrf_and_get_never_starts_an_attempt(self):
        self.assertEqual(self.client.get(reverse("quiz-start", args=[self.quiz.pk])).status_code, 405)
        self.assertFalse(QuizAttempt.objects.exists())
        guarded = Client(enforce_csrf_checks=True)
        guarded.force_login(self.student)
        self.assertEqual(guarded.post(reverse("quiz-start", args=[self.quiz.pk])).status_code, 403)
        attempt = self.start()
        self.assertEqual(guarded.post(reverse("quiz-attempt", args=[attempt.pk]), {"revision": 0, "action": "submit"}).status_code, 403)
        self.student.is_active = False
        self.student.save()
        with self.assertRaises(PermissionDenied):
            save_attempt(self.student, attempt.pk, {}, 0)

    def test_attempt_view_rejects_invalid_action_and_keeps_answers_on_incomplete_submission(self):
        attempt = self.start()
        url = reverse("quiz-attempt", args=[attempt.pk])
        self.assertEqual(self.client.post(url, {"revision": 0, "action": "invented"}).status_code, 400)
        response = self.client.post(url, {"revision": 0, "action": "submit", "question_0": "0"})
        self.assertContains(response, "Responde todas", status_code=409)
        self.assertEqual(response.context["form"]["question_0"].value(), "0")
        attempt.refresh_from_db()
        self.assertIsNone(attempt.submitted_at)
