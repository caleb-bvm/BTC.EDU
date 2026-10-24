from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
    require_safe,
)

from content.models import (
    Chapter,
    Course,
    Lesson,
    LessonResource,
    Material,
    PublicationStatus,
    Video,
)
from media.delivery import file_response
from media.models import Asset

from .forms import (
    ChapterForm,
    CourseForm,
    DecisionForm,
    LessonForm,
    MaterialForm,
    ProfileForm,
    ResourceForm,
    UploadForm,
)
from .models import CreatorProfile, Submission
from .presentation import (
    content_cards,
    course_requirements,
    course_sections,
    form_groups,
    resource_requirements,
)
from .services import decide, require_creator, require_reviewer, submit


def creator_required(view):
    @login_required(login_url="creator-login")
    @never_cache
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.user.account_type != "creator":
            return redirect_to_login(request.get_full_path(), reverse("creator-login"))
        profile = getattr(request.user, "creator_profile", None)
        if (not profile or profile.status != "approved") and request.method in ("GET", "HEAD"):
            return redirect("creator-application")
        require_creator(request.user)
        return view(request, *args, **kwargs)
    return wrapped


def resource_model(kind):
    model = {"videos": Video, "materiales": Material}.get(kind)
    if model is None:
        raise Http404
    return model


def saved_redirect(request, destination, **kwargs):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"redirect": reverse(destination, kwargs=kwargs)} if not destination.startswith("/") else {"redirect": destination})
    return redirect(destination, **kwargs)


def editor_return(request):
    back = request.POST.get("volver") or request.GET.get("volver", "")
    if back.startswith(reverse("creator-dashboard")) and not back.startswith("//") and url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return back
    return ""


@login_required(login_url="creator-login")
@never_cache
@require_http_methods(["GET", "POST"])
def application(request):
    if request.user.account_type != "creator":
        return redirect_to_login(request.get_full_path(), reverse("creator-login"))
    profile = CreatorProfile.objects.filter(user=request.user).first()
    from accounts.account_views import account_context

    from .application_service import save_application
    context = account_context(request, True, "profile", profile=profile, history=profile.history.all()[:20] if profile else [])
    if profile and profile.status == CreatorProfile.Status.SUSPENDED:
        return render(request, "creators/application.html", context, status=403 if request.method == "POST" else 200)
    form = ProfileForm(request.POST if request.method == "POST" else None, instance=profile)
    if request.method == "POST" and form.is_valid():
        try:
            profile = save_application(request.user, form.cleaned_data, form.cleaned_data.get("application_revision"))
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Perfil guardado." if profile.status == CreatorProfile.Status.APPROVED else "Solicitud enviada. Te avisaremos cuando tenga una decisión.")
            return saved_redirect(request, "creator-application")
    return render(request, "creators/application.html", {**context, "form": form})


@creator_required
@require_GET
def dashboard(request):
    from learning.models import CommunityReport, LessonQuestion, PracticeDelivery
    from learning.support import awaiting_creator_questions
    submissions = Submission.objects.filter(creator=request.user).select_related("course_version", "resource_version")
    questions = awaiting_creator_questions(LessonQuestion.objects.filter(enrollment__version__course__creator=request.user))
    reports = CommunityReport.objects.filter(post__version__course__creator=request.user, resolved=False)
    cards = content_cards(request.user)
    changes_count = sum(card["state"] == "changes" for card in cards)
    next_draft = next((card for card in cards if card["state"] in ("draft", "changes")), None)
    return render(request, "creators/dashboard.html", {"cards": cards[:5], "next_draft": next_draft, "submissions": submissions.order_by("-created_at", "-pk")[:8], "pending_count": submissions.filter(status="pending").count(), "changes_count": changes_count, "practice_pending_count": PracticeDelivery.objects.filter(practice__lesson__chapter__version__course__creator=request.user, review__isnull=True).count(), "unanswered_count": questions.count(), "report_count": reports.count(), "has_publication": any(card["snapshot"] for card in cards), "active": "studio"})


