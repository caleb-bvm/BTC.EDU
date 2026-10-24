import uuid

from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .avatars import normalize_avatar
from .models import AccountSupportRequest, User


class PhotoForm(forms.Form):
    photo = forms.FileField(label="Elige una foto", required=False, widget=forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-avatar-input": ""}))
    crop_x = forms.IntegerField(label="Posición horizontal", min_value=0, max_value=100, initial=50, required=False, widget=forms.NumberInput(attrs={"type": "range", "min": 0, "max": 100, "data-avatar-x": ""}))
    crop_y = forms.IntegerField(label="Posición vertical", min_value=0, max_value=100, initial=50, required=False, widget=forms.NumberInput(attrs={"type": "range", "min": 0, "max": 100, "data-avatar-y": ""}))
    zoom = forms.DecimalField(label="Acercar", min_value=1, max_value=3, initial=1, required=False, widget=forms.NumberInput(attrs={"type": "range", "min": 1, "max": 3, "step": "0.1", "data-avatar-zoom": ""}))
    remove_photo = forms.BooleanField(label="Eliminar mi foto", required=False)

    def clean(self):
        data = super().clean()
        if data.get("photo") and data.get("remove_photo"):
            self.add_error("remove_photo", "Elige cambiar la foto o eliminarla.")
        if data.get("photo") and not self.errors:
            try:
                data["photo"] = normalize_avatar(data["photo"], data.get("crop_x") if data.get("crop_x") is not None else 50,
                                                   data.get("crop_y") if data.get("crop_y") is not None else 50, data.get("zoom") or 1)
            except forms.ValidationError as exc:
                self.add_error("photo", exc)
        return data


class CurrentPasswordForm(forms.Form):
    password = forms.CharField(label="Contraseña actual", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("La contraseña actual no es correcta.")
        return password


class EmailChangeForm(CurrentPasswordForm):
    email = forms.EmailField(label="Nuevo correo electrónico")


class CloseAccountForm(CurrentPasswordForm):
    confirm = forms.BooleanField(label="Entiendo que perderé el acceso mientras mi cuenta esté desactivada y que se conservarán mis compras y registros históricos.")


class AccountPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "Contraseña actual"
        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password2"].label = "Repite la nueva contraseña"


class PreferencesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("notify_questions", "notify_community")
        help_texts = {"notify_questions": "Recibe avisos internos de preguntas y respuestas.",
                      "notify_community": "Recibe avisos de nuevas respuestas y comentarios de lecciones. Los avisos de cuenta, revisión y moderación se conservan."}


class SupportForm(forms.ModelForm):
    request_key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)

    class Meta:
        model = AccountSupportRequest
        fields = ("kind", "body", "request_key")
        labels = {"kind": "Sobre qué necesitas ayuda", "body": "Cuéntanos qué ocurrió"}
        widgets = {"body": forms.Textarea(attrs={"rows": 5, "maxlength": 2000})}

    def __init__(self, *args, user, context=None, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(user, "creator_profile", None)
        if not profile or profile.status != "suspended":
            self.fields["kind"].choices = [(key, label) for key, label in self.fields["kind"].choices if key != "appeal"]
        if context:
            self.fields["kind"].choices = [("other", "Ayuda con una compra o acceso")]
            self.initial["kind"] = "other"
            limit = max(0, 2000 - len(context["body_prefix"]))
            self.fields["body"].max_length = limit
            self.fields["body"].widget.attrs["maxlength"] = limit
            from django.core.validators import MaxLengthValidator
            self.fields["body"].validators = [validator for validator in self.fields["body"].validators if not isinstance(validator, MaxLengthValidator)] + [MaxLengthValidator(limit)]


class RestoreAccountForm(forms.Form):
    email = forms.EmailField(label="Correo de tu cuenta")
    account_type = forms.ChoiceField(label="Espacio", choices=(("student", "Estudiante"), ("creator", "Creador")))
