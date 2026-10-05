from django.contrib import admin

from commerce.admin import HistoryAdmin

from .models import Enrollment, LessonProgress

admin.site.register(Enrollment, HistoryAdmin)
admin.site.register(LessonProgress, HistoryAdmin)
