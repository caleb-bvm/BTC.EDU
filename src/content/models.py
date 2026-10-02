from django.conf import settings
from django.db import models


class PublicationStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicado"


class AccessType(models.TextChoices):
    FREE = "free", "Gratis"
    PAID = "paid", "De pago"


class Publication(models.Model):
    title = models.CharField("título", max_length=200)
    description = models.TextField("descripción", blank=True)
    status = models.CharField("estado", max_length=12, choices=PublicationStatus, default=PublicationStatus.DRAFT)
    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        abstract = True
        ordering = ("title", "pk")

    def __str__(self):
        return self.title


class Course(Publication):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="courses", verbose_name="creador")
    objective = models.TextField("objetivo", blank=True)
    requirements = models.TextField("requisitos", blank=True)

    class Meta(Publication.Meta):
        abstract = False
        verbose_name = "curso"
        verbose_name_plural = "cursos"


class Chapter(Publication):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters", verbose_name="curso")
    position = models.PositiveIntegerField("orden", default=1)

    class Meta:
        ordering = ("position", "pk")
        verbose_name = "capítulo"
        verbose_name_plural = "capítulos"
        constraints = [models.UniqueConstraint(fields=("course", "position"), name="unique_chapter_position")]


class Lesson(Publication):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="lessons", verbose_name="capítulo")
    position = models.PositiveIntegerField("orden", default=1)
    access_type = models.CharField("acceso", max_length=8, choices=AccessType, default=AccessType.FREE)
    body = models.TextField("contenido de texto", blank=True)

    class Meta:
        ordering = ("position", "pk")
        verbose_name = "lección"
        verbose_name_plural = "lecciones"
        constraints = [models.UniqueConstraint(fields=("chapter", "position"), name="unique_lesson_position")]


class StandaloneResource(Publication):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="creador")
    access_type = models.CharField("acceso", max_length=8, choices=AccessType, default=AccessType.FREE)

    class Meta(Publication.Meta):
        abstract = True


class Video(StandaloneResource):
    class Meta(StandaloneResource.Meta):
        abstract = False
        verbose_name = "video"
        verbose_name_plural = "videos"


class Material(StandaloneResource):
    class Meta(StandaloneResource.Meta):
        abstract = False
        verbose_name = "material"
        verbose_name_plural = "materiales"
