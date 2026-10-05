from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import CreatorProfile, Submission
from .services import decide


@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "specialty", "status", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("display_name", "user__email", "specialty")
    readonly_fields = ("user", "display_name", "bio", "specialty", "website", "reviewed_by", "reviewed_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.reviewed_by = request.user
        obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "creator", "status", "created_at", "review_link")
    list_filter = ("status",)
    readonly_fields = ("creator", "course", "video", "material", "course_version", "resource_version", "status", "feedback", "created_at", "reviewed_by", "reviewed_at", "review_link")
    actions = ("approve",)

    @admin.display(description="Revisar composición")
    def review_link(self, obj):
        return format_html('<a href="{}">Abrir revisión y observaciones</a>', reverse("creator-review", args=[obj.pk]))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description="Aprobar y publicar la composición enviada")
    def approve(self, request, queryset):
        for submission in queryset:
            try:
                decide(submission, request.user, True)
            except ValidationError as exc:
                self.message_user(request, " ".join(exc.messages), messages.ERROR)
            else:
                self.message_user(request, "Composición revisada publicada.")
