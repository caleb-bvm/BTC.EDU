from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_safe

from commerce.models import Entitlement
from commerce.views import student_required
from content.access import content_access
from content.models import CourseVersion, VersionLesson
from media.delivery import file_response

from .models import Enrollment
from .services import enroll


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
    enrollments = Enrollment.objects.filter(student=request.user).select_related("version__course").prefetch_related("version__chapters__lessons__content")
    page = Paginator(enrollments.order_by("-created_at"), 12).get_page(request.GET.get("pagina"))
    for enrollment in page:
        version = enrollment.version
        lessons = [lesson for chapter in version.chapters.all() for lesson in chapter.lessons.all()]
        first = next((lesson for lesson in lessons if content_access(request.user, lesson).allowed), None)
        enrollment.open_url = reverse("version-lesson", args=[version.course_id, version.number, first.pk]) if first else reverse("course-version", args=[version.course_id, version.number])
        enrollment.lesson_count = len(lessons)
        enrollment.retired = version.course.status == "archived" or version.course.current_version_id != version.pk
    resources = Entitlement.objects.filter(buyer=request.user, resource__kind__in=("video", "material")).select_related("resource__asset").order_by("-created_at")
    return render(request, "core/workspace.html", {"enrollments": page, "resources": Paginator(resources, 12).get_page(request.GET.get("recursos_pagina")), "active": "workspace"})


@student_required
@require_GET
def purchased_resource(request, pk):
    right = get_object_or_404(Entitlement.objects.select_related("resource__asset", "resource__subtitles", "resource__creator"), buyer=request.user, resource_id=pk)
    resource = right.resource
    if resource.kind == "text":
        lesson = VersionLesson.objects.filter(content=resource, chapter__version__published_at__isnull=False).select_related("chapter__version").first()
        if lesson:
            return redirect("version-lesson", course_pk=lesson.chapter.version.course_id, number=lesson.chapter.version.number, lesson_pk=lesson.pk)
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
    return file_response(request, asset)
