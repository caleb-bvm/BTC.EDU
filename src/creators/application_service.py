from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from learning.support import notify

from .models import CreatorApplicationEvent, CreatorProfile


@transaction.atomic
def save_application(actor, values, expected_revision=None):
    User.objects.filter(pk=actor.pk).update(profile_public=F("profile_public"))
    actor.refresh_from_db()
    if not actor.is_active or actor.account_type != "creator":
        raise PermissionDenied
    current = CreatorProfile.objects.filter(user=actor).first()
    if current and current.status == "suspended":
        raise PermissionDenied
    if current and expected_revision is not None and current.review_revision != expected_revision:
        raise ValidationError("Tu solicitud cambió mientras editabas. Recarga para consultar la decisión antes de guardar.")
    previous = current.status if current else ""
    profile = current or CreatorProfile(user=actor)
    for field in ("display_name", "bio", "specialty", "website"):
        setattr(profile, field, values[field])
    profile.status = "pending" if previous in ("", "changes") else previous
    profile.review_revision += 1
    profile.save()
    CreatorApplicationEvent.objects.create(profile=profile, actor=actor, previous_status=previous, status=profile.status,
                                            kind="submitted" if previous in ("", "changes") else "profile_updated")
    return profile


@transaction.atomic
def review_application(profile, actor, status, feedback, expected_revision=None):
    if not actor.is_active or not actor.is_staff or not actor.has_perm("creators.change_creatorprofile"):
        raise PermissionDenied
    CreatorProfile.objects.filter(pk=profile.pk).update(updated_at=F("updated_at"))
    current = CreatorProfile.objects.select_related("user").get(pk=profile.pk)
    if expected_revision is not None and current.review_revision != expected_revision:
        raise ValidationError("La solicitud cambió. Recarga antes de registrar otra decisión.")
    if status not in CreatorProfile.Status.values:
        raise ValidationError("Elige un estado disponible.")
    if status == "approved" and settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL and not current.user.email_verified_at:
        raise ValidationError("El creador debe confirmar su correo antes de aprobar su cuenta.")
    feedback = feedback.strip()
    if status in ("changes", "suspended") and not feedback:
        raise ValidationError("Explica el motivo para que el creador pueda actuar.")
    if current.status == status and current.feedback == feedback:
        return current
    previous = current.status
    current.status, current.feedback = status, feedback
    current.reviewed_by, current.reviewed_at = actor, timezone.now()
    current.review_revision += 1
    current.save(update_fields=("status", "feedback", "reviewed_by", "reviewed_at", "review_revision", "updated_at"))
    event = CreatorApplicationEvent.objects.create(profile=current, actor=actor, previous_status=previous, status=status, kind="decision", reason=feedback)
    titles = {"approved": "Tu cuenta de creador está aprobada", "changes": "Tu solicitud necesita algunos cambios", "suspended": "Consulta el estado de tu cuenta de creador", "pending": "Tu solicitud vuelve a estar en revisión"}
    notify(current.user, f"creator-application:{event.pk}", titles[status], reverse("creator-application"))
    return current
