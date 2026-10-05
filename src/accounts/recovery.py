from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy


class StudentPasswordResetForm(PasswordResetForm):
    account_type = "student"

    def get_users(self, email):
        users = get_user_model().objects.filter(email__iexact=email.strip(), account_type=self.account_type, is_active=True)
        return (user for user in users if user.has_usable_password())


class CreatorPasswordResetForm(StudentPasswordResetForm):
    account_type = "creator"


class ScopedResetConfirmView(PasswordResetConfirmView):
    account_type = "student"

    def get_user(self, uidb64):
        user = super().get_user(uidb64)
        return user if user and user.account_type == self.account_type else None


def recovery_patterns(creator=False):
    name = "creator" if creator else "student"
    context = {
        "auth_base": "creators/auth_base.html" if creator else "academy.html",
        "space_label": "creador" if creator else "estudiante",
        "login_name": "creator-login" if creator else "login",
    }
    return [
        path("recuperar/", PasswordResetView.as_view(
            form_class=CreatorPasswordResetForm if creator else StudentPasswordResetForm,
            template_name="registration/reset_request.html",
            email_template_name="registration/reset_email.txt",
            subject_template_name="registration/reset_subject.txt",
            extra_email_context={"reset_confirm_name": f"{name}-password-reset-confirm", "space_label": context["space_label"]},
            success_url=reverse_lazy(f"{name}-password-reset-done"),
            extra_context=context,
        ), name=f"{name}-password-reset"),
        path("recuperar/enviada/", PasswordResetDoneView.as_view(template_name="registration/reset_done.html", extra_context=context), name=f"{name}-password-reset-done"),
        path("recuperar/listo/", PasswordResetCompleteView.as_view(template_name="registration/reset_complete.html", extra_context=context), name=f"{name}-password-reset-complete"),
        path("recuperar/<uidb64>/<token>/", ScopedResetConfirmView.as_view(
            account_type="creator" if creator else "student",
            template_name="registration/reset_confirm.html",
            success_url=reverse_lazy(f"{name}-password-reset-complete"),
            extra_context=context,
        ), name=f"{name}-password-reset-confirm"),
    ]
