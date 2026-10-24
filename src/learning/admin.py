from django.contrib import admin

from commerce.admin import HistoryAdmin

from .models import (
    Certificate,
    CertificateRevocation,
    CertificateTimestamp,
    CommunityDecision,
    CommunityPost,
    CommunityReport,
    CommunitySuspension,
    CourseReview,
    Enrollment,
    ExtraQuizAttempt,
    LearningPath,
    LessonProgress,
    LessonQuestion,
    Notification,
    PathCompletion,
    PathCourse,
    PracticeShowcase,
    QuestionReply,
    QuizAttempt,
    VersionCertificatePolicy,
    VersionQuiz,
)

admin.site.register(Enrollment, HistoryAdmin)
admin.site.register(LessonProgress, HistoryAdmin)
admin.site.register(VersionQuiz, HistoryAdmin)
admin.site.register(QuizAttempt, HistoryAdmin)
admin.site.register(ExtraQuizAttempt, HistoryAdmin)
admin.site.register(VersionCertificatePolicy, HistoryAdmin)
admin.site.register(LessonQuestion, HistoryAdmin)
admin.site.register(QuestionReply, HistoryAdmin)
admin.site.register(Notification, HistoryAdmin)
admin.site.register(CertificateRevocation, HistoryAdmin)
admin.site.register(CommunityDecision, HistoryAdmin)
admin.site.register(CommunityReport, HistoryAdmin)
admin.site.register(CommunitySuspension, HistoryAdmin)


@admin.register(CommunityPost)
class CommunityPostAdmin(HistoryAdmin):
    list_display = ("id", "version", "created_at", "hidden", "closed", "moderation_link")

    @admin.display(description="Moderación")
    def moderation_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        return format_html('<a href="{}">Abrir comunidad</a>', reverse("community-space", args=[obj.version_id]))


@admin.register(Certificate)
class CertificateAdmin(HistoryAdmin):
    list_display = ("course_title", "student_name", "issued_at", "revoke_link")

    @admin.display(description="Estado")
    def revoke_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        if hasattr(obj, "revocation"):
            return "Revocado"
        return format_html('<a href="{}">Revisar revocación</a>', reverse("certificate-revoke", args=[obj.pk]))


admin.site.register(PathCompletion, HistoryAdmin)


@admin.register(CertificateTimestamp)
class CertificateTimestampAdmin(HistoryAdmin):
    list_display = ("certificate", "submitted_at", "bitcoin_height", "checked_at")
    exclude = ("proof",)

    def get_readonly_fields(self, request, obj=None):
        return tuple(field for field in super().get_readonly_fields(request, obj) if field != "proof")


class PathCourseInline(admin.TabularInline):
    model = PathCourse
    extra = 1
    autocomplete_fields = ()


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "published", "position")
    list_filter = ("published",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = (PathCourseInline,)


class ModeratedAdmin(HistoryAdmin):
    actions = ("hide", "show")

    @admin.action(description="Ocultar por moderación", permissions=["change"])
    def hide(self, request, queryset):
        queryset.update(hidden=True)

    @admin.action(description="Mostrar de nuevo", permissions=["change"])
    def show(self, request, queryset):
        queryset.update(hidden=False)


@admin.register(CourseReview)
class CourseReviewAdmin(ModeratedAdmin):
    list_display = ("course", "student", "rating", "basis", "hidden", "updated_at")
    list_filter = ("hidden", "rating", "basis")


@admin.register(PracticeShowcase)
class PracticeShowcaseAdmin(ModeratedAdmin):
    list_display = ("delivery", "public", "hidden", "created_at")
    list_filter = ("public", "hidden")
