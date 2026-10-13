from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django.core.exceptions import ValidationError

from .throttling import AccessThrottled, allow


class AccountLoginForm(AuthenticationForm):
    account_type = "student"

    def get_invalid_login_error(self):
        label = "creador" if self.account_type == "creator" else "estudiante"
        return ValidationError(f"No pudimos iniciar sesión. Revisa las credenciales de tu cuenta de {label}.", code="invalid_login")

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if email and password:
            try:
                allow(self.request, self.account_type, "login", email)
            except AccessThrottled as exc:
                raise ValidationError(str(exc)) from exc
            self.user_cache = authenticate(self.request, username=email, password=password, account_type=self.account_type)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class CreatorLoginForm(AccountLoginForm):
    account_type = "creator"


class AccountRegistrationForm(BaseUserCreationForm):
    email = forms.EmailField(label="Correo electrónico", max_length=254)
    account_type = "student"

    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.account_type = self.account_type
        self.fields["first_name"].required = True
        self.fields["first_name"].label = "Nombre"
        self.fields["last_name"].label = "Apellido"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if self._meta.model.objects.filter(email__iexact=email, account_type=self.account_type).exists():
            raise ValidationError("Ya existe una cuenta con este correo en este espacio. Inicia sesión.")
        return email


class CreatorRegistrationForm(AccountRegistrationForm):
    account_type = "creator"


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "display_name", "bio", "interests", "learning_goal", "website", "profile_public")
        labels = {"first_name": "Nombre", "last_name": "Apellido"}
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}
        help_texts = {
            "display_name": "Este nombre aparece en tus mensajes. Puedes usar un alias; si lo dejas vacío se muestra Participante.",
            "profile_public": "Tu alias, foto, presentación, intereses y sitio web podrán verse sin iniciar sesión. Tu correo, compras, progreso y notas siguen privados. Ocultar el perfil no elimina tus mensajes.",
        }

    def clean(self):
        data = super().clean()
        if data.get("profile_public") and not data.get("display_name"):
            self.add_error("display_name", "Elige un nombre público para compartir tu perfil.")
        if data.get("profile_public") and settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL and not self.instance.email_verified_at:
            self.add_error("profile_public", "Confirma tu correo desde Acceso antes de compartir tu perfil.")
        return data
