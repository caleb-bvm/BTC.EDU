import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from content.immutability import FrozenQuerySet, FrozenRecord


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


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
                                related_name="commerce_cart")
    revision = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, related_name="cart_items")
    return_lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT, null=True, blank=True,
                                     related_name="cart_origins")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "pk")
        constraints = [models.UniqueConstraint(fields=("cart", "offer"), name="unique_cart_offer")]


class Order(FrozenRecord):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="commerce_orders")
    title = models.CharField(max_length=200)
    amount_sats = models.PositiveIntegerField()
    inventory = models.JSONField()
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, null=True, blank=True, related_name="orders")
    cart_revision = models.PositiveIntegerField(default=0)
    fingerprint = models.CharField(max_length=64)
    request_key = models.UUIDField(default=uuid.uuid4, editable=False)
    sealed = models.BooleanField(default=False, editable=False)
    # A gift order grants nothing to the buyer; its access is redeemed through a link.
    gift = models.BooleanField(default=False)
    gift_message = models.CharField(max_length=280, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("buyer", "request_key"), name="unique_order_buyer_request"),
                       models.CheckConstraint(condition=models.Q(amount_sats__gte=1, amount_sats__lte=2000000), name="order_total_bounds")]


class OrderLine(FrozenRecord):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="lines")
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, related_name="order_lines")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sale_order_lines")
    title = models.CharField(max_length=200)
    amount_sats = models.PositiveIntegerField()
    logical_key = models.CharField(max_length=64)
    course_version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT, null=True, blank=True,
                                       related_name="order_lines")
    inventory = models.JSONField()
    return_lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT, null=True, blank=True,
                                     related_name="order_origins")
    cart_item_key = models.UUIDField(null=True, blank=True)
    position = models.PositiveIntegerField(default=1)
    # The line charges the offer price minus recognized purchases and a coupon.
    credit_sats = models.PositiveIntegerField(default=0)
    coupon = models.ForeignKey("Coupon", on_delete=models.PROTECT, null=True, blank=True, related_name="order_lines")
    discount_sats = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("position", "pk")
        constraints = [models.UniqueConstraint(fields=("order", "offer"), name="unique_order_offer"),
                       models.UniqueConstraint(fields=("order", "position"), name="unique_order_line_position")]

    def clean(self):
        if self.order.sealed or self.creator_id != self.offer.creator_id:
            raise ValidationError("El pedido solo se compone antes de confirmar su selección, con el educador de cada oferta.")
        if self.amount_sats + self.credit_sats + self.discount_sats != self.offer.amount_sats or self.course_version_id != self.offer.course_version_id:
            raise ValidationError("La línea debe conservar el precio y la versión de su oferta.")
        if bool(self.discount_sats) != bool(self.coupon_id) or (self.coupon_id and self.coupon.creator_id != self.creator_id):
            raise ValidationError("Un descuento requiere un cupón del educador de la oferta.")
        resources = {item.resource_id for item in self.offer.items.all()}
        included = {item["resource_id"] for item in self.inventory}
        # A credited line completes a package and keeps only the components still missing.
        if (not included or not included < resources) if self.credit_sats else included != resources:
            raise ValidationError("La línea debe conservar todo el inventario de su oferta.")
        if self.return_lesson_id and (self.return_lesson.chapter.version_id != self.course_version_id or self.return_lesson.content_id not in resources):
            raise ValidationError("El destino elegido debe formar parte de la oferta.")


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
    offer = models.ForeignKey(Offer, on_delete=models.PROTECT, null=True, blank=True)
    order = models.OneToOneField(Order, on_delete=models.PROTECT, null=True, blank=True, related_name="invoice")
    logical_key = models.CharField(max_length=64, default="", editable=False)
    title = models.CharField(max_length=200)
    amount_sats = models.PositiveIntegerField()
    inventory = models.JSONField()
    return_lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT, null=True, blank=True,
                                      related_name="purchase_returns")
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
        constraints = [models.UniqueConstraint(fields=("buyer", "logical_key"), condition=models.Q(status="pending"), name="one_pending_invoice_per_offer"),
                       models.CheckConstraint(condition=(models.Q(offer__isnull=False, order__isnull=True) |
                                                         models.Q(offer__isnull=True, order__isnull=False)), name="invoice_exactly_one_target")]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            original = type(self).objects.get(pk=self.pk)
            if any(getattr(self, field) != getattr(original, field) for field in ("buyer_id", "offer_id", "order_id", "logical_key", "title", "amount_sats", "inventory", "expires_at")):
                raise ValidationError("La factura conserva el precio y contenido originales.")
        return super().save(*args, **kwargs)


class Purchase(FrozenRecord):
    invoice = models.OneToOneField(Invoice, on_delete=models.PROTECT, related_name="purchase")
    created_at = models.DateTimeField(auto_now_add=True)


class EntitlementQuerySet(FrozenQuerySet):
    def active(self):
        """A right ends only when every purchase that granted it was refunded."""
        sources = EntitlementSource.objects.filter(entitlement=models.OuterRef("pk"))
        refunded = sources.filter(purchase__invoice__refund__status="refunded")
        return self.exclude(models.Exists(refunded) & ~models.Exists(sources.exclude(purchase__invoice__refund__status="refunded")))


