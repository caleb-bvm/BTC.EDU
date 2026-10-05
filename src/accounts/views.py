from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, redirect_to_login
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .forms import (
    AccountLoginForm,
    AccountRegistrationForm,
    CreatorLoginForm,
    CreatorRegistrationForm,
    StudentProfileForm,
)


class StudentLoginView(LoginView):
    authentication_form = AccountLoginForm
    template_name = "registration/login.html"

    def get_redirect_url(self):
        destination = super().get_redirect_url()
        return destination if destination.startswith(("/mi-espacio/", "/cuenta/perfil/", "/cursos/", "/tutoriales/", "/recursos/", "/lecciones/", "/ofertas/", "/facturas/", "/aprendizaje/")) else ""


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
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
        except IntegrityError:
            form.add_error("email", "Ya existe una cuenta con este correo en este espacio. Inicia sesión.")
        else:
            login(request, user, backend="accounts.backends.AccountBackend")
            messages.success(request, "Cuenta de creador creada. Completa tu perfil para solicitar la aprobación." if creator else "Cuenta de estudiante creada.")
            return redirect("creator-application" if creator else "workspace")
    return render(request, "creators/register.html" if creator else "registration/register.html", {"form": form, "creator_auth": creator})


@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def student_profile(request):
    if request.user.account_type != "student":
        return redirect_to_login(request.get_full_path(), reverse("login"))
    form = StudentProfileForm(request.POST if request.method == "POST" else None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil de estudiante guardado.")
        return redirect("student-profile")
    return render(request, "registration/profile.html", {"form": form, "active": "workspace"})
