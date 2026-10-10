from uuid import uuid4

from django import forms

from content.models import Lesson


class CertificatePolicyForm(forms.Form):
    enabled = forms.BooleanField(label="Ofrecer certificado de finalización", required=False)
    required_lessons = forms.ModelMultipleChoiceField(label="Lecciones obligatorias", queryset=Lesson.objects.none(), required=False, widget=forms.CheckboxSelectMultiple)
    revision = forms.IntegerField(min_value=0, widget=forms.HiddenInput)

    def __init__(self, *args, course, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["required_lessons"].queryset = Lesson.objects.filter(chapter__course=course, chapter__status="published", status="published").order_by("chapter__position", "position", "pk")

    def clean(self):
        values = super().clean()
        if values.get("enabled") and not values.get("required_lessons"):
            self.add_error("required_lessons", "Selecciona al menos una lección obligatoria.")
        return values


class CertificateNameForm(forms.Form):
    student_name = forms.CharField(label="Nombre que aparecerá en el certificado", max_length=150)
    confirm_name = forms.BooleanField(label="Confirmo que este nombre es correcto. El certificado emitido conservará este nombre.")


class MessageForm(forms.Form):
    body = forms.CharField(label="Tu mensaje", max_length=2000, widget=forms.Textarea(attrs={"rows": 5}))
    request_key = forms.UUIDField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["request_key"] = uuid4()
