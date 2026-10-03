from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F, Max

from .models import (
    Course,
    CourseVersion,
    Material,
    PublicationStatus,
    ResourceVersion,
    VersionAttachment,
    VersionChapter,
    VersionLesson,
    Video,
)


def authorize_publisher(actor):
    if not actor.is_authenticated or not actor.is_active or not actor.is_staff or not actor.has_perm("content.change_course"):
        raise PermissionDenied("La publicación requiere revisión administrativa.")


def next_revision(key):
    return (ResourceVersion.objects.filter(resource_key=key).aggregate(value=Max("number"))["value"] or 0) + 1


@transaction.atomic
def publish_resource(resource, actor):
    original = resource
    if not actor.is_authenticated or not actor.is_active or not actor.is_staff or not actor.has_perm(f"content.change_{resource._meta.model_name}"):
        raise PermissionDenied
    model = type(resource)
    if model not in (Video, Material):
        raise ValidationError("Formato de recurso no admitido.")
    # Reserve the SQLite writer before reading the mutable composition.
    model.objects.filter(pk=resource.pk).update(updated_at=F("updated_at"))
    resource = model.objects.select_related("pending_asset", "pending_subtitles").get(pk=resource.pk)
    revision = ResourceVersion.objects.create(
        resource_key=resource.resource_key, number=next_revision(resource.resource_key),
        creator=resource.creator, kind="video" if model == Video else "material",
        title=resource.title, description=resource.description, access_type=resource.access_type,
        body=resource.transcript, asset=resource.pending_asset, subtitles=resource.pending_subtitles,
    )
    model.objects.filter(pk=resource.pk).update(revision=revision, status=PublicationStatus.PUBLISHED)
    original.revision = revision
    original.status = PublicationStatus.PUBLISHED
    return revision


@transaction.atomic
def publish_course(course, actor):
    original = course
    authorize_publisher(actor)
    # No remote operations under the write transaction. Constraint numbers are
    # still unique; SQLite lock failures propagate, never report false success.
    Course.objects.filter(pk=course.pk).update(updated_at=F("updated_at"))
    course = Course.objects.select_related("creator", "topic").get(pk=course.pk)
    chapters = list(course.chapters.filter(status=PublicationStatus.PUBLISHED).prefetch_related("lessons__attachments__resource"))
    visible = [(chapter, list(chapter.lessons.filter(status=PublicationStatus.PUBLISHED).prefetch_related("attachments__resource"))) for chapter in chapters]
    if not visible or any(not lessons for _, lessons in visible):
        raise ValidationError("Publica al menos un capítulo con lecciones; no se admiten capítulos vacíos.")
    if any(not lesson.body.strip() for _, lessons in visible for lesson in lessons):
        raise ValidationError("Cada lección publicada necesita texto, aunque incluya video o materiales.")
    number = (course.versions.aggregate(value=Max("number"))["value"] or 0) + 1
    version = CourseVersion.objects.create(
        course=course, number=number, title=course.title, description=course.description,
        objective=course.objective, requirements=course.requirements, kind=course.kind,
        topic=course.topic, level=course.level, estimated_minutes=course.estimated_minutes,
        creator_name=course.creator.get_full_name().strip() or "Creador de BTC.EDU",
    )
    for chapter, lessons in visible:
        frozen_chapter = VersionChapter.objects.create(version=version, title=chapter.title, description=chapter.description, position=chapter.position)
        for lesson in lessons:
            values = {"title": lesson.title, "description": lesson.description, "access_type": lesson.access_type, "body": lesson.body}
            text = ResourceVersion.objects.filter(resource_key=lesson.resource_key).order_by("-number").first()
            if text is None or any(getattr(text, key) != value for key, value in values.items()):
                text = ResourceVersion.objects.create(resource_key=lesson.resource_key, number=next_revision(lesson.resource_key), creator=course.creator, kind="text", **values)
            frozen_lesson = VersionLesson.objects.create(chapter=frozen_chapter, source_lesson_id=lesson.pk, position=lesson.position, content=text)
            for attachment in lesson.attachments.all():
                attachment.full_clean()
                VersionAttachment.objects.create(lesson=frozen_lesson, resource=attachment.resource, position=attachment.position)
    # Only the publication service seals a composition; public managers reject
    # mutations, and children reject additions once sealed.
    CourseVersion._base_manager.filter(pk=version.pk).update(sealed=True)
    Course.objects.filter(pk=course.pk).update(current_version=version, status=PublicationStatus.PUBLISHED)
    version.sealed = True
    original.current_version = version
    original.status = PublicationStatus.PUBLISHED
    return version
