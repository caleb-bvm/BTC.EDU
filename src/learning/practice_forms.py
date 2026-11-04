"""Practice editor, delivery and review forms."""
from django import forms
from django.utils.translation import gettext, gettext_lazy

from .models import PracticeReview
from .practices import validate_attachment


class PracticeForm(forms.Form):
    enabled = forms.BooleanField(label=gettext_lazy("Incluir práctica en la próxima versión"), required=False)
    title = forms.CharField(label=gettext_lazy("Título"), max_length=200)
    instructions = forms.CharField(label=gettext_lazy("Qué debe entregar el estudiante"), max_length=10000, widget=forms.Textarea(attrs={"rows": 6}))
    criteria_text = forms.CharField(label=gettext_lazy("Criterios de aprobación"), help_text=gettext_lazy("Un criterio concreto por línea; entre 1 y 12, hasta 300 caracteres cada uno."), widget=forms.Textarea(attrs={"rows": 5}))
    review_days = forms.IntegerField(label=gettext_lazy("Plazo previsto de revisión (días naturales)"), initial=7, min_value=1, max_value=30,
        help_text=gettext_lazy("Cuenta desde cada entrega. El estudiante verá este plazo y los retrasos quedarán en tu bandeja."))
    revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def clean_criteria_text(self):
        criteria = [line.strip() for line in self.cleaned_data["criteria_text"].splitlines() if line.strip()]
        if not 1 <= len(criteria) <= 12 or any(len(line) > 300 for line in criteria):
            raise forms.ValidationError(gettext("Define entre 1 y 12 criterios de hasta 300 caracteres."))
        return criteria


class DeliveryForm(forms.Form):
    body = forms.CharField(label=gettext_lazy("Tu solución"), required=False, max_length=10000, widget=forms.Textarea(attrs={"rows": 7, "placeholder": gettext_lazy("Explica qué hiciste, el resultado y cómo comprobarlo.")}))
    project_url = forms.URLField(label=gettext_lazy("Enlace al proyecto"), required=False, max_length=500, assume_scheme="https",
        help_text=gettext_lazy("Comprueba que el educador pueda abrirlo. No incluyas contraseñas ni claves privadas."))
    attachment = forms.FileField(label=gettext_lazy("Archivo adjunto"), required=False, help_text=gettext_lazy("Un PDF, ZIP, TXT en UTF-8, PNG o JPG. Máximo 10 MB."), widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.zip,.txt,.png,.jpg,.jpeg"}))
    request_key = forms.UUIDField(widget=forms.HiddenInput)
    previous_id = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def clean_attachment(self):
        upload = self.cleaned_data.get("attachment")
        validate_attachment(upload)
        return upload

    def clean_project_url(self):
        value = self.cleaned_data.get("project_url", "")
        if value and not value.lower().startswith(("https://", "http://")):
            raise forms.ValidationError(gettext("Usa un enlace HTTP o HTTPS."))
        return value

    def clean(self):
        data = super().clean()
        if not (data.get("body") or data.get("project_url") or data.get("attachment")):
            raise forms.ValidationError(gettext("Añade tu solución, un enlace o un archivo antes de enviar."))
        return data


class ReviewForm(forms.Form):
    met_criteria = forms.MultipleChoiceField(label=gettext_lazy("Criterios cumplidos"), required=False, widget=forms.CheckboxSelectMultiple)
    outcome = forms.ChoiceField(label=gettext_lazy("Resultado"), choices=PracticeReview._meta.get_field("outcome").choices)
    feedback = forms.CharField(label=gettext_lazy("Retroalimentación y siguiente paso"), max_length=5000, widget=forms.Textarea(attrs={"rows": 6}))

    def __init__(self, *args, practice, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["met_criteria"].choices = [(str(i), criterion) for i, criterion in enumerate(practice.criteria)]

    def clean(self):
        data = super().clean()
        if data.get("outcome") == "accepted" and len(data.get("met_criteria", [])) != len(self.fields["met_criteria"].choices):
            raise forms.ValidationError(gettext("Marca todos los criterios cumplidos para aprobar, o solicita cambios explicando qué falta."))
        return data