@creator_required
@require_GET
def content_list(request):
    cards = content_cards(request.user)
    kind = request.GET.get("tipo", "")
    state = request.GET.get("estado", "")
    query = request.GET.get("q", "").strip()[:200]
    if kind not in ("course", "tutorial", "video", "material"):
        kind = ""
    if state not in ("draft", "published", "review", "changes"):
        state = ""
    if kind:
        cards = [card for card in cards if card["kind"] == kind]
    if state:
        cards = [card for card in cards if card["state"] == state]
    if query:
        cards = [card for card in cards if query.casefold() in card["item"].title.casefold()]
    from django.core.paginator import Paginator
    return render(request, "creators/content.html", {"cards": Paginator(cards, 12).get_page(request.GET.get("pagina")), "content_type": kind, "content_state": state, "query": query, "active": "creator-content"})


def save_form(request, form, title, back, extra=None):
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                item = form.save()
                if isinstance(item, Chapter):
                    Course.objects.filter(pk=item.course_id).update(updated_at=timezone.now())
        except ValidationError as exc:
            form.add_error(None, exc)
        except IntegrityError:
            form.add_error(None, "El orden cambió mientras editabas. Elige un número libre y reintenta.")
        else:
            messages.success(request, "Cambios guardados en el borrador. La publicación vigente se conserva.")
            return saved_redirect(request, back)
    return render(request, "creators/form.html", {"form": form, "form_groups": form_groups(form), "page_title": title, "back": back, "active": "creator-content", **(extra or {})})


@creator_required
@require_http_methods(["GET", "POST"])
def course_edit(request, pk=None):
    course = get_object_or_404(Course, pk=pk, creator=request.user) if pk else Course(creator=request.user)
    protect_legacy(course)
    initial = {"kind": "tutorial"} if not pk and request.GET.get("tipo") == "tutorial" else {}
    form = CourseForm(request.POST if request.method == "POST" else None, instance=course, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Información guardada. Continúa con el temario.")
        return saved_redirect(request, reverse("creator-course", args=[course.pk]) + "?seccion=temario")
    section = request.GET.get("seccion", "informacion")
    if section not in ("informacion", "temario", "evaluaciones", "publicacion", "precio"):
        section = "informacion"
    if request.method == "POST":
        section = "informacion"
    if pk:
        chapters = list(course.chapters.prefetch_related("lessons__quiz_draft", "lessons__practice_draft", "lessons__attachments__resource"))
        course._prefetched_objects_cache = {"chapters": chapters}
        requirements = course_requirements(course)
    else:
        chapters, requirements = [], []
    submissions = Submission.objects.filter(course=course).select_related("course_version").order_by("-created_at", "-pk") if pk else Submission.objects.none()
    latest = submissions.first()
    return render(request, "creators/course.html", {"form": form, "form_groups": form_groups(form), "course": course, "chapters": chapters, "section": section, "course_sections": course_sections(course, section), "requirements": requirements, "ready_to_send": bool(requirements) and all(check["ready"] for check in requirements), "pending_submission": next((submission for submission in submissions if submission.status == "pending"), None), "latest_submission": latest, "submissions": submissions, "active": "creator-content"})


@creator_required
@require_http_methods(["GET", "POST"])
def chapter_edit(request, course_pk, pk=None):
    course = get_object_or_404(Course, pk=course_pk, creator=request.user)
    protect_legacy(course)
    chapter = get_object_or_404(Chapter, pk=pk, course=course) if pk else Chapter(course=course, status=PublicationStatus.PUBLISHED, position=(course.chapters.order_by("-position").values_list("position", flat=True).first() or 0) + 1)
    return save_form(request, ChapterForm(request.POST if request.method == "POST" else None, instance=chapter), "Editar capítulo" if pk else "Nuevo capítulo", reverse("creator-course", args=[course.pk]) + "?seccion=temario", {"course": course, "course_sections": course_sections(course, "temario")})


@creator_required
@require_http_methods(["GET", "POST"])
def lesson_edit(request, chapter_pk, pk=None):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, course__creator=request.user)
    protect_legacy(chapter.course)
    lesson = get_object_or_404(Lesson, pk=pk, chapter=chapter) if pk else Lesson(chapter=chapter, status=PublicationStatus.PUBLISHED, position=(chapter.lessons.order_by("-position").values_list("position", flat=True).first() or 0) + 1)
    form = LessonForm(request.POST if request.method == "POST" else None, instance=lesson, actor=request.user)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                lesson = form.save()
                lesson.attachments.all().delete()
                for position, revision in enumerate(form.cleaned_data["resources"], 1):
                    LessonResource.objects.create(lesson=lesson, resource=revision, position=position)
                Course.objects.filter(pk=chapter.course_id).update(updated_at=timezone.now())
        except IntegrityError:
            form.add_error(None, "El orden cambió mientras editabas. Elige un número libre y reintenta.")
        else:
            messages.success(request, "Lección guardada en el borrador.")
            return saved_redirect(request, reverse("creator-course", args=[chapter.course_id]) + "?seccion=temario")
    return render(request, "creators/form.html", {"form": form, "form_groups": form_groups(form), "lesson": lesson, "course": chapter.course, "course_sections": course_sections(chapter.course, "temario"), "page_title": "Editar lección" if pk else "Nueva lección", "back": reverse("creator-course", args=[chapter.course_id]) + "?seccion=temario", "active": "creator-content"})


