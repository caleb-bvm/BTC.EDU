"""Course reviews limited to students who bought from or completed the course."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.urls import reverse
from django.utils import timezone

from commerce.models import Entitlement
from content.models import VersionAttachment, VersionLesson

from .models import CourseReview, Enrollment
from .support import notify


def review_basis(user, course):
    """Return (basis, version) for an eligible reviewer, or (None, None)."""
    if not user.is_authenticated or not user.is_active or user.account_type != "student" or user.pk == course.creator_id:
        return None, None
    enrollments = list(Enrollment.objects.filter(student=user, version__course=course).select_related("version").order_by("-version__number"))
    for enrollment in enrollments:
        version = enrollment.version
        resources = VersionLesson.objects.filter(chapter__version=version).values("content_id")
        attachments = VersionAttachment.objects.filter(lesson__chapter__version=version).values("resource_id")
        if Entitlement.objects.active().filter(buyer=user, resource__access_type="paid").filter(
                Q(resource_id__in=resources) | Q(resource_id__in=attachments)).exists():
            return CourseReview.Basis.PURCHASE, version
    for enrollment in enrollments:
        total = VersionLesson.objects.filter(chapter__version=enrollment.version).count()
        if total and enrollment.completed_lessons.count() >= total:
            return CourseReview.Basis.COMPLETED, enrollment.version
    return None, None


def visible_reviews(course):
    return CourseReview.objects.filter(course=course, hidden=False).select_related("student", "version")


def rating_summary(course):
    data = visible_reviews(course).aggregate(average=Avg("rating"), count=Count("pk"))
    count = data["count"] or 0
    return {"count": count, "average": round(data["average"], 1) if count else None,
            "stars": round(data["average"]) if count else 0}


@transaction.atomic
def save_review(actor, course, rating, body):
    basis, version = review_basis(actor, course)
    if basis is None:
        raise PermissionDenied("Solo pueden opinar quienes compraron o completaron este curso.")
    if type(rating) is not int or not 1 <= rating <= 5:
        raise ValidationError("Elige una valoración de 1 a 5.")
    body = str(body or "").strip()
    if len(body) > 2000:
        raise ValidationError("La reseña admite hasta 2000 caracteres.")
    review, created = CourseReview.objects.get_or_create(course=course, student=actor, defaults={
        "version": version, "rating": rating, "body": body, "basis": basis})
    if not created:
        review.version, review.rating, review.body, review.basis = version, rating, body, basis
        review.full_clean()
        review.save(update_fields=("version", "rating", "body", "basis", "updated_at"))
    notify(course.creator, f"review:{review.pk}:{int(review.updated_at.timestamp())}", f"Nueva reseña de {rating} estrellas en «{course.title}»",
           reverse("course-detail", args=[course.pk]) + "#course-reviews")
    return review


@transaction.atomic
def reply_review(actor, review, body):
    if not actor.is_authenticated or not actor.is_active or actor.pk != review.course.creator_id:
        raise PermissionDenied
    body = str(body or "").strip()
    if not body or len(body) > 1000:
        raise ValidationError("Escribe una respuesta de hasta 1000 caracteres.")
    CourseReview.objects.filter(pk=review.pk).update(reply=body, replied_at=timezone.now())
    review.refresh_from_db()
    return review
