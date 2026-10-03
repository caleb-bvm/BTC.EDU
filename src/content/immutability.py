from django.core.exceptions import ValidationError
from django.db import models


class FrozenQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Las revisiones se conservan. Crea una nueva versión.")

    def delete(self):
        raise ValidationError("Las revisiones no se eliminan.")

    def bulk_create(self, objs, **kwargs):
        raise ValidationError("Usa el servicio de publicación para crear revisiones.")


class FrozenRecord(models.Model):
    objects = FrozenQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Las revisiones no se sobrescriben.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Las revisiones no se eliminan.")
