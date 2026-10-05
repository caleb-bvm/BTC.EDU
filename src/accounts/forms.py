from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django.core.exceptions import ValidationError


class AccountLoginForm(AuthenticationForm):
    account_type = "student"

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password, account_type=self.account_type)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class CreatorLoginForm(AccountLoginForm):
    account_type = "creator"

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        profile = getattr(user, "creator_profile", None)
        if profile and profile.status == "suspended":
            raise self.get_invalid_login_error()


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
        fields = ("first_name", "last_name")
        labels = {"first_name": "Nombre", "last_name": "Apellido"}
