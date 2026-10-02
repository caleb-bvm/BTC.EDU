from dataclasses import dataclass

from .models import AccessType, Chapter, Course, Lesson, PublicationStatus


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reason: str


def content_access(user, resource):
    """Evalúa acceso; compras y membresías aún no conceden permisos.

    Las lecciones gratis siguen disponibles aunque otras sean de pago.
    El catálogo futuro debe omitir body y aplicar esta regla al entregar contenido.
    """
    if isinstance(resource, Lesson):
        chapter = resource.chapter
        course = chapter.course
        publications = (course, chapter, resource)
        creator_id = course.creator_id
    elif isinstance(resource, Chapter):
        publications = (resource.course, resource)
        creator_id = resource.course.creator_id
    elif isinstance(resource, Course):
        publications = (resource,)
        creator_id = resource.creator_id
    else:
        publications = (resource,)
        creator_id = resource.creator_id

    if user.is_authenticated and user.is_active and user.pk == creator_id:
        return AccessDecision(True, "creator_preview")
    if any(item.status != PublicationStatus.PUBLISHED for item in publications):
        return AccessDecision(False, "unpublished")
    if getattr(resource, "access_type", AccessType.FREE) == AccessType.FREE:
        return AccessDecision(True, "free")
    return AccessDecision(False, "purchase_required")
