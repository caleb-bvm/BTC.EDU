from django.contrib import admin

from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("original_name", "creator", "kind", "size", "created_at")
    list_filter = ("kind",)
    search_fields = ("original_name", "creator__email")
    fields = ("creator", "file")

    def get_fields(self, request, obj=None):
        return ("creator", "original_name", "kind", "mime_type", "size", "sha256", "created_at") if obj else self.fields

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj) if obj else ()

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
