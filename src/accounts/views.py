from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from .destinations import student_destination
from .forms import (
    AccountLoginForm,
    AccountRegistrationForm,
    CreatorLoginForm,
    CreatorRegistrationForm,
    StudentProfileForm,
)
from .security import request_email_action
from .throttling import AccessThrottled, allow


class StudentLoginView(LoginView):
    authentication_form = AccountLoginForm
    template_name = "registration/login.html"

    def get_redirect_url(self):
        return student_destination(self.request, super().get_redirect_url())


class CreatorLoginView(LoginView):
    authentication_form = CreatorLoginForm
    template_name = "creators/login.html"

    def get_redirect_url(self):
        destination = super().get_redirect_url()
        profile = getattr(self.request.user, "creator_profile", None)
        # During form_valid request.user is already the newly authenticated user.
        if not profile or profile.status != "approved":
            return ""
        return destination if destination.startswith("/crear/") and destination not in (reverse("creator-login"), reverse("creator-signup")) else ""

    def get_default_redirect_url(self):
        profile = getattr(self.request.user, "creator_profile", None)
        return reverse("creator-dashboard" if profile and profile.status == "approved" else "creator-application")


class ScopedLogoutView(LogoutView):
    account_type = "student"

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.account_type != self.account_type:
            return redirect(self.next_page)
        return super().post(request, *args, **kwargs)


class StudentLogoutView(ScopedLogoutView):
    next_page = "home"


class CreatorLogoutView(ScopedLogoutView):
    account_type = "creator"
    next_page = "creator-login"


@never_cache
@require_http_methods(["GET", "POST"])
def register(request, creator=False):
    form_class = CreatorRegistrationForm if creator else AccountRegistrationForm
    form = form_class(request.POST if request.method == "POST" else None)
    next_url = "" if creator else student_destination(request, request.POST.get("next", request.GET.get("next", "")))
    throttled = False
    if request.method == "POST":
        try:
            allow(request, "creator" if creator else "student", "signup", request.POST.get("email", ""))
        except AccessThrottled as exc:
            form.add_error(None, str(exc))
            throttled = True
    if request.method == "POST" and not throttled and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
        except IntegrityError:
            form.add_error("email", "Ya existe una cuenta con este correo en este espacio. Inicia sesión.")
        else:
            login(request, user, backend="accounts.backends.AccountBackend")
            request_email_action(request, user, "verify", destination=reverse("creator-application") if creator else next_url)
            messages.success(request, "Cuenta de creador creada. Completa tu perfil para solicitar la aprobación." if creator else "Cuenta de estudiante creada.")
            return redirect("creator-application" if creator else next_url or "workspace")
    return render(request, "creators/register.html" if creator else "registration/register.html", {"form": form, "creator_auth": creator, "next": next_url})


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def student_profile(request):
    if request.user.account_type != "student":
        return redirect_to_login(request.get_full_path(), reverse("login"))
    form = StudentProfileForm(request.POST if request.method == "POST" else None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            get_user_model().objects.filter(pk=request.user.pk).update(profile_public=F("profile_public"))
            member = get_user_model().objects.get(pk=request.user.pk)
            if not member.is_active or member.account_type != "student" or member.get_session_auth_hash() != request.user.get_session_auth_hash():
                raise PermissionDenied("La cuenta cambió. Vuelve a entrar antes de guardar el perfil.")
            for field in StudentProfileForm.Meta.fields:
                setattr(member, field, form.cleaned_data[field])
            member.save(update_fields=StudentProfileForm.Meta.fields)
        messages.success(request, "Perfil de estudiante guardado.")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"redirect": reverse("student-profile")})
        return redirect("student-profile")
    from .account_views import account_context
    return render(request, "registration/profile.html", account_context(request, False, "profile", form=form))


@never_cache
@require_GET
def member_profile(request, pk):
    member = get_object_or_404(get_user_model().objects.select_related("creator_profile"), pk=pk, is_active=True)
    if member.account_type == "creator" and member.has_public_profile:
        return redirect("creator-public-profile", pk=member.pk)
    if member.account_type != "student" or (not member.has_public_profile and request.user != member):
        raise Http404
    return render(request, "accounts/member_profile.html", {"member": member, "base_template": "creators/base.html" if request.user.is_authenticated and request.user.account_type == "creator" else "academy.html"})


@login_required
@never_cache
@require_GET
def members(request):
    query = request.GET.get("q", "").strip()[:100]
    kind = request.GET.get("tipo", "")
    people = get_user_model().objects.filter(is_active=True).filter(
        Q(account_type="student", profile_public=True) | Q(account_type="creator", creator_profile__status="approved")
    ).select_related("creator_profile")
    if settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL:
        people = people.filter(email_verified_at__isnull=False)
    if kind in ("student", "creator"):
        people = people.filter(account_type=kind)
    else:
        kind = ""
    if query:
        people = people.filter(
            Q(account_type="student") & (Q(display_name__icontains=query) | Q(interests__icontains=query))
            | Q(account_type="creator") & (Q(creator_profile__display_name__icontains=query) | Q(creator_profile__specialty__icontains=query))
        )
    return render(request, "accounts/members.html", {
        "people": Paginator(people.order_by("-date_joined", "-pk"), 20).get_page(request.GET.get("pagina")),
        "query": query, "kind": kind,
        "base_template": "creators/base.html" if request.user.account_type == "creator" else "academy.html",
    })
