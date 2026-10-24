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


def target_choices(actor, course=None, resource=None):
    if resource is not None:
        revision = resource.revision
        if resource.creator_id != actor.pk or not revision or revision.access_type != "paid" or not public_resource(revision):
            return []
        return [(f"resource:{revision.pk}", f"{revision.title} · revisión {revision.number} · {revision.get_kind_display()}")]
    versions = CourseVersion.objects.filter(course__creator=actor, sealed=True, course__status="published", pk=F("course__current_version_id"))
    if course is not None:
        versions = versions.filter(course=course)
    choices = []
    for version in versions:
        chapters = list(version.chapters.prefetch_related("lessons__content", "lessons__attachments__resource"))
        paid_chapters = {chapter.pk for chapter in chapters if any(
            lesson.content.access_type == "paid" or any(item.resource.access_type == "paid" for item in lesson.attachments.all())
            for lesson in chapter.lessons.all()
        )}
        if paid_chapters:
            label = "tutorial completo" if version.kind == "tutorial" else "curso completo"
            choices.append((f"course:{version.pk}", f"{version.title} · v{version.number} · {label}"))
        for chapter in chapters:
            if chapter.pk in paid_chapters:
                choices.append((f"chapter:{chapter.pk}", f"{version.title} / {chapter.title} · capítulo"))
            for lesson in chapter.lessons.all():
                if lesson.content.access_type == "paid":
                    choices.append((f"lesson:{lesson.pk}", f"{version.title} / {lesson.content.title} · texto de lección"))
    resources = ResourceVersion.objects.filter(creator=actor, access_type="paid").exclude(kind="text")
    if course is not None:
        resources = resources.filter(pk__in=VersionAttachment.objects.filter(lesson__chapter__version__in=versions).values("resource_id"))
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
    return set(Entitlement.objects.active().filter(buyer=user, resource_id__in=resource_ids).values_list("resource_id", flat=True))


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
    return Entitlement.objects.active().filter(buyer=user).filter(Q(resource__in=ResourceVersion.objects.filter(pk__in=VersionLesson.objects.filter(chapter__version=version).values("content_id"))) | Q(resource__in=ResourceVersion.objects.filter(pk__in=VersionAttachment.objects.filter(lesson__chapter__version=version).values("resource_id")))).exists()


def version_offers(version):
    offers = Offer.objects.filter(course_version=version, status="active").select_related("creator", "course_version__course").prefetch_related("items__resource")
    return [offer for offer in offers if available(offer)]


def lesson_offers(user, lesson):
    """Only purchases that unlock this exact lesson, without charging owned units."""
    offers = Offer.objects.filter(course_version=lesson.chapter.version, status="active",
                                  items__resource_id=lesson.content_id).select_related(
        "creator", "course_version__course", "chapter", "lesson__content"
    ).prefetch_related("items__resource")
    order = {"lesson": 0, "chapter": 1, "course": 2}
    from .pricing import upgrade_quote
    choices = []
    for offer in offers:
        if not available(offer):
            continue
        state = ownership(user, offer)
        # A package partly owned is offered only for the difference, never at full price.
        offer.upgrade = upgrade_quote(user, offer) if state == "partial" else None
        if state == "none" or offer.upgrade:
            choices.append(offer)
    return sorted(choices, key=lambda offer: (order.get(offer.kind, 3), offer.upgrade["amount_sats"] if offer.upgrade else offer.amount_sats, offer.pk))
