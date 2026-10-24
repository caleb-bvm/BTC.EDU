from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from commerce.services import require_student, reserve_writer

from .models import SavedCollection, SavedItem


def locked_student(actor):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)


@transaction.atomic
def change_collection(actor, action, name="", pk=None):
    locked_student(actor)
    collection = None
    if pk is not None:
        collection = SavedCollection.objects.select_for_update().filter(pk=pk, student=actor).first()
        if not collection:
            raise PermissionDenied
    if action == "delete" and collection:
        collection.delete()
        return None
    if action not in ("create", "rename") or (action == "rename" and not collection):
        raise ValidationError("La acción no es válida.")
    name = " ".join(name.split())
    if not name or len(name) > 60:
        raise ValidationError("Usa un nombre de entre 1 y 60 caracteres.")
    if SavedCollection.objects.filter(student=actor, normalized_name=name.casefold()).exclude(pk=pk).exists():
        raise ValidationError("Ya tienes una colección con ese nombre.")
    collection = collection or SavedCollection(student=actor)
    collection.name, collection.normalized_name = name, name.casefold()
    collection.full_clean()
    collection.save()
    return collection


@transaction.atomic
def organize_item(actor, item_id, collection_ids):
    locked_student(actor)
    item = SavedItem.objects.select_for_update().filter(pk=item_id, student=actor).first()
    if not item:
        raise PermissionDenied
    try:
        ids = {int(pk) for pk in collection_ids}
    except (ValueError, TypeError):
        raise ValidationError("Selecciona tus colecciones de nuevo.")
    collections = list(SavedCollection.objects.filter(student=actor, pk__in=ids))
    if len(collections) != len(ids):
        raise PermissionDenied
    item.collections.set(collections)