class Entitlement(FrozenRecord):
    objects = EntitlementQuerySet.as_manager()
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


class Coupon(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="coupons")
    code = models.CharField("código", max_length=24, unique=True)
    percent_off = models.PositiveSmallIntegerField("porcentaje de descuento", null=True, blank=True)
    amount_off_sats = models.PositiveIntegerField("descuento en sats", null=True, blank=True)
    course = models.ForeignKey("content.Course", on_delete=models.PROTECT, null=True, blank=True, related_name="coupons",
                               verbose_name="curso o tutorial")
    starts_at = models.DateTimeField("desde")
    expires_at = models.DateTimeField("vence")
    max_uses = models.PositiveIntegerField("usos disponibles")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-pk")
        constraints = [
            models.CheckConstraint(condition=(models.Q(percent_off__isnull=False, amount_off_sats__isnull=True)
                                              | models.Q(percent_off__isnull=True, amount_off_sats__isnull=False)), name="coupon_one_discount"),
            models.CheckConstraint(condition=models.Q(percent_off__isnull=True) | models.Q(percent_off__gte=1, percent_off__lte=90), name="coupon_percent_bounds"),
            models.CheckConstraint(condition=models.Q(amount_off_sats__isnull=True) | models.Q(amount_off_sats__gte=1, amount_off_sats__lte=100000), name="coupon_amount_bounds"),
            models.CheckConstraint(condition=models.Q(max_uses__gte=1, max_uses__lte=10000), name="coupon_use_bounds"),
        ]

    def __str__(self):
        return self.code

    def clean(self):
        if self.course_id and self.course.creator_id != self.creator_id:
            raise ValidationError("El cupón solo puede aplicarse a tu propio contenido.")
        if self.expires_at and self.starts_at and self.expires_at <= self.starts_at:
            raise ValidationError("La fecha de vencimiento debe ser posterior al inicio.")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            original = type(self).objects.get(pk=self.pk)
            if any(getattr(self, field) != getattr(original, field) for field in ("creator_id", "code", "percent_off", "amount_off_sats", "course_id", "starts_at", "expires_at", "max_uses")):
                raise ValidationError("Desactiva el cupón y crea otro para cambiar sus condiciones.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Desactiva el cupón; se conserva su historial.")

    @property
    def label(self):
        return f"{self.percent_off} %" if self.percent_off else f"{self.amount_off_sats} sats"


class Gift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.OneToOneField(Purchase, on_delete=models.PROTECT, related_name="gift")
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="gift_card")
    token = models.CharField(max_length=64, unique=True, editable=False)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="gifts_received")
    redeemed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(recipient__isnull=True, redeemed_at__isnull=True)
                                              | models.Q(recipient__isnull=False, redeemed_at__isnull=False), name="gift_redemption_complete")]


class LightningPayment(models.Model):
    """A payment that grants no content; amount and recipient never change."""
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PAID = "paid", "Pagada"
        EXPIRED = "expired", "Vencida"
        FAILED = "failed", "No completada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount_sats = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=Status, default=Status.PENDING)
    issue_state = models.CharField(max_length=12, choices=Invoice.Issue, default=Invoice.Issue.NEW)
    payment_hash = models.CharField(max_length=64, null=True, blank=True, unique=True)
    payment_request = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Tip(LightningPayment):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tips_sent")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tips_received")
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT, null=True, blank=True, related_name="tips")
    lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT, null=True, blank=True, related_name="tips")
    message = models.CharField(max_length=280, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [models.CheckConstraint(condition=models.Q(amount_sats__gte=10, amount_sats__lte=100000), name="tip_amount_bounds")]

    @property
    def memo(self):
        return f"BTC.EDU propina {self.pk}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            original = type(self).objects.get(pk=self.pk)
            if any(getattr(self, field) != getattr(original, field) for field in ("sender_id", "creator_id", "amount_sats", "message", "expires_at")):
                raise ValidationError("La propina conserva su importe, destinatario y mensaje.")
        return super().save(*args, **kwargs)


class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Solicitada"
        PAYING = "paying", "Pago en curso"
        REFUNDED = "refunded", "Reembolsada"
        REJECTED = "rejected", "Rechazada"
        REVIEW = "review", "Por conciliar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.OneToOneField(Invoice, on_delete=models.PROTECT, related_name="refund")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="refunds")
    amount_sats = models.PositiveIntegerField()
    reason = models.TextField(max_length=1000)
    payment_request = models.TextField()
    status = models.CharField(max_length=12, choices=Status, default=Status.REQUESTED)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="refund_decisions")
    decision_note = models.CharField(max_length=500, blank=True)
    payment_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        permissions = [("decide_refund", "Aprobar o rechazar reembolsos")]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            original = type(self).objects.get(pk=self.pk)
            if any(getattr(self, field) != getattr(original, field) for field in ("invoice_id", "buyer_id", "amount_sats", "reason", "payment_request")):
                raise ValidationError("La solicitud conserva su factura, importe y destino.")
        return super().save(*args, **kwargs)