@creator_required
@require_http_methods(["GET", "POST"])
def resource_edit(request, kind, pk=None):
    model = resource_model(kind)
    item = get_object_or_404(model, pk=pk, creator=request.user) if pk else model(creator=request.user)
    if item.status == PublicationStatus.PUBLISHED and not item.revision_id:
        raise PermissionDenied("El administrador debe publicar una revisión del recurso anterior antes de habilitar su edición.")
    form_type = ResourceForm if model is Video else MaterialForm
    form = form_type(request.POST if request.method == "POST" else None, request.FILES if request.method == "POST" else None, instance=item, actor=request.user)
    back = editor_return(request)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, "Recurso guardado. Puedes enviarlo a revisión.")
        from urllib.parse import urlencode
        destination = reverse("creator-resource", args=[kind, item.pk]) + ("?" + urlencode({"volver": back}) if back else "")
        return saved_redirect(request, destination)
    submissions = Submission.objects.filter(**{model._meta.model_name: item}).select_related("resource_version").order_by("-created_at", "-pk") if pk else Submission.objects.none()
    requirements = resource_requirements(model.objects.get(pk=item.pk)) if item.pk else []
    return render(request, "creators/resource.html", {"form": form, "form_groups": form_groups(form), "back": back, "item": item, "kind": kind, "submissions": submissions, "requirements": requirements, "ready_to_send": bool(requirements) and all(check["ready"] for check in requirements), "pending_submission": next((submission for submission in submissions if submission.status == "pending"), None), "active": "creator-content"})


@creator_required
@require_http_methods(["GET", "POST"])
def files(request):
    back = editor_return(request)
    form = UploadForm(request.POST if request.method == "POST" else None, request.FILES if request.method == "POST" else None, instance=Asset(creator=request.user))
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Archivo validado y guardado en tu biblioteca privada.")
            return saved_redirect(request, back or "creator-files")
    return render(request, "creators/files.html", {"form": form, "back": back, "assets": Asset.objects.filter(creator=request.user).order_by("-pk"), "active": "creator-content"})


@creator_required
@require_safe
def own_file(request, pk):
    return file_response(request, get_object_or_404(Asset, pk=pk, creator=request.user))


@creator_required
@require_POST
def send(request, kind, pk):
    model = Course if kind == "cursos" else resource_model(kind)
    item = get_object_or_404(model, pk=pk, creator=request.user)
    try:
        submission = submit(item, request.user)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("creator-course", pk=pk) if model is Course else redirect("creator-resource", kind=kind, pk=pk)
    messages.success(request, "Versión enviada a revisión. Puedes seguir editando un nuevo borrador.")
    return redirect("creator-review", pk=submission.pk)


