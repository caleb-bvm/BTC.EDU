from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_safe

from commerce.models import Entitlement
from commerce.views import student_required
from content.access import content_access
from content.models import CourseVersion, VersionLesson
from media.delivery import file_response

from .models import Enrollment, QuizAttempt, VersionQuiz
from .services import StaleProgress, enroll, save_progress


@student_required
@require_POST
def enrollment_create(request, version_pk):
    version = get_object_or_404(CourseVersion.objects.select_related("course"), pk=version_pk)
    try:
        enroll(request.user, version)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Curso añadido a Mi aprendizaje. La inscripción conserva esta versión y no compra los contenidos de pago.")
    return redirect("course-version", course_pk=version.course_id, number=version.number)


@student_required
@require_GET
def library(request):
    from core.telemetry import record_activity
    record_activity(request, "library_viewed")
    enrollments = Enrollment.objects.filter(student=request.user).select_related("version__course", "last_lesson__content", "last_lesson__chapter__version__course").prefetch_related("version__chapters__lessons__content", "completed_lessons")
    page = Paginator(enrollments.order_by("-updated_at", "-pk"), 12).get_page(request.GET.get("pagina"))
    for enrollment in page:
        version = enrollment.version
        lessons = [lesson for chapter in version.chapters.all() for lesson in chapter.lessons.all()]
        completed = {item.lesson_id for item in enrollment.completed_lessons.all()}
        unfinished = [lesson for lesson in lessons if lesson.pk not in completed and content_access(request.user, lesson).allowed]
        last_index = next((index for index, lesson in enumerate(lessons) if lesson.pk == enrollment.last_lesson_id), -1)
        if enrollment.last_lesson_id and enrollment.last_lesson_id not in completed and content_access(request.user, enrollment.last_lesson).allowed:
            first = enrollment.last_lesson
        else:
            first = next((lesson for lesson in lessons[last_index + 1:] if lesson in unfinished), unfinished[0] if unfinished else None)
        if not first and len(completed) == len(lessons):
            first = next((lesson for lesson in lessons if content_access(request.user, lesson).allowed), None)
        enrollment.open_label = "Ver acceso" if not first else "Repasar" if len(completed) == len(lessons) else "Continuar" if enrollment.last_lesson_id else "Estudiar"
        enrollment.open_url = reverse("version-lesson", args=[version.course_id, version.number, first.pk]) if first else reverse("course-version", args=[version.course_id, version.number])
        enrollment.lesson_count = len(lessons)
        enrollment.completed_count = len(completed)
        enrollment.percentage = round(len(completed) * 100 / len(lessons)) if lessons else 0
        enrollment.retired = version.course.status == "archived" or version.course.current_version_id != version.pk
        from .certificates import completion_status
        enrollment.certificate_status = completion_status(enrollment)
    resources = Entitlement.objects.filter(buyer=request.user, resource__kind__in=("video", "material")).select_related("resource__asset").order_by("-created_at")
    return render(request, "core/workspace.html", {"enrollments": page, "resources": Paginator(resources, 12).get_page(request.GET.get("recursos_pagina")), "active": "workspace"})


def lesson_learning_context(user, version, record):
    if not user.is_authenticated or not user.is_active or user.account_type != "student":
        return {}
    enrollment = Enrollment.objects.filter(student=user, version=version).first()
    quiz = VersionQuiz.objects.filter(lesson=record).first()
    if not enrollment:
        return {"version": version, "lesson_quiz": quiz}
    completed = enrollment.completed_lessons.count()
    total = VersionLesson.objects.filter(chapter__version=version).count()
    passed = bool(quiz and QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz, passed=True, submitted_at__isnull=False).exists())
    return {"enrollment": enrollment, "lesson_quiz": quiz, "quiz_passed": passed, "quiz_blocks_completion": bool(quiz and quiz.required and not passed), "record_id": record.pk, "question_lesson_id": record.pk, "completed": enrollment.completed_lessons.filter(lesson=record).exists(), "completed_count": completed, "lesson_total": total, "percentage": round(completed * 100 / total) if total else 0}


@student_required
@require_POST
def progress_update(request, pk):
    enrollment = get_object_or_404(Enrollment.objects.select_related("version"), pk=pk, student=request.user)
    wants_json = "application/json" in request.headers.get("Accept", "")
    try:
        lesson_id, revision = int(request.POST.get("lesson", "")), int(request.POST.get("revision", ""))
        enrollment = save_progress(request.user, enrollment.pk, lesson_id, revision, request.POST.get("action", ""))
    except (ValueError, ValidationError) as exc:
        message = " ".join(exc.messages) if isinstance(exc, ValidationError) else "El avance enviado no es válido."
        if wants_json:
            return JsonResponse({"saved": False, "message": message}, status=409 if isinstance(exc, StaleProgress) else 400)
        messages.error(request, message)
        return redirect("course-version", course_pk=enrollment.version.course_id, number=enrollment.version.number)
    completed = enrollment.completed_lessons.count()
    total = VersionLesson.objects.filter(chapter__version=enrollment.version).count()
    if wants_json:
        return JsonResponse({"saved": True, "revision": enrollment.revision, "completed": completed, "total": total,
                             "is_completed": enrollment.completed_lessons.filter(lesson_id=lesson_id).exists(),
                             "message": "Lección completada y avance guardado." if request.POST.get("action") == "complete" else "Lección pendiente y avance guardado." if request.POST.get("action") == "incomplete" else "Tu punto de continuación quedó guardado."})
    messages.success(request, "Avance guardado.")
    return redirect("version-lesson", course_pk=enrollment.version.course_id, number=enrollment.version.number, lesson_pk=lesson_id)


@student_required
@require_GET
def purchased_resource(request, pk):
    right = get_object_or_404(Entitlement.objects.select_related("resource__asset", "resource__subtitles", "resource__creator"), buyer=request.user, resource_id=pk)
    resource = right.resource
    from core.telemetry import content_opened
    if resource.kind == "text":
        lesson = VersionLesson.objects.filter(content=resource, chapter__version__published_at__isnull=False).select_related("chapter__version").first()
        if lesson:
            return redirect("version-lesson", course_pk=lesson.chapter.version.course_id, number=lesson.chapter.version.number, lesson_pk=lesson.pk)
    content_opened(request, resource)
    file_url = reverse("purchased-resource-file", args=[resource.pk, "archivo"]) if resource.asset_id and resource.asset.file.storage.exists(resource.asset.file.name) else ""
    return render(request, "learning/resource.html", {"resource": resource, "media": {"standalone": True, "title": resource.title, "kind": resource.kind, "allowed": True, "file_url": file_url, "subtitle_url": reverse("purchased-resource-file", args=[resource.pk, "subtitulos"]) if resource.subtitles_id else "", "body": resource.body, "size": resource.asset.size if resource.asset_id else 0, "mime": resource.asset.mime_type if resource.asset_id else ""}, "active": "workspace"})


@student_required
@require_safe
def purchased_resource_file(request, pk, part):
    right = get_object_or_404(Entitlement.objects.select_related("resource__asset", "resource__subtitles"), buyer=request.user, resource_id=pk)
    asset = right.resource.asset if part == "archivo" else right.resource.subtitles if part == "subtitulos" else None
    if asset is None:
        from django.http import Http404
        raise Http404
    response = file_response(request, asset)
    if request.method == "GET" and response.status_code in (200, 206) and part == "archivo":
        from core.telemetry import content_opened
        content_opened(request, right.resource)
    return response
