import uuid

from django.conf import settings
from django.db import models

from content.immutability import FrozenRecord


class ActivityEvent(FrozenRecord):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    kind = models.CharField(max_length=40, db_index=True)
    session_id = models.UUIDField(db_index=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="activity_events")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="content_events")
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT, null=True, blank=True)
    resource = models.ForeignKey("content.ResourceVersion", on_delete=models.PROTECT, null=True, blank=True)
    offer = models.ForeignKey("commerce.Offer", on_delete=models.PROTECT, null=True, blank=True)
    invoice = models.ForeignKey("commerce.Invoice", on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
