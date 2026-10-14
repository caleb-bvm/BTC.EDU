"""Public educational information, distinct from protected teaching content."""
from django.core.exceptions import ValidationError

EDUCATION_FIELDS = ("learning_outcome", "requirements", "activity_kind", "public_preview", "support_scope")


def education_values(unit):
    return {field: getattr(unit, field) for field in EDUCATION_FIELDS}


def validate_education(unit):
    labels = {
        "learning_outcome": "qué aprenderá el alumno",
        "requirements": "los requisitos (o indica que no hay requisitos previos)",
        "activity_kind": "el tipo de actividad",
        "public_preview": "una muestra pública",
        "support_scope": "el alcance del acompañamiento",
    }
    missing = [label for field, label in labels.items() if not getattr(unit, field).strip()]
    if missing:
        raise ValidationError(f"{unit.title}: completa " + ", ".join(missing) + ".")
    if unit.activity_kind not in ("understand", "design", "execute"):
        raise ValidationError(f"{unit.title}: elige un tipo de actividad válido.")


def validate_snapshot(snapshot):
    if hasattr(snapshot, "chapters"):
        for chapter in snapshot.chapters.prefetch_related("lessons__content", "lessons__attachments__resource"):
            for lesson in chapter.lessons.all():
                validate_education(lesson.content)
                for attachment in lesson.attachments.all():
                    validate_education(attachment.resource)
    else:
        validate_education(snapshot)
