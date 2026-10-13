import hashlib
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from .destinations import student_destination
from .mail import queue_mail
from .models import AccountEmailAction, AccountEvent, AccountSession


def state_digest(user):
    value = f"{user.pk}|{user.account_type}|{user.email}|{user.password}|{user.is_active}|{user.closed_at}|{user.session_revision}"
    return hashlib.sha256(value.encode()).hexdigest()


def action_token(action, stage="new"):
    return signing.dumps({"id": str(action.pk), "stage": stage}, salt="accounts.email-action", compress=True)


def action_url(request, action, stage="new"):
    return request.build_absolute_uri(reverse("account-email-confirm", args=[action_token(action, stage)]))


@transaction.atomic
def request_email_action(request, user, purpose, new_email="", destination=""):
    User = get_user_model()
    User.objects.filter(pk=user.pk).update(profile_public=F("profile_public"))
    user.refresh_from_db()
    if purpose not in ("verify", "change", "restore"):
        raise ValidationError("La solicitud no es válida.")
    if purpose == "restore":
        if user.is_active or not user.closed_at:
            raise PermissionDenied
    elif not user.is_active:
        raise PermissionDenied
    if purpose == "change":
        new_email = new_email.strip().lower()
        if not new_email or new_email == user.email:
            raise ValidationError("Escribe un correo diferente al actual.")
        if User.objects.filter(account_type=user.account_type, email__iexact=new_email).exclude(pk=user.pk).exists():
            raise ValidationError("No podemos utilizar ese correo en esta cuenta.")
    now = timezone.now()
    if purpose == "verify":
        destination = destination or getattr(request, "session", {}).get("account_verify_destination", "")
        destination = student_destination(request, destination) if user.account_type == "student" else destination if destination.startswith("/crear/") and not destination.startswith(("/crear/entrar/", "/crear/registro/")) else ""
    else:
        destination = ""
    AccountEmailAction.objects.filter(user=user, purpose=purpose, consumed_at__isnull=True).update(consumed_at=now)
    action = AccountEmailAction.objects.create(user=user, purpose=purpose, original_email=user.email,
                                               new_email=new_email, destination=destination[:500], state_digest=state_digest(user),
                                               expires_at=now + timedelta(seconds=settings.ACCOUNT_EMAIL_TOKEN_TIMEOUT))
    label = user.get_account_type_display().lower()
    if purpose == "change":
        queue_mail(user, user.email, f"Autoriza el cambio de correo · BTC.EDU · {label}",
                   f"Has solicitado cambiar el correo de tu cuenta de {label}. Confirma desde tu correo actual:\n\n{action_url(request, action, 'old')}\n\nTambién debes confirmar el correo nuevo. Si no lo solicitaste, no confirmes el cambio.", action=action)
        queue_mail(user, new_email, f"Confirma tu nuevo correo · BTC.EDU · {label}",
                   f"Confirma este correo para tu cuenta de {label}:\n\n{action_url(request, action)}\n\nEl cambio requiere también la aprobación desde tu correo actual.", action=action)
    else:
        title = "Confirma tu correo" if purpose == "verify" else "Reactiva tu cuenta"
        queue_mail(user, user.email, f"{title} · BTC.EDU · {label}",
                   f"{title} para tu cuenta de {label}:\n\n{action_url(request, action)}\n\nEl enlace vence en {settings.ACCOUNT_EMAIL_TOKEN_TIMEOUT // 60} minutos. Si no lo solicitaste, puedes ignorarlo.", action=action)
    AccountEvent.objects.create(user=user, kind=f"email_{purpose}_requested")
    return action


def resolve_action(token):
    try:
        data = signing.loads(token, salt="accounts.email-action", max_age=settings.ACCOUNT_EMAIL_TOKEN_TIMEOUT)
        action = AccountEmailAction.objects.select_related("user").get(pk=data["id"], consumed_at__isnull=True)
        stage = data["stage"]
    except (signing.BadSignature, signing.SignatureExpired, AccountEmailAction.DoesNotExist, ValueError, KeyError, TypeError) as exc:
        raise ValidationError("El enlace venció o ya fue utilizado. Solicita uno nuevo desde tu cuenta.") from exc
    if stage not in ("old", "new") or (stage == "old" and action.purpose != "change"):
        raise ValidationError("El enlace no es válido.")
    if action.expires_at <= timezone.now() or not constant_time_compare(action.state_digest, state_digest(action.user)):
        raise ValidationError("El enlace venció o la cuenta cambió. Solicita uno nuevo.")
    return action, stage


