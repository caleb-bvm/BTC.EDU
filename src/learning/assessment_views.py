from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from commerce.views import student_required
from content.models import Lesson
from creators.services import require_creator
from creators.views import creator_required, protect_legacy

from .assessment_forms import AttemptForm, QuestionFormSet, QuizForm, question_initial
from .assessment_services import (
    authorized_enrollment,
    grant_attempt,
    quiz_status,
    save_attempt,
    start_attempt,
)
from .models import Enrollment, ExtraQuizAttempt, QuizAttempt, QuizDraft, VersionQuiz


@creator_required
@require_http_methods(["GET", "POST"])
def quiz_edit(request, lesson_pk):
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=lesson_pk, chapter__course__creator=request.user)
    protect_legacy(lesson.chapter.course)
    draft = QuizDraft.objects.filter(lesson=lesson).first() or QuizDraft(lesson=lesson, title=f"Evaluación: {lesson.title}"[:200])
    form = QuizForm(request.POST if request.method == "POST" else None, instance=draft, initial={"revision": draft.revision})
    questions = QuestionFormSet(request.POST if request.method == "POST" else None, initial=[question_initial(question) for question in draft.questions], prefix="questions")
    if request.method == "POST":
        form_valid, questions_valid = form.is_valid(), questions.is_valid()
        if form_valid and questions_valid:
            try:
                with transaction.atomic():
                    # Share the publication writer lock: the snapshot cannot read half an edit.
                    from content.models import Course
                    Course.objects.filter(pk=lesson.chapter.course_id).update(updated_at=F("updated_at"))
                    locked_lesson = Lesson.objects.select_related("chapter__course").get(pk=lesson.pk)
                    require_creator(request.user)
                    if locked_lesson.chapter.course.creator_id != request.user.pk:
                        from django.core.exceptions import PermissionDenied
                        raise PermissionDenied
                    current = QuizDraft.objects.filter(lesson=lesson).first()
                    if (current.revision if current else 0) != form.cleaned_data["revision"]:
                        raise ValidationError("Hay un borrador más reciente. Recarga antes de guardar para conservarlo.")
                    draft = form.save(commit=False)
                    draft.questions = [item.cleaned_data["question"] for item in questions if item.cleaned_data and not item.cleaned_data.get("DELETE") and "question" in item.cleaned_data]
                    draft.revision = (current.revision if current else 0) + 1
                    draft.full_clean()
                    draft.save()
                    from django.utils import timezone
                    Course.objects.filter(pk=lesson.chapter.course_id).update(updated_at=timezone.now())
            except ValidationError as exc:
                form.add_error(None, " ".join(exc.messages))
            else:
                messages.success(request, "Evaluación guardada en el borrador. Envía el curso a revisión para publicarla.")
                return redirect("creator-quiz", lesson_pk=lesson.pk)
    from creators.presentation import course_sections
    return render(request, "learning/quiz_editor.html", {"form": form, "questions": questions, "lesson": lesson, "course_sections": course_sections(lesson.chapter.course, "evaluaciones"), "active": "creator-content"})


def student_quiz(request, pk):
    quiz = get_object_or_404(VersionQuiz.objects.select_related("lesson__content", "lesson__chapter__version__course"), pk=pk)
    enrollment = get_object_or_404(Enrollment, student=request.user, version=quiz.lesson.chapter.version)
    authorized_enrollment(request.user, enrollment.pk, quiz)
    return quiz, enrollment


@student_required
@require_GET
def quiz_detail(request, pk):
    quiz, enrollment = student_quiz(request, pk)
    return render(request, "learning/quiz.html", {"quiz": quiz, "enrollment": enrollment, "lesson_completed": enrollment.completed_lessons.filter(lesson=quiz.lesson).exists(), **quiz_status(enrollment, quiz), "active": "workspace"})


@student_required
@require_POST
def quiz_start(request, pk):
    quiz, enrollment = student_quiz(request, pk)
    try:
        attempt = start_attempt(request.user, enrollment.pk, quiz.pk)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("quiz-detail", pk=pk)
    return redirect("quiz-attempt", pk=attempt.pk)


