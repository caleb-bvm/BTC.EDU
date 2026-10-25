from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from commerce.views import student_required
from content.identity import public_creator_name
from content.models import Course, PublicationStatus
from creators.views import creator_required

from .models import (
    Certificate,
    CertificateTimestamp,
    CourseReview,
    LearningPath,
    PathCompletion,
)
from .paths import issue_path_credential, path_bytes, path_progress, published_paths
from .reviews import reply_review, save_review
from .showcase import gallery_items, set_showcase
from .timestamps import describe, stamp_certificate


def public_course(pk):
    course = get_object_or_404(Course.objects.select_related("creator", "current_version"), pk=pk)
    if course.status != PublicationStatus.PUBLISHED or not course.current_version_id:
        raise Http404
    return course


def course_url(course):
    return reverse("course-version", args=[course.pk, course.current_version.number])


@student_required
@require_POST
def review_save(request, course_pk):
    course = public_course(course_pk)
    try:
        rating = int(request.POST.get("rating", ""))
    except ValueError:
        rating = 0
    try:
        save_review(request.user, course, rating, request.POST.get("body", ""))
    except (ValidationError, PermissionDenied) as exc:
        messages.error(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Solo pueden opinar quienes compraron o completaron este curso.")
    else:
        messages.success(request, "Gracias. Tu reseña ya es visible en el curso.")
    return redirect(course_url(course) + "#course-reviews")


@creator_required
@require_POST
def review_reply(request, pk):
    review = get_object_or_404(CourseReview.objects.select_related("course__current_version"), pk=pk, course__creator=request.user)
    try:
        reply_review(request.user, review, request.POST.get("reply", ""))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Respuesta publicada.")
    return redirect(course_url(review.course) + "#course-reviews" if review.course.current_version_id else "creator-dashboard")


@require_GET
@never_cache
def course_gallery(request, pk):
    course = public_course(pk)
    page = Paginator(gallery_items(course), 12).get_page(request.GET.get("pagina"))
    return render(request, "learning/gallery.html", {"course": course, "items": page, "course_url": course_url(course),
                                                    "creator_name": public_creator_name(course.creator),
                                                    "active": "tutorials" if course.kind == "tutorial" else "courses"})


@student_required
@require_POST
def showcase_toggle(request, pk):
    try:
        showcase = set_showcase(request.user, pk, request.POST.get("public") == "yes")
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("student-practices")
    messages.success(request, "Tu práctica aparece en la galería del curso." if showcase.public else "Tu práctica ya no aparece en la galería.")
    return redirect("student-practice", pk=showcase.delivery.practice_id)


def path_overview(user, path):
    """Progress joined with how each course is reached and the bundle price, for the path pages."""
    from commerce.bundles import BUNDLE_MIN_COURSES, bundle_quote, bundle_rows
    progress = path_progress(user, path)
    rows = bundle_rows(user, path)
    access = {row["course"].pk: row for row in rows}
    for item in progress["steps"]:
        row = access.get(item["course"].pk)
        item["access"] = row["state"] if row else "free"
        item["price"] = row["offer"].amount_sats if row and row["offer"] else None
    buy = sum(row["state"] == "bundle" for row in rows)
    quote = bundle_quote(user, path, rows) if path.bundle_percent and buy >= BUNDLE_MIN_COURSES else None
    return {"path": path, "progress": progress, "bundle": quote, "to_buy": buy,
            "membership_steps": sum(item["access"] == "membership" for item in progress["steps"])}


@require_GET
@never_cache
def paths_list(request):
    entries = [path_overview(request.user, path) for path in published_paths()]
    return render(request, "learning/paths.html", {"editorial": [entry for entry in entries if not entry["path"].creator_id],
                                                   "educators": [entry for entry in entries if entry["path"].creator_id],
                                                   "active": "learning-paths"})


@require_http_methods(["GET", "POST"])
@never_cache
def path_detail(request, slug):
    path = get_object_or_404(LearningPath.objects.select_related("creator__creator_profile"), slug=slug, published=True)
    if request.method == "POST":
        if not request.user.is_authenticated or request.user.account_type != "student":
            raise PermissionDenied
        try:
            completion = issue_path_credential(request.user, path, request.POST.get("student_name", ""))
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        else:
            return redirect("path-credential", pk=completion.pk)
    return render(request, "learning/path.html", {**path_overview(request.user, path), "active": "learning-paths"})


@student_required
@require_http_methods(["GET", "POST"])
def path_credential(request, pk):
    completion = get_object_or_404(PathCompletion.objects.select_related("path"), pk=pk, student=request.user)
    if request.method == "POST" and request.POST.get("public") in ("yes", "no"):
        PathCompletion.objects.filter(pk=completion.pk).update(public=request.POST["public"] == "yes")
        return redirect("path-credential", pk=pk)
    return render(request, "learning/path_credential.html", {"completion": completion, "owner": True, "active": "workspace",
                                                            "verification_url": request.build_absolute_uri(reverse("path-verify", args=[pk]))})


@require_GET
@never_cache
def path_verify(request, pk):
    completion = get_object_or_404(PathCompletion.objects.select_related("path"), pk=pk, public=True)
    from .paths import path_digest
    response = render(request, "learning/path_credential.html", {"completion": completion, "owner": False,
                                                                "integrity_ok": path_digest(completion) == completion.fingerprint})
    response["X-Robots-Tag"] = "noindex, nofollow"
    response["Referrer-Policy"] = "no-referrer"
    return response


@require_GET
@never_cache
def path_verify_data(request, pk):
    completion = get_object_or_404(PathCompletion, pk=pk, public=True)
    response = HttpResponse(path_bytes(completion), content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="ruta-{completion.pk}.json"'
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


def proof_response(certificate):
    record = CertificateTimestamp.objects.filter(certificate=certificate).first()
    if record is None:
        raise Http404
    response = HttpResponse(bytes(record.proof), content_type="application/octet-stream")
    response["Content-Disposition"] = f'attachment; filename="certificado-{certificate.pk}.json.ots"'
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


@student_required
@require_GET
def certificate_proof(request, pk):
    return proof_response(get_object_or_404(Certificate, pk=pk, enrollment__student=request.user))


@require_GET
@never_cache
def certificate_public_proof(request, pk):
    return proof_response(get_object_or_404(Certificate, pk=pk, sharing__public=True))


@student_required
@require_POST
def certificate_stamp(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related("enrollment__version"), pk=pk, enrollment__student=request.user)
    if stamp_certificate(certificate) is None and not CertificateTimestamp.objects.filter(certificate=certificate).exists():
        messages.warning(request, "No pudimos solicitar el sello ahora. Inténtalo más tarde.")
    else:
        messages.success(request, "Sello solicitado. La confirmación en Bitcoin suele tardar algunas horas.")
    return redirect("certificate-detail", pk=pk)


def timestamp_context(certificate):
    return describe(CertificateTimestamp.objects.filter(certificate=certificate).first())
