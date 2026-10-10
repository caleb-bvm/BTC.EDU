from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse

from commerce.services import require_student

from .models import (
    Certificate,
    CertificateDraft,
    CertificateRevocation,
    CertificateSharing,
    Enrollment,
    LessonProgress,
    QuizAttempt,
    VersionCertificatePolicy,
    VersionQuiz,
)
from .support import notify


def freeze_certificate_policy(course, version):
    draft = CertificateDraft.objects.filter(course=course, enabled=True).first()
    if not draft:
        return
    source_ids = set(draft.required_lessons.values_list("pk", flat=True))
    lessons = list(version.chapters.values_list("lessons__pk", "lessons__source_lesson_id"))
    included = {source for _, source in lessons}
    if not source_ids or not source_ids.issubset(included):
        raise ValidationError("Selecciona al menos una lección obligatoria incluida en la publicación para el certificado.")
    VersionCertificatePolicy.objects.create(version=version, required_lesson_ids=[pk for pk, source in lessons if source in source_ids])


def completion_status(enrollment):
    policy = VersionCertificatePolicy.objects.filter(version=enrollment.version).first()
    certificate = Certificate.objects.filter(enrollment=enrollment).first()
    if not policy:
        return {"enabled": False, "certificate": certificate, "eligible": False}
    ids = policy.required_lesson_ids
    completed = set(LessonProgress.objects.filter(enrollment=enrollment, lesson_id__in=ids).values_list("lesson_id", flat=True))
    # Every mandatory quiz in the course is required, including optional lessons.
    required_quizzes = list(VersionQuiz.objects.filter(lesson__chapter__version=enrollment.version, required=True))
    passed = set(QuizAttempt.objects.filter(enrollment=enrollment, submitted_at__isnull=False, passed=True).values_list("quiz_id", flat=True))
    return {"enabled": True, "certificate": certificate, "required_count": len(ids), "completed_required": len(completed),
            "pending_quizzes": sum(quiz.pk not in passed for quiz in required_quizzes),
            "eligible": set(ids).issubset(completed) and all(quiz.pk in passed for quiz in required_quizzes)}


@transaction.atomic
def issue_certificate(actor, enrollment_id, student_name):
    require_student(actor)
    if not Enrollment.objects.filter(pk=enrollment_id, student=actor).update(revision=F("revision")):
        raise PermissionDenied
    enrollment = Enrollment.objects.select_for_update().select_related("version__course").get(pk=enrollment_id)
    actor.refresh_from_db()
    require_student(actor)
    existing = Certificate.objects.filter(enrollment=enrollment).first()
    if existing:
        return existing
    name = student_name.strip() if isinstance(student_name, str) else ""
    if not name or len(name) > 150 or any(ord(char) < 32 for char in name):
        raise ValidationError("Indica el nombre que aparecerá en tu certificado, hasta 150 caracteres.")
    version = enrollment.version
    status = completion_status(enrollment)
    if not version.sealed or not version.published_at or not status["eligible"]:
        raise ValidationError("Completa las lecciones requeridas y aprueba las evaluaciones obligatorias de esta versión.")
    policy = version.certificate_policy
    completions = LessonProgress.objects.filter(enrollment=enrollment, lesson_id__in=policy.required_lesson_ids)
    attempts = QuizAttempt.objects.filter(enrollment=enrollment, quiz__required=True, quiz__lesson__chapter__version=version, passed=True, submitted_at__isnull=False).order_by("number", "pk")
    evidence = {"version": version.number, "lessons": [{"id": item.lesson_id, "completed_at": item.completed_at.isoformat()} for item in completions],
                "assessments": [{"quiz": item.quiz_id, "attempt": item.pk, "score": str(item.score)} for item in attempts]}
    certificate = Certificate.objects.create(enrollment=enrollment, student_name=name, course_title=version.title, creator_name=version.creator_name, evidence=evidence)
    CertificateSharing.objects.create(certificate=certificate)
    notify(actor, f"certificate:{certificate.pk}", "Tu certificado está disponible", reverse("certificate-detail", args=[certificate.pk]))
    return certificate


@transaction.atomic
def revoke_certificate(actor, certificate_id, reason):
    if not actor.is_authenticated or not actor.is_active or not actor.is_staff or not actor.has_perm("learning.add_certificaterevocation"):
        raise PermissionDenied
    reason = reason.strip()
    if not reason or len(reason) > 500:
        raise ValidationError("Indica un motivo de hasta 500 caracteres.")
    # Serialize with other revocations without modifying the immutable credential.
    CertificateSharing.objects.filter(certificate_id=certificate_id).update(public=F("public"))
    certificate = Certificate.objects.select_related("enrollment__student").get(pk=certificate_id)
    revocation, _ = CertificateRevocation.objects.get_or_create(certificate=certificate, defaults={"actor": actor, "reason": reason})
    notify(certificate.enrollment.student, f"revoked:{certificate.pk}", "Revisa el estado de tu certificado", reverse("certificate-detail", args=[certificate.pk]))
    return revocation