def review_access(request, pk):
    submission = get_object_or_404(Submission.objects.select_related("creator", "course__creator", "video", "material", "course_version", "resource_version__asset", "resource_version__subtitles"), pk=pk)
    if submission.creator_id == request.user.pk:
        require_creator(request.user)
        return submission, False
    require_reviewer(request.user)
    item = submission.course or submission.video or submission.material
    if not request.user.has_perm(f"content.change_{item._meta.model_name}"):
        raise PermissionDenied
    return submission, True


@login_required(login_url="creator-login")
@never_cache
@require_http_methods(["GET", "POST"])
def review(request, pk):
    submission, reviewer = review_access(request, pk)
    form = DecisionForm(request.POST if request.method == "POST" else None) if reviewer else None
    if request.method == "POST":
        if not reviewer:
            raise PermissionDenied
        if form.is_valid():
            try:
                decide(submission, request.user, form.cleaned_data["decision"] == "approve", form.cleaned_data["feedback"])
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, "Decisión registrada.")
                return redirect("creator-review", pk=pk)
    chapters = submission.course_version.chapters.prefetch_related("lessons__content", "lessons__attachments__resource__asset", "lessons__attachments__resource__subtitles") if submission.course_id else []
    return render(request, "creators/review.html", {"submission": submission, "snapshot": submission.snapshot, "chapters": chapters, "reviewer": reviewer, "form": form, "active": "studio"})


@creator_required
@require_POST
def withdraw(request, pk):
    submission = get_object_or_404(Submission, pk=pk, creator=request.user)
    changed = Submission.objects.filter(pk=submission.pk, status=Submission.Status.PENDING).update(status=Submission.Status.WITHDRAWN)
    messages.info(request, "Envío retirado. Puedes preparar y enviar otra versión." if changed else "Este envío ya fue resuelto.")
    return redirect("creator-review", pk=pk)


@login_required(login_url="creator-login")
@never_cache
@require_safe
def review_file(request, pk, asset_pk):
    submission, _ = review_access(request, pk)
    if submission.course_id:
        resources = [attachment.resource for chapter in submission.course_version.chapters.all() for lesson in chapter.lessons.all() for attachment in lesson.attachments.select_related("resource")]
    else:
        resources = [submission.resource_version]
    permitted = {asset for resource in resources for asset in (resource.asset_id, resource.subtitles_id) if asset}
    if asset_pk not in permitted:
        raise Http404
    return file_response(request, get_object_or_404(Asset, pk=asset_pk, creator=submission.creator))


@never_cache
@require_GET
def public_profile(request, pk):
    profile = get_object_or_404(CreatorProfile.objects.select_related("user"), user_id=pk, status=CreatorProfile.Status.APPROVED, user__is_active=True, user__account_type="creator")
    if not profile.user.has_public_profile:
        raise Http404
    from urllib.parse import urlencode

    from content.catalog import catalog_context
    context = catalog_context(request.GET, creator=profile.user)
    for card in context["all_cards"]:
        card["url"] += "?" + urlencode({"volver": request.get_full_path()})
    return render(request, "creators/public_profile.html", {**context, "profile": profile, "active": "courses", "base_template": "creators/base.html" if request.user.is_authenticated and request.user.account_type == "creator" else "academy.html"})


def protect_legacy(course):
    if course.status == PublicationStatus.PUBLISHED and not course.current_version_id:
        raise PermissionDenied("El administrador debe publicar una versión del curso anterior antes de habilitar su edición.")


