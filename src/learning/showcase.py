"""Course project gallery: approved practices the student chose to share."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import PracticeDelivery, PracticeShowcase


def gallery_items(course):
    return (PracticeShowcase.objects.filter(public=True, hidden=False, delivery__practice__lesson__chapter__version__course=course,
                                            delivery__review__outcome="accepted")
            .select_related("delivery__enrollment__student", "delivery__practice__lesson__content",
                            "delivery__practice__lesson__chapter__version", "delivery__review")
            .order_by("-created_at", "-pk"))


@transaction.atomic
def set_showcase(actor, delivery_id, public):
    delivery = PracticeDelivery.objects.select_related("enrollment", "review").get(pk=delivery_id)
    if not actor.is_authenticated or delivery.enrollment.student_id != actor.pk:
        raise PermissionDenied
    if delivery.state != "accepted":
        raise ValidationError("Solo puedes compartir prácticas aprobadas.")
    showcase, created = PracticeShowcase.objects.get_or_create(delivery=delivery, defaults={"public": public})
    if not created and showcase.public != public:
        PracticeShowcase.objects.filter(pk=showcase.pk).update(public=public)
        showcase.refresh_from_db()
    return showcase
