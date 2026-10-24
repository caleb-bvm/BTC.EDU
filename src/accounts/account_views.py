from functools import wraps
from urllib.parse import urlencode
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import get_user_model, logout, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import redirect_to_login
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
    require_safe,
)

from .account_forms import (
    AccountPasswordForm,
    CloseAccountForm,
    CurrentPasswordForm,
    EmailChangeForm,
    PhotoForm,
    PreferencesForm,
    RestoreAccountForm,
    SupportForm,
)
from .avatars import avatar_token, avatar_visible, update_avatar
from .models import (
    AccountEvent,
    AccountMail,
    AccountSession,
    AccountSupportRequest,
    SupportEvent,
)
from .security import (
    change_password,
    close_account,
    confirm_action,
    request_email_action,
    resolve_action,
    revoke_sessions,
)
from .throttling import AccessThrottled, allow


def account_required(view):
    @never_cache
    @wraps(view)
    def wrapped(request, *args, creator=False, **kwargs):
        kind = "creator" if creator else "student"
        if not request.user.is_authenticated or request.user.account_type != kind:
            return redirect_to_login(request.get_full_path(), reverse("creator-login" if creator else "login"))
        if not request.user.is_active:
            raise PermissionDenied
        if request.method == "POST" and request.POST.get("account_id", str(request.user.pk)) != str(request.user.pk):
            messages.error(request, "La cuenta activa cambió. Revisa el formulario antes de guardar.")
            return redirect("creator-account" if creator else "student-account")
        response = view(request, *args, creator=creator, **kwargs)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" and response.status_code == 302:
            return JsonResponse({"redirect": response.url})
        return response
    return wrapped


def account_context(request, creator, tab="home", **extra):
    prefix = "creator" if creator else "student"
    tabs = [("home", "Resumen", "account"), ("photo", "Foto", "account-photo"),
            ("profile", "Perfil", "application" if creator else "profile"),
            ("security", "Acceso", "account-security"), ("preferences", "Avisos", "account-preferences"),
            ("support", "Ayuda", "account-support")]
    navigation = []
    for key, label, target in tabs:
        name = "creator-application" if target == "application" else "student-profile" if target == "profile" else f"{prefix}-{target}"
        navigation.append({"key": key, "label": label, "url": reverse(name)})
    return {"base_template": "creators/base.html" if creator else "academy.html", "account_prefix": prefix,
            "account_tab": tab, "account_tabs": navigation, "creator_space": creator, "active": "account", **extra}


def account_render(request, creator, tab="home", **extra):
    return render(request, "accounts/settings.html", account_context(request, creator, tab, **extra))


@account_required
@require_GET
def overview(request, creator=False):
    profile = getattr(request.user, "creator_profile", None)
    steps = [bool(request.user.avatar), bool(profile if creator else request.user.display_name), bool(request.user.email_verified_at)]
    return account_render(request, creator, completion=sum(steps), profile=profile,
                          account_history=request.user.accountevent_set.all()[:6])


@account_required
@require_http_methods(["GET", "POST"])
def photo(request, creator=False):
    form = PhotoForm(request.POST if request.method == "POST" else None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        if form.cleaned_data.get("photo") or form.cleaned_data["remove_photo"] and request.user.avatar:
            update_avatar(request.user, form.cleaned_data.get("photo"), form.cleaned_data["remove_photo"])
            AccountEvent.objects.create(user=request.user, kind="photo_updated")
            messages.success(request, "Foto de perfil actualizada.")
            return redirect(f"{'creator' if creator else 'student'}-account-photo")
        form.add_error(None, "Elige una foto nueva antes de guardar.")
    return account_render(request, creator, "photo", form=form)


@never_cache
@require_safe
def avatar(request, pk, token):
    member = get_object_or_404(get_user_model().objects.select_related("creator_profile"), pk=pk)
    if not member.avatar or token != avatar_token(member) or not avatar_visible(request.user, member):
        raise Http404
    try:
        response = FileResponse(member.avatar.storage.open(member.avatar.name, "rb"), content_type="image/webp")
    except OSError as exc:
        raise Http404 from exc
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@never_cache
@require_GET
def session_context(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "session_expired"}, status=401)
    return JsonResponse({"account_id": str(request.user.pk), "account_type": request.user.account_type, "csrf_token": get_token(request)})


