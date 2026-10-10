from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from creators.models import CreatorProfile
from creators.services import decide, submit

from .assessment_services import save_attempt, start_attempt
from .certificates import completion_status, issue_certificate, revoke_certificate
from .models import (
    Certificate,
    CertificateDraft,
    CertificateRevocation,
    CertificateSharing,
    LessonQuestion,
    Notification,
    QuestionReply,
    QuizDraft,
)
from .services import enroll, save_progress
from .support import post_question, reply_question


@override_settings(SECURE_SSL_REDIRECT=False)
class EssentialTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("creator@essential.invalid", account_type="creator")
        self.admin = users.create_superuser("admin@essential.invalid")
        self.student = users.create_user("student@essential.invalid", first_name="Lucía")
        self.other = users.create_user("other@essential.invalid")
        self.other_creator = users.create_user("another@essential.invalid", account_type="creator")
        CreatorProfile.objects.create(user=self.creator, display_name="Ana López", status="approved")
        CreatorProfile.objects.create(user=self.other_creator, display_name="Otro docente", status="approved")
        self.course = Course.objects.create(creator=self.creator, title="Curso esencial", description="Descripción")
        chapter = Chapter.objects.create(course=self.course, title="Inicio", status="published")
        self.lesson = Lesson.objects.create(chapter=chapter, title="Lección obligatoria", body="Texto", status="published")
        self.optional = Lesson.objects.create(chapter=chapter, title="Lección opcional", body="Texto", status="published", position=2)
        self.policy = CertificateDraft.objects.create(course=self.course, enabled=True)
        self.policy.required_lessons.add(self.lesson)
        self.draft = QuizDraft.objects.create(lesson=self.lesson, title="Evaluación", questions=[{"prompt": "Elige A", "multiple": False, "options": ["A", "B"], "correct": [0], "explanation": "A"}])
        self.version = publish_course(self.course, self.admin)
        self.record = self.version.chapters.first().lessons.get(source_lesson_id=self.lesson.pk)
        self.enrollment = enroll(self.student, self.version)
        self.client.force_login(self.student)

    def complete(self):
        attempt = start_attempt(self.student, self.enrollment.pk, self.record.quiz.pk)
        save_attempt(self.student, attempt.pk, {"0": [0]}, 0, submit=True)
        save_progress(self.student, self.enrollment.pk, self.record.pk, 0, "complete")

    def certificate(self):
        self.complete()
        return issue_certificate(self.student, self.enrollment.pk, "Lucía López")

    def question(self):
        return post_question(self.student, self.record.pk, "¿Cómo se conserva la versión?", uuid4())

    def test_certificate_requires_completion_and_approval_not_only_enrollment(self):
        self.assertFalse(completion_status(self.enrollment)["eligible"])
        with self.assertRaises(ValidationError):
            issue_certificate(self.student, self.enrollment.pk, "Lucía")
        with self.assertRaises(PermissionDenied):
            issue_certificate(self.other, self.enrollment.pk, "Otra persona")
        self.complete()
        self.assertTrue(completion_status(self.enrollment)["eligible"])
        certificate = issue_certificate(self.student, self.enrollment.pk, "Lucía López")
        self.assertEqual(len(certificate.evidence["lessons"]), 1)
        self.assertEqual(certificate.evidence["assessments"][0]["score"], "100.00")

    def test_all_required_quizzes_include_optional_lessons(self):
        QuizDraft.objects.create(lesson=self.optional, title="Obligatoria", questions=self.draft.questions)
        version = publish_course(self.course, self.admin)
        enrollment = enroll(self.student, version)
        required = version.chapters.first().lessons.get(source_lesson_id=self.lesson.pk)
        attempt = start_attempt(self.student, enrollment.pk, required.quiz.pk)
        save_attempt(self.student, attempt.pk, {"0": [0]}, 0, submit=True)
        save_progress(self.student, enrollment.pk, required.pk, 0, "complete")
        self.assertEqual(completion_status(enrollment)["pending_quizzes"], 1)
        with self.assertRaises(ValidationError):
            issue_certificate(self.student, enrollment.pk, "Lucía")

    def test_certificate_retry_and_unmark_preserve_unique_frozen_evidence(self):
        certificate = self.certificate()
        retry = issue_certificate(self.student, self.enrollment.pk, "Otro nombre")
        self.assertEqual(retry.pk, certificate.pk)
        self.assertEqual(Certificate.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(event_key=f"certificate:{certificate.pk}").count(), 1)
        save_progress(self.student, self.enrollment.pk, self.record.pk, 1, "incomplete")
        self.assertFalse(completion_status(self.enrollment)["eligible"])
        self.assertEqual(issue_certificate(self.student, self.enrollment.pk, "Lucía").pk, certificate.pk)
        with self.assertRaises(ValidationError):
            Certificate.objects.filter(pk=certificate.pk).update(student_name="Otro")

    def test_certificate_name_and_course_version_remain_after_edits(self):
        certificate = self.certificate()
        self.policy.required_lessons.add(self.optional)
        self.course.title = "Título nuevo"
        self.course.save()
        new = publish_course(self.course, self.admin)
        self.assertNotEqual(new.certificate_policy.required_lesson_ids, self.version.certificate_policy.required_lesson_ids)
        certificate.refresh_from_db()
        self.assertEqual(certificate.course_title, "Curso esencial")
        self.assertEqual(certificate.enrollment.version_id, self.version.pk)
        self.assertEqual(certificate.student_name, "Lucía López")

    def test_policy_rejects_foreign_or_excluded_requirements(self):
        self.lesson.status = "draft"
        self.lesson.save()
        with self.assertRaises(ValidationError):
            publish_course(self.course, self.admin)
        self.assertEqual(self.course.versions.count(), 1)

    def test_sharing_opt_in_and_public_verification_has_no_private_data(self):
        certificate = self.certificate()
        url = reverse("certificate-verify", args=[certificate.pk])
        anonymous = Client()
        self.assertEqual(anonymous.get(url).status_code, 404)
        share = reverse("certificate-share", args=[certificate.pk])
        self.assertEqual(self.client.get(share).status_code, 405)
        self.assertEqual(self.client.post(share, {"public": "yes"}).status_code, 302)
        public = anonymous.get(url)
        self.assertContains(public, "Lucía López")
        self.assertNotContains(public, self.student.email)
        self.assertNotContains(public, '"score"')
        self.assertEqual(public["X-Robots-Tag"], "noindex, nofollow")
        self.client.post(share, {"public": "no"})
        self.assertEqual(anonymous.get(url).status_code, 404)
        self.client.force_login(self.other)
        for endpoint in ("certificate-detail", "certificate-pdf", "certificate-share"):
            response = self.client.post(reverse(endpoint, args=[certificate.pk]), {"public": "yes"}) if endpoint == "certificate-share" else self.client.get(reverse(endpoint, args=[certificate.pk]))
            self.assertEqual(response.status_code, 404)

    def test_revocation_is_audited_idempotent_and_blocks_pdf(self):
        certificate = self.certificate()
        with self.assertRaises(PermissionDenied):
            revoke_certificate(self.creator, certificate.pk, "No autorizado")
        CertificateSharing.objects.filter(certificate=certificate).update(public=True)
        revoke_certificate(self.admin, certificate.pk, "Nombre incorrecto")
        revoke_certificate(self.admin, certificate.pk, "Otro motivo")
        self.assertEqual(CertificateRevocation.objects.count(), 1)
        self.assertEqual(self.client.get(reverse("certificate-pdf", args=[certificate.pk])).status_code, 404)
        self.assertContains(Client().get(reverse("certificate-verify", args=[certificate.pk])), "revocado")
        self.assertNotContains(Client().get(reverse("certificate-verify", args=[certificate.pk])), "Nombre incorrecto")
        self.assertEqual(Certificate.objects.count(), 1)

    def test_certificate_forms_pdf_and_library_link(self):
        self.complete()
        url = reverse("certificate-request", args=[self.enrollment.pk])
        self.assertContains(self.client.get(url), "Emitir certificado")
        invalid = self.client.post(url, {"student_name": "Lucía"})
        self.assertEqual(invalid.status_code, 200)
        self.assertFalse(Certificate.objects.exists())
        response = self.client.post(url, {"student_name": "Lucía", "confirm_name": "on"})
        self.assertEqual(response.status_code, 302)
        certificate = Certificate.objects.get()
        pdf = self.client.get(reverse("certificate-pdf", args=[certificate.pk]))
        self.assertTrue(pdf.content.startswith(b"%PDF-"))
        self.assertEqual(pdf["Content-Type"], "application/pdf")
        self.assertContains(self.client.get(reverse("workspace")), "Ver certificado")
        self.assertContains(self.client.get(reverse("certificates")), "Curso esencial")

    def test_policy_editor_stale_and_foreign_course_cannot_change_snapshot(self):
        self.client.force_login(self.creator)
        url = reverse("creator-certificate-policy", args=[self.course.pk])
        self.assertEqual(self.client.post(url, {"revision": 0, "enabled": "on", "required_lessons": [self.optional.pk]}).status_code, 302)
        response = self.client.post(url, {"revision": 0, "enabled": "on", "required_lessons": [self.lesson.pk]})
        self.assertContains(response, "borrador más reciente")
        self.assertEqual(self.version.certificate_policy.required_lesson_ids, [self.record.pk])
        self.client.force_login(self.other_creator)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_question_requires_access_and_matching_enrollment(self):
        with self.assertRaises(PermissionDenied):
            post_question(self.other, self.record.pk, "Hola", uuid4())
        question = self.question()
        self.assertEqual(question.enrollment_id, self.enrollment.pk)
        self.assertEqual(Notification.objects.get(event_key=f"question:{question.pk}").recipient_id, self.creator.pk)
        self.assertContains(self.client.get(reverse("version-lesson", args=[self.course.pk, self.version.number, self.record.pk])), "Preguntar al creador")

    def test_question_retry_reply_retry_and_conflicting_nonce(self):
        key = uuid4()
        question = post_question(self.student, self.record.pk, "Duda", key)
        self.assertEqual(post_question(self.student, self.record.pk, "Duda", key).pk, question.pk)
        with self.assertRaises(ValidationError):
            post_question(self.student, self.record.pk, "Otro contenido", key)
        reply_key = uuid4()
        reply = reply_question(self.creator, question.pk, "Respuesta", reply_key)
        self.assertEqual(reply_question(self.creator, question.pk, "Respuesta", reply_key).pk, reply.pk)
        self.assertEqual(QuestionReply.objects.count(), 1)
        self.assertEqual(Notification.objects.get(event_key=f"reply:{reply.pk}").recipient_id, self.student.pk)
        reply_question(self.student, question.pk, "Gracias", uuid4())
        self.assertEqual(LessonQuestion.objects.count(), 1)
        self.assertEqual(QuestionReply.objects.count(), 2)

    def test_questions_private_to_participants_including_other_creator_and_admin(self):
        question = self.question()
        for actor in (self.other, self.other_creator, self.admin):
            with self.assertRaises(PermissionDenied):
                reply_question(actor, question.pk, "Inyección", uuid4())
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("student-question", args=[question.pk])).status_code, 403)
        self.assertNotContains(self.client.get(reverse("student-questions")), question.body)
        self.client.force_login(self.other_creator)
        self.assertEqual(self.client.get(reverse("creator-question", args=[question.pk])).status_code, 403)
        self.assertNotContains(self.client.get(reverse("creator-questions")), question.body)

    def test_suspended_creator_cannot_reply(self):
        question = self.question()
        CreatorProfile.objects.filter(user=self.creator).update(status="suspended")
        with self.assertRaises(PermissionDenied):
            reply_question(self.creator, question.pk, "Respuesta", uuid4())
        self.assertFalse(QuestionReply.objects.exists())

    def test_html_in_question_escaped_and_forms_preserve_history(self):
        question = post_question(self.student, self.record.pk, "<script>alert('x')</script>", uuid4())
        page = self.client.get(reverse("student-question", args=[question.pk]))
        self.assertContains(page, "&lt;script&gt;")
        self.assertNotContains(page, "<script>alert")
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(reverse("creator-questions")), "Esperando al creador")
        response = self.client.post(reverse("creator-question", args=[question.pk]), {"body": "Respuesta", "request_key": uuid4()})
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get(reverse("creator-questions")), "Con respuesta del creador")
        with self.assertRaises(ValidationError):
            question.delete()

    def test_rate_limit_and_retry_do_not_duplicate_messages(self):
        for _ in range(30):
            self.question()
        with self.assertRaises(ValidationError):
            self.question()
        self.assertEqual(LessonQuestion.objects.count(), 30)

    def test_notification_read_is_private_post_only_and_repeat_safe(self):
        question = self.question()
        notice = Notification.objects.get(event_key=f"question:{question.pk}")
        self.assertEqual(self.client.post(reverse("notification-read", args=[notice.pk])).status_code, 404)
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(reverse("notifications")), "1 sin leer")
        self.assertEqual(self.client.get(reverse("notification-read", args=[notice.pk])).status_code, 405)
        self.client.post(reverse("notification-read", args=[notice.pk]))
        notice.refresh_from_db()
        first = notice.read_at
        self.client.post(reverse("notification-read", args=[notice.pk]))
        notice.refresh_from_db()
        self.assertEqual(notice.read_at, first)

    def test_question_and_sharing_require_csrf(self):
        csrf = Client(enforce_csrf_checks=True)
        csrf.force_login(self.student)
        self.assertEqual(csrf.post(reverse("question-create", args=[self.record.pk]), {"body": "Pregunta", "request_key": uuid4()}).status_code, 403)
        certificate = self.certificate()
        self.assertEqual(csrf.post(reverse("certificate-share", args=[certificate.pk]), {"public": "yes"}).status_code, 403)

    def test_revision_decision_notifies_creator_without_feedback_in_notification(self):
        submission = submit(self.course, self.creator)
        decide(submission, self.admin, False, "OBSERVACION_PRIVADA")
        notice = Notification.objects.get(event_key=f"submission:{submission.pk}")
        self.assertEqual(notice.recipient_id, self.creator.pk)
        self.assertNotIn("OBSERVACION_PRIVADA", notice.title)
