from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import F
from django.urls import reverse

from accounts.models import User
from commerce.models import Entitlement
from commerce.services import require_student
from content.models import (
    CourseVersion,
    ExternalReference,
    Material,
    ResourceVersion,
    Video,
)

from .models import SavedItem


def resource_target(user, resource):
    for model, kind in ((Video, "videos"), (Material, "materiales")):
        item = model.objects.filter(revision=resource, status="published").first()
        if item:
            return reverse("resource-detail", args=[kind, item.pk])
    if Entitlement.objects.active().filter(buyer=user, resource=resource).exists():
        return reverse("purchased-resource", args=[resource.pk])
    return ""


def course_target(user, version):
    from .services import can_visit_version
    if version.sealed and version.published_at and version.course.status in ("published", "archived") and can_visit_version(user, version):
        return reverse("course-version", args=[version.course_id, version.number])
    return ""


@transaction.atomic
def save_item(actor, kind, pk, action):
    require_student(actor)
    User.objects.filter(pk=actor.pk).update(profile_public=F("profile_public"))
    actor.refresh_from_db()
    require_student(actor)
    if action not in ("save", "remove") or kind not in ("recurso", "referencia", "curso", "tutorial"):
        raise ValidationError("Elige una acción disponible.")
    field = {"recurso": "resource", "referencia": "reference", "curso": "course_version", "tutorial": "course_version"}[kind]
    if action == "remove":
        SavedItem.objects.filter(student=actor, **{field + "_id": pk}).delete()
        return None
    if field == "course_version":
        item = CourseVersion.objects.select_related("course").filter(pk=pk).first()
        if not item or not course_target(actor, item):
            raise PermissionDenied
        defaults = {"title": item.title}
    elif kind == "referencia":
        item = ExternalReference.objects.filter(pk=pk, status="published").first()
        if not item:
            raise PermissionDenied
        URLValidator(schemes=["http", "https"])(item.source_url)
        defaults = {"title": item.title, "source_url": item.source_url}
    else:
        item = ResourceVersion.objects.filter(pk=pk).first()
        if not item or not resource_target(actor, item):
            raise PermissionDenied
        defaults = {"title": item.title}
    return SavedItem.objects.get_or_create(student=actor, **{field: item}, defaults=defaults)[0]


def bookmark_context(user, resource=None, reference=None, course_version=None):
    if sum(bool(item) for item in (resource, reference, course_version)) != 1:
        return {}
    field, item = ("resource", resource) if resource else ("reference", reference) if reference else ("course_version", course_version)
    saved = bool(user.is_authenticated and user.is_active and user.account_type == "student" and SavedItem.objects.filter(student=user, **{field: item}).exists())
    kind = "recurso" if resource else "referencia" if reference else "tutorial" if course_version.kind == "tutorial" else "curso"
    return {"bookmark_enabled": True, "bookmark_kind": kind, "bookmark_pk": item.pk, "is_saved": saved}


def saved_item_presentation(user, item):
    if item.course_version_id:
        version = item.course_version
        item.bookmark_kind, item.bookmark_target_pk = "tutorial" if version.kind == "tutorial" else "curso", version.pk
        item.type_label = f"{version.get_kind_display()} · Versión {version.number}"
        item.open_label = "Abrir tutorial" if version.kind == "tutorial" else "Abrir curso"
        item.available = bool(course_target(user, version))
    elif item.resource_id:
        item.bookmark_kind, item.bookmark_target_pk = "recurso", item.resource_id
        item.type_label = f"{item.resource.get_kind_display()} · Revisión {item.resource.number}"
        item.open_label = "Abrir recurso"
        item.available = bool(resource_target(user, item.resource))
    else:
        item.bookmark_kind, item.bookmark_target_pk = "referencia", item.reference_id
        item.type_label, item.open_label = "Fuente externa", "Abrir referencia"
        item.available = item.reference.status == "published"
    return item
