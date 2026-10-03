from django.conf import settings
from django.core.validators import URLValidator
from django.db import models


class PublicationStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicado"


class AccessType(models.TextChoices):
    FREE = "free", "Gratis"
    PAID = "paid", "De pago"


class CourseKind(models.TextChoices):
    COURSE = "course", "Curso"
    TUTORIAL = "tutorial", "Tutorial"


class CourseLevel(models.TextChoices):
    BEGINNER = "beginner", "Principiante"
    INTERMEDIATE = "intermediate", "Intermedio"
    ADVANCED = "advanced", "Avanzado"


class Topic(models.Model):
    name = models.CharField("nombre", max_length=100, unique=True)
    slug = models.SlugField("identificador", unique=True)

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "tema"
        verbose_name_plural = "temas"

    def __str__(self):
        return self.name


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
    kind = models.CharField("tipo", max_length=12, choices=CourseKind, default=CourseKind.COURSE)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="tema")
    level = models.CharField("nivel", max_length=12, choices=CourseLevel, blank=True)
    estimated_minutes = models.PositiveIntegerField("duración estimada en minutos", null=True, blank=True)

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
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="tema")

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


class ExternalReference(Publication):
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="tema")
    source_name = models.CharField("fuente", max_length=160)
    source_url = models.URLField("enlace a la fuente", max_length=500, validators=[URLValidator(schemes=["http", "https"])])

    class Meta(Publication.Meta):
        abstract = False
        verbose_name = "referencia externa"
        verbose_name_plural = "referencias externas"
