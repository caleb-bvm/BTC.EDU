from datetime import timedelta
from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from commerce.services import require_student, reserve_writer
from content.access import content_access
from content.models import VersionLesson
from creators.services import require_creator

from .models import Enrollment, LessonQuestion, Notification, QuestionReply


def notify(recipient, event_key, title, url):
    return Notification.objects.get_or_create(event_key=event_key, defaults={"recipient": recipient, "title": title, "url": url})[0]


def valid_message(body, request_key):
    if not isinstance(body, str) or not body.strip() or len(body.strip()) > 2000:
        raise ValidationError("Escribe un mensaje de hasta 2000 caracteres.")
    try:
        key = UUID(str(request_key))
    except (ValueError, TypeError, AttributeError):
        raise ValidationError("Recarga el formulario antes de enviar.") from None
    return body.strip(), key


def rate_limit(actor):
    since = timezone.now() - timedelta(hours=1)
    count = LessonQuestion.objects.filter(enrollment__student=actor, created_at__gte=since).count()
    count += QuestionReply.objects.filter(author=actor, created_at__gte=since).count()
    if count >= 30:
        raise ValidationError("Has enviado muchos mensajes. Espera antes de volver a escribir.")


def question_access(actor, question, writing=False):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied
    if actor.pk == question.enrollment.student_id:
        require_student(actor)
        if writing and not content_access(actor, question.lesson).allowed:
            raise PermissionDenied("Necesitas acceso a la lección para escribir.")
    elif actor.pk == question.enrollment.version.course.creator_id:
        require_creator(actor)
    else:
        raise PermissionDenied


@transaction.atomic
def post_question(actor, lesson_id, body, request_key):
    require_student(actor)
    body, key = valid_message(body, request_key)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    lesson = VersionLesson.objects.select_related("content", "chapter__version__course").get(pk=lesson_id)
    enrollment = Enrollment.objects.filter(student=actor, version=lesson.chapter.version).first()
    if not enrollment or not content_access(actor, lesson).allowed:
        raise PermissionDenied("Inscríbete y abre una lección accesible para preguntar.")
    existing = LessonQuestion.objects.filter(enrollment=enrollment, request_key=key).first()
    if existing:
        if existing.lesson_id != lesson.pk or existing.body != body:
            raise ValidationError("Este envío ya fue utilizado. Recarga para enviar otro mensaje.")
        return existing
    rate_limit(actor)
    question = LessonQuestion.objects.create(enrollment=enrollment, lesson=lesson, body=body, request_key=key)
    notify(enrollment.version.course.creator, f"question:{question.pk}", "Una pregunta espera tu respuesta", reverse("creator-question", args=[question.pk]))
    return question


@transaction.atomic
def reply_question(actor, question_id, body, request_key):
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied
    body, key = valid_message(body, request_key)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    question = LessonQuestion.objects.select_related("enrollment__version__course", "enrollment__student", "lesson__content", "lesson__chapter__version__course").get(pk=question_id)
    question_access(actor, question, writing=True)
    existing = QuestionReply.objects.filter(question=question, author=actor, request_key=key).first()
    if existing:
        if existing.body != body:
            raise ValidationError("Este envío ya fue utilizado. Recarga para enviar otro mensaje.")
        return existing
    rate_limit(actor)
    reply = QuestionReply.objects.create(question=question, author=actor, body=body, request_key=key)
    is_student = actor.pk == question.enrollment.student_id
    recipient = question.enrollment.version.course.creator if is_student else question.enrollment.student
    target = "creator-question" if is_student else "student-question"
    notify(recipient, f"reply:{reply.pk}", "Tienes una respuesta en tu pregunta", reverse(target, args=[question.pk]))
    return reply
