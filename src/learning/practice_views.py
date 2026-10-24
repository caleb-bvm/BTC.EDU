import uuid

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from commerce.views import student_required
from content.access import content_access
from content.models import Course, Lesson
from creators.views import creator_required, protect_legacy

from .essential_views import account_required
from .models import PracticeDelivery, PracticeDraft, VersionPractice
from .practice_forms import DeliveryForm, PracticeForm, ReviewForm
from .practices import (
    educator_practice,
    practice_is_open,
    review_delivery,
    save_practice,
    set_intake,
    student_practice,
    submit_delivery,
)


@creator_required
@require_http_methods(["GET", "POST"])
def edit(request, lesson_pk):
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=lesson_pk, chapter__course__creator=request.user)
    protect_legacy(lesson.chapter.course)
    draft = PracticeDraft.objects.filter(lesson=lesson).first()
    initial = {field: getattr(draft, field) for field in ("enabled", "title", "instructions", "review_days", "revision")} if draft else {"enabled": True, "title": f"Práctica: {lesson.title}"[:200], "revision": 0}
    initial["criteria_text"] = "\n".join(draft.criteria) if draft else ""
    form = PracticeForm(request.POST if request.method == "POST" else None, initial=initial)
    if request.method == "POST" and form.is_valid():
        values = {**form.cleaned_data, "criteria": form.cleaned_data["criteria_text"]}
        try:
            save_practice(request.user, lesson.pk, values, form.cleaned_data["revision"])
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, "Práctica guardada. Envía el curso a revisión para publicarla.")
            return redirect("creator-practice", lesson_pk=lesson.pk)
    from creators.presentation import course_sections
    return render(request, "learning/practice_editor.html", {"form": form, "lesson": lesson, "course_sections": course_sections(lesson.chapter.course, "evaluaciones"), "active": "creator-content"})


@student_required
@require_GET
def student_list(request):
    practices = VersionPractice.objects.filter(lesson__chapter__version__enrollment__student=request.user).select_related("lesson__content", "lesson__chapter__version__course", "intake").order_by("lesson__chapter__version__title", "lesson__chapter__position", "lesson__position", "pk")
    page = Paginator(practices, 12).get_page(request.GET.get("pagina"))
    for practice in page:
        practice.latest = practice.deliveries.filter(enrollment__student=request.user).select_related("review").order_by("-number").first()
    return render(request, "learning/practices.html", {"practices": page, "active": "workspace"})


