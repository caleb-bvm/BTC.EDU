"""Public educational information, distinct from protected teaching content."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext

EDUCATION_FIELDS = ("learning_outcome", "requirements", "activity_kind", "public_preview", "support_scope")


def education_values(unit):
    return {field: getattr(unit, field) for field in EDUCATION_FIELDS}


def validate_education(unit):
    labels = {
        "learning_outcome": gettext("qué aprenderá el alumno"),
        "requirements": gettext("los requisitos (o indica que no hay requisitos previos)"),
        "activity_kind": gettext("el tipo de actividad"),
        "public_preview": gettext("una muestra pública"),
        "support_scope": gettext("el alcance del acompañamiento"),
    }
    missing = [label for field, label in labels.items() if not getattr(unit, field).strip()]
    if missing:
        raise ValidationError(gettext("%(title)s: completa %(missing)s.") % {"title": unit.title, "missing": ", ".join(missing)})
    if unit.activity_kind not in ("understand", "design", "execute"):
        raise ValidationError((gettext('%(title)s: elige un tipo de actividad válido.') % {"title": unit.title}))


def validate_snapshot(snapshot):
    if hasattr(snapshot, "chapters"):
        for chapter in snapshot.chapters.prefetch_related("lessons__content", "lessons__attachments__resource"):
            for lesson in chapter.lessons.all():
                validate_education(lesson.content)
                for attachment in lesson.attachments.all():
                    validate_education(attachment.resource)
    else:
        validate_education(snapshot)
