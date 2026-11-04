"""Creator profiles, application history and content submissions."""
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy

from content.immutability import FrozenRecord


class CreatorProfile(models.Model):
    """Creator application and public profile; only approved creators can publish."""
    class Status(models.TextChoices):
        PENDING = "pending", gettext_lazy("Solicitud pendiente")
        APPROVED = "approved", gettext_lazy("Aprobado")
        CHANGES = "changes", gettext_lazy("Cambios solicitados")
        SUSPENDED = "suspended", gettext_lazy("Suspendido")

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="creator_profile")
    display_name = models.CharField(gettext_lazy("nombre público"), max_length=160)
    bio = models.TextField(gettext_lazy("biografía"))
    specialty = models.CharField("especialidad", max_length=200)
    website = models.URLField("sitio web", blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.PENDING)
    feedback = models.TextField("observaciones", blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="creator_approvals")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    review_revision = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.display_name


class CreatorApplicationEvent(FrozenRecord):
    """Append-only history of an application."""
    profile = models.ForeignKey(CreatorProfile, on_delete=models.PROTECT, related_name="history")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    previous_status = models.CharField(max_length=12, blank=True)
    status = models.CharField(max_length=12, choices=CreatorProfile.Status)
    kind = models.CharField(max_length=20, choices=(("submitted", gettext_lazy("Solicitud enviada")), ("profile_updated", gettext_lazy("Perfil actualizado")), ("decision", gettext_lazy("Decisión de revisión"))))
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-pk")


class Submission(models.Model):
    """Request to publish a course or resource, holding the frozen copy under review."""
    class Status(models.TextChoices):
        PENDING = "pending", gettext_lazy("En revisión")
        APPROVED = "approved", gettext_lazy("Publicado")
        CHANGES = "changes", gettext_lazy("Cambios solicitados")
        WITHDRAWN = "withdrawn", gettext_lazy("Retirado por el creador")

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