@student_required
@never_cache
@require_http_methods(["GET", "POST"])
def detail(request, pk):
    practice = get_object_or_404(VersionPractice.objects.select_related("lesson__content", "lesson__chapter__version__course"), pk=pk)
    enrollment = student_practice(request.user, practice)
    history = practice.deliveries.filter(enrollment=enrollment).select_related("review").order_by("-number")
    last = history.first()
    accepting = practice_is_open(practice)
    allowed = content_access(request.user, practice.lesson).allowed
    can_submit = accepting and allowed and (not last or last.state == "changes")
    initial = {"request_key": uuid.uuid4(), "previous_id": last.pk if last else 0,
               "body": last.body if last and last.state == "changes" else "", "project_url": last.project_url if last and last.state == "changes" else ""}
    form = DeliveryForm(request.POST if request.method == "POST" else None, request.FILES if request.method == "POST" else None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            submit_delivery(request.user, practice.pk, **form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, "Entrega enviada al educador. Te avisaremos aquí cuando la revise.")
            return redirect("student-practice", pk=practice.pk)
    return render(request, "learning/practice.html", {"practice": practice, "last": last, "history": history, "form": form, "can_submit": can_submit, "accepting": accepting, "allowed": allowed, "active": "workspace"})


@creator_required
@require_GET
def inbox(request):
    deliveries = PracticeDelivery.objects.filter(practice__lesson__chapter__version__course__creator=request.user).select_related("enrollment__student", "practice__lesson__chapter__version__course", "review")
    pending_count = deliveries.filter(review__isnull=True).count()
    state = request.GET.get("estado", "pending")
    if state == "pending":
        deliveries = deliveries.filter(review__isnull=True)
    elif state in ("changes", "accepted"):
        deliveries = deliveries.filter(review__outcome=state)
    else:
        state = "all"
    courses = Course.objects.filter(creator=request.user, versions__chapters__lessons__practice__isnull=False).distinct().order_by("title")
    course_id = request.GET.get("curso", "")
    if course_id.isdecimal():
        deliveries = deliveries.filter(practice__lesson__chapter__version__course_id=course_id)
    else:
        course_id = ""
    practices = VersionPractice.objects.filter(lesson__chapter__version__course__creator=request.user, lesson__chapter__version__published_at__isnull=False).select_related("lesson__chapter__version", "intake")
    if course_id:
        practices = practices.filter(lesson__chapter__version__course_id=course_id)
    return render(request, "learning/practice_inbox.html", {"deliveries": Paginator(deliveries.order_by("submitted_at", "pk"), 20).get_page(request.GET.get("pagina")), "pending_count": pending_count, "state": state, "course_id": course_id, "courses": courses, "intakes": Paginator(practices.order_by("-lesson__chapter__version_id", "pk"), 10).get_page(request.GET.get("recepcion_pagina")), "active": "creator-questions"})


@creator_required
@never_cache
@require_http_methods(["GET", "POST"])
def delivery_review(request, pk):
    delivery = get_object_or_404(PracticeDelivery.objects.select_related("enrollment__student", "practice__lesson__content", "practice__lesson__chapter__version__course", "review"), pk=pk, practice__lesson__chapter__version__course__creator=request.user)
    practice = delivery.practice
    history = practice.deliveries.filter(enrollment=delivery.enrollment).select_related("review").order_by("-number")
    review = getattr(delivery, "review", None)
    form = ReviewForm(request.POST if request.method == "POST" else None, practice=practice)
    if request.method == "POST" and form.is_valid():
        try:
            review_delivery(request.user, delivery.pk, form.cleaned_data["outcome"], form.cleaned_data["feedback"], [int(i) for i in form.cleaned_data["met_criteria"]])
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, "Revisión enviada al estudiante.")
            return redirect("creator-practice-delivery", pk=delivery.pk)
    return render(request, "learning/practice_review.html", {"delivery": delivery, "practice": practice, "history": history, "review": review, "form": form, "active": "creator-questions"})


@creator_required
@require_POST
def intake(request, pk):
    get_object_or_404(VersionPractice, pk=pk, lesson__chapter__version__course__creator=request.user)
    try:
        revision = int(request.POST.get("revision", ""))
        if request.POST.get("action") not in ("pause", "open"):
            raise ValueError
        set_intake(request.user, pk, request.POST["action"] == "open", revision)
    except (ValidationError, ValueError) as exc:
        messages.error(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Recarga antes de cambiar la recepción.")
    else:
        messages.success(request, "Recepción actualizada. Las entregas recibidas siguen disponibles para revisión.")
    return redirect("creator-practices")


@account_required
@never_cache
@require_GET
def attachment(request, pk):
    delivery = get_object_or_404(PracticeDelivery.objects.select_related("enrollment", "practice__lesson__chapter__version__course"), pk=pk)
    if request.user.account_type == "student":
        if delivery.enrollment.student_id != request.user.pk:
            raise PermissionDenied
    else:
        educator_practice(request.user, delivery.practice)
    if not delivery.attachment:
        raise Http404
    try:
        file = delivery.attachment.open("rb")
    except (OSError, ValueError):
        raise Http404("El archivo no está disponible.")
    response = FileResponse(file, as_attachment=True, filename=delivery.attachment_name, content_type="application/octet-stream")
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Security-Policy"] = "sandbox; default-src 'none'"
    response["Cache-Control"] = "private, no-store"
    return response

