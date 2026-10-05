from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
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
from .services import decide, require_creator, require_reviewer, submit


def creator_required(view):
    @login_required(login_url="creator-login")
    @never_cache
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.user.account_type != "creator":
            return redirect_to_login(request.get_full_path(), reverse("creator-login"))
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


@login_required(login_url="creator-login")
@never_cache
@require_http_methods(["GET", "POST"])
def application(request):
    if request.user.account_type != "creator":
        return redirect_to_login(request.get_full_path(), reverse("creator-login"))
    profile = CreatorProfile.objects.filter(user=request.user).first()
    if profile and profile.status == CreatorProfile.Status.SUSPENDED:
        return render(request, "creators/application.html", {"profile": profile, "active": "studio"}, status=403)
    form = ProfileForm(request.POST if request.method == "POST" else None, instance=profile)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            # Preserve the administrative decision, including concurrent suspension.
            CreatorProfile.objects.filter(user=request.user).update(updated_at=F("updated_at"))
            current = CreatorProfile.objects.filter(user=request.user).first()
            if current and current.status == CreatorProfile.Status.SUSPENDED:
                raise PermissionDenied
            profile = form.save(commit=False)
            profile.user = request.user
            profile.status = current.status if current and current.status != CreatorProfile.Status.CHANGES else CreatorProfile.Status.PENDING
            profile.save(update_fields=("display_name", "bio", "specialty", "website", "status", "updated_at") if current else None)
        messages.success(request, "Perfil guardado." if profile.status == CreatorProfile.Status.APPROVED else "Solicitud enviada. Recibirás la decisión en esta página.")
        return saved_redirect(request, "creator-application")
    return render(request, "creators/application.html", {"profile": profile, "form": form, "active": "studio"})


@creator_required
@require_GET
def dashboard(request):
    courses = Course.objects.filter(creator=request.user).select_related("current_version")
    submissions = Submission.objects.filter(creator=request.user).select_related("course_version", "resource_version")
    return render(request, "creators/dashboard.html", {"courses": courses, "videos": Video.objects.filter(creator=request.user).select_related("revision"), "materials": Material.objects.filter(creator=request.user).select_related("revision"), "submissions": submissions[:12], "pending_count": submissions.filter(status="pending").count(), "changes_count": submissions.filter(status="changes").count(), "active": "studio"})


def save_form(request, form, title, back, extra=None):
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except ValidationError as exc:
            form.add_error(None, exc)
        except IntegrityError:
            form.add_error(None, "El orden cambió mientras editabas. Elige un número libre y reintenta.")
        else:
            messages.success(request, "Cambios guardados en el borrador. La publicación vigente se conserva.")
            return saved_redirect(request, back)
    return render(request, "creators/form.html", {"form": form, "page_title": title, "back": back, "active": "studio", **(extra or {})})


@creator_required
@require_http_methods(["GET", "POST"])
def course_edit(request, pk=None):
    course = get_object_or_404(Course, pk=pk, creator=request.user) if pk else Course(creator=request.user)
    protect_legacy(course)
    form = CourseForm(request.POST if request.method == "POST" else None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Información guardada. Continúa con el temario.")
        return saved_redirect(request, "creator-course", pk=course.pk)
    return render(request, "creators/course.html", {"form": form, "course": course, "chapters": course.chapters.prefetch_related("lessons") if pk else [], "submissions": Submission.objects.filter(course=course).select_related("course_version") if pk else [], "active": "studio"})


@creator_required
@require_http_methods(["GET", "POST"])
def chapter_edit(request, course_pk, pk=None):
    course = get_object_or_404(Course, pk=course_pk, creator=request.user)
    protect_legacy(course)
    chapter = get_object_or_404(Chapter, pk=pk, course=course) if pk else Chapter(course=course, status=PublicationStatus.PUBLISHED, position=(course.chapters.order_by("-position").values_list("position", flat=True).first() or 0) + 1)
    return save_form(request, ChapterForm(request.POST if request.method == "POST" else None, instance=chapter), "Editar capítulo" if pk else "Nuevo capítulo", reverse("creator-course", args=[course.pk]))


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
        except IntegrityError:
            form.add_error(None, "El orden cambió mientras editabas. Elige un número libre y reintenta.")
        else:
            messages.success(request, "Lección guardada en el borrador.")
            return saved_redirect(request, "creator-course", pk=chapter.course_id)
    return render(request, "creators/form.html", {"form": form, "page_title": "Editar lección" if pk else "Nueva lección", "back": reverse("creator-course", args=[chapter.course_id]), "active": "studio"})


@creator_required
@require_http_methods(["GET", "POST"])
def resource_edit(request, kind, pk=None):
    model = resource_model(kind)
    item = get_object_or_404(model, pk=pk, creator=request.user) if pk else model(creator=request.user)
    if item.status == PublicationStatus.PUBLISHED and not item.revision_id:
        raise PermissionDenied("El administrador debe publicar una revisión del recurso anterior antes de habilitar su edición.")
    form_type = ResourceForm if model is Video else MaterialForm
    form = form_type(request.POST if request.method == "POST" else None, instance=item, actor=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Recurso guardado. Puedes enviarlo a revisión.")
        return saved_redirect(request, "creator-resource", kind=kind, pk=item.pk)
    return render(request, "creators/resource.html", {"form": form, "item": item, "kind": kind, "submissions": Submission.objects.filter(**{model._meta.model_name: item}).select_related("resource_version") if pk else [], "active": "studio"})


@creator_required
@require_http_methods(["GET", "POST"])
def files(request):
    form = UploadForm(request.POST if request.method == "POST" else None, request.FILES if request.method == "POST" else None, instance=Asset(creator=request.user))
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Archivo validado y guardado en tu biblioteca privada.")
            return saved_redirect(request, "creator-files")
    return render(request, "creators/files.html", {"form": form, "assets": Asset.objects.filter(creator=request.user).order_by("-pk"), "active": "studio"})


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


@require_GET
def public_profile(request, pk):
    profile = get_object_or_404(CreatorProfile.objects.select_related("user"), user_id=pk, status=CreatorProfile.Status.APPROVED, user__is_active=True)
    courses = Course.objects.filter(creator=profile.user, status=PublicationStatus.PUBLISHED, current_version__isnull=False).select_related("current_version")
    videos = Video.objects.filter(creator=profile.user, status=PublicationStatus.PUBLISHED, revision__isnull=False).select_related("revision")
    materials = Material.objects.filter(creator=profile.user, status=PublicationStatus.PUBLISHED, revision__isnull=False).select_related("revision")
    return render(request, "creators/public_profile.html", {"profile": profile, "courses": courses, "videos": videos, "materials": materials, "active": "courses"})


def protect_legacy(course):
    if course.status == PublicationStatus.PUBLISHED and not course.current_version_id:
        raise PermissionDenied("El administrador debe publicar una versión del curso anterior antes de habilitar su edición.")


@creator_required
@require_GET
def course_preview(request, pk):
    course = get_object_or_404(Course, pk=pk, creator=request.user)
    chapters = course.chapters.prefetch_related("lessons__attachments__resource__asset", "lessons__attachments__resource__subtitles")
    return render(request, "creators/preview.html", {"item": course, "chapters": chapters, "back": reverse("creator-course", args=[pk]), "active": "studio"})


@creator_required
@require_GET
def resource_preview(request, kind, pk):
    item = get_object_or_404(resource_model(kind), pk=pk, creator=request.user)
    return render(request, "creators/preview.html", {"item": item, "kind": kind, "back": reverse("creator-resource", args=[kind, pk]), "active": "studio"})
