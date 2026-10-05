from dataclasses import dataclass

from .models import (
    AccessType,
    Chapter,
    Course,
    Lesson,
    PublicationStatus,
    VersionAttachment,
    VersionLesson,
)


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reason: str


def content_access(user, resource):
    """One authorization rule for HTML, JSON, files and frozen purchases."""
    if isinstance(resource, VersionAttachment):
        decision = content_access(user, resource.lesson)
        if not decision.allowed:
            return decision
        if decision.reason == "creator_preview" or resource.resource.access_type == AccessType.FREE:
            return decision
        if owns_revision(user, resource.resource_id):
            return AccessDecision(True, "purchase")
        return AccessDecision(False, "purchase_required")
    if isinstance(resource, VersionLesson):
        version = resource.chapter.version
        course = version.course
        if user.is_authenticated and user.is_active and user.pk == course.creator_id:
            return AccessDecision(True, "creator_preview")
        from learning.services import can_visit_version, enrolled
        if not version.sealed or course.status not in (PublicationStatus.PUBLISHED, PublicationStatus.ARCHIVED) or not can_visit_version(user, version):
            return AccessDecision(False, "unpublished")
        if owns_revision(user, resource.content_id):
            return AccessDecision(True, "purchase")
        if course.current_version_id != version.pk or course.status == PublicationStatus.ARCHIVED:
            if resource.content.access_type == AccessType.FREE and enrolled(user, version):
                return AccessDecision(True, "enrolled_free")
            return AccessDecision(False, "purchase_required")
        return AccessDecision(resource.content.access_type == AccessType.FREE, "free" if resource.content.access_type == AccessType.FREE else "purchase_required")
    if isinstance(resource, Lesson):
        chapter = resource.chapter
        course = chapter.course
        publications = (course, chapter, resource)
        creator_id = course.creator_id
    elif isinstance(resource, Chapter):
        publications = (resource.course, resource)
        creator_id = resource.course.creator_id
    elif isinstance(resource, Course):
        publications = (resource,)
        creator_id = resource.creator_id
    else:
        publications = (resource,)
        creator_id = resource.creator_id

    if user.is_authenticated and user.is_active and user.pk == creator_id:
        return AccessDecision(True, "creator_preview")
    if any(item.status != PublicationStatus.PUBLISHED for item in publications):
        return AccessDecision(False, "unpublished")
    revision = getattr(resource, "revision", None)
    if revision and owns_revision(user, revision.pk):
        return AccessDecision(True, "purchase")
    access_type = revision.access_type if revision else getattr(resource, "access_type", AccessType.FREE)
    if access_type == AccessType.FREE:
        return AccessDecision(True, "free")
    return AccessDecision(False, "purchase_required")


def owns_revision(user, resource_id):
    if not user.is_authenticated or not user.is_active or user.account_type != "student":
        return False
    from commerce.models import Entitlement
    return Entitlement.objects.filter(buyer=user, resource_id=resource_id).exists()
