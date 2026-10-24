"""Multi-course paths: ordered courses, combined progress and a verifiable credential."""
import hashlib
from datetime import UTC

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Max
from django.urls import reverse

from commerce.services import require_student

from .certificate_integrity import canonical_json
from .models import (
    Certificate,
    Enrollment,
    LearningPath,
    LessonProgress,
    PathCompletion,
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
    return LearningPath.objects.filter(published=True).prefetch_related("steps__course__current_version", "steps__course__creator")


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


def path_progress(user, path):
    steps = []
    for step in path.steps.select_related("course__current_version", "course__creator").order_by("position", "pk"):
        status = course_state(user, step.course)
        version = step.course.current_version
        url = reverse("course-version", args=[step.course_id, version.number]) if version else reverse("course-detail", args=[step.course_id])
        steps.append({"step": step, "course": step.course, "url": url, **status})
    finished = sum(item["state"] in ("certified", "completed") for item in steps)
    completion = PathCompletion.objects.filter(path=path, student=user).first() if user.is_authenticated else None
    return {"steps": steps, "finished": finished, "total": len(steps),
            "percentage": round(finished * 100 / len(steps)) if steps else 0,
            "eligible": bool(steps) and finished == len(steps), "completion": completion,
            "next": next((item for item in steps if item["state"] not in ("certified", "completed")), None)}


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
        raise ValidationError("Completa todos los cursos de la ruta para obtener la credencial.")
    evidence = []
    for item in progress["steps"]:
        if item["certificate"]:
            evidence.append({"course": item["course"].title, "certificate": str(item["certificate"].pk),
                             "certificate_sha256": item["certificate"].fingerprint})
        else:
            last = LessonProgress.objects.filter(enrollment=item["enrollment"]).aggregate(last=Max("completed_at"))["last"]
            evidence.append({"course": item["course"].title, "version": item["enrollment"].version.number,
                             "lessons_completed": item["done"], "completed_at": last.isoformat() if last else ""})
    completion = PathCompletion.objects.create(path=path, student=actor, student_name=name, path_title=path.title, evidence=evidence)
    notify(actor, f"path:{completion.pk}", f"Completaste la ruta «{path.title}»", reverse("path-credential", args=[completion.pk]))
    return completion
