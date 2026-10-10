from django.contrib import admin

from commerce.admin import HistoryAdmin

from .models import ActivityEvent

admin.site.register(ActivityEvent, HistoryAdmin)
