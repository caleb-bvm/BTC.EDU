from functools import wraps
from hmac import compare_digest

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from commerce.views import student_required
from content.models import Course, VersionLesson
from creators.services import require_creator
from creators.views import creator_required, protect_legacy

from .certificate_integrity import certificate_bytes, certificate_intact
from .certificates import completion_status, issue_certificate, revoke_certificate
from .essential_forms import (
    CertificateFingerprintForm,
    CertificateNameForm,
    CertificatePolicyForm,
    MessageForm,
)
from .models import (
    Certificate,
    CertificateDraft,
    CertificateSharing,
    Enrollment,
    LessonQuestion,
    Notification,
)
from .support import post_question, question_access, reply_question


def account_required(view):
    @login_required
    @never_cache
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_active or request.user.account_type not in ("student", "creator"):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped


@creator_required
@require_http_methods(["GET", "POST"])
def certificate_policy_edit(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, creator=request.user)
    protect_legacy(course)
    draft = CertificateDraft.objects.filter(course=course).first()
    initial = {"enabled": draft.enabled if draft else False, "required_lessons": draft.required_lessons.all() if draft else [], "revision": draft.revision if draft else 0}
    form = CertificatePolicyForm(request.POST if request.method == "POST" else None, course=course, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                Course.objects.filter(pk=course.pk).update(updated_at=F("updated_at"))
                course.refresh_from_db()
                request.user.refresh_from_db()
                require_creator(request.user)
                if course.creator_id != request.user.pk:
                    raise PermissionDenied
                current, _ = CertificateDraft.objects.get_or_create(course=course)
                if current.revision != form.cleaned_data["revision"]:
                    raise ValidationError("Hay un borrador más reciente. Recarga antes de guardar.")
                from content.models import Lesson
                selected_ids = [item.pk for item in form.cleaned_data["required_lessons"]]
                selected = list(Lesson.objects.select_related("chapter").filter(pk__in=selected_ids))
                if len(selected) != len(selected_ids):
                    raise ValidationError("Las lecciones seleccionadas cambiaron. Recarga el temario.")
                if any(item.chapter.course_id != course.pk or item.status != "published" or item.chapter.status != "published" for item in selected):
                    raise ValidationError("Las lecciones seleccionadas cambiaron. Recarga el temario.")
                current.enabled = form.cleaned_data["enabled"]
                current.revision += 1
                current.save()
                current.required_lessons.set(selected)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Requisitos guardados. Envía el curso a revisión para publicarlos.")
            return redirect("creator-certificate-policy", course_pk=course.pk)
    return render(request, "learning/certificate_policy.html", {"form": form, "course": course})


@student_required
@require_http_methods(["GET", "POST"])
def certificate_request(request, enrollment_pk):
    enrollment = get_object_or_404(Enrollment.objects.select_related("version"), pk=enrollment_pk, student=request.user)
    status = completion_status(enrollment)
    if status["certificate"]:
        return redirect("certificate-detail", pk=status["certificate"].pk)
    form = CertificateNameForm(request.POST if request.method == "POST" else None, initial={"student_name": request.user.get_full_name()})
    if request.method == "POST" and form.is_valid():
        try:
            certificate = issue_certificate(request.user, enrollment.pk, form.cleaned_data["student_name"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("certificate-detail", pk=certificate.pk)
    return render(request, "learning/certificate_request.html", {"enrollment": enrollment, "form": form, **status})


@student_required
@require_GET
def certificates_list(request):
    certificates = Certificate.objects.filter(enrollment__student=request.user).select_related("enrollment__version", "sharing", "revocation").order_by("-issued_at")
    return render(request, "learning/certificates.html", {"certificates": Paginator(certificates, 12).get_page(request.GET.get("pagina"))})


@student_required
@require_GET
def certificate_detail(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related("enrollment__version", "sharing", "revocation"), pk=pk, enrollment__student=request.user)
    return render(request, "learning/certificate.html", {"certificate": certificate, "verification_url": request.build_absolute_uri(reverse("certificate-verify", args=[pk]))})


@student_required
@require_POST
def certificate_share(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk, enrollment__student=request.user)
    if request.POST.get("public") not in ("yes", "no"):
        return HttpResponse("Elige una opción de compartición.", status=400)
    CertificateSharing.objects.filter(certificate=certificate).update(public=request.POST["public"] == "yes")
    return redirect("certificate-detail", pk=pk)


@require_GET
@never_cache
def certificate_verify(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related("enrollment__version", "revocation"), pk=pk, sharing__public=True)
    intact = certificate_intact(certificate)
    form = CertificateFingerprintForm(request.GET if "sha256" in request.GET else None)
    matches = compare_digest(form.cleaned_data["sha256"].lower(), certificate.fingerprint) if form.is_bound and form.is_valid() else None
    response = render(request, "learning/certificate_verify.html", {"certificate": certificate, "integrity_ok": intact, "fingerprint_form": form, "fingerprint_matches": matches})
    response["X-Robots-Tag"] = "noindex, nofollow"
    response["Referrer-Policy"] = "no-referrer"
    return response


def certificate_data_response(certificate):
    if not certificate_intact(certificate):
        return HttpResponse("No se pudo comprobar la integridad del certificado.", status=409)
    response = HttpResponse(certificate_bytes(certificate), content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="certificado-{certificate.pk}.json"'
    response["X-Robots-Tag"] = "noindex, nofollow"
    response["Referrer-Policy"] = "no-referrer"
    return response


@student_required
@never_cache
@require_GET
def certificate_data(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related("enrollment__version"), pk=pk, enrollment__student=request.user)
    return certificate_data_response(certificate)


@never_cache
@require_GET
def certificate_public_data(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related("enrollment__version"), pk=pk, sharing__public=True)
    return certificate_data_response(certificate)


@student_required
@require_GET
def certificate_pdf(request, pk):
    certificate = get_object_or_404(Certificate.objects.select_related("enrollment__version", "revocation"), pk=pk, enrollment__student=request.user)
    if hasattr(certificate, "revocation"):
        raise Http404
    if not certificate_intact(certificate):
        return HttpResponse("No se pudo comprobar la integridad del certificado.", status=409)
    from .certificate_pdf import render_certificate
    response = HttpResponse(render_certificate(certificate), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="certificado-{certificate.pk}.pdf"'
    return response


@login_required(login_url="admin:login")
@never_cache
@require_http_methods(["GET", "POST"])
def certificate_revoke(request, pk):
    if not request.user.is_active or not request.user.is_staff or not request.user.has_perm("learning.add_certificaterevocation"):
        raise PermissionDenied
    certificate = get_object_or_404(Certificate, pk=pk)
    error = ""
    if request.method == "POST":
        try:
            revoke_certificate(request.user, pk, request.POST.get("reason", ""))
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            return redirect("admin:learning_certificate_changelist")
    return render(request, "learning/certificate_revoke.html", {"certificate": certificate, "error": error})


@student_required
@require_http_methods(["GET", "POST"])
def question_create(request, lesson_pk):
    lesson = get_object_or_404(VersionLesson.objects.select_related("content", "chapter__version__course"), pk=lesson_pk)
    from content.access import content_access
    if not Enrollment.objects.filter(student=request.user, version=lesson.chapter.version).exists() or not content_access(request.user, lesson).allowed:
        raise PermissionDenied
    form = MessageForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            question = post_question(request.user, lesson.pk, form.cleaned_data["body"], form.cleaned_data["request_key"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("student-question", pk=question.pk)
    return render(request, "learning/question_create.html", {"lesson": lesson, "form": form})


def questions_context(queryset, request):
    page = Paginator(queryset.select_related("lesson__content", "enrollment__version", "enrollment__student").prefetch_related("replies").order_by("-created_at", "-pk"), 20).get_page(request.GET.get("pagina"))
    for question in page:
        replies = list(question.replies.all())
        question.awaiting_creator = not replies or replies[-1].author_id == question.enrollment.student_id
    return {"questions": page}


@student_required
@require_GET
def student_questions(request):
    return render(request, "learning/questions.html", {"base_template": "academy.html", **questions_context(LessonQuestion.objects.filter(enrollment__student=request.user), request)})


@creator_required
@require_GET
def creator_questions(request):
    return render(request, "learning/questions.html", {"base_template": "creators/base.html", "creator_space": True, **questions_context(LessonQuestion.objects.filter(enrollment__version__course__creator=request.user), request)})


@account_required
@require_http_methods(["GET", "POST"])
def question_detail(request, pk, creator_space=False):
    if (request.user.account_type == "creator") != creator_space:
        raise PermissionDenied
    question = get_object_or_404(LessonQuestion.objects.select_related("lesson__content", "lesson__chapter__version__course", "enrollment__version__course", "enrollment__student"), pk=pk)
    question_access(request.user, question)
    form = MessageForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            reply_question(request.user, question.pk, form.cleaned_data["body"], form.cleaned_data["request_key"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("creator-question" if creator_space else "student-question", pk=pk)
    return render(request, "learning/question.html", {"base_template": "creators/base.html" if creator_space else "academy.html", "creator_space": creator_space, "question": question, "replies": question.replies.select_related("author"), "form": form})


@account_required
@require_GET
def notifications(request):
    notices = Notification.objects.filter(recipient=request.user)
    return render(request, "learning/notifications.html", {"base_template": "creators/base.html" if request.user.account_type == "creator" else "academy.html", "notices": Paginator(notices, 20).get_page(request.GET.get("pagina")), "unread_count": notices.filter(read_at__isnull=True).count()})


@account_required
@require_POST
def notification_read(request, pk):
    notice = get_object_or_404(Notification, pk=pk, recipient=request.user)
    Notification.objects.filter(pk=pk, recipient=request.user, read_at__isnull=True).update(read_at=timezone.now())
    return redirect(notice.url)
