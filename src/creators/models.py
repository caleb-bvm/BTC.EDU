from django.conf import settings
from django.db import models
from django.db.models import Q


class CreatorProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Solicitud pendiente"
        APPROVED = "approved", "Aprobado"
        CHANGES = "changes", "Cambios solicitados"
        SUSPENDED = "suspended", "Suspendido"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="creator_profile")
    display_name = models.CharField("nombre público", max_length=160)
    bio = models.TextField("biografía")
    specialty = models.CharField("especialidad", max_length=200)
    website = models.URLField("sitio web", blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.PENDING)
    feedback = models.TextField("observaciones", blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="creator_approvals")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En revisión"
        APPROVED = "approved", "Publicado"
        CHANGES = "changes", "Cambios solicitados"
        WITHDRAWN = "withdrawn", "Retirado por el creador"

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    course = models.ForeignKey("content.Course", on_delete=models.PROTECT, null=True, blank=True)
    video = models.ForeignKey("content.Video", on_delete=models.PROTECT, null=True, blank=True)
    material = models.ForeignKey("content.Material", on_delete=models.PROTECT, null=True, blank=True)
    course_version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT, null=True, blank=True)
    resource_version = models.ForeignKey("content.ResourceVersion", on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.PENDING)
    feedback = models.TextField("observaciones", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="content_reviews")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at", "-pk")
        constraints = [
            models.CheckConstraint(condition=(
                Q(course__isnull=False, course_version__isnull=False, video__isnull=True, material__isnull=True, resource_version__isnull=True)
                | Q(video__isnull=False, resource_version__isnull=False, course__isnull=True, material__isnull=True, course_version__isnull=True)
                | Q(material__isnull=False, resource_version__isnull=False, course__isnull=True, video__isnull=True, course_version__isnull=True)
            ), name="submission_exactly_one_content"),
            *[models.UniqueConstraint(fields=(field,), condition=Q(status="pending"), name=f"one_pending_{field}") for field in ("course", "video", "material")],
        ]

    @property
    def snapshot(self):
        return self.course_version or self.resource_version

    def __str__(self):
        return f"{self.snapshot} · {self.get_status_display()}"
