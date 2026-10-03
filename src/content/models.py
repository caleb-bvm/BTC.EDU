import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models

from .immutability import FrozenRecord


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
    current_version = models.ForeignKey("CourseVersion", on_delete=models.PROTECT, null=True, blank=True, related_name="+", editable=False)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.current_version_id = type(self).objects.values_list("current_version_id", flat=True).get(pk=self.pk)
        return super().save(*args, **kwargs)

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
    resource_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ("position", "pk")
        verbose_name = "lección"
        verbose_name_plural = "lecciones"
        constraints = [models.UniqueConstraint(fields=("chapter", "position"), name="unique_lesson_position")]


class StandaloneResource(Publication):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="creador")
    access_type = models.CharField("acceso", max_length=8, choices=AccessType, default=AccessType.FREE)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="tema")
    resource_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    pending_asset = models.ForeignKey("media.Asset", on_delete=models.PROTECT, null=True, blank=True, related_name="+", verbose_name="archivo de la próxima revisión")
    pending_subtitles = models.ForeignKey("media.Asset", on_delete=models.PROTECT, null=True, blank=True, related_name="+", verbose_name="subtítulos VTT de la próxima revisión")
    transcript = models.TextField("transcripción", blank=True)
    revision = models.ForeignKey("ResourceVersion", on_delete=models.PROTECT, null=True, blank=True, related_name="+", editable=False)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.revision_id = type(self).objects.values_list("revision_id", flat=True).get(pk=self.pk)
        return super().save(*args, **kwargs)

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


class ResourceVersion(FrozenRecord):
    resource_key = models.UUIDField(default=uuid.uuid4)
    number = models.PositiveIntegerField(default=1)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    kind = models.CharField(max_length=12, choices=(("text", "Texto"), ("video", "Video"), ("material", "Material")))
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    access_type = models.CharField(max_length=8, choices=AccessType)
    body = models.TextField(blank=True)
    asset = models.ForeignKey("media.Asset", on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    subtitles = models.ForeignKey("media.Asset", on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("resource_key", "number"), name="unique_resource_revision")]
        verbose_name = "revisión de recurso"
        verbose_name_plural = "revisiones de recursos"

    def __str__(self):
        return f"{self.title} · v{self.number}"

    def clean(self):
        if self.kind == "text":
            if self.asset_id or self.subtitles_id or not self.body.strip():
                raise ValidationError("Un recurso de texto requiere contenido y no admite archivos.")
        elif not self.asset_id or self.asset.kind != self.kind or self.asset.creator_id != self.creator_id:
            raise ValidationError("El archivo debe pertenecer al creador y corresponder al formato del recurso.")
        if self.subtitles_id and (self.kind != "video" or self.subtitles.kind != "subtitle" or self.subtitles.creator_id != self.creator_id):
            raise ValidationError("Los subtítulos deben ser VTT del mismo propietario y acompañar un video.")


class CourseVersion(FrozenRecord):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="versions")
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    objective = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    kind = models.CharField(max_length=12, choices=CourseKind)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, null=True, blank=True)
    level = models.CharField(max_length=12, choices=CourseLevel, blank=True)
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    creator_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    sealed = models.BooleanField(default=False, editable=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("course", "number"), name="unique_course_version")]
        verbose_name = "versión publicada"
        verbose_name_plural = "versiones publicadas"

    def __str__(self):
        return f"{self.title} · v{self.number}"

    def clean(self):
        if self.course_id and self.course.current_version_id and self.course.current_version.course_id != self.course_id:
            raise ValidationError("La versión vigente debe pertenecer al curso.")


class VersionChapter(FrozenRecord):
    version = models.ForeignKey(CourseVersion, on_delete=models.PROTECT, related_name="chapters")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ("position", "pk")
        constraints = [models.UniqueConstraint(fields=("version", "position"), name="unique_version_chapter_position")]

    def clean(self):
        if self.version.sealed:
            raise ValidationError("No se pueden añadir capítulos a la versión ya publicada.")


class VersionLesson(FrozenRecord):
    chapter = models.ForeignKey(VersionChapter, on_delete=models.PROTECT, related_name="lessons")
    source_lesson_id = models.PositiveBigIntegerField()
    position = models.PositiveIntegerField()
    content = models.ForeignKey(ResourceVersion, on_delete=models.PROTECT, related_name="+")

    class Meta:
        ordering = ("position", "pk")
        constraints = [models.UniqueConstraint(fields=("chapter", "position"), name="unique_version_lesson_position")]

    def clean(self):
        version = self.chapter.version
        if version.sealed or self.content.kind != "text" or self.content.creator_id != version.course.creator_id:
            raise ValidationError("Lección incompatible o versión ya publicada.")


class LessonResource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attachments")
    resource = models.ForeignKey(ResourceVersion, on_delete=models.PROTECT, verbose_name="revisión de recurso")
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("position", "pk")
        constraints = [models.UniqueConstraint(fields=("lesson", "position"), name="unique_lesson_attachment_position")]

    def clean(self):
        if self.resource_id and self.lesson_id and (self.resource.kind == "text" or self.resource.creator_id != self.lesson.chapter.course.creator_id):
            raise ValidationError("Adjunta un video o material del mismo creador.")


class VersionAttachment(FrozenRecord):
    lesson = models.ForeignKey(VersionLesson, on_delete=models.PROTECT, related_name="attachments")
    resource = models.ForeignKey(ResourceVersion, on_delete=models.PROTECT, related_name="+")
    position = models.PositiveIntegerField()

    class Meta:
        ordering = ("position", "pk")
        constraints = [models.UniqueConstraint(fields=("lesson", "position"), name="unique_version_attachment_position")]

    def clean(self):
        version = self.lesson.chapter.version
        if version.sealed or self.resource.kind == "text" or self.resource.creator_id != version.course.creator_id:
            raise ValidationError("Adjunto incompatible o versión ya publicada.")
