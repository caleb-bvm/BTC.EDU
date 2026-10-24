from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_safe

from commerce.models import Entitlement
from commerce.views import student_required
from content.access import content_access
from content.models import CourseVersion, VersionLesson
from media.delivery import file_response

from .models import Enrollment, QuizAttempt, SavedItem, VersionQuiz
from .presentation import continuation, library_journey
from .services import StaleProgress, enroll, save_progress


@student_required
@require_POST
def enrollment_create(request, version_pk):
    version = get_object_or_404(CourseVersion.objects.select_related("course"), pk=version_pk)
    try:
        enrollment = enroll(request.user, version)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Curso añadido a Mi aprendizaje. La inscripción conserva esta versión y no compra los contenidos de pago.")
        if request.POST.get("start") == "1":
            lessons = list(VersionLesson.objects.filter(chapter__version=version).select_related("content", "chapter__version__course").order_by("chapter__position", "chapter__pk", "position", "pk"))
            target = continuation(lessons, set(enrollment.completed_lessons.values_list("lesson_id", flat=True)), enrollment.last_lesson_id,
                                  {lesson.pk for lesson in lessons if content_access(request.user, lesson).allowed})
            requested = next((lesson for lesson in lessons if str(lesson.pk) == request.POST.get("lesson")), None)
            if requested and content_access(request.user, requested).allowed:
                target = requested
            if target:
                return redirect("version-lesson", course_pk=version.course_id, number=version.number, lesson_pk=target.pk)
    return redirect("course-version", course_pk=version.course_id, number=version.number)


@student_required
@require_GET
def library(request):
    from core.telemetry import record_activity
    record_activity(request, "library_viewed")
    enrollments = Enrollment.objects.filter(student=request.user).select_related("version__course", "version__topic", "last_lesson__content", "last_lesson__chapter__version__course").prefetch_related("version__chapters__lessons__content", "completed_lessons").annotate(learning_total=Count("version__chapters__lessons", distinct=True), learning_done=Count("completed_lessons", distinct=True))
    all_enrollments = enrollments
    stats = {"courses": enrollments.count(), "completed": enrollments.filter(learning_total__gt=0, learning_done=F("learning_total")).count(),
             "lessons": enrollments.aggregate(total=Sum("learning_done"))["total"] or 0}
    section = request.GET.get("seccion", "cursos" if request.GET.get("q") or request.GET.get("estado") else "continuar")
    if section not in ("continuar", "cursos", "recursos", "guardados", "certificados"):
        section = "continuar"
    state = request.GET.get("estado", "todos")
    if state == "en-curso":
        enrollments = enrollments.filter(Q(learning_done__gt=0) | Q(last_lesson__isnull=False)).filter(learning_done__lt=F("learning_total"))
    elif state == "completados":
        enrollments = enrollments.filter(learning_total__gt=0, learning_done=F("learning_total"))
    elif state == "por-empezar":
        enrollments = enrollments.filter(learning_done=0, last_lesson__isnull=True)
    else:
        state = "todos"
    query = request.GET.get("q", "").strip()[:200]
    if query:
        enrollments = enrollments.filter(version__title__icontains=query)
    page = Paginator(enrollments.order_by("-updated_at", "-pk"), 12).get_page(request.GET.get("pagina"))
    from .certificates import completion_status
    for enrollment in page:
        library_journey(request.user, enrollment)
        enrollment.certificate_status = completion_status(enrollment)
    # Continuation belongs to the whole library, independently of filters or page.
    resume = None
    unfinished = all_enrollments.filter(learning_done__lt=F("learning_total")).order_by("-updated_at", "-pk")
    started = Q(learning_done__gt=0) | Q(last_lesson__isnull=False)
    for candidates in (unfinished.filter(started), unfinished.exclude(started)):
        for candidate in candidates.iterator(chunk_size=30):
            library_journey(request.user, candidate)
            if candidate.can_continue:
                resume = candidate
                break
        if resume:
            break
    resources = Entitlement.objects.active().filter(buyer=request.user, resource__kind__in=("video", "material")).select_related("resource__asset").order_by("-created_at")
    from .models import SavedCollection
    collections = list(SavedCollection.objects.filter(student=request.user).annotate(item_count=Count("items")))
    selected_collection = None
    collection_filter = request.GET.get("coleccion", "")
    saved = SavedItem.objects.filter(student=request.user).select_related("resource", "reference", "course_version__course").prefetch_related("collections")
    if collection_filter == "sin-coleccion":
        saved = saved.filter(collections__isnull=True)
    elif collection_filter:
        if not collection_filter.isdecimal():
            from django.http import Http404
            raise Http404
        selected_collection = get_object_or_404(SavedCollection, student=request.user, pk=collection_filter)
        saved = saved.filter(collections=selected_collection)
    saved_type = request.GET.get("guardados_tipo", "")
    if saved_type == "cursos":
        saved = saved.filter(course_version__kind="course")
    elif saved_type == "tutoriales":
        saved = saved.filter(course_version__kind="tutorial")
    elif saved_type == "recursos":
        saved = saved.filter(resource__isnull=False)
    elif saved_type == "referencias":
        saved = saved.filter(reference__isnull=False)
    else:
        saved_type = ""
    saved_query = request.GET.get("guardados_q", "").strip()[:200]
    if saved_query:
        saved = saved.filter(title__icontains=saved_query)
    saved_page = Paginator(saved, 12).get_page(request.GET.get("guardados_pagina"))
    from .bookmarks import saved_item_presentation
    for item in saved_page:
        saved_item_presentation(request.user, item)
        item.collection_ids = {collection.pk for collection in item.collections.all()}
    certificate_enrollments = Paginator(all_enrollments.filter(version__certificate_policy__isnull=False).order_by("-updated_at", "-pk"), 12).get_page(request.GET.get("certificados_pagina"))
    if section == "certificados":
        for enrollment in certificate_enrollments:
            enrollment.certificate_status = completion_status(enrollment)
    return render(request, "core/workspace.html", {"collections": collections, "selected_collection": selected_collection, "collection_filter": collection_filter, "enrollments": page, "resources": Paginator(resources, 12).get_page(request.GET.get("recursos_pagina")), "saved_items": saved_page, "saved_type": saved_type, "saved_query": saved_query, "active": "workspace", "learning_stats": stats, "learning_state": state, "learning_query": query, "learning_section": section, "resume": resume, "certificate_enrollments": certificate_enrollments})


