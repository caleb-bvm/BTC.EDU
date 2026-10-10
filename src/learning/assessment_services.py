from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from commerce.services import require_student
from content.access import content_access
from creators.services import require_creator

from .models import Enrollment, ExtraQuizAttempt, QuizAttempt, QuizDraft, VersionQuiz

RULE_FIELDS = ("title", "pass_mark", "max_attempts", "wait_minutes", "required", "feedback", "questions")


def freeze_quiz(source_lesson, published_lesson):
    draft = QuizDraft.objects.filter(lesson=source_lesson, enabled=True).first()
    if draft:
        draft.full_clean()
        VersionQuiz.objects.create(lesson=published_lesson, **{field: getattr(draft, field) for field in RULE_FIELDS})


def quiz_status(enrollment, quiz):
    attempts = QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz)
    allowance = quiz.max_attempts + ExtraQuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz).count()
    last = attempts.filter(submitted_at__isnull=False).order_by("-number").first()
    ready_at = last.submitted_at + timedelta(minutes=quiz.wait_minutes) if last else None
    return {"attempts": attempts.order_by("-number"), "active_attempt": attempts.filter(submitted_at__isnull=True).first(),
            "passed_quiz": attempts.filter(passed=True).exists(), "remaining": max(0, allowance - attempts.count()),
            "allowance": allowance, "ready_at": ready_at, "waiting": bool(ready_at and ready_at > timezone.now())}


def authorized_enrollment(actor, enrollment_id, quiz):
    require_student(actor)
    enrollment = Enrollment.objects.select_related("version__course").filter(pk=enrollment_id, student=actor, version_id=quiz.lesson.chapter.version_id).first()
    if not enrollment or not content_access(actor, quiz.lesson).allowed:
        raise PermissionDenied("La evaluación requiere inscripción y acceso a esta lección.")
    return enrollment


@transaction.atomic
def start_attempt(actor, enrollment_id, quiz_id):
    require_student(actor)
    # Reserve the writer before reads on SQLite; select_for_update covers row-locking databases.
    if not Enrollment.objects.filter(pk=enrollment_id, student=actor).update(revision=F("revision")):
        raise PermissionDenied
    Enrollment.objects.select_for_update().get(pk=enrollment_id)
    actor.refresh_from_db()
    quiz = VersionQuiz.objects.select_related("lesson__content", "lesson__chapter__version__course").get(pk=quiz_id)
    enrollment = authorized_enrollment(actor, enrollment_id, quiz)
    status = quiz_status(enrollment, quiz)
    if status["active_attempt"]:
        return status["active_attempt"]
    if not status["remaining"]:
        raise ValidationError("Has utilizado los intentos disponibles. Puedes solicitar otro al creador.")
    if status["waiting"]:
        raise ValidationError("Aún no termina la espera indicada entre intentos.")
    return QuizAttempt.objects.create(enrollment=enrollment, quiz=quiz, number=status["attempts"].count() + 1)


def normalize_answers(quiz, answers, complete):
    if not isinstance(answers, dict) or set(answers) - {str(index) for index in range(len(quiz.questions))}:
        raise ValidationError("Las respuestas no corresponden a esta evaluación.")
    cleaned = {}
    for index, question in enumerate(quiz.questions):
        selections = answers.get(str(index), [])
        if not isinstance(selections, list) or any(type(option) is not int or not 0 <= option < len(question["options"]) for option in selections) or len(set(selections)) != len(selections) or (not question["multiple"] and len(selections) > 1):
            raise ValidationError("Selecciona opciones válidas, sin repetirlas.")
        if complete and not selections:
            raise ValidationError("Responde todas las preguntas antes de entregar. Puedes guardar y continuar después.")
        cleaned[str(index)] = sorted(selections)
    return cleaned


@transaction.atomic
def save_attempt(actor, attempt_id, answers, revision, submit=False):
    require_student(actor)
    if type(revision) is not int or revision < 0:
        raise ValidationError("La revisión del intento no es válida.")
    if not QuizAttempt.objects.filter(pk=attempt_id, enrollment__student=actor).update(revision=F("revision")):
        raise PermissionDenied
    attempt = QuizAttempt.objects.select_for_update().select_related("quiz__lesson__content", "quiz__lesson__chapter__version__course", "enrollment").get(pk=attempt_id)
    actor.refresh_from_db()
    authorized_enrollment(actor, attempt.enrollment_id, attempt.quiz)
    if attempt.submitted_at:
        if submit:
            return attempt
        raise ValidationError("El intento ya fue entregado; su resultado se conserva.")
    if revision != attempt.revision:
        raise ValidationError("Hay respuestas guardadas desde otra sesión. Recarga el intento antes de continuar.")
    attempt.answers = normalize_answers(attempt.quiz, answers, submit)
    attempt.revision += 1
    if submit:
        count = sum(set(attempt.answers[str(index)]) == set(question["correct"]) for index, question in enumerate(attempt.quiz.questions))
        total = len(attempt.quiz.questions)
        attempt.correct_count = count
        attempt.score = (Decimal(count * 100) / Decimal(total)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        attempt.passed = count * 100 >= attempt.quiz.pass_mark * total
        attempt.submitted_at = timezone.now()
    attempt.save(update_fields=("answers", "revision", "correct_count", "score", "passed", "submitted_at"))
    return attempt


@transaction.atomic
def grant_attempt(actor, enrollment_id, quiz_id, allowance_before, reason):
    if not actor.is_authenticated or not actor.is_active or actor.account_type != "creator":
        raise PermissionDenied
    if type(allowance_before) is not int or not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 500:
        raise ValidationError("Indica un motivo de hasta 500 caracteres.")
    Enrollment.objects.filter(pk=enrollment_id).update(revision=F("revision"))
    enrollment = Enrollment.objects.select_for_update().get(pk=enrollment_id)
    actor.refresh_from_db()
    quiz = VersionQuiz.objects.select_related("lesson__chapter__version__course").get(pk=quiz_id)
    require_creator(actor)
    if quiz.lesson.chapter.version.course.creator_id != actor.pk or enrollment.version_id != quiz.lesson.chapter.version_id:
        raise PermissionDenied
    existing = ExtraQuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz, allowance_before=allowance_before).first()
    if existing:
        return existing
    status = quiz_status(enrollment, quiz)
    if status["allowance"] != allowance_before or status["remaining"] or status["active_attempt"]:
        raise ValidationError("Solo puedes conceder otro intento cuando el alumno haya agotado los disponibles. Recarga los resultados.")
    grant = ExtraQuizAttempt.objects.create(enrollment=enrollment, quiz=quiz, granted_by=actor, reason=reason.strip(), allowance_before=allowance_before)
    from django.urls import reverse

    from .support import notify
    notify(enrollment.student, f"grant:{grant.pk}", "Tienes otro intento autorizado", reverse("quiz-detail", args=[quiz.pk]))
    return grant
