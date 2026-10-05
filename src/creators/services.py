from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from content.models import Course, Material, PublicationStatus, Video
from content.publication import prepare_course, prepare_resource

from .models import CreatorProfile, Submission


def require_creator(actor):
    if not actor.is_authenticated or not actor.is_active or actor.account_type != "creator" or not CreatorProfile.objects.filter(user=actor, status=CreatorProfile.Status.APPROVED).exists():
        raise PermissionDenied("Necesitas la aprobación como creador.")


@transaction.atomic
def submit(item, actor):
    require_creator(actor)
    if item.creator_id != actor.pk:
        raise PermissionDenied
    field = {Course: "course", Video: "video", Material: "material"}[type(item)]
    # Reserve the SQLite writer before checking pending submissions or composing.
    type(item).objects.filter(pk=item.pk).update(updated_at=timezone.now())
    item.refresh_from_db()
    require_creator(actor)
    if item.creator_id != actor.pk:
        raise PermissionDenied
    if Submission.objects.filter(**{field: item}, status=Submission.Status.PENDING).exists():
        raise ValidationError("Ya hay una versión en revisión. Retira el envío antes de reenviar.")
    if not item.title.strip() or not item.description.strip():
        raise ValidationError("Completa el título y la descripción antes de enviar.")
    snapshot = prepare_course(item, actor) if field == "course" else prepare_resource(item, actor)
    return Submission.objects.create(creator=actor, **{field: item}, **{"course_version" if field == "course" else "resource_version": snapshot})


def require_reviewer(actor):
    if not actor.is_authenticated or not actor.is_active or not actor.is_staff or not actor.has_perm("creators.change_submission"):
        raise PermissionDenied


@transaction.atomic
def decide(submission, actor, approve, feedback=""):
    require_reviewer(actor)
    Submission.objects.filter(pk=submission.pk).update(status=F("status"))
    # Never overwrite a previous decision: the writer lock is reserved above by
    # updating a neutral field instead of changing the status.
    submission.refresh_from_db()
    if submission.status != Submission.Status.PENDING:
        raise ValidationError("Este envío ya fue resuelto.")
    if not approve and not feedback.strip():
        raise ValidationError("Explica qué debe corregir el creador.")
    require_creator(submission.creator)
    if approve:
        item = submission.course or submission.video or submission.material
        permission = f"content.change_{item._meta.model_name}"
        if not actor.has_perm(permission):
            raise PermissionDenied
        snapshot_owner = submission.course_version.course.creator_id if submission.course_id else submission.resource_version.creator_id
        if item.creator_id != submission.creator_id or snapshot_owner != submission.creator_id:
            raise ValidationError("El propietario del contenido cambió; revisa el envío.")
        pointer = "current_version" if submission.course_id else "revision"
        current = getattr(item, pointer)
        if current and current.number >= submission.snapshot.number:
            raise ValidationError("Ya existe una publicación posterior. Solicita un nuevo envío para revisar los cambios.")
        type(item).objects.filter(pk=item.pk).update(**{pointer: submission.snapshot, "status": PublicationStatus.PUBLISHED})
    submission.status = Submission.Status.APPROVED if approve else Submission.Status.CHANGES
    submission.feedback = feedback.strip()
    submission.reviewed_by = actor
    submission.reviewed_at = timezone.now()
    submission.save(update_fields=("status", "feedback", "reviewed_by", "reviewed_at"))
    return submission