@creator_required
@require_GET
def course_preview(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)
    from content.reading import reading_sections
    chapters = list(course.chapters.filter(status="published").prefetch_related("lessons__attachments__resource__asset", "lessons__attachments__resource__subtitles", "lessons__quiz_draft", "lessons__practice_draft"))
    view_mode = request.GET.get("acceso", "incluido")
    if view_mode not in ("incluido", "sin-compra"):
        view_mode = "incluido"
    for chapter in chapters:
        chapter.preview_lessons = [lesson for lesson in chapter.lessons.all() if lesson.status == "published"]
        for lesson in chapter.preview_lessons:
            lesson.reading_sections = reading_sections(lesson.body)
            lesson.preview_allowed = view_mode == "incluido" or lesson.access_type == "free"
    return render(request, "creators/preview.html", {"item": course, "chapters": chapters, "view_mode": view_mode, "course_sections": course_sections(course), "back": reverse("creator-course", args=[pk]) + "?seccion=publicacion", "active": "creator-content"})


@creator_required
@require_GET
def resource_preview(request, kind, pk):
    item = get_object_or_404(resource_model(kind), pk=pk, creator=request.user)
    return render(request, "creators/preview.html", {"item": item, "kind": kind, "back": reverse("creator-resource", args=[kind, pk]), "active": "creator-content"})


@creator_required
@require_http_methods(["GET", "POST"])
def quiz_preview(request, lesson_pk):
    from learning.assessment_forms import AttemptForm
    from learning.models import QuizDraft
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=lesson_pk, chapter__course__creator=request.user)
    quiz = get_object_or_404(QuizDraft, lesson=lesson, enabled=True)
    form = AttemptForm(request.POST if request.method == "POST" else None, quiz=quiz, answers={}, revision=0)
    review, score = [], None
    if request.method == "POST" and form.is_valid():
        answers = form.answers()
        correct_count = 0
        for index, question in enumerate(quiz.questions):
            selected = answers.get(str(index), [])
            correct = set(selected) == set(question["correct"])
            correct_count += correct
            review.append({"prompt": question["prompt"], "correct": correct, "selected": [question["options"][option] for option in selected], "solutions": [question["options"][option] for option in question["correct"]], "explanation": question["explanation"]})
        score = round(correct_count * 100 / len(quiz.questions), 2) if quiz.questions else 0
    passed = score is not None and score >= quiz.pass_mark
    solutions_visible = score is not None and (quiz.feedback == "submitted" or passed)
    if not solutions_visible:
        for row in review:
            for name in ("solutions", "explanation", "correct"):
                row.pop(name, None)
    return render(request, "creators/quiz_preview.html", {"lesson": lesson, "quiz": quiz, "form": form, "review": review, "score": score, "passed": passed, "solutions_visible": solutions_visible, "active": "creator-content"})


@creator_required
@require_POST
def reorder(request, kind, pk):
    model = {"capitulos": Chapter, "lecciones": Lesson}.get(kind)
    if model is None:
        raise Http404
    relation = "course" if model is Chapter else "chapter__course"
    item = get_object_or_404(model.objects.select_related(relation), pk=pk, **{relation + "__creator": request.user})
    course = item.course if model is Chapter else item.chapter.course
    protect_legacy(course)
    if request.POST.get("direction") not in ("up", "down"):
        return JsonResponse({"error": "Elige subir o bajar."}, status=400)
    with transaction.atomic():
        from django.db.models import Max
        Course.objects.filter(pk=course.pk).update(updated_at=timezone.now())
        request.user.refresh_from_db()
        require_creator(request.user)
        item = get_object_or_404(model.objects.select_related(relation), pk=pk, **{relation + "__creator": request.user})
        group = {"course_id": item.course_id} if model is Chapter else {"chapter_id": item.chapter_id}
        siblings = model.objects.filter(**group)
        if request.POST["direction"] == "up":
            adjacent = siblings.filter(position__lt=item.position).order_by("-position").first()
        else:
            adjacent = siblings.filter(position__gt=item.position).order_by("position").first()
        if adjacent:
            temporary = (siblings.aggregate(value=Max("position"))["value"] or 0) + 1
            original = item.position
            model.objects.filter(pk=item.pk).update(position=temporary)
            model.objects.filter(pk=adjacent.pk).update(position=original)
            model.objects.filter(pk=item.pk).update(position=adjacent.position)
            messages.success(request, "Orden del temario actualizado.")
    return redirect(reverse("creator-course", args=[course.pk]) + "?seccion=temario")
