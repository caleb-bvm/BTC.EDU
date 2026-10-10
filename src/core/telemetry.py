import logging
from uuid import uuid4

from django.db import DatabaseError

from .models import ActivityEvent

logger = logging.getLogger(__name__)


def session_id(request):
    if "activity_session" not in request.session:
        request.session["activity_session"] = str(uuid4())
    return request.session["activity_session"]


def audience(request):
    user = request.user
    return not user.is_authenticated or (user.is_active and user.account_type == "student" and not user.is_staff)


def record_activity(request, kind, **fields):
    if not audience(request) or request.method != "GET":
        return
    try:
        ActivityEvent.objects.create(kind=kind, session_id=session_id(request), actor=request.user if request.user.is_authenticated else None, **fields)
    except DatabaseError:
        # Read activity must not prevent authorized content delivery.
        logger.warning("No se pudo registrar actividad del contenido.", exc_info=True)


def offer_views(request, offers):
    for offer in offers:
        record_activity(request, "offer_viewed", offer=offer, creator_id=offer.creator_id, version_id=offer.course_version_id)


def content_opened(request, resource, version=None):
    from content.access import owns_revision
    if owns_revision(request.user, resource.pk):
        kind = "purchased_content_opened"
    elif resource.access_type == "free":
        kind = "free_content_opened"
    else:
        return
    record_activity(request, kind, resource=resource, creator_id=resource.creator_id, version=version)
