from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_safe

from media.delivery import file_response

from .access import content_access
from .education import education_values
from .identity import public_creator_name
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
    version = get_object_or_404(CourseVersion.objects.select_related("course__creator__creator_profile", "topic"), course_id=course_pk, number=number, sealed=True)
    owner = user.is_authenticated and user.is_active and user.pk == version.course.creator_id
    from learning.services import can_visit_version
    if not owner and (version.course.status not in (PublicationStatus.PUBLISHED, PublicationStatus.ARCHIVED) or not can_visit_version(user, version)):
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
            lesson = Lesson(pk=record.source_lesson_id, chapter=chapter, position=record.position, title=record.content.title, description=record.content.description, body="", access_type=record.content.access_type, status=PublicationStatus.PUBLISHED, **education_values(record.content))
            lesson.detail_url = reverse("version-lesson", args=[course.pk, version.number, record.pk])
            lesson.version_record = record
            chapter.visible_lessons.append(lesson)
        course.visible_chapters.append(chapter)
    return course


@require_GET
@never_cache
def course_version_detail(request, course_pk, number):
    from learning.bookmarks import bookmark_context

    from .catalog import course_summary
    from .views import return_path
    version, preview = load_version(request.user, course_pk, number)
    course = version_course(version)
    summary = course_summary(course)
    first = next((item for item in summary["lessons"] if content_access(request.user, item.version_record).allowed), None)
    from commerce.catalog import version_offers, version_owned
    from core.telemetry import offer_views
    from learning.presentation import course_learning_context
    journey = course_learning_context(request.user, course, version)
    from commerce.pricing import annotate_upgrades
    offers = annotate_upgrades(request.user, version_offers(version))
    if not preview:
        offer_views(request, offers)
    from learning.models import VersionCertificatePolicy
    policy = VersionCertificatePolicy.objects.filter(version=version).first()
    required_lessons = VersionLesson.objects.filter(pk__in=policy.required_lesson_ids).select_related("content") if policy else []
    from learning.models import CourseReview, PathCourse
    from learning.reviews import rating_summary, review_basis, visible_reviews
    from learning.showcase import gallery_items
    basis, _ = review_basis(request.user, version.course) if not preview else (None, None)
    community = {"rating": rating_summary(version.course), "reviews": visible_reviews(version.course)[:10],
                 "can_review": basis is not None, "review_basis": basis,
                 "my_review": CourseReview.objects.filter(course=version.course, student=request.user).first() if request.user.is_authenticated else None,
                 "gallery_count": gallery_items(version.course).count(),
                 "course_paths": [step.path for step in PathCourse.objects.filter(course=version.course, path__published=True).select_related("path")]}
    return render(request, "content/course.html", {"course": course, **community, "active": "tutorials" if course.kind == "tutorial" else "courses", "summary": summary, "preview": preview, "first_lesson": first, "creator_name": public_creator_name(version.course.creator), "return_to": return_path(request, "tutorials" if course.kind == "tutorial" else "courses"), "offers": offers, "version": version, "has_purchase": version_owned(request.user, version), "certificate_policy": policy, "certificate_lessons": required_lessons, **journey, **bookmark_context(request.user, course_version=version)})


def attachment_cards(request, attachments):
    cards = []
    for attachment in attachments:
        resource = attachment.resource
        allowed = content_access(request.user, attachment).allowed
        cards.append({"title": resource.title, "kind": resource.kind, "allowed": allowed, "unit": resource,
                      "size": resource.asset.size, "mime": resource.asset.mime_type,
                      "body": resource.body if allowed else "",
                      "file_url": reverse("attachment-file", args=[attachment.pk, "archivo"]) if allowed and resource.asset.file.storage.exists(resource.asset.file.name) else "",
                      "subtitle_url": reverse("attachment-file", args=[attachment.pk, "subtitulos"]) if allowed and resource.subtitles_id else ""})
    return cards


@require_http_methods(["GET", "POST"])
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
    from learning.lesson_discussion import conversation_url, reader_context, submit
    submitted_form, submitted_parent = None, None
    if request.method == "POST":
        if not decision.allowed:
            raise PermissionDenied
        post, submitted_form, submitted_parent = submit(request, version, record)
        if post:
            return redirect(conversation_url(request.user, post))
    discussion = reader_context(request, version, record, submitted_form, submitted_parent) if decision.allowed else {}
    body = record.content.body if decision.allowed else None
    lesson.body = ""
    attachments = attachment_cards(request, record.attachments.select_related("resource__asset", "resource__subtitles", "lesson__chapter__version__course")) if decision.allowed else []
    from commerce.catalog import lesson_offers
    from learning.presentation import course_learning_context
    from learning.views import lesson_learning_context

    from .reading import reading_sections
    journey = course_learning_context(request.user, course, version, record.pk)
    learning = lesson_learning_context(request.user, version, record) if decision.allowed else {}
    if decision.allowed and not preview:
        from core.telemetry import content_opened
        content_opened(request, record.content, version)
    offers = lesson_offers(request.user, record) if not decision.allowed else []
    if offers and not preview:
        from core.telemetry import offer_views
        offer_views(request, offers)
    return render(request, "content/lesson.html", {"course": course, "lesson": lesson, "body": body, "reading_sections": reading_sections(body), "allowed": decision.allowed, "preview": preview, "version": version, "active": "tutorials" if course.kind == "tutorial" else "courses", "return_to": return_path(request, "tutorials" if course.kind == "tutorial" else "courses"), "previous": lessons[index - 1] if index else None, "next_lesson": lessons[index + 1] if index + 1 < len(lessons) else None, "lesson_number": index + 1, "lesson_count": len(lessons), "attachments": attachments, "offers": offers, "purchase_return": record.pk, "lesson_context": True, **learning, **journey, **discussion}, status=200 if decision.allowed else 403)


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
    response = file_response(request, asset)
    if request.method == "GET" and response.status_code in (200, 206) and part == "archivo":
        from core.telemetry import content_opened
        content_opened(request, attachment.resource, attachment.lesson.chapter.version)
    return response
