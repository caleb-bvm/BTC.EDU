"""Path bundles: the courses of a path a buyer still needs, sold in one order with the path discount."""
import uuid

from django.core.exceptions import ValidationError
from django.db import transaction

from .catalog import available, ownership, public_version
from .models import Offer
from .orders import create_reserved_order, load_quote, quote_selection, sign_quote
from .services import require_student, reserve_writer

BUNDLE_MIN_COURSES = 2


def course_offer(version):
    """The active offer for a whole course version, when the course is sold."""
    offer = (Offer.objects.filter(kind="course", course_version=version, status="active")
             .select_related("creator", "course_version__course").first())
    return offer if offer and available(offer) else None


def bundle_rows(user, path):
    """How each public course of the path is reached: bought in the bundle, already owned, membership or free."""
    from content.access import membership_covers
    rows = []
    for step in path.steps.select_related("course__current_version").order_by("position", "pk"):
        version = step.course.current_version
        if version is None or not public_version(version):
            continue
        offer = course_offer(version)
        if offer is None:
            state = "membership" if step.course.membership else "free"
        elif ownership(user, offer) == "owned":
            state = "owned"
        elif membership_covers(user, version):
            state = "membership"
        else:
            state = "bundle"
        rows.append({"step": step, "course": step.course, "offer": offer if state == "bundle" else None, "state": state})
    return rows


def path_selection(rows):
    return [{"offer_id": row["offer"].pk, "return_lesson_id": None, "cart_item_key": None} for row in rows if row["state"] == "bundle"]


def bundle_quote(actor, path, rows=None):
    """Server-priced bundle with the path discount; it needs at least two courses still to buy."""
    rows = bundle_rows(actor, path) if rows is None else rows
    selection = path_selection(rows)
    quote = quote_selection(actor, selection, path=path)
    quote["list_total_sats"] = sum(line["list_sats"] for line in quote["lines"])
    quote["path"] = path
    if not path.published or not path.bundle_percent or len(selection) < BUNDLE_MIN_COURSES:
        quote["conflicts"].append({"code": "bundle_unavailable", "offer_id": None, "cart_item_key": None, "invoice_id": None,
                                   "message": "Este paquete no está disponible. Puedes comprar cada curso por separado."})
        quote["can_checkout"] = False
    return sign_quote(actor, quote, f"path:{path.pk}")


@transaction.atomic
def reserve_path_order(actor, path, token, request_key=None, activity_session=None):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    payload, existing = load_quote(actor, token, request_key, f"path:{path.pk}")
    if existing:
        return existing
    quote = bundle_quote(actor, path)
    if quote["fingerprint"] != payload.get("fingerprint"):
        raise ValidationError("Los cursos de la ruta o su precio cambiaron. Revisa el paquete antes de pagar.")
    return create_reserved_order(actor, quote, uuid.UUID(payload["request_key"]), activity_session=activity_session,
                                 title=f"Ruta · {path.title}")
