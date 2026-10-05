from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower


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
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        constraints = [models.UniqueConstraint(Lower("email"), "account_type", name="unique_email_per_account_type")]

    def natural_key(self):
        return (self.email, self.account_type)

    def __str__(self):
        return f"{self.email} · {self.get_account_type_display()}"
