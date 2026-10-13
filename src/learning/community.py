"""Version-scoped discussion; all mutations reserve the SQLite writer first."""
from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from commerce.services import reserve_writer
from content.access import content_access
from content.models import VersionLesson
from creators.services import require_creator

from .models import (
    CommunityDecision,
    CommunityPost,
    CommunityReport,
    CommunitySubscription,
    CommunitySuspension,
    Enrollment,
)
from .support import notify, valid_message


def moderator(actor, version):
    if not actor.is_authenticated or not actor.is_active:
        return False
    if actor.is_staff and actor.has_perm("learning.moderate_community"):
        return True
    if actor.account_type == "creator" and version.course.creator_id == actor.pk:
        require_creator(actor)
        return True
    return False


def access(actor, version, writing=False):
    if not actor.is_authenticated or not actor.is_active or not version.published_at or not version.sealed:
        raise PermissionDenied
    if moderator(actor, version):
        if writing:
            if actor.account_type != "creator" or version.course.creator_id != actor.pk:
                raise PermissionDenied
            require_creator(actor)
        return
    if actor.account_type != "student" or not Enrollment.objects.filter(student=actor, version=version).exists():
        raise PermissionDenied("Inscríbete en esta versión para entrar a su comunidad.")
    if writing and CommunitySuspension.objects.filter(version=version, student=actor, active=True).exists():
        raise PermissionDenied("Tu participación está suspendida. Puedes seguir leyendo y estudiando.")


@transaction.atomic
def post_message(actor, version, body, key, parent_id=None, lesson_id=None):
    body, key = valid_message(body, key)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    version.refresh_from_db()
    access(actor, version)
    parent = None
    if parent_id is not None:
        parent = CommunityPost.objects.filter(pk=parent_id, version=version, parent__isnull=True).first()
        if not parent or (lesson_id is not None and lesson_id != parent.lesson_id):
            raise ValidationError("Selecciona una conversación de esta lección.")
        lesson_id = parent.lesson_id
    if lesson_id is not None:
        lesson = VersionLesson.objects.select_related("content", "chapter__version__course").filter(pk=lesson_id, chapter__version=version).first()
        if lesson is None:
            raise ValidationError("Selecciona una lección de esta versión.")
        lesson_access(actor, version, lesson)
    previous = CommunityPost.objects.filter(author=actor, request_key=key).first()
    if previous:
        if previous.body != body or previous.version_id != version.pk or previous.parent_id != parent_id or previous.lesson_id != lesson_id:
            raise ValidationError("Este envío ya fue utilizado. Recarga el formulario.")
        return previous
    access(actor, version, writing=True)
    if parent is not None:
        if parent.hidden or parent.closed:
            raise ValidationError("Esta conversación no admite respuestas.")
    since = timezone.now() - timedelta(hours=1)
    if CommunityPost.objects.filter(author=actor, created_at__gte=since).count() >= 30:
        raise ValidationError("Has enviado muchos mensajes. Espera antes de escribir de nuevo.")
    post = CommunityPost.objects.create(version=version, lesson_id=lesson_id, author=actor, body=body, request_key=key, parent_id=parent_id)
    if parent_id:
        recipients = {parent.author_id: parent.author}
        recipients.update({sub.user_id: sub.user for sub in parent.subscriptions.select_related("user")})
        for recipient in recipients.values():
            if recipient.pk == actor.pk:
                continue
            try:
                access(recipient, version)
                if lesson_id:
                    lesson_access(recipient, version, lesson)
            except PermissionDenied:
                continue
            key = f"community-reply:{post.pk}" if recipient.pk == parent.author_id else f"community-reply:{post.pk}:{recipient.pk}"
            notify(recipient, key, "Una conversación tiene una respuesta", reverse("community-thread", args=[parent.pk]))
    elif lesson_id and version.course.creator_id != actor.pk:
        creator = version.course.creator
        try:
            access(creator, version)
            lesson_access(creator, version, lesson)
        except PermissionDenied:
            pass
        else:
            notify(creator, f"community-lesson:{post.pk}", "Un nuevo comentario en una lección", reverse("community-thread", args=[post.pk]))
    return post


def lesson_access(actor, version, lesson):
    """Course community membership never unlocks a lesson's discussion."""
    if lesson.chapter.version_id != version.pk or (not moderator(actor, version) and not content_access(actor, lesson).allowed):
        raise PermissionDenied("Necesitas acceso a esta lección para consultar su conversación.")


def post_access(actor, post):
    access(actor, post.version)
    if post.lesson_id:
        lesson_access(actor, post.version, post.lesson)


