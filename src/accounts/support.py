from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone

from .models import AccountSupportRequest, SupportEvent


@transaction.atomic
def review_support(item, actor, status, response):
    if not actor.is_active or not actor.is_staff or not actor.has_perm("accounts.change_accountsupportrequest"):
        raise PermissionDenied
    AccountSupportRequest.objects.filter(pk=item.pk).update(status=F("status"))
    current = AccountSupportRequest.objects.get(pk=item.pk)
    if status not in ("open", "review", "resolved"):
        raise ValidationError("El estado no está disponible.")
    response = response.strip()
    if status == "resolved" and not response:
        raise ValidationError("Escribe una respuesta antes de cerrar la consulta.")
    if current.status == status and current.response == response:
        return current
    current.status, current.response, current.reviewed_by, current.reviewed_at = status, response, actor, timezone.now()
    current.save(update_fields=("status", "response", "reviewed_by", "reviewed_at"))
    event = SupportEvent.objects.create(request=current, status=status, response=response, actor=actor)
    from learning.support import notify
    notify(current.user, f"account-support:{event.pk}", "Tu solicitud de ayuda tiene una actualización", reverse(f"{'creator' if current.user.account_type == 'creator' else 'student'}-account-support"))
    return current
