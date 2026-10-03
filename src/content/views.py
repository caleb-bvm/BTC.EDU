from urllib.parse import urlsplit

from django.db.models import F, Prefetch
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_safe

from media.delivery import file_response

from .access import content_access
from .catalog import course_summary, course_tree
from .models import (
    Course,
    CourseKind,
    ExternalReference,
    Lesson,
    Material,
    PublicationStatus,
    VersionLesson,
    Video,
)


def is_owner(user, course):
    return user.is_authenticated and user.is_active and user.pk == course.creator_id


def return_path(request, default):
    destination = request.GET.get("volver", "")
    if destination.startswith("/") and not destination.startswith("//") and url_has_allowed_host_and_scheme(destination, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return destination
    return reverse(default)


def load_course(user, pk):
    course = get_object_or_404(Course.objects.select_related("creator", "topic"), pk=pk)
    preview = is_owner(user, course)
    if course.status != PublicationStatus.PUBLISHED and not preview:
        raise Http404
    course = (
        Course.objects.prefetch_related(
            Prefetch(
                "chapters", queryset=course_tree(preview), to_attr="visible_chapters"
            )
        )
        .select_related("creator", "topic")
        .get(pk=pk)
    )
    course.detail_url = reverse("course-detail", args=[course.pk])
    for chapter in course.visible_chapters:
        for lesson in chapter.visible_lessons:
            lesson.detail_url = reverse("lesson-detail", args=[lesson.pk])
    return course, preview


@require_GET
@never_cache
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if course.current_version_id and not (request.GET.get("borrador") == "1" and is_owner(request.user, course)):
        from .version_views import course_version_detail
        return course_version_detail(request, pk, course.current_version.number)
    course, preview = load_course(request.user, pk)
    summary = course_summary(course)
    first = next(
        (
            lesson
            for lesson in summary["lessons"]
            if content_access(request.user, lesson).allowed
        ),
        None,
    )
    return render(
        request,
        "content/course.html",
        {
            "active": "tutorials" if course.kind == CourseKind.TUTORIAL else "courses",
            "course": course,
            "summary": summary,
            "preview": preview,
            "first_lesson": first,
            "return_to": return_path(request, "tutorials" if course.kind == CourseKind.TUTORIAL else "courses"),
            "creator_name": course.creator.get_full_name().strip()
            or "Creador de BTC.EDU",
        },
    )


@require_GET
@never_cache
def lesson_detail(request, pk):
    frozen = VersionLesson.objects.select_related("chapter__version__course").filter(source_lesson_id=pk, chapter__version_id=F("chapter__version__course__current_version_id")).first()
    if frozen and request.GET.get("borrador") != "1":
        from .version_views import version_lesson_detail
        return version_lesson_detail(request, frozen.chapter.version.course_id, frozen.chapter.version.number, frozen.pk)
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=pk)
    if lesson.chapter.course.current_version_id and not is_owner(request.user, lesson.chapter.course):
        raise Http404
    decision = content_access(request.user, lesson)
    if decision.reason == "unpublished":
        raise Http404
    course, preview = load_course(request.user, lesson.chapter.course_id)
    lessons = course_summary(course)["lessons"]
    index = next(i for i, item in enumerate(lessons) if item.pk == lesson.pk)
    # El cuerpo protegido no se pasa a la plantilla cuando falta acceso.
    body = lesson.body if decision.allowed else None
    lesson.body = ""
    return render(
        request,
        "content/lesson.html",
        {
            "active": "tutorials" if course.kind == CourseKind.TUTORIAL else "courses",
            "course": course,
            "lesson": lesson,
            "body": body,
            "allowed": decision.allowed,
            "preview": preview,
            "return_to": return_path(request, "tutorials" if course.kind == CourseKind.TUTORIAL else "courses"),
            "previous": lessons[index - 1] if index else None,
            "next_lesson": lessons[index + 1] if index + 1 < len(lessons) else None,
            "lesson_number": index + 1,
            "lesson_count": len(lessons),
        },
        status=200 if decision.allowed else 403,
    )


