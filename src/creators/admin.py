from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html

from .application_service import review_application
from .models import CreatorApplicationEvent, CreatorProfile, Submission
from .services import decide


class ApplicationReviewForm(forms.ModelForm):
    expected_revision = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = CreatorProfile
        fields = ("status", "feedback")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["expected_revision"].initial = self.instance.review_revision

    def clean(self):
        data = super().clean()
        if data.get("status") in ("changes", "suspended") and not data.get("feedback", "").strip():
            self.add_error("feedback", "Explica el motivo de la decisión.")
        if data.get("status") == "approved" and settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL and not self.instance.user.email_verified_at:
            self.add_error("status", "El creador debe confirmar su correo antes de aprobar su cuenta.")
        if self.instance.pk:
            from django.db.models import F
            # The admin change form runs inside a transaction; reserve the writer
            # before validating the posted revision and later saving the decision.
            CreatorProfile.objects.filter(pk=self.instance.pk).update(updated_at=F("updated_at"))
            current = CreatorProfile.objects.get(pk=self.instance.pk)
            if current.review_revision != data.get("expected_revision"):
                raise forms.ValidationError("La solicitud cambió. Recarga antes de registrar la decisión.")
        return data


class ApplicationHistoryInline(admin.TabularInline):
    model = CreatorApplicationEvent
    extra = 0
    can_delete = False
    readonly_fields = ("created_at", "actor", "kind", "previous_status", "status", "reason")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    form = ApplicationReviewForm
    inlines = (ApplicationHistoryInline,)
    list_display = ("display_name", "user", "specialty", "status", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("display_name", "user__email", "specialty")
    readonly_fields = ("user", "display_name", "bio", "specialty", "website", "reviewed_by", "reviewed_at", "updated_at", "review_revision")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        updated = review_application(obj, request.user, obj.status, obj.feedback, form.cleaned_data.get("expected_revision") if form else None)
        obj.__dict__.update(updated.__dict__)


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
