from django.contrib import admin

from commerce.admin import HistoryAdmin

from .models import (
    Enrollment,
    ExtraQuizAttempt,
    LessonProgress,
    QuizAttempt,
    VersionQuiz,
)

admin.site.register(Enrollment, HistoryAdmin)
admin.site.register(LessonProgress, HistoryAdmin)
admin.site.register(VersionQuiz, HistoryAdmin)
admin.site.register(QuizAttempt, HistoryAdmin)
admin.site.register(ExtraQuizAttempt, HistoryAdmin)