@student_required
@require_http_methods(["GET", "POST"])
def attempt_detail(request, pk):
    attempt = get_object_or_404(QuizAttempt.objects.select_related("quiz__lesson__content", "quiz__lesson__chapter__version__course", "enrollment"), pk=pk, enrollment__student=request.user)
    quiz = attempt.quiz
    authorized_enrollment(request.user, attempt.enrollment_id, quiz)
    form = AttemptForm(request.POST if request.method == "POST" else None, quiz=quiz, answers=attempt.answers, revision=attempt.revision)
    response_status = 200
    if request.method == "POST":
        if request.POST.get("action") not in ("save", "submit"):
            form.add_error(None, "Elige guardar respuestas o entregar el intento.")
            response_status = 400
        elif form.is_valid():
            try:
                save_attempt(request.user, attempt.pk, form.answers(), form.cleaned_data["revision"], submit=request.POST["action"] == "submit")
            except ValidationError as exc:
                form.add_error(None, " ".join(exc.messages))
                response_status = 409
            else:
                messages.success(request, "Intento entregado." if request.POST["action"] == "submit" else "Respuestas guardadas. Puedes continuar después.")
                return redirect("quiz-attempt", pk=pk)
    solutions_visible = bool(attempt.submitted_at and (quiz.feedback == "submitted" or attempt.passed))
    review = []
    if attempt.submitted_at:
        for index, question in enumerate(quiz.questions):
            selected = attempt.answers.get(str(index), [])
            row = {"prompt": question["prompt"], "selected": [question["options"][option] for option in selected]}
            if solutions_visible:
                row.update(correct=set(selected) == set(question["correct"]), solutions=[question["options"][option] for option in question["correct"]], explanation=question["explanation"])
            review.append(row)
    # Only sanitized form fields/review rows reach the student template; no answer key.
    return render(request, "learning/attempt.html", {"form": form, "attempt": attempt, "review": review, "solutions_visible": solutions_visible, "lesson_completed": attempt.enrollment.completed_lessons.filter(lesson=quiz.lesson).exists(), **quiz_status(attempt.enrollment, quiz), "active": "workspace"}, status=response_status)


@creator_required
@require_GET
def quiz_results(request, course_pk=None):
    from content.models import Course
    courses = Course.objects.filter(creator=request.user).order_by("title", "pk")
    course = get_object_or_404(courses, pk=course_pk) if course_pk else None
    selected_course = request.GET.get("curso", "")
    if selected_course.isdigit() and courses.filter(pk=selected_course).exists() and (not course or int(selected_course) != course.pk):
        from urllib.parse import urlencode
        filters = {name: request.GET[name] for name in ("estado", "version") if request.GET.get(name)}
        return redirect(reverse("creator-quiz-results", args=[selected_course]) + ("?" + urlencode(filters) if filters else ""))
    attempts = QuizAttempt.objects.filter(quiz__lesson__chapter__version__course__creator=request.user).select_related("quiz__lesson__chapter__version", "enrollment__student", "enrollment__version")
    if course:
        attempts = attempts.filter(quiz__lesson__chapter__version__course=course)
    state = request.GET.get("estado", "")
    if state == "active":
        attempts = attempts.filter(submitted_at__isnull=True)
    elif state in ("passed", "failed"):
        attempts = attempts.filter(submitted_at__isnull=False, passed=state == "passed")
    else:
        state = ""
    versions = course.versions.filter(published_at__isnull=False).order_by("-number") if course else []
    version = request.GET.get("version", "")
    if course and version.isdigit() and versions.filter(number=version).exists():
        attempts = attempts.filter(quiz__lesson__chapter__version__number=version)
    else:
        version = ""
    from django.db.models import OuterRef, Subquery
    from django.db.models.functions import Coalesce
    last_activity = QuizAttempt.objects.filter(enrollment_id=OuterRef("enrollment_id")).annotate(activity=Coalesce("submitted_at", "started_at")).order_by("-activity", "-pk").values("activity")[:1]
    attempts = attempts.annotate(student_activity=Subquery(last_activity)).order_by("-student_activity", "enrollment_id", "quiz_id", "-started_at", "-pk")
    from django.core.paginator import Paginator
    page = Paginator(attempts, 30).get_page(request.GET.get("pagina"))
    statuses = {}
    for attempt in page:
        key = (attempt.enrollment_id, attempt.quiz_id)
        if key not in statuses:
            statuses[key] = quiz_status(attempt.enrollment, attempt.quiz)
        attempt.quiz_status = statuses[key]
    grants = ExtraQuizAttempt.objects.filter(quiz__lesson__chapter__version__course__creator=request.user)
    if course:
        grants = grants.filter(quiz__lesson__chapter__version__course=course)
    grants = grants.select_related("enrollment__student", "quiz", "granted_by").order_by("-created_at")[:30]
    return render(request, "learning/quiz_results.html", {"course": course, "courses": courses, "result_state": state, "result_version": version, "versions": versions, "attempts": page, "grants": grants, "active": "students"})


@creator_required
@require_POST
def quiz_grant(request, pk):
    from django.http import JsonResponse

    attempt = get_object_or_404(QuizAttempt.objects.select_related("quiz__lesson__chapter__version__course"), pk=pk, quiz__lesson__chapter__version__course__creator=request.user)
    ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    destination = reverse("creator-quiz-results", args=[attempt.quiz.lesson.chapter.version.course_id])
    try:
        allowance = int(request.POST.get("allowance", ""))
        grant_attempt(request.user, attempt.enrollment_id, attempt.quiz_id, allowance, request.POST.get("reason", ""))
    except (ValueError, ValidationError) as exc:
        errors = exc.messages if isinstance(exc, ValidationError) else ["La solicitud no es válida."]
        if ajax:
            return JsonResponse({"errors": errors}, status=400)
        messages.error(request, " ".join(errors))
    else:
        messages.success(request, "Otro intento autorizado. Se conservan las notas y la espera entre intentos.")
        if ajax:
            return JsonResponse({"redirect": destination})
    return redirect(destination)
