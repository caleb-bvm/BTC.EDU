"""Private, versioned practice delivery and educator review."""
import hashlib
import uuid
import zipfile
from datetime import timedelta
from pathlib import PurePath

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from commerce.services import require_student, reserve_writer
from content.access import content_access
from content.models import Course, Lesson
from creators.services import require_creator
from creators.views import protect_legacy

from .models import (
    Enrollment,
    PracticeDelivery,
    PracticeDraft,
    PracticeIntake,
    PracticeReview,
    VersionPractice,
)
from .support import notify

MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
PRACTICE_FIELDS = ("title", "instructions", "criteria", "review_days")


def freeze_practice(source, target):
    draft = PracticeDraft.objects.filter(lesson=source, enabled=True).first()
    if draft:
        draft.full_clean()
        VersionPractice.objects.create(lesson=target, **{field: getattr(draft, field) for field in PRACTICE_FIELDS})


@transaction.atomic
def save_practice(actor, lesson_id, values, revision):
    require_creator(actor)
    # Same lock as publication: the snapshot sees one complete editor revision.
    Course.objects.filter(chapters__lessons__pk=lesson_id).update(updated_at=F("updated_at"))
    lesson = Lesson.objects.select_related("chapter__course").get(pk=lesson_id)
    actor.refresh_from_db()
    require_creator(actor)
    if lesson.chapter.course.creator_id != actor.pk:
        raise PermissionDenied
    protect_legacy(lesson.chapter.course)
    draft = PracticeDraft.objects.filter(lesson=lesson).first()
    if (draft.revision if draft else 0) != revision:
        raise ValidationError("Hay cambios más recientes. Recarga antes de guardar.")
    draft = draft or PracticeDraft(lesson=lesson)
    for field in (*PRACTICE_FIELDS, "enabled"):
        setattr(draft, field, values[field])
    draft.revision = revision + 1
    draft.full_clean()
    draft.save()
    Course.objects.filter(pk=lesson.chapter.course_id).update(updated_at=timezone.now())
    return draft


def validate_attachment(upload):
    if not upload:
        return None
    if not 0 < upload.size <= MAX_ATTACHMENT_BYTES:
        raise ValidationError("El archivo debe pesar entre 1 byte y 10 MB.")
    name = PurePath(upload.name.replace("\\", "/")).name
    suffix = PurePath(name).suffix.lower()
    header = upload.read(16)
    upload.seek(0)
    valid = False
    try:
        if suffix == ".pdf":
            valid = header.startswith(b"%PDF-")
        elif suffix == ".zip":
            valid = zipfile.is_zipfile(upload)
        elif suffix == ".txt":
            text = upload.read().decode("utf-8")
            valid = "\x00" not in text
        elif suffix in (".png", ".jpg", ".jpeg"):
            with Image.open(upload) as image:
                valid = image.format == ("PNG" if suffix == ".png" else "JPEG")
                image.verify()
    except (ValueError, OSError, UnicodeError, Image.DecompressionBombError):
        valid = False
    finally:
        upload.seek(0)
    if not valid:
        raise ValidationError("Adjunta un PDF, ZIP, TXT en UTF-8, PNG o JPG válido (máximo 10 MB).")
    if any(ord(char) < 32 or ord(char) == 127 for char in name):
        raise ValidationError("El nombre del archivo contiene caracteres no válidos.")
    if len(name) > 200:
        raise ValidationError("Acorta el nombre del archivo a 200 caracteres.")
    return name


def student_practice(actor, practice):
    require_student(actor)
    enrollment = Enrollment.objects.filter(student=actor, version=practice.lesson.chapter.version).first()
    if not enrollment:
        raise PermissionDenied("Inscríbete en esta versión para entregar la práctica.")
    return enrollment


def educator_practice(actor, practice):
    require_creator(actor)
    if practice.lesson.chapter.version.course.creator_id != actor.pk:
        raise PermissionDenied


def practice_is_open(practice):
    intake = PracticeIntake.objects.filter(practice=practice).first()
    return intake.accepting if intake else True


def key_value(value):
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        raise ValidationError("Recarga el formulario para volver a enviar.")


