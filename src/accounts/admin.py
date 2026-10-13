from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AccountEvent, AccountMail, AccountSupportRequest, SupportEvent, User
from .support import review_support


@admin.register(User)
class PlatformUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "account_type", "is_staff", "is_active")
    list_filter = ("account_type", "is_staff", "is_active")
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("first_name", "last_name", "account_type")}),
        ("Presentación pública", {"fields": ("display_name", "bio", "interests", "learning_goal", "website", "profile_public", "avatar")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined", "email_verified_at", "closed_at")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "account_type", "password1", "password2")}),)

    def get_readonly_fields(self, request, obj=None):
        return ("account_type", "avatar", "email_verified_at", "closed_at") if obj else ()

    def save_model(self, request, obj, form, change):
        if change:
            previous = User.objects.get(pk=obj.pk)
            if previous.email != obj.email:
                obj.email_verified_at = None
            if not obj.is_active:
                obj.closed_at = None
            if previous.is_active != obj.is_active or previous.email != obj.email:
                obj.session_revision = previous.session_revision + 1
        super().save_model(request, obj, form, change)


class SupportReviewForm(forms.ModelForm):
    class Meta:
        model = AccountSupportRequest
        fields = ("status", "response")

    def clean(self):
        data = super().clean()
        if data.get("status") == "resolved" and not data.get("response", "").strip():
            self.add_error("response", "Escribe una respuesta antes de cerrar la consulta.")
        return data


class SupportHistoryInline(admin.TabularInline):
    model = SupportEvent
    extra = 0
    can_delete = False
    readonly_fields = ("status", "response", "actor", "created_at")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AccountSupportRequest)
class AccountSupportAdmin(admin.ModelAdmin):
    form = SupportReviewForm
    list_display = ("user", "kind", "status", "created_at")
    list_filter = ("status", "kind")
    readonly_fields = ("user", "kind", "body", "request_key", "created_at", "reviewed_by", "reviewed_at")
    inlines = (SupportHistoryInline,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        updated = review_support(obj, request.user, obj.status, obj.response)
        obj.__dict__.update(updated.__dict__)


@admin.register(AccountMail)
class AccountMailAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "attempts", "created_at", "sent_at")
    list_filter = ("status",)
    fields = ("id", "user", "status", "attempts", "created_at", "sent_at", "next_attempt_at")
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AccountEvent)
class AccountEventAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "created_at")
    readonly_fields = ("user", "kind", "detail", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
