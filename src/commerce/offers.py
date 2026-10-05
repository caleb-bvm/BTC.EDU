from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F

from creators.services import require_creator

from .catalog import (
    individual_offers,
    public_resource,
    public_version,
    target_inventory,
)
from .models import Offer, OfferItem


@transaction.atomic
def create_offer(actor, target, title, amount):
    require_creator(actor)
    get_user_model().objects.filter(pk=actor.pk).update(email=F("email"))
    require_creator(actor)
    try:
        kind, pk = target.split(":")
        fields, resources = target_inventory(kind, int(pk), actor)
    except (ValueError, KeyError):
        raise ValidationError("Elige contenido publicado.") from None
    offer = Offer.objects.create(creator=actor, title=title.strip(), amount_sats=amount, logical_key=f"{kind}:{int(pk)}", **fields)
    for resource in resources:
        OfferItem.objects.create(offer=offer, resource=resource)
    return offer


def validate_inventory(offer):
    target = offer.course_version_id if offer.kind == "course" else offer.chapter_id if offer.kind == "chapter" else offer.lesson_id if offer.kind == "lesson" else offer.resource_id
    fields, resources = target_inventory(offer.kind, target, offer.creator)
    if fields["course_version"] != offer.course_version or set(offer.items.values_list("resource_id", flat=True)) != {item.pk for item in resources}:
        raise ValidationError("La composición de la oferta no corresponde al contenido.")


@transaction.atomic
def submit_offer(actor, offer):
    require_creator(actor)
    Offer.objects.filter(pk=offer.pk).update(status=F("status"))
    offer.refresh_from_db()
    require_creator(actor)
    if offer.creator_id != actor.pk:
        raise PermissionDenied
    if offer.status != "draft":
        raise ValidationError("Solo puedes enviar una oferta en borrador.")
    validate_inventory(offer)
    offer.status = "pending"
    offer.feedback = ""
    offer.save(update_fields=("status", "feedback"))
    return offer


def missing_individuals(offer):
    paid = set(offer.items.filter(resource__access_type="paid").values_list("resource_id", flat=True))
    covered = set()
    for individual in individual_offers(paid):
        if public_version(individual.course_version) if individual.course_version_id else public_resource(individual.resource):
            covered.add(individual.lesson.content_id if individual.kind == "lesson" else individual.resource_id)
    return list(offer.items.select_related("resource").filter(resource_id__in=paid - covered))


@transaction.atomic
def review_offer(actor, offer, approve, feedback=""):
    if not actor.is_authenticated or not actor.is_active or not actor.is_staff or not actor.has_perm("commerce.change_offer"):
        raise PermissionDenied
    Offer.objects.filter(pk=offer.pk).update(status=F("status"))
    offer.refresh_from_db()
    if offer.status != "pending":
        raise ValidationError("La oferta ya fue revisada o retirada.")
    if approve:
        require_creator(offer.creator)
        validate_inventory(offer)
        if offer.kind in ("course", "chapter"):
            missing = missing_individuals(offer)
            if missing:
                raise ValidationError("Publica primero ofertas individuales para: " + ", ".join(item.resource.title for item in missing))
    elif not feedback.strip():
        raise ValidationError("Indica qué debe corregirse.")
    offer.status = "active" if approve else "draft"
    if approve:
        Offer.objects.filter(logical_key=offer.logical_key, status="active").exclude(pk=offer.pk).update(status="archived")
    offer.feedback = feedback.strip()
    offer.reviewed_by = actor
    offer.save(update_fields=("status", "feedback", "reviewed_by"))
    return offer


@transaction.atomic
def archive_offer(actor, offer):
    Offer.objects.filter(pk=offer.pk).update(status=F("status"))
    offer.refresh_from_db()
    if actor.pk == offer.creator_id:
        require_creator(actor)
    elif not actor.is_active or not actor.is_staff or not actor.has_perm("commerce.change_offer"):
        raise PermissionDenied
    offer.status = "archived"
    offer.save(update_fields=("status",))