@require_GET
@never_cache
def resource_detail(request, kind, pk):
    model = {"videos": Video, "materiales": Material}.get(kind)
    if model is None:
        raise Http404
    resource = get_object_or_404(
        model.objects.select_related("creator"),
        pk=pk,
        status=PublicationStatus.PUBLISHED,
    )
    decision = content_access(request.user, resource)
    revision = resource.revision
    if revision:
        resource.title, resource.description, resource.access_type = revision.title, revision.description, revision.access_type
    file_url = reverse("resource-file", args=[kind, pk, revision.number, "archivo"]) if revision and decision.allowed else ""
    subtitles_url = reverse("resource-file", args=[kind, pk, revision.number, "subtitulos"]) if revision and revision.subtitles_id and decision.allowed else ""
    return render(
        request,
        "content/resource.html",
        {
            "active": "resources",
            "resource": resource,
            "kind": "Video" if kind == "videos" else "Material",
            "allowed": decision.allowed, "file_url": file_url, "subtitle_url": subtitles_url,
            "asset": revision.asset if revision else None,
            "transcript": revision.body if revision and decision.allowed else "",
            "media": {"standalone": True, "title": resource.title, "kind": "video" if kind == "videos" else "material", "allowed": decision.allowed, "file_url": file_url if revision and revision.asset.file.storage.exists(revision.asset.file.name) else "", "subtitle_url": subtitles_url, "body": revision.body if revision and decision.allowed else "", "size": revision.asset.size if revision else 0, "mime": revision.asset.mime_type if revision else ""},
            "return_to": return_path(request, "resources"),
            "creator_name": resource.creator.get_full_name().strip()
            or "Creador de BTC.EDU",
        },
    )


@require_GET
def reference_detail(request, pk):
    reference = get_object_or_404(ExternalReference.objects.select_related("topic"), pk=pk, status=PublicationStatus.PUBLISHED)
    parsed_url = urlsplit(reference.source_url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
        raise Http404
    return render(request, "content/reference.html", {"active": "resources", "reference": reference, "return_to": return_path(request, "resources")})


@require_GET
@never_cache
def lesson_content(request, pk):
    frozen = VersionLesson.objects.select_related("content", "chapter__version__course").filter(source_lesson_id=pk, chapter__version_id=F("chapter__version__course__current_version_id")).first()
    if frozen:
        decision = content_access(request.user, frozen)
        if not decision.allowed:
            return JsonResponse({"error": "not_found" if decision.reason == "unpublished" else "purchase_required"}, status=404 if decision.reason == "unpublished" else 403)
        return JsonResponse({"id": pk, "title": frozen.content.title, "body": frozen.content.body, "access": decision.reason, "version": frozen.chapter.version.number})
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=pk)
    if lesson.chapter.course.current_version_id:
        raise Http404
    decision = content_access(request.user, lesson)
    if not decision.allowed:
        if decision.reason == "unpublished":
            return JsonResponse({"error": "not_found"}, status=404)
        return JsonResponse({"error": "purchase_required"}, status=403)
    return JsonResponse(
        {
            "id": lesson.pk,
            "title": lesson.title,
            "body": lesson.body,
            "access": decision.reason,
        }
    )


@require_safe
@never_cache
def resource_file(request, kind, pk, number, part):
    model = {"videos": Video, "materiales": Material}.get(kind)
    if model is None:
        raise Http404
    resource = get_object_or_404(model.objects.select_related("revision__asset", "revision__subtitles"), pk=pk)
    revision = resource.revision
    if revision is None or revision.number != number:
        raise Http404
    decision = content_access(request.user, resource)
    if not decision.allowed:
        if decision.reason == "unpublished":
            raise Http404
        return HttpResponse("Este contenido requiere una compra.", status=403)
    asset = revision.asset if part == "archivo" else revision.subtitles if part == "subtitulos" else None
    if asset is None:
        raise Http404
    return file_response(request, asset)
