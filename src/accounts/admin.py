from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class PlatformUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "account_type", "is_staff", "is_active")
    list_filter = ("account_type", "is_staff", "is_active")
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("first_name", "last_name", "account_type")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "account_type", "password1", "password2")}),)

    def get_readonly_fields(self, request, obj=None):
        return ("account_type",) if obj else ()
