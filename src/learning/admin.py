from django.contrib import admin

from commerce.admin import HistoryAdmin

from .models import Enrollment

admin.site.register(Enrollment, HistoryAdmin)
