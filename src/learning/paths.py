"""Multi-course paths: ordered courses, combined progress and a verifiable credential."""
import hashlib
from datetime import UTC

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Count, F, Max
from django.urls import reverse
from django.utils.text import slugify

from commerce.services import require_student

from .certificate_integrity import canonical_json
from .models import (
    Certificate,
    Enrollment,
    LearningPath,
    LessonProgress,
    PathCompletion,
    PathCourse,
)
from .support import notify


def path_record(completion):
    return {
        "schema": "btc.edu.path.v1",
        "id": str(completion.pk),
        "student_name": completion.student_name,
        "path_title": completion.path_title,
        "issued_at": completion.issued_at.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z"),
        "evidence_sha256": hashlib.sha256(canonical_json(completion.evidence)).hexdigest(),
    }


def path_bytes(completion):
    return canonical_json(path_record(completion))


def path_digest(completion):
    return hashlib.sha256(path_bytes(completion)).hexdigest()


def published_paths():
    return (LearningPath.objects.filter(published=True).select_related("creator__creator_profile")
            .order_by(F("creator").asc(nulls_first=True), "position", "pk"))


def public_steps(path):
    """Steps whose course is published; a withdrawn course leaves the trail without breaking it."""
    steps = path.steps.select_related("course__current_version", "course__creator__creator_profile", "course__topic").order_by("position", "pk")
    return [step for step in steps if step.course.status == "published" and step.course.current_version_id]


def duration_label(minutes):
    if not minutes:
        return ""
    return f"~{minutes} min" if minutes < 60 else f"~{round(minutes / 60)} h"


def course_state(user, course):
    """How far a student is in one course of a path, using any of its versions."""
    if not user.is_authenticated or user.account_type != "student":
        return {"state": "not_started", "done": 0, "total": 0, "percentage": 0}
    certificate = (Certificate.objects.filter(enrollment__student=user, enrollment__version__course=course, revocation__isnull=True)
                   .select_related("enrollment__version").order_by("issued_at").first())
    enrollments = (Enrollment.objects.filter(student=user, version__course=course)
                   .annotate(done=Count("completed_lessons", distinct=True), total=Count("version__chapters__lessons", distinct=True))
                   .order_by("-done", "-pk"))
    best = enrollments.first()
    done, total = (best.done, best.total) if best else (0, 0)
    percentage = round(done * 100 / total) if total else 0
    if certificate:
        state = "certified"
    elif best and total and done == total:
        state = "completed"
    elif best:
        state = "in_progress"
    else:
        state = "not_started"
    return {"state": state, "done": done, "total": total, "percentage": percentage, "certificate": certificate, "enrollment": best}


def suggested_step(steps):
    """Continue a course in progress, else the first pending step after the last one finished.

    Steps are a recommended trail: skipped ones stay available but never hold the suggestion back.
    """
    pending = [item for item in steps if item["state"] not in ("certified", "completed")]
    current = next((item for item in pending if item["state"] == "in_progress"), None)
    if current or not pending:
        return current
    last = max((index for index, item in enumerate(steps) if item["state"] in ("certified", "completed")), default=-1)
    return (next((item for item in steps[last + 1:] if item in pending), None)
            or next((item for item in pending if not item["optional"]), pending[0]))


def path_progress(user, path):
    steps = []
    for step in public_steps(path):
        status = course_state(user, step.course)
        version = step.course.current_version
        url = reverse("course-version", args=[step.course_id, version.number]) if version else reverse("course-detail", args=[step.course_id])
        steps.append({"step": step, "course": step.course, "url": url, "optional": step.optional, **status})
    finished_states = ("certified", "completed")
    required = [item for item in steps if not item["optional"]]
    done = sum(item["state"] in finished_states for item in required)
    completion = PathCompletion.objects.filter(path=path, student=user).first() if user.is_authenticated else None
    suggestion = suggested_step(steps)
    for item in steps:
        item["is_next"] = item is suggestion
    return {"steps": steps, "finished": sum(item["state"] in finished_states for item in steps), "total": len(steps),
            "required_total": len(required), "required_finished": done, "optional_total": len(steps) - len(required),
            "percentage": round(done * 100 / len(required)) if required else 0,
            "started": any(item["state"] != "not_started" for item in steps),
            "duration": duration_label(sum(item["course"].estimated_minutes or 0 for item in steps)),
            "eligible": bool(required) and done == len(required), "completion": completion, "next": suggestion}


@transaction.atomic
def issue_path_credential(actor, path, student_name):
    require_student(actor)
    from commerce.services import reserve_writer
    reserve_writer(actor.pk)
    existing = PathCompletion.objects.filter(path=path, student=actor).first()
    if existing:
        return existing
    name = student_name.strip() if isinstance(student_name, str) else ""
    if not name or len(name) > 150 or any(ord(char) < 32 for char in name):
        raise ValidationError("Indica el nombre que aparecerá en tu credencial, hasta 150 caracteres.")
    if not path.published:
        raise ValidationError("Esta ruta no está disponible.")
    progress = path_progress(actor, path)
    if not progress["eligible"]:
        raise ValidationError("Completa los cursos obligatorios de la ruta para obtener la credencial.")
    evidence = []
    for item in progress["steps"]:
        if item["optional"] and item["state"] not in ("certified", "completed"):
            continue
        if item["certificate"]:
            evidence.append({"course": item["course"].title, "certificate": str(item["certificate"].pk),
                             "certificate_sha256": item["certificate"].fingerprint})
        else:
            last = LessonProgress.objects.filter(enrollment=item["enrollment"]).aggregate(last=Max("completed_at"))["last"]
            evidence.append({"course": item["course"].title, "version": item["enrollment"].version.number,
                             "lessons_completed": item["done"], "completed_at": last.isoformat() if last else ""})
        if item["optional"]:
            evidence[-1]["optional"] = True
    completion = PathCompletion.objects.create(path=path, student=actor, student_name=name, path_title=path.title, evidence=evidence)
    notify(actor, f"path:{completion.pk}", f"Completaste la ruta «{path.title}»", reverse("path-credential", args=[completion.pk]))
    return completion


def studio_courses(creator):
    """Courses an educator may place in their own paths: published and with a public version."""
    from content.models import Course
    return list(Course.objects.filter(creator=creator, status="published", current_version__isnull=False)
                .select_related("current_version").order_by("title"))


def unique_slug(title):
    base = slugify(title)[:44] or "ruta"
    slug, suffix = base, 2
    while LearningPath.objects.filter(slug=slug).exists():
        slug, suffix = f"{base}-{suffix}", suffix + 1
    return slug


@transaction.atomic
def save_creator_path(creator, path, fields, steps):
    """An educator curates a trail from their own published courses; steps arrive in their final order."""
    if path.pk and path.creator_id != creator.pk:
        raise PermissionDenied
    allowed = {course.pk for course in studio_courses(creator)}
    if any(item["course"].pk not in allowed for item in steps):
        raise ValidationError("Elige solo tus cursos publicados.")
    if fields.get("published") and (len(steps) < 2 or all(item["optional"] for item in steps)):
        raise ValidationError("Para publicar la ruta, incluye al menos dos cursos y uno obligatorio.")
    for name, value in fields.items():
        setattr(path, name, value)
    path.creator = creator
    if not path.slug:
        path.slug = unique_slug(path.title)
    path.full_clean()
    path.save()
    path.steps.all().delete()
    PathCourse.objects.bulk_create([PathCourse(path=path, course=item["course"], position=position, optional=item["optional"], note=item["note"])
                                    for position, item in enumerate(steps, 1)])
    return path
