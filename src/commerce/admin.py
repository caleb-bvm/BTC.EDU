from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    CommerceEvent,
    Coupon,
    Entitlement,
    EntitlementSource,
    Gift,
    Invoice,
    Offer,
    OfferItem,
    Order,
    OrderLine,
    PaymentEvidence,
    Purchase,
    Refund,
    Tip,
)
from .offers import archive_offer, review_offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "amount_sats", "kind", "status", "review_link")
    list_filter = ("status", "kind")
    actions = ("approve", "archive")
    readonly_fields = tuple(field.name for field in Offer._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def act(self, request, queryset, action):
        for offer in queryset:
            try:
                action(offer)
            except (ValidationError, PermissionDenied) as exc:
                self.message_user(request, str(exc), messages.ERROR)
            else:
                self.message_user(request, f"{offer.title}: decisión guardada.", messages.SUCCESS)

    @admin.action(description="Aprobar ofertas revisadas", permissions=["change"])
    def approve(self, request, queryset):
        self.act(request, queryset, lambda offer: review_offer(request.user, offer, True))

    @admin.display(description="Revisión")
    def review_link(self, obj):
        return format_html('<a href="{}">Revisar oferta</a>', reverse("offer-review", args=[obj.pk]))

    @admin.action(description="Retirar ofertas sin eliminar compras", permissions=["change"])
    def archive(self, request, queryset):
        self.act(request, queryset, lambda offer: archive_offer(request.user, offer))


class HistoryAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Invoice)
class InvoiceAdmin(HistoryAdmin):
    list_display = ("id", "buyer", "title", "amount_sats", "status", "issue_state", "incident")
    list_filter = ("status", "issue_state", "incident")
    exclude = ("payment_request",)

    def get_readonly_fields(self, request, obj=None):
        return tuple(field for field in super().get_readonly_fields(request, obj) if field != "payment_request")


for model in (OfferItem, Order, OrderLine, Purchase, Entitlement, EntitlementSource, PaymentEvidence, CommerceEvent):
    admin.site.register(model, HistoryAdmin)


@admin.register(Coupon)
class CouponAdmin(HistoryAdmin):
    list_display = ("code", "creator", "label", "course", "expires_at", "max_uses", "active")
    list_filter = ("active",)
    actions = ("deactivate",)

    @admin.action(description="Desactivar cupones", permissions=["change"])
    def deactivate(self, request, queryset):
        queryset.update(active=False)


@admin.register(Gift)
class GiftAdmin(HistoryAdmin):
    list_display = ("order", "recipient", "redeemed_at", "created_at")
    exclude = ("token",)

    def get_readonly_fields(self, request, obj=None):
        return tuple(field for field in super().get_readonly_fields(request, obj) if field != "token")


@admin.register(Tip)
class TipAdmin(HistoryAdmin):
    list_display = ("id", "sender", "creator", "amount_sats", "status", "created_at")
    list_filter = ("status",)
    exclude = ("payment_request",)

    def get_readonly_fields(self, request, obj=None):
        return tuple(field for field in super().get_readonly_fields(request, obj) if field != "payment_request")


@admin.register(Refund)
class RefundAdmin(HistoryAdmin):
    list_display = ("id", "buyer", "amount_sats", "status", "created_at", "review_link")
    list_filter = ("status",)

    @admin.display(description="Revisión")
    def review_link(self, obj):
        return format_html('<a href="{}">Revisar reembolso</a>', reverse("refund-review", args=[obj.pk]))
