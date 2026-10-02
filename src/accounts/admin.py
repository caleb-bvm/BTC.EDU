from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class PlatformUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "is_staff", "is_active")
    search_fields = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("first_name", "last_name")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),)
