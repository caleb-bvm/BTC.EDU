from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import F
from django.urls import reverse

from accounts.models import User
from commerce.models import Entitlement
from commerce.services import require_student
from content.models import (
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
    if Entitlement.objects.filter(buyer=user, resource=resource).exists():
        return reverse("purchased-resource", args=[resource.pk])
    return ""


@transaction.atomic
def save_item(actor, kind, pk, action):
    require_student(actor)
    User.objects.filter(pk=actor.pk).update(profile_public=F("profile_public"))
    actor.refresh_from_db()
    require_student(actor)
    if action not in ("save", "remove") or kind not in ("recurso", "referencia"):
        raise ValidationError("Elige una acción disponible.")
    field = "resource" if kind == "recurso" else "reference"
    if action == "remove":
        SavedItem.objects.filter(student=actor, **{field + "_id": pk}).delete()
        return None
    if kind == "referencia":
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


def bookmark_context(user, resource=None, reference=None):
    if not resource and not reference:
        return {}
    field, item = ("resource", resource) if resource else ("reference", reference)
    saved = user.is_authenticated and user.account_type == "student" and SavedItem.objects.filter(student=user, **{field: item}).exists()
    return {"bookmark_enabled": True, "bookmark_kind": "recurso" if resource else "referencia", "bookmark_pk": item.pk, "is_saved": saved}
