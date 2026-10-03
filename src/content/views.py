from urllib.parse import urlsplit

from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .access import content_access
from .catalog import course_summary, course_tree
from .models import (
    Course,
    CourseKind,
    ExternalReference,
    Lesson,
    Material,
    PublicationStatus,
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
    return course, preview


@require_GET
@never_cache
def course_detail(request, pk):
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
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=pk)
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
def resource_detail(request, kind, pk):
    model = {"videos": Video, "materiales": Material}.get(kind)
    if model is None:
        raise Http404
    resource = get_object_or_404(
        model.objects.select_related("creator"),
        pk=pk,
        status=PublicationStatus.PUBLISHED,
    )
    return render(
        request,
        "content/resource.html",
        {
            "active": "resources",
            "resource": resource,
            "kind": "Video" if kind == "videos" else "Material",
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
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=pk)
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
