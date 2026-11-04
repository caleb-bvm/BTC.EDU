"""Append-only records: published versions, purchases and evidence are never updated or deleted."""
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext


class FrozenQuerySet(models.QuerySet):
    """Queryset that refuses bulk updates, deletes and bulk inserts."""
    def update(self, **kwargs):
        raise ValidationError(gettext("Las revisiones se conservan. Crea una nueva versión."))

    def delete(self):
        raise ValidationError(gettext("Las revisiones no se eliminan."))

    def bulk_create(self, objs, **kwargs):
        raise ValidationError(gettext("Usa el servicio de publicación para crear revisiones."))


class FrozenRecord(models.Model):
    """Abstract model that can be created once, validated, and never changed afterwards."""
    objects = FrozenQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(gettext("Las revisiones no se sobrescriben."))
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(gettext("Las revisiones no se eliminan."))