def accessible_posts(actor, version):
    """Filter before searching, counting or paginating, including replies."""
    posts = CommunityPost.objects.filter(version=version)
    if moderator(actor, version):
        return posts
    from commerce.models import Entitlement
    lessons = VersionLesson.objects.filter(chapter__version=version)
    if version.course.status not in ("published", "archived"):
        lessons = lessons.none()
    else:
        lessons = lessons.filter(Q(content__access_type="free") | Q(content_id__in=Entitlement.objects.filter(buyer=actor).values("resource_id")))
    return posts.filter(Q(lesson__isnull=True) | Q(lesson_id__in=lessons.values("pk")))


@transaction.atomic
def follow_thread(actor, post_id, following):
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    post = CommunityPost.objects.select_related("version__course", "lesson__content", "lesson__chapter__version__course").get(pk=post_id, parent__isnull=True)
    post_access(actor, post)
    if post.hidden:
        raise PermissionDenied
    if following:
        CommunitySubscription.objects.get_or_create(thread=post, user=actor)
    else:
        CommunitySubscription.objects.filter(thread=post, user=actor).delete()


def reason_text(reason):
    if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 500:
        raise ValidationError("Escribe un motivo de hasta 500 caracteres.")
    return reason.strip()


@transaction.atomic
def report_message(actor, post_id, reason):
    reason = reason_text(reason)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    post = CommunityPost.objects.select_related("version__course", "parent", "lesson__content", "lesson__chapter__version__course").get(pk=post_id)
    post_access(actor, post)
    previous = CommunityReport.objects.filter(post=post, reporter=actor).first()
    if previous:
        return previous
    if post.hidden or (post.parent_id and post.parent.hidden):
        raise ValidationError("El mensaje ya está oculto.")
    if CommunityReport.objects.filter(reporter=actor, created_at__gte=timezone.now() - timedelta(hours=1)).count() >= 30:
        raise ValidationError("Has enviado muchos reportes. Espera antes de enviar otro.")
    report = CommunityReport.objects.create(post=post, reporter=actor, reason=reason)
    if post.version.course.creator_id:
        notify(post.version.course.creator, f"community-report:{report.pk}", "Un reporte requiere revisión", reverse("community-moderation", args=[post.version_id]))
    return report


@transaction.atomic
def moderate(actor, version, action, reason, post_id=None, student_id=None):
    reason = reason_text(reason)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    # Clear permission caches before rechecking administrative authorization.
    for name in ("_perm_cache", "_user_perm_cache", "_group_perm_cache"):
        actor.__dict__.pop(name, None)
    version.refresh_from_db()
    access(actor, version)
    if not moderator(actor, version):
        raise PermissionDenied
    post = None
    if action in ("hide", "show", "close", "open", "dismiss"):
        post = CommunityPost.objects.filter(pk=post_id, version=version).first()
        if not post or (action in ("close", "open") and post.parent_id):
            raise ValidationError("Selecciona una conversación válida de este espacio.")
        if action == "dismiss":
            changed = CommunityReport._base_manager.filter(post=post, resolved=False).update(resolved=True)
        else:
            field, value = ("hidden", action == "hide") if action in ("hide", "show") else ("closed", action == "close")
            changed = CommunityPost._base_manager.filter(pk=post.pk, **{field: not value}).update(**{field: value})
            if action == "hide":
                CommunityReport._base_manager.filter(post=post, resolved=False).update(resolved=True)
        if not changed:
            return None
    elif action in ("suspend", "restore"):
        if not Enrollment.objects.filter(version=version, student_id=student_id).exists():
            raise ValidationError("Selecciona un alumno inscrito en este espacio.")
        suspension, created = CommunitySuspension.objects.get_or_create(version=version, student_id=student_id, defaults={"active": action == "suspend"})
        value = action == "suspend"
        if not created and suspension.active == value:
            return None
        if created and not value:
            return None
        CommunitySuspension.objects.filter(pk=suspension.pk).update(active=value)
    else:
        raise ValidationError("La acción de moderación no es válida.")
    decision = CommunityDecision.objects.create(version=version, actor=actor, post=post, student_id=student_id if action in ("suspend", "restore") else None, action=action, reason=reason)
    recipient_id = student_id if action in ("suspend", "restore") else post.author_id if action in ("hide", "show") else None
    if recipient_id and recipient_id != actor.pk:
        from django.contrib.auth import get_user_model
        titles = {"hide": "Tu mensaje se ocultó en la comunidad", "show": "Tu mensaje vuelve a estar visible", "suspend": "Tu escritura se suspendió en una comunidad", "restore": "Puedes volver a escribir en la comunidad"}
        notify(get_user_model().objects.get(pk=recipient_id), f"community-decision:{decision.pk}", titles[action], reverse("community-space", args=[version.pk]))
    return decision
