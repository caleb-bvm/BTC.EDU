from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from content.models import CourseVersion
from creators.services import require_creator

from .community import access, moderate, moderator, post_message, report_message
from .essential_forms import MessageForm
from .models import (
    CommunityDecision,
    CommunityPost,
    CommunityReport,
    CommunitySuspension,
)


def layout(user):
    return "creators/base.html" if user.account_type == "creator" else "academy.html"


@login_required
@never_cache
@require_GET
def spaces(request):
    user = request.user
    versions = CourseVersion.objects.filter(sealed=True, published_at__isnull=False).select_related("course")
    if user.is_staff and user.has_perm("learning.moderate_community"):
        pass
    elif user.account_type == "creator":
        require_creator(user)
        versions = versions.filter(course__creator=user)
    elif user.account_type == "student":
        versions = versions.filter(enrollment__student=user)
    else:
        raise PermissionDenied
    return render(request, "learning/community_spaces.html", {"base_template": layout(user), "versions": Paginator(versions.order_by("-published_at", "-pk"), 20).get_page(request.GET.get("pagina"))})


def context(request, version):
    can_moderate = moderator(request.user, version)
    suspended = CommunitySuspension.objects.filter(version=version, student=request.user, active=True).exists()
    return {"base_template": layout(request.user), "version": version, "can_moderate": can_moderate, "suspended": suspended, "can_write": not suspended and request.user.account_type in ("student", "creator")}


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def space(request, version_pk):
    version = get_object_or_404(CourseVersion.objects.select_related("course"), pk=version_pk)
    access(request.user, version)
    form = MessageForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            post = post_message(request.user, version, form.cleaned_data["body"], form.cleaned_data["request_key"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("community-thread", pk=post.pk)
    data = context(request, version)
    posts = CommunityPost.objects.filter(version=version, parent__isnull=True).select_related("author")
    if not data["can_moderate"]:
        posts = posts.filter(hidden=False)
    data.update(form=form, posts=Paginator(posts.order_by("-created_at", "-pk"), 20).get_page(request.GET.get("pagina")))
    return render(request, "learning/community_space.html", data)


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def thread(request, pk):
    post = get_object_or_404(CommunityPost.objects.select_related("version__course", "author"), pk=pk, parent__isnull=True)
    access(request.user, post.version)
    data = context(request, post.version)
    if post.hidden and not data["can_moderate"]:
        # No content or replies from a hidden thread are exposed.
        from django.http import Http404
        raise Http404
    form = MessageForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            post_message(request.user, post.version, form.cleaned_data["body"], form.cleaned_data["request_key"], post.pk)
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            return redirect("community-thread", pk=pk)
    replies = post.replies.select_related("author")
    if not data["can_moderate"]:
        replies = replies.filter(hidden=False)
    data.update(post=post, replies=Paginator(replies, 20).get_page(request.GET.get("pagina")), form=form)
    return render(request, "learning/community_thread.html", data)


@login_required
@never_cache
@require_POST
def report(request, pk):
    post = get_object_or_404(CommunityPost.objects.select_related("version__course"), pk=pk)
    access(request.user, post.version)
    try:
        report_message(request.user, pk, request.POST.get("reason", ""))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Reporte recibido. El equipo de moderación lo revisará.")
    return redirect("community-thread", pk=post.parent_id or post.pk)


@login_required
@never_cache
@require_POST
def decision(request, version_pk):
    version = get_object_or_404(CourseVersion.objects.select_related("course"), pk=version_pk)
    try:
        post_id = int(request.POST["post"]) if request.POST.get("post") else None
        student_id = int(request.POST["student"]) if request.POST.get("student") else None
        moderate(request.user, version, request.POST.get("action"), request.POST.get("reason", ""), post_id, student_id)
    except (ValueError, ValidationError) as exc:
        messages.error(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Selecciona un destino válido.")
    else:
        messages.success(request, "Decisión guardada.")
    return redirect("community-moderation", version_pk=version.pk)


@login_required
@never_cache
@require_GET
def moderation(request, version_pk):
    version = get_object_or_404(CourseVersion.objects.select_related("course"), pk=version_pk)
    access(request.user, version)
    if not moderator(request.user, version):
        raise PermissionDenied
    reports = CommunityReport.objects.filter(post__version=version, resolved=False).select_related("post__author", "reporter")
    suspensions = CommunitySuspension.objects.filter(version=version, active=True).select_related("student")
    decisions = CommunityDecision.objects.filter(version=version).select_related("actor", "student").order_by("-created_at", "-pk")
    return render(request, "learning/community_moderation.html", {**context(request, version), "reports": Paginator(reports.order_by("created_at", "pk"), 20).get_page(request.GET.get("pagina")), "suspensions": Paginator(suspensions.order_by("pk"), 20).get_page(request.GET.get("suspensiones")), "decisions": Paginator(decisions, 20).get_page(request.GET.get("historial"))})
