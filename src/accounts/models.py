import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower

from content.immutability import FrozenRecord


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, email, account_type="admin"):
        # Django's createsuperuser command checks the administration identity;
        # serialized accounts include both parts of their natural key.
        return self.get(email__iexact=email, account_type=account_type)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio.")
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("account_type", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("El administrador requiere permisos de staff y superuser.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Identidades independientes por espacio; nunca se convierten al solicitar un rol."""
    class Type(models.TextChoices):
        STUDENT = "student", "Estudiante"
        CREATOR = "creator", "Creador"
        ADMIN = "admin", "Administración"

    username = None
    email = models.EmailField("correo")
    account_type = models.CharField("tipo de cuenta", max_length=12, choices=Type, default=Type.STUDENT)
    display_name = models.CharField("nombre público o alias", max_length=80, blank=True)
    bio = models.TextField("sobre ti", max_length=1000, blank=True)
    interests = models.CharField("intereses de aprendizaje", max_length=200, blank=True)
    website = models.URLField("sitio web", blank=True)
    profile_public = models.BooleanField("Compartir mi perfil", default=False)
    avatar = models.FileField("foto de perfil", upload_to="account-avatars/", blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    notify_questions = models.BooleanField("Preguntas y respuestas", default=True)
    notify_community = models.BooleanField("Conversaciones que sigo", default=True)
    learning_goal = models.CharField("qué quieres aprender", max_length=200, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    session_revision = models.PositiveIntegerField(default=0)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        constraints = [models.UniqueConstraint(Lower("email"), "account_type", name="unique_email_per_account_type")]

    def natural_key(self):
        return (self.email, self.account_type)

    def _get_session_auth_hash(self, secret=None):
        from django.utils.crypto import salted_hmac
        return salted_hmac("accounts.User.session", f"{self.password}:{self.email}:{self.session_revision}:{self.account_type}", secret=secret, algorithm="sha256").hexdigest()

    @property
    def public_name(self):
        if self.account_type == self.Type.CREATOR:
            profile = getattr(self, "creator_profile", None)
            if profile and profile.status == "approved":
                return profile.display_name
        return self.display_name or "Participante"

    @property
    def has_public_profile(self):
        if not self.is_active:
            return False
        if settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL and not self.email_verified_at:
            return False
        if self.account_type == self.Type.CREATOR:
            profile = getattr(self, "creator_profile", None)
            return bool(profile and profile.status == "approved")
        return self.account_type == self.Type.STUDENT and self.profile_public

    @property
    def profile_initials(self):
        return "".join(word[0] for word in self.public_name.split()[:2]).upper()

    @property
    def avatar_url(self):
        if not self.avatar:
            return ""
        from pathlib import PurePosixPath

        from django.urls import reverse
        return reverse("account-avatar", args=[self.pk, PurePosixPath(self.avatar.name).stem])

    def __str__(self):
        return f"{self.email} · {self.get_account_type_display()}"


class AccountEmailAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=20, choices=(("verify", "Verificar correo"), ("change", "Cambiar correo"), ("restore", "Reactivar cuenta")))
    original_email = models.EmailField()
    new_email = models.EmailField(blank=True)
    destination = models.CharField(max_length=500, blank=True)
    state_digest = models.CharField(max_length=64)
    old_confirmed = models.BooleanField(default=False)
    new_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)


class AccountMail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=10, default="pending", choices=(("pending", "Pendiente"), ("sent", "Enviado"), ("failed", "Reintentar"), ("cancelled", "Vencido o sustituido")))
    action = models.ForeignKey(AccountEmailAction, on_delete=models.PROTECT, null=True, blank=True)
    state_digest = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    next_attempt_at = models.DateTimeField(null=True, blank=True)


class AccountSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    session_key = models.CharField(max_length=40, unique=True)
    browser = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)


class AccountEvent(FrozenRecord):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    kind = models.CharField(max_length=40, choices=(
        ("photo_updated", "Foto de perfil actualizada"), ("password_changed", "Contraseña actualizada"),
        ("email_verify_requested", "Confirmación de correo solicitada"), ("email_change_requested", "Cambio de correo solicitado"),
        ("email_restore_requested", "Reactivación solicitada"), ("email_verified", "Correo confirmado"),
        ("email_changed", "Correo actualizado"), ("session_ended", "Sesión cerrada"),
        ("account_closed", "Cuenta desactivada"), ("account_restored", "Cuenta reactivada"),
        ("account_exported", "Resumen de datos descargado"),
    ))
    detail = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-pk")


class AccessAttempt(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    window_started_at = models.DateTimeField()
    count = models.PositiveIntegerField(default=0)


class AccountSupportRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    kind = models.CharField(max_length=20, choices=(("appeal", "Revisar suspensión"), ("access", "Acceso a mi cuenta"), ("other", "Otra consulta")))
    body = models.TextField(max_length=2000)
    request_key = models.UUIDField(default=uuid.uuid4)
    status = models.CharField(max_length=10, default="open", choices=(("open", "Recibida"), ("review", "En revisión"), ("resolved", "Respondida")))
    response = models.TextField(max_length=2000, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="account_support_reviews")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at", "-pk")
        constraints = [
            models.UniqueConstraint(fields=("user", "request_key"), name="unique_account_support_request"),
            models.UniqueConstraint(fields=("user",), condition=models.Q(kind="appeal", status__in=("open", "review")), name="one_open_creator_appeal"),
        ]


class SupportEvent(FrozenRecord):
    request = models.ForeignKey(AccountSupportRequest, on_delete=models.PROTECT, related_name="history")
    status = models.CharField(max_length=10)
    response = models.TextField(blank=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
