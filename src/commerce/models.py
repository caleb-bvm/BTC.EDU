import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from content.immutability import FrozenRecord


class Offer(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PENDING = "pending", "En revisión"
        ACTIVE = "active", "Disponible"
        ARCHIVED = "archived", "Retirada"

    class Kind(models.TextChoices):
        COURSE = "course", "Curso o tutorial"
        CHAPTER = "chapter", "Capítulo"
        LESSON = "lesson", "Texto de lección"
        RESOURCE = "resource", "Video o material"

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField("nombre de la oferta", max_length=200)
    amount_sats = models.PositiveIntegerField("precio en sats de prueba")
    kind = models.CharField(max_length=12, choices=Kind)
    logical_key = models.CharField(max_length=64, default="", editable=False)
    course_version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT, null=True, blank=True)
    chapter = models.ForeignKey("content.VersionChapter", on_delete=models.PROTECT, null=True, blank=True)
    lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT, null=True, blank=True)
    resource = models.ForeignKey("content.ResourceVersion", on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status, default=Status.DRAFT)
    feedback = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="reviewed_offers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-pk",)
        constraints = [models.CheckConstraint(condition=models.Q(amount_sats__gte=1, amount_sats__lte=100000), name="offer_positive_simulated_price"),
            models.UniqueConstraint(fields=("logical_key",), condition=models.Q(status="active"), name="one_active_offer_per_target")]

    def __str__(self):
        return f"{self.title} · {self.amount_sats} sats"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            original = type(self).objects.get(pk=self.pk)
            if any(getattr(self, field) != getattr(original, field) for field in ("creator_id", "title", "amount_sats", "kind", "logical_key", "course_version_id", "chapter_id", "lesson_id", "resource_id")):
                raise ValidationError("Crea otra oferta para cambiar el precio o lo incluido.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Retira la oferta; se conserva su historial.")


class OfferItem(FrozenRecord):
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, related_name="items")
    resource = models.ForeignKey("content.ResourceVersion", on_delete=models.PROTECT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("offer", "resource"), name="unique_offer_resource")]

    def clean(self):
        if self.offer.status != Offer.Status.DRAFT or self.resource.creator_id != self.offer.creator_id:
            raise ValidationError("Solo se puede componer un borrador con recursos propios.")


class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PAID = "paid", "Pagada"
        EXPIRED = "expired", "Vencida"
        FAILED = "failed", "No completada"

    class Issue(models.TextChoices):
        NEW = "new", "Sin emitir"
        REQUESTED = "requested", "Emisión solicitada"
        READY = "ready", "Emitida"
        UNKNOWN = "unknown", "Por conciliar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT)
    logical_key = models.CharField(max_length=64, default="", editable=False)
    title = models.CharField(max_length=200)
    amount_sats = models.PositiveIntegerField()
    inventory = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status, default=Status.PENDING)
    issue_state = models.CharField(max_length=12, choices=Issue, default=Issue.NEW)
    payment_hash = models.CharField(max_length=64, null=True, blank=True, unique=True)
    payment_request = models.TextField(blank=True)
    incident = models.CharField(max_length=40, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("buyer", "logical_key"), condition=models.Q(status="pending"), name="one_pending_invoice_per_offer")]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            original = type(self).objects.get(pk=self.pk)
            if any(getattr(self, field) != getattr(original, field) for field in ("buyer_id", "offer_id", "logical_key", "title", "amount_sats", "inventory", "expires_at")):
                raise ValidationError("La factura conserva el precio y contenido originales.")
        return super().save(*args, **kwargs)


class Purchase(FrozenRecord):
    invoice = models.OneToOneField(Invoice, on_delete=models.PROTECT, related_name="purchase")
    created_at = models.DateTimeField(auto_now_add=True)


class Entitlement(FrozenRecord):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    resource = models.ForeignKey("content.ResourceVersion", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("buyer", "resource"), name="unique_buyer_resource_right")]


class EntitlementSource(FrozenRecord):
    entitlement = models.ForeignKey(Entitlement, on_delete=models.PROTECT)
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("entitlement", "purchase"), name="unique_right_purchase_source")]


class PaymentEvidence(FrozenRecord):
    invoice = models.OneToOneField(Invoice, on_delete=models.PROTECT, related_name="evidence")
    payment_hash = models.CharField(max_length=64, unique=True)
    amount_msat = models.BigIntegerField()
    observed_at = models.DateTimeField()
    resolution = models.CharField(max_length=40)


class CommerceEvent(FrozenRecord):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="events")
    kind = models.CharField(max_length=40)
    message = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("invoice", "kind"), name="unique_invoice_event")]
