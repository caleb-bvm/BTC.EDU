from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import (
    INTERNAL_RESET_SESSION_TOKEN,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import path, reverse_lazy

from .mail import queue_mail
from .throttling import AccessThrottled, allow


class AccountResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return super()._make_hash_value(user, timestamp) + f":{user.account_type}:{user.session_revision}:{user.is_active}"


account_reset_tokens = AccountResetTokenGenerator()


class StudentPasswordResetForm(PasswordResetForm):
    account_type = "student"

    def get_users(self, email):
        users = get_user_model().objects.filter(email__iexact=email.strip(), account_type=self.account_type, is_active=True)
        return (user for user in users if user.has_usable_password())

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        subject = "".join(render_to_string(subject_template_name, context).splitlines())
        queue_mail(context["user"], to_email, subject, render_to_string(email_template_name, context))


class LimitedPasswordResetView(PasswordResetView):
    account_type = "student"
    token_generator = account_reset_tokens

    def form_valid(self, form):
        try:
            allow(self.request, self.account_type, "reset", form.cleaned_data["email"])
        except AccessThrottled as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        return super().form_valid(form)


class CreatorPasswordResetForm(StudentPasswordResetForm):
    account_type = "creator"


class ScopedResetConfirmView(PasswordResetConfirmView):
    account_type = "student"
    token_generator = account_reset_tokens

    def get_user(self, uidb64):
        user = super().get_user(uidb64)
        return user if user and user.is_active and user.account_type == self.account_type else None

    def form_valid(self, form):
        with transaction.atomic():
            User = get_user_model()
            User.objects.filter(pk=self.user.pk).update(profile_public=F("profile_public"))
            current = User.objects.get(pk=self.user.pk)
            token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN, "")
            if not current.is_active or current.account_type != self.account_type or not self.token_generator.check_token(current, token):
                self.validlink = False
                return self.form_invalid(form)
            current.set_password(form.cleaned_data["new_password1"])
            current.save(update_fields=("password",))
            from .models import AccountEvent
            from .security import revoke_sessions
            revoke_sessions(current)
            AccountEvent.objects.create(user=current, kind="password_changed")
        self.request.session.pop(INTERNAL_RESET_SESSION_TOKEN, None)
        return HttpResponseRedirect(self.get_success_url())


def recovery_patterns(creator=False):
    name = "creator" if creator else "student"
    context = {
        "auth_base": "creators/auth_base.html" if creator else "_auth_base.html",
        "space_label": "creador" if creator else "estudiante",
        "login_name": "creator-login" if creator else "login",
    }
    return [
        path("recuperar/", LimitedPasswordResetView.as_view(
            account_type="creator" if creator else "student",
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
