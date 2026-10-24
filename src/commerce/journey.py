"""Typed purchase destinations; request URLs never become payment return URLs."""
from urllib.parse import urlencode

from django.urls import reverse

from content.access import content_access, owns_revision
from content.models import VersionLesson


def return_lesson(offer, value):
    if not value or not offer.course_version_id:
        return None
    try:
        lesson_id = int(value)
    except (TypeError, ValueError):
        return None
    if not 0 < lesson_id <= 9223372036854775807:
        return None
    return VersionLesson.objects.select_related("content", "chapter__version__course").filter(
        pk=lesson_id, chapter__version_id=offer.course_version_id,
        content_id__in=offer.items.values("resource_id"),
        chapter__version__sealed=True, chapter__version__published_at__isnull=False,
    ).first()


def lesson_url(lesson):
    version = lesson.chapter.version
    return reverse("version-lesson", args=[version.course_id, version.number, lesson.pk])


def offer_url(offer, lesson=None):
    url = reverse("offer-detail", args=[offer.pk])
    return f"{url}?{urlencode({'leccion': lesson.pk})}" if lesson else url


def public_destination(offer):
    if offer.course_version_id:
        return reverse("course-version", args=[offer.course_version.course_id, offer.course_version.number])
    from content.models import Material, Video
    for model, kind in ((Video, "videos"), (Material, "materiales")):
        resource = model.objects.filter(revision_id=offer.resource_id, status="published").first()
        if resource:
            return reverse("resource-detail", args=[kind, resource.pk])
    return reverse("resources")


def destination(user, offer, lesson=None, inventory=None):
    """Return an accessible destination without granting any access."""
    included = {item["resource_id"] for item in inventory} if inventory is not None else set(offer.items.values_list("resource_id", flat=True))
    lesson = lesson or (offer.lesson if offer.lesson_id else None)
    if (lesson and lesson.chapter.version_id == offer.course_version_id
            and lesson.content_id in included and content_access(user, lesson).allowed):
        return {"url": lesson_url(lesson), "label": "Abrir lección", "title": lesson.content.title}
    if offer.resource_id and offer.resource_id in included and owns_revision(user, offer.resource_id):
        return {"url": reverse("purchased-resource", args=[offer.resource_id]), "label": "Abrir recurso", "title": offer.resource.title}
    if offer.course_version_id:
        from learning.services import can_visit_version
        version = offer.course_version
        if version.sealed and version.course.status in ("published", "archived") and can_visit_version(user, version):
            return {"url": reverse("course-version", args=[version.course_id, version.number]), "label": "Abrir contenido", "title": version.title}
    return {"url": reverse("workspace"), "label": "Ir a mi aprendizaje", "title": "Mi aprendizaje"}


def invoice_destination(invoice, user):
    if invoice.order_id and invoice.order.gift:
        gift = getattr(invoice.order, "gift_card", None) if invoice.status == "paid" else None
        if gift:
            return {"url": reverse("gift-detail", args=[gift.token]), "label": "Ver enlace del regalo", "title": invoice.order.title}
        return {"url": reverse("purchases"), "label": "Ver mis compras", "title": "Mis compras"}
    if invoice.order_id:
        lines = list(invoice.order.lines.all())
        if len(lines) == 1:
            line = lines[0]
            return destination(user, line.offer, line.return_lesson, line.inventory)
        return {"url": reverse("workspace"), "label": "Ir a mi aprendizaje", "title": "Mi aprendizaje"}
    return destination(user, invoice.offer, invoice.return_lesson, invoice.inventory)


def order_content(invoice, user):
    if not invoice.order_id:
        return []
    rows = []
    for line in invoice.order.lines.all():
        target = destination(user, line.offer, line.return_lesson, line.inventory)
        scope = line.offer.get_kind_display()
        if line.offer.kind == "course" and line.course_version_id:
            scope = "Tutorial completo" if line.course_version.kind == "tutorial" else "Curso completo"
        elif line.offer.kind == "lesson":
            scope = "Texto de la lección"
        elif line.offer.kind == "resource" and line.offer.resource_id:
            scope = "Video" if line.offer.resource.kind == "video" else "Material"
        rows.append({"line": line, "destination": target, "creator": line.creator,
                     "scope": scope,
                     "creator_label": getattr(getattr(line.creator, "creator_profile", None), "display_name", "") or "Educador"})
    return rows


def invoice_access_conflict(invoice, user):
    from .models import Entitlement
    if invoice.order_id and invoice.order.gift:
        return False
    paid = {item["resource_id"] for item in invoice.inventory if item.get("paid")}
    return invoice.status == "pending" and Entitlement.objects.active().filter(buyer=user, resource_id__in=paid).exists()
