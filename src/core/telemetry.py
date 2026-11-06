"""Record product activity for analytics without tracking identifiers."""
import logging
from hashlib import sha256
from uuid import uuid4

from django.db import DatabaseError, transaction

from .models import ActivityEvent

logger = logging.getLogger(__name__)


def session_id(request):
    """Random activity id stored in the session."""
    if "activity_session" not in request.session:
        request.session["activity_session"] = str(uuid4())
    return request.session["activity_session"]


def audience(request):
    """Only visitors and students are measured; creators and staff are excluded."""
    user = request.user
    return not user.is_authenticated or (user.is_active and user.account_type == "student" and not user.is_staff)


def record_activity(request, kind, **fields):
    """Store an activity event for GET requests; failures never block the page."""
    if not audience(request) or request.method != "GET":
        return
    try:
        ActivityEvent.objects.create(kind=kind, session_id=session_id(request), actor=request.user if request.user.is_authenticated else None, **fields)
    except DatabaseError:
        # Read activity must not prevent authorized content delivery.
        logger.warning("No se pudo registrar actividad del contenido.", exc_info=True)


def offer_views(request, offers):
    """Record that offers were shown."""
    for offer in offers:
        record_activity(request, "offer_viewed", offer=offer, creator_id=offer.creator_id, version_id=offer.course_version_id)


def record_commerce_action(request, kind, object_key, offer=None, invoice=None):
    """Record accepted cart actions/review snapshots, deduplicating reloads and retries."""
    if not audience(request) or kind not in {"cart_added", "checkout_started"}:
        return
    identifier = session_id(request)
    key = kind + ":" + sha256(f"{identifier}:{object_key}".encode()).hexdigest()
    try:
        with transaction.atomic():
            ActivityEvent.objects.get_or_create(event_key=key, defaults={
                "kind": kind, "session_id": identifier, "actor": request.user if request.user.is_authenticated else None,
                "offer": offer, "invoice": invoice, "creator_id": offer.creator_id if offer else None,
                "version_id": offer.course_version_id if offer else None,
            })
    except DatabaseError:
        logger.warning("No se pudo registrar actividad de compra.", exc_info=True)


def content_opened(request, resource, version=None):
    """Record that a resource or lesson was opened."""
    from content.access import membership_covers, owns_revision
    if owns_revision(request.user, resource.pk):
        kind = "purchased_content_opened"
    elif resource.access_type == "free":
        kind = "free_content_opened"
    elif version is not None and membership_covers(request.user, version):
        # Opening included content uses the period and ends the right to withdraw from it.
        kind = "membership_content_opened"
    else:
        return
    record_activity(request, kind, resource=resource, creator_id=resource.creator_id, version=version)