@account_required
@require_GET
def security(request, creator=False):
    failed = AccountMail.objects.filter(user=request.user, status="failed", expires_at__gt=timezone.now()).filter(action__consumed_at__isnull=True).exists()
    return account_render(request, creator, "security", mail_delivery_failed=failed)


@account_required
@require_http_methods(["GET", "POST"])
def password(request, creator=False):
    form = AccountPasswordForm(request.user, request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            current = change_password(request.user, form.cleaned_data["old_password"], form.cleaned_data["new_password1"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            update_session_auth_hash(request, current)
            revoke_sessions(current, except_key=request.session.session_key)
            messages.success(request, "Contraseña actualizada. Las otras sesiones de esta cuenta se cerraron.")
            return redirect(f"{'creator' if creator else 'student'}-account-security")
    return account_render(request, creator, "password", form=form)


@account_required
@require_http_methods(["GET", "POST"])
def email(request, creator=False):
    form = EmailChangeForm(request.user, request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            allow(request, request.user.account_type, "email", request.user.email)
            request_email_action(request, request.user, "change", form.cleaned_data["email"])
        except (ValidationError, AccessThrottled) as exc:
            form.add_error(None, " ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc))
        else:
            messages.success(request, "Confirma el cambio desde tu correo actual y el nuevo. El correo de tu cuenta se conserva hasta completar ambos pasos.")
            return redirect(f"{'creator' if creator else 'student'}-account-security")
    return account_render(request, creator, "email", form=form)


@account_required
@require_POST
def verify(request, creator=False):
    try:
        allow(request, request.user.account_type, "email", request.user.email)
        request_email_action(request, request.user, "verify")
    except (ValidationError, AccessThrottled) as exc:
        messages.error(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc))
    else:
        messages.success(request, "Solicitamos el envío del enlace de confirmación a tu correo. Si no llega, puedes volver a solicitarlo.")
    return redirect(f"{'creator' if creator else 'student'}-account-security")


@never_cache
@require_http_methods(["GET", "POST"])
def email_confirm(request, token):
    action, error, form, done = None, "", None, False
    try:
        action, stage = resolve_action(token)
        if action.purpose == "restore":
            form = SetPasswordForm(action.user, request.POST if request.method == "POST" else None)
        if request.method == "POST" and (form is None or form.is_valid()):
            user, done = confirm_action(token, form.cleaned_data["new_password1"] if form else None)
            if done and action.purpose == "change" and request.user.is_authenticated and request.user.pk == user.pk:
                logout(request)
    except (ValidationError, IntegrityError) as exc:
        error = " ".join(exc.messages) if isinstance(exc, ValidationError) else "Ese correo ya no está disponible. Solicita otro cambio."
    continue_url = ""
    if action:
        login_url = reverse("creator-login" if action.user.account_type == "creator" else "login")
        if action.destination:
            login_url += "?" + urlencode({"next": action.destination})
        continue_url = action.destination if done and action.purpose == "verify" and request.user.is_authenticated and request.user.pk == action.user_id and action.destination else login_url
    return render(request, "accounts/confirm_email.html", {"action": action, "error": error, "form": form, "done": done, "submitted": request.method == "POST", "continue_url": continue_url})


@account_required
@require_http_methods(["GET", "POST"])
def preferences(request, creator=False):
    form = PreferencesForm(request.POST if request.method == "POST" else None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        member = form.save(commit=False)
        member.save(update_fields=PreferencesForm.Meta.fields)
        messages.success(request, "Preferencias de avisos guardadas.")
        return redirect(f"{'creator' if creator else 'student'}-account-preferences")
    return account_render(request, creator, "preferences", form=form)


@account_required
@require_http_methods(["GET", "POST"])
def sessions(request, creator=False):
    if request.method == "POST":
        try:
            session_id = UUID(request.POST.get("session", ""))
        except (ValueError, TypeError, AttributeError) as exc:
            raise Http404 from exc
        session = get_object_or_404(AccountSession, pk=session_id, user=request.user, ended_at__isnull=True)
        Session.objects.filter(session_key=session.session_key).delete()
        session.ended_at = timezone.now()
        session.save(update_fields=("ended_at",))
        AccountEvent.objects.create(user=request.user, kind="session_ended")
        if session.session_key == request.session.session_key:
            logout(request)
            return redirect("creator-login" if creator else "login")
        messages.success(request, "Sesión cerrada.")
        return redirect(f"{'creator' if creator else 'student'}-account-sessions")
    rows = AccountSession.objects.filter(user=request.user, ended_at__isnull=True, session_key__in=Session.objects.filter(expire_date__gt=timezone.now()).values_list("session_key", flat=True)).order_by("-last_seen_at")
    for row in rows:
        row.is_current = row.session_key == request.session.session_key
    return account_render(request, creator, "sessions", sessions=rows)


@account_required
@require_http_methods(["GET", "POST"])
def support(request, creator=False):
    from .support_context import verified_support_context
    context = verified_support_context(request.user, request.POST if request.method == "POST" else request.GET)
    form = SupportForm(request.POST if request.method == "POST" else None, user=request.user, context=context)
    if request.method == "POST" and form.is_valid():
        try:
            allow(request, request.user.account_type, "support", request.user.email)
            with transaction.atomic():
                body = (context["body_prefix"] if context else "") + form.cleaned_data["body"]
                item, created = AccountSupportRequest.objects.get_or_create(user=request.user, request_key=form.cleaned_data["request_key"], defaults={"kind": form.cleaned_data["kind"], "body": body})
                if item.kind != form.cleaned_data["kind"] or item.body != body:
                    raise ValidationError("Este envío ya fue utilizado. Recarga antes de enviar otro mensaje.")
                if created:
                    SupportEvent.objects.create(request=item, status="open", actor=request.user)
        except (IntegrityError, AccessThrottled, ValidationError) as exc:
            form.add_error(None, "Ya tienes una solicitud de revisión de suspensión abierta." if isinstance(exc, IntegrityError) else " ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc))
        else:
            messages.success(request, "Solicitud recibida. Puedes consultar su estado y las respuestas aquí.")
            return redirect(f"{'creator' if creator else 'student'}-account-support")
    return account_render(request, creator, "support", form=form, support_context=context, requests=Paginator(AccountSupportRequest.objects.filter(user=request.user).prefetch_related("history"), 10).get_page(request.GET.get("pagina")))


@account_required
@require_http_methods(["GET", "POST"])
def export(request, creator=False):
    form = CurrentPasswordForm(request.user, request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        from .export import account_data
        response = JsonResponse(account_data(request.user))
        response["Content-Disposition"] = 'attachment; filename="btc-edu-mi-cuenta.json"'
        response["Cache-Control"] = "private, no-store"
        AccountEvent.objects.create(user=request.user, kind="account_exported")
        return response
    return account_render(request, creator, "export", form=form)


@account_required
@require_http_methods(["GET", "POST"])
def close(request, creator=False):
    form = CloseAccountForm(request.user, request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        close_account(request.user)
        logout(request)
        return render(request, "accounts/closed.html")
    return account_render(request, creator, "close", form=form)


@never_cache
@require_http_methods(["GET", "POST"])
def restore(request):
    form = RestoreAccountForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            allow(request, form.cleaned_data["account_type"], "restore", form.cleaned_data["email"])
            user = get_user_model().objects.filter(email__iexact=form.cleaned_data["email"], account_type=form.cleaned_data["account_type"], is_active=False, closed_at__isnull=False).first()
            if user:
                request_email_action(request, user, "restore")
        except AccessThrottled as exc:
            form.add_error(None, str(exc))
        else:
            return render(request, "accounts/restore.html", {"submitted": True})
    return render(request, "accounts/restore.html", {"form": form})


@account_required
@require_GET
def switch(request, creator=False):
    target = "student" if creator else "creator"
    return account_render(request, creator, "switch", target_space="estudiante" if creator else "creador", target_login=reverse("login" if creator else "creator-login"), target_type=target)
