from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_safe

from media.delivery import file_response

from .access import content_access
from .models import (
    Chapter,
    Course,
    CourseVersion,
    Lesson,
    PublicationStatus,
    VersionAttachment,
    VersionLesson,
)


def load_version(user, course_pk, number):
    version = get_object_or_404(CourseVersion.objects.select_related("course__creator", "topic"), course_id=course_pk, number=number, sealed=True)
    owner = user.is_authenticated and user.is_active and user.pk == version.course.creator_id
    if not owner and (version.course.status != PublicationStatus.PUBLISHED or version.course.current_version_id != version.pk):
        raise Http404
    return version, owner


def version_course(version):
    """Presentation objects keep existing templates, never write draft records."""
    course = Course(pk=version.course_id, creator=version.course.creator, current_version=version, status=version.course.status)
    for field in ("title", "description", "objective", "requirements", "kind", "topic", "level", "estimated_minutes"):
        setattr(course, field, getattr(version, field))
    course.visible_chapters = []
    course.version_number = version.number
    course.detail_url = reverse("course-version", args=[course.pk, version.number])
    metadata = VersionLesson.objects.select_related("content").defer("content__body")
    for stored in version.chapters.prefetch_related(Prefetch("lessons", queryset=metadata)):
        chapter = Chapter(title=stored.title, description=stored.description, course=course, position=stored.position, status=PublicationStatus.PUBLISHED)
        chapter.visible_lessons = []
        for record in stored.lessons.all():
            lesson = Lesson(pk=record.source_lesson_id, chapter=chapter, position=record.position, title=record.content.title, description=record.content.description, body="", access_type=record.content.access_type, status=PublicationStatus.PUBLISHED)
            lesson.detail_url = reverse("version-lesson", args=[course.pk, version.number, record.pk])
            lesson.version_record = record
            chapter.visible_lessons.append(lesson)
        course.visible_chapters.append(chapter)
    return course


@require_GET
@never_cache
def course_version_detail(request, course_pk, number):
    from .catalog import course_summary
    from .views import return_path
    version, preview = load_version(request.user, course_pk, number)
    course = version_course(version)
    summary = course_summary(course)
    first = next((item for item in summary["lessons"] if content_access(request.user, item.version_record).allowed), None)
    return render(request, "content/course.html", {"course": course, "active": "tutorials" if course.kind == "tutorial" else "courses", "summary": summary, "preview": preview, "first_lesson": first, "creator_name": version.creator_name, "return_to": return_path(request, "tutorials" if course.kind == "tutorial" else "courses")})


def attachment_cards(request, attachments):
    cards = []
    for attachment in attachments:
        resource = attachment.resource
        allowed = content_access(request.user, attachment).allowed
        cards.append({"title": resource.title, "kind": resource.kind, "allowed": allowed,
                      "size": resource.asset.size, "mime": resource.asset.mime_type,
                      "body": resource.body if allowed else "",
                      "file_url": reverse("attachment-file", args=[attachment.pk, "archivo"]) if allowed and resource.asset.file.storage.exists(resource.asset.file.name) else "",
                      "subtitle_url": reverse("attachment-file", args=[attachment.pk, "subtitulos"]) if allowed and resource.subtitles_id else ""})
    return cards


@require_GET
@never_cache
def version_lesson_detail(request, course_pk, number, lesson_pk):
    from .catalog import course_summary
    from .views import return_path
    version, preview = load_version(request.user, course_pk, number)
    course = version_course(version)
    lessons = course_summary(course)["lessons"]
    index = next((i for i, item in enumerate(lessons) if item.version_record.pk == lesson_pk), None)
    if index is None:
        raise Http404
    lesson = lessons[index]
    record = lesson.version_record
    decision = content_access(request.user, record)
    body = record.content.body if decision.allowed else None
    lesson.body = ""
    attachments = attachment_cards(request, record.attachments.select_related("resource__asset", "resource__subtitles", "lesson__chapter__version__course")) if decision.allowed else []
    return render(request, "content/lesson.html", {"course": course, "lesson": lesson, "body": body, "allowed": decision.allowed, "preview": preview, "active": "tutorials" if course.kind == "tutorial" else "courses", "return_to": return_path(request, "tutorials" if course.kind == "tutorial" else "courses"), "previous": lessons[index - 1] if index else None, "next_lesson": lessons[index + 1] if index + 1 < len(lessons) else None, "lesson_number": index + 1, "lesson_count": len(lessons), "attachments": attachments}, status=200 if decision.allowed else 403)


@require_safe
@never_cache
def attachment_file(request, pk, part):
    attachment = get_object_or_404(VersionAttachment.objects.select_related("resource__asset", "resource__subtitles", "lesson__content", "lesson__chapter__version__course"), pk=pk)
    decision = content_access(request.user, attachment)
    if not decision.allowed:
        if decision.reason == "unpublished":
            raise Http404
        return HttpResponse("Este contenido requiere una compra.", status=403)
    asset = attachment.resource.asset if part == "archivo" else attachment.resource.subtitles if part == "subtitulos" else None
    if asset is None:
        raise Http404
    return file_response(request, asset)
