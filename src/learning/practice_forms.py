from django import forms

from .models import PracticeReview
from .practices import validate_attachment


class PracticeForm(forms.Form):
    enabled = forms.BooleanField(label="Incluir práctica en la próxima versión", required=False)
    title = forms.CharField(label="Título", max_length=200)
    instructions = forms.CharField(label="Qué debe entregar el estudiante", max_length=10000, widget=forms.Textarea(attrs={"rows": 6}))
    criteria_text = forms.CharField(label="Criterios de aprobación", help_text="Un criterio concreto por línea; entre 1 y 12, hasta 300 caracteres cada uno.", widget=forms.Textarea(attrs={"rows": 5}))
    review_days = forms.IntegerField(label="Plazo previsto de revisión (días naturales)", initial=7, min_value=1, max_value=30,
        help_text="Cuenta desde cada entrega. El estudiante verá este plazo y los retrasos quedarán en tu bandeja.")
    revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def clean_criteria_text(self):
        criteria = [line.strip() for line in self.cleaned_data["criteria_text"].splitlines() if line.strip()]
        if not 1 <= len(criteria) <= 12 or any(len(line) > 300 for line in criteria):
            raise forms.ValidationError("Define entre 1 y 12 criterios de hasta 300 caracteres.")
        return criteria


class DeliveryForm(forms.Form):
    body = forms.CharField(label="Tu solución", required=False, max_length=10000, widget=forms.Textarea(attrs={"rows": 7, "placeholder": "Explica qué hiciste, el resultado y cómo comprobarlo."}))
    project_url = forms.URLField(label="Enlace al proyecto", required=False, max_length=500, assume_scheme="https",
        help_text="Comprueba que el educador pueda abrirlo. No incluyas contraseñas ni claves privadas.")
    attachment = forms.FileField(label="Archivo adjunto", required=False, help_text="Un PDF, ZIP, TXT en UTF-8, PNG o JPG. Máximo 10 MB.", widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.zip,.txt,.png,.jpg,.jpeg"}))
    request_key = forms.UUIDField(widget=forms.HiddenInput)
    previous_id = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def clean_attachment(self):
        upload = self.cleaned_data.get("attachment")
        validate_attachment(upload)
        return upload

    def clean_project_url(self):
        value = self.cleaned_data.get("project_url", "")
        if value and not value.lower().startswith(("https://", "http://")):
            raise forms.ValidationError("Usa un enlace HTTP o HTTPS.")
        return value

    def clean(self):
        data = super().clean()
        if not (data.get("body") or data.get("project_url") or data.get("attachment")):
            raise forms.ValidationError("Añade tu solución, un enlace o un archivo antes de enviar.")
        return data


class ReviewForm(forms.Form):
    met_criteria = forms.MultipleChoiceField(label="Criterios cumplidos", required=False, widget=forms.CheckboxSelectMultiple)
    outcome = forms.ChoiceField(label="Resultado", choices=PracticeReview._meta.get_field("outcome").choices)
    feedback = forms.CharField(label="Retroalimentación y siguiente paso", max_length=5000, widget=forms.Textarea(attrs={"rows": 6}))

    def __init__(self, *args, practice, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["met_criteria"].choices = [(str(i), criterion) for i, criterion in enumerate(practice.criteria)]

    def clean(self):
        data = super().clean()
        if data.get("outcome") == "accepted" and len(data.get("met_criteria", [])) != len(self.fields["met_criteria"].choices):
            raise forms.ValidationError("Marca todos los criterios cumplidos para aprobar, o solicita cambios explicando qué falta.")
        return data