@transaction.atomic
def confirm_action(token, new_password=None):
    # Reserve the SQLite writer before reading: two confirmations must not
    # both begin from a read snapshot that cannot safely become a write.
    try:
        data = signing.loads(token, salt="accounts.email-action", max_age=settings.ACCOUNT_EMAIL_TOKEN_TIMEOUT)
        AccountEmailAction.objects.filter(pk=data["id"]).update(consumed_at=F("consumed_at"))
    except (signing.BadSignature, signing.SignatureExpired, ValueError, KeyError, TypeError, ValidationError) as exc:
        raise ValidationError("El enlace venció o ya fue utilizado. Solicita uno nuevo desde tu cuenta.") from exc
    action, stage = resolve_action(token)
    User = get_user_model()
    user, now = action.user, timezone.now()
    if action.purpose == "verify":
        if not user.is_active:
            raise PermissionDenied
        user.email_verified_at = now
        user.save(update_fields=("email_verified_at",))
        AccountEvent.objects.create(user=user, kind="email_verified")
    elif action.purpose == "change":
        if not user.is_active:
            raise PermissionDenied
        setattr(action, "old_confirmed" if stage == "old" else "new_confirmed", True)
        if not (action.old_confirmed and action.new_confirmed):
            action.save(update_fields=("old_confirmed", "new_confirmed"))
            return user, False
        if User.objects.filter(account_type=user.account_type, email__iexact=action.new_email).exclude(pk=user.pk).exists():
            raise ValidationError("Ese correo ya no está disponible. Solicita otro cambio desde tu cuenta.")
        user.email, user.email_verified_at = action.new_email, now
        user.save(update_fields=("email", "email_verified_at"))
        AccountEvent.objects.create(user=user, kind="email_changed")
        revoke_sessions(user)
    elif action.purpose == "restore":
        if user.is_active or not user.closed_at or not new_password:
            raise ValidationError("La cuenta no está disponible para reactivación.")
        user.set_password(new_password)
        user.is_active, user.closed_at, user.email_verified_at = True, None, now
        user.save(update_fields=("password", "is_active", "closed_at", "email_verified_at"))
        AccountEvent.objects.create(user=user, kind="account_restored")
    action.consumed_at = now
    action.save(update_fields=("consumed_at", "old_confirmed", "new_confirmed"))
    return user, True


def revoke_sessions(user, except_key=None):
    from django.contrib.sessions.models import Session
    sessions = AccountSession.objects.filter(user=user, ended_at__isnull=True)
    if except_key:
        sessions = sessions.exclude(session_key=except_key)
    Session.objects.filter(session_key__in=sessions.values_list("session_key", flat=True)).delete()
    sessions.update(ended_at=timezone.now())


@transaction.atomic
def change_password(actor, old_password, new_password):
    User = get_user_model()
    User.objects.filter(pk=actor.pk).update(profile_public=F("profile_public"))
    current = User.objects.get(pk=actor.pk)
    if not current.is_active or current.get_session_auth_hash() != actor.get_session_auth_hash():
        raise ValidationError("La cuenta cambió. Vuelve a entrar antes de actualizar tu contraseña.")
    if not current.check_password(old_password):
        raise ValidationError("La contraseña actual ya no coincide. Recarga tu cuenta y vuelve a intentarlo.")
    current.set_password(new_password)
    current.save(update_fields=("password",))
    AccountEvent.objects.create(user=current, kind="password_changed")
    return current


@transaction.atomic
def close_account(user):
    from .avatars import update_avatar
    User = get_user_model()
    User.objects.filter(pk=user.pk).update(profile_public=F("profile_public"))
    user.refresh_from_db()
    if user.account_type not in ("student", "creator") or not user.is_active:
        raise PermissionDenied
    update_avatar(user, remove=True)
    user.is_active, user.profile_public, user.closed_at = False, False, timezone.now()
    user.save(update_fields=("is_active", "profile_public", "closed_at"))
    if user.account_type == "student":
        from learning.models import CertificateSharing
        CertificateSharing.objects.filter(certificate__enrollment__student=user).update(public=False)
    revoke_sessions(user)
    AccountEmailAction.objects.filter(user=user, consumed_at__isnull=True).update(consumed_at=timezone.now())
    AccountEvent.objects.create(user=user, kind="account_closed")
