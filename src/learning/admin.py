from django.contrib import admin

from commerce.admin import HistoryAdmin

from .models import (
    Certificate,
    CertificateRevocation,
    Enrollment,
    ExtraQuizAttempt,
    LessonProgress,
    LessonQuestion,
    Notification,
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
