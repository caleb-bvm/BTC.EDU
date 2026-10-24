"""Gift links: the buyer pays, whoever redeems the link receives the access."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from .models import Entitlement, EntitlementSource, Gift
from .services import require_student, reserve_writer


def gift_for_token(token):
    return (Gift.objects.select_related("order__buyer", "purchase__invoice", "recipient")
            .prefetch_related("order__lines__creator__creator_profile", "order__lines__course_version")
            .filter(token=str(token or "")[:64]).first())


@transaction.atomic
def redeem_gift(actor, token):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    gift = Gift.objects.select_related("order", "purchase__invoice").filter(token=str(token or "")[:64]).first()
    if gift is None:
        raise ValidationError("Este enlace de regalo no es válido.")
    if gift.recipient_id:
        raise ValidationError("Este regalo ya fue canjeado." if gift.recipient_id != actor.pk else "Ya canjeaste este regalo. Lo encontrarás en Mi aprendizaje.")
    if gift.order.buyer_id == actor.pk:
        raise ValidationError("Comparte este enlace con la persona a quien quieres regalar el contenido.")
    if gift.purchase.invoice.status != "paid":
        raise ValidationError("Este regalo todavía no está disponible.")
    now = timezone.now()
    # Only an unredeemed gift changes state; a concurrent redemption updates nothing.
    if not Gift.objects.filter(pk=gift.pk, recipient__isnull=True).update(recipient=actor, redeemed_at=now):
        raise ValidationError("Este regalo ya fue canjeado.")
    for item in {item["resource_id"]: item for item in gift.order.inventory}.values():
        right, _ = Entitlement.objects.get_or_create(buyer=actor, resource_id=item["resource_id"])
        if not EntitlementSource.objects.filter(entitlement=right, purchase=gift.purchase).exists():
            EntitlementSource.objects.create(entitlement=right, purchase=gift.purchase)
    from learning.models import Enrollment
    for version_id in set(gift.order.lines.exclude(course_version=None).values_list("course_version_id", flat=True)):
        Enrollment.objects.get_or_create(student=actor, version_id=version_id)
    from learning.support import notify
    notify(gift.order.buyer, f"gift-redeemed:{gift.pk}", f"Tu regalo «{gift.order.lines.first().title}» fue canjeado.", reverse("purchases"))
    gift.refresh_from_db()
    return gift
