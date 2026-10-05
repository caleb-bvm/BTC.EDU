from django.db.models import F, Q

from content.models import (
    CourseVersion,
    Material,
    ResourceVersion,
    VersionAttachment,
    VersionChapter,
    VersionLesson,
    Video,
)

from .models import Entitlement, Offer


def public_version(version):
    return version.sealed and bool(version.published_at) and version.course.status == "published" and version.course.current_version_id == version.pk


def public_resource(resource):
    return (Video.objects.filter(revision=resource, status="published").exists()
            or Material.objects.filter(revision=resource, status="published").exists()
            or VersionAttachment.objects.filter(resource=resource, lesson__chapter__version__sealed=True,
                lesson__chapter__version__course__status="published",
                lesson__chapter__version_id=F("lesson__chapter__version__course__current_version_id")).exists())


def available(offer):
    if offer.status != Offer.Status.ACTIVE or not offer.creator.is_active:
        return False
    from creators.models import CreatorProfile
    if not CreatorProfile.objects.filter(user=offer.creator, status="approved").exists():
        return False
    return public_version(offer.course_version) if offer.course_version_id else public_resource(offer.resource)


def target_choices(actor):
    versions = CourseVersion.objects.filter(course__creator=actor, sealed=True, course__status="published", pk=F("course__current_version_id"))
    choices = []
    for version in versions:
        choices.append((f"course:{version.pk}", f"{version.title} · v{version.number} · curso completo"))
        for chapter in version.chapters.prefetch_related("lessons__content", "lessons__attachments__resource"):
            choices.append((f"chapter:{chapter.pk}", f"{version.title} / {chapter.title} · capítulo"))
            for lesson in chapter.lessons.all():
                if lesson.content.access_type == "paid":
                    choices.append((f"lesson:{lesson.pk}", f"{version.title} / {lesson.content.title} · texto de lección"))
    resources = ResourceVersion.objects.filter(creator=actor, access_type="paid").exclude(kind="text")
    for resource in resources:
        if public_resource(resource):
            choices.append((f"resource:{resource.pk}", f"{resource.title} · revisión {resource.number} · {resource.get_kind_display()}"))
    return choices


def target_inventory(kind, pk, actor):
    from django.core.exceptions import PermissionDenied, ValidationError
    models = {"course": CourseVersion, "chapter": VersionChapter, "lesson": VersionLesson, "resource": ResourceVersion}
    if kind not in models:
        raise ValidationError("Elige contenido publicado.")
    target = models[kind].objects.get(pk=pk)
    version = target if kind == "course" else target.version if kind == "chapter" else target.chapter.version if kind == "lesson" else None
    owner = version.course.creator_id if version else target.creator_id
    if owner != actor.pk:
        raise PermissionDenied
    if not (public_version(version) if version else public_resource(target)):
        raise ValidationError("Publica primero esa versión del contenido.")
    resources = {}
    if kind == "resource":
        resources[target.pk] = target
    else:
        lessons = version.chapters.values_list("lessons__pk", flat=True) if kind == "course" else target.lessons.values_list("pk", flat=True) if kind == "chapter" else [target.pk]
        for lesson in VersionLesson.objects.filter(pk__in=lessons).select_related("content").prefetch_related("attachments__resource"):
            resources[lesson.content_id] = lesson.content
            for attachment in lesson.attachments.all():
                # A text-only offer never silently sells optional paid files.
                if kind != "lesson" or attachment.resource.access_type == "free":
                    resources[attachment.resource_id] = attachment.resource
    if not any(resource.access_type == "paid" for resource in resources.values()):
        raise ValidationError("Este contenido es gratuito; no necesita una oferta.")
    fields = {"course_version": version, "kind": kind}
    if kind != "course":
        fields[kind] = target
    return fields, list(resources.values())


def owned_ids(user, resource_ids):
    if not user.is_authenticated or not user.is_active or user.account_type != "student":
        return set()
    return set(Entitlement.objects.filter(buyer=user, resource_id__in=resource_ids).values_list("resource_id", flat=True))


def ownership(user, offer):
    paid = set(offer.items.filter(resource__access_type="paid").values_list("resource_id", flat=True))
    owned = owned_ids(user, paid)
    return "owned" if paid and owned == paid else "partial" if owned else "none"


def individual_offers(resource_ids):
    return Offer.objects.filter(status="active").filter(Q(kind="lesson", lesson__content_id__in=resource_ids) | Q(kind="resource", resource_id__in=resource_ids)).select_related("creator", "course_version__course", "resource", "lesson__content")


def missing_alternatives(user, offer):
    paid = set(offer.items.filter(resource__access_type="paid").values_list("resource_id", flat=True))
    missing = paid - owned_ids(user, paid)
    return [alternative for alternative in individual_offers(missing) if available(alternative)]


def version_owned(user, version):
    if not user.is_authenticated or not user.is_active or user.account_type != "student":
        return False
    return Entitlement.objects.filter(buyer=user).filter(Q(resource__in=ResourceVersion.objects.filter(pk__in=VersionLesson.objects.filter(chapter__version=version).values("content_id"))) | Q(resource__in=ResourceVersion.objects.filter(pk__in=VersionAttachment.objects.filter(lesson__chapter__version=version).values("resource_id")))).exists()


def version_offers(version):
    offers = Offer.objects.filter(course_version=version, status="active").select_related("creator", "course_version__course").prefetch_related("items__resource")
    return [offer for offer in offers if available(offer)]