def lesson_learning_context(user, version, record):
    if not user.is_authenticated or not user.is_active or user.account_type != "student":
        return {}
    enrollment = Enrollment.objects.filter(student=user, version=version).first()
    from .models import VersionPractice
    practice = VersionPractice.objects.filter(lesson=record).first()
    if practice:
        from .practices import practice_is_open
        practice.accepting = practice_is_open(practice)
    quiz = VersionQuiz.objects.filter(lesson=record).first()
    if not enrollment:
        return {"version": version, "lesson_quiz": quiz, "lesson_practice": practice}
    completed = enrollment.completed_lessons.count()
    total = VersionLesson.objects.filter(chapter__version=version).count()
    passed = bool(quiz and QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz, passed=True, submitted_at__isnull=False).exists())
    return {"enrollment": enrollment, "lesson_practice": practice, "lesson_quiz": quiz, "quiz_passed": passed, "quiz_blocks_completion": bool(quiz and quiz.required and not passed), "record_id": record.pk, "question_lesson_id": record.pk, "completed": enrollment.completed_lessons.filter(lesson=record).exists(), "completed_count": completed, "lesson_total": total, "percentage": round(completed * 100 / total) if total else 0}


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
    from .bookmarks import bookmark_context
    right = get_object_or_404(Entitlement.objects.active().select_related("resource__asset", "resource__subtitles", "resource__creator"), buyer=request.user, resource_id=pk)
    resource = right.resource
    from core.telemetry import content_opened
    if resource.kind == "text":
        lesson = VersionLesson.objects.filter(content=resource, chapter__version__published_at__isnull=False).select_related("chapter__version").first()
        if lesson:
            return redirect("version-lesson", course_pk=lesson.chapter.version.course_id, number=lesson.chapter.version.number, lesson_pk=lesson.pk)
    content_opened(request, resource)
    file_url = reverse("purchased-resource-file", args=[resource.pk, "archivo"]) if resource.asset_id and resource.asset.file.storage.exists(resource.asset.file.name) else ""
    return render(request, "learning/resource.html", {"resource": resource, "media": {"standalone": True, "title": resource.title, "kind": resource.kind, "allowed": True, "file_url": file_url, "subtitle_url": reverse("purchased-resource-file", args=[resource.pk, "subtitulos"]) if resource.subtitles_id else "", "body": resource.body, "size": resource.asset.size if resource.asset_id else 0, "mime": resource.asset.mime_type if resource.asset_id else ""}, "active": "workspace", **bookmark_context(request.user, resource=resource)})


@student_required
@require_safe
def purchased_resource_file(request, pk, part):
    right = get_object_or_404(Entitlement.objects.active().select_related("resource__asset", "resource__subtitles"), buyer=request.user, resource_id=pk)
    asset = right.resource.asset if part == "archivo" else right.resource.subtitles if part == "subtitulos" else None
    if asset is None:
        from django.http import Http404
        raise Http404
    response = file_response(request, asset)
    if request.method == "GET" and response.status_code in (200, 206) and part == "archivo":
        from core.telemetry import content_opened
        content_opened(request, right.resource)
    return response