def submit_delivery(actor, practice_id, body, project_url, attachment, request_key, previous_id):
    # Validate uploads before taking any database lock; never fetch project URLs.
    attachment_name = validate_attachment(attachment)
    project_url = project_url.strip()
    attachment_hash = ""
    if attachment:
        digest = hashlib.sha256()
        for chunk in attachment.chunks():
            digest.update(chunk)
        attachment_hash = digest.hexdigest()
        attachment.seek(0)
    if project_url and not project_url.lower().startswith(("https://", "http://")):
        raise ValidationError("Usa un enlace HTTP o HTTPS para el proyecto.")
    stored_file = None
    try:
        with transaction.atomic():
            require_student(actor)
            reserve_writer(actor.pk)
            actor.refresh_from_db()
            require_student(actor)
            practice = VersionPractice.objects.select_related("lesson__content", "lesson__chapter__version__course").get(pk=practice_id)
            enrollment = student_practice(actor, practice)
            Enrollment.objects.select_for_update().get(pk=enrollment.pk)
            key = key_value(request_key)
            existing = PracticeDelivery.objects.filter(enrollment=enrollment, request_key=key).first()
            if existing:
                if existing.practice_id != practice.pk or existing.body != body.strip() or existing.project_url != project_url.strip() or existing.attachment_sha256 != attachment_hash or existing.attachment_name != (attachment_name or ""):
                    raise ValidationError("Este formulario ya se utilizó para otra entrega. Recarga para consultar la solución registrada.")
                return existing
            if not content_access(actor, practice.lesson).allowed:
                raise PermissionDenied("Necesitas acceso a esta lección para entregar.")
            if not practice_is_open(practice):
                raise ValidationError("El educador ha pausado la recepción. Puedes consultar tus entregas anteriores.")
            last = PracticeDelivery.objects.filter(enrollment=enrollment, practice=practice).select_related("review").order_by("-number").first()
            if (last.pk if last else 0) != previous_id:
                raise ValidationError("Ya hay una entrega más reciente. Recarga para consultarla.")
            if last and last.state != "changes":
                raise ValidationError("Espera la revisión del educador antes de volver a entregar." if last.state == "pending" else "Esta práctica ya está aprobada.")
            now = timezone.now()
            delivery = PracticeDelivery(enrollment=enrollment, practice=practice, number=last.number + 1 if last else 1,
                request_key=key, body=body.strip(), project_url=project_url.strip(), submitted_at=now,
                due_at=now + timedelta(days=practice.review_days), attachment_name=attachment_name or "", attachment_size=attachment.size if attachment else 0)
            delivery.attachment_sha256 = attachment_hash
            # Check all model fields before writing to private storage.
            delivery.attachment = "practice-deliveries/pending" if attachment else ""
            delivery.full_clean()
            if attachment:
                delivery.attachment.save(attachment.name, attachment, save=False)
                stored_file = (delivery.attachment.storage, delivery.attachment.name)
            delivery.save()
            notify(practice.lesson.chapter.version.course.creator, f"practice-delivery:{delivery.pk}",
                f"Nueva entrega: {practice.title}", reverse("creator-practice-delivery", args=[delivery.pk]))
            return delivery
    except BaseException:
        if stored_file:
            stored_file[0].delete(stored_file[1])
        raise


@transaction.atomic
def review_delivery(actor, delivery_id, outcome, feedback, met_criteria):
    require_creator(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_creator(actor)
    delivery = PracticeDelivery.objects.select_for_update().select_related("enrollment__student", "practice__lesson__chapter__version__course").get(pk=delivery_id)
    educator_practice(actor, delivery.practice)
    existing = PracticeReview.objects.filter(delivery=delivery).first()
    values = dict(outcome=outcome, feedback=feedback.strip(), met_criteria=sorted(set(met_criteria)))
    if existing:
        if all(getattr(existing, field) == value for field, value in values.items()):
            return existing
        raise ValidationError("Esta entrega ya tiene una revisión. Consulta su historial.")
    review = PracticeReview(delivery=delivery, educator=actor, **values)
    review.save()
    notify(delivery.enrollment.student, f"practice-review:{review.pk}", f"Práctica revisada: {delivery.practice.title}",
        reverse("student-practice", args=[delivery.practice_id]))
    return review


@transaction.atomic
def set_intake(actor, practice_id, accepting, revision):
    require_creator(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    practice = VersionPractice.objects.select_related("lesson__chapter__version__course").get(pk=practice_id)
    educator_practice(actor, practice)
    # Locks a row present even when the optional intake control has not been created.
    Course.objects.select_for_update().get(pk=practice.lesson.chapter.version.course_id)
    intake, _ = PracticeIntake.objects.get_or_create(practice=practice)
    if intake.revision != revision:
        raise ValidationError("La recepción cambió desde otra ventana. Recarga la página.")
    intake.accepting, intake.revision = accepting, revision + 1
    intake.save()

