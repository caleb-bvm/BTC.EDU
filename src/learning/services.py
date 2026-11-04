"""Enrollment and lesson progress for students."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext

from commerce.catalog import public_version, version_owned
from commerce.services import require_student, reserve_writer
from content.access import content_access
from content.models import VersionLesson

from .models import Enrollment, LessonProgress


def enrolled(user, version):
    """True when an active student is enrolled in the version."""
    return user.is_authenticated and user.is_active and user.account_type == "student" and Enrollment.objects.filter(student=user, version=version).exists()


def can_visit_version(user, version):
    """A published version can be visited when it is current, owned or already enrolled."""
    if not version.published_at:
        return False
    return public_version(version) or version_owned(user, version) or enrolled(user, version)


@transaction.atomic
def enroll(actor, version):
    """Enroll a student in a visible version; enrolling never unlocks paid lessons."""
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    version.refresh_from_db()
    if not version.sealed or not can_visit_version(actor, version):
        raise PermissionDenied(gettext("Esta versión no está disponible para tu cuenta."))
    if version.course.status not in ("published", "archived"):
        raise ValidationError(gettext("Este curso no está disponible para estudiar."))
    enrollment, _ = Enrollment.objects.get_or_create(student=actor, version=version)
    return enrollment


class StaleProgress(ValidationError):
    """Raised when the progress revision changed since the page was loaded."""
    pass


@transaction.atomic
def save_progress(actor, enrollment_id, lesson_id, expected_revision, action):
    """Save the reading position or completion of an accessible lesson.

    Uses an optimistic revision so two tabs never overwrite each other, and requires passing a
    mandatory quiz before completion.
    """
    require_student(actor)
    if type(expected_revision) is not int or expected_revision < 0 or action not in ("position", "complete", "incomplete"):
        raise ValidationError(gettext("El avance enviado no es válido."))
    changed = Enrollment.objects.filter(pk=enrollment_id, student=actor).update(revision=F("revision"))
    if not changed:
        raise PermissionDenied
    actor.refresh_from_db()
    require_student(actor)
    enrollment = Enrollment.objects.select_related("version__course").get(pk=enrollment_id, student=actor)
    if enrollment.revision != expected_revision:
        raise StaleProgress(gettext("Hay un avance más reciente. Recarga la lección antes de guardar para conservarlo."))
    lesson = VersionLesson.objects.select_related("content", "chapter__version__course").filter(pk=lesson_id, chapter__version=enrollment.version).first()
    if lesson is None or not content_access(actor, lesson).allowed:
        raise PermissionDenied(gettext("Solo puedes guardar una lección accesible de esta inscripción."))
    if action == "complete":
        from .models import QuizAttempt, VersionQuiz
        quiz = VersionQuiz.objects.filter(lesson=lesson, required=True).first()
        if quiz and not QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz, passed=True, submitted_at__isnull=False).exists():
            raise ValidationError(gettext("Aprueba la evaluación obligatoria antes de completar esta lección."))
        LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    elif action == "incomplete":
        LessonProgress.objects.filter(enrollment=enrollment, lesson=lesson).delete()
    enrollment.last_lesson = lesson
    enrollment.revision += 1
    enrollment.updated_at = timezone.now()
    enrollment.save(update_fields=("last_lesson", "revision", "updated_at"))
    return enrollment
