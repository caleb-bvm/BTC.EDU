from django import forms

from .catalog import target_choices


class OfferForm(forms.Form):
    target = forms.ChoiceField(label="Qué incluye", choices=())
    title = forms.CharField(label="Nombre de la oferta", max_length=200)
    amount_sats = forms.IntegerField(label="Precio en sats de prueba", min_value=1, max_value=100000,
        help_text="Importe simulado. Para cambiarlo después, crea otra oferta y retira la anterior.")

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target"].choices = target_choices(actor)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class OfferReviewForm(forms.Form):
    decision = forms.ChoiceField(label="Decisión", choices=(("approve", "Aprobar oferta"), ("changes", "Solicitar cambios")))
    feedback = forms.CharField(label="Observaciones", required=False, widget=forms.Textarea(attrs={"rows": 4}))

    def clean(self):
        data = super().clean()
        if data.get("decision") == "changes" and not data.get("feedback", "").strip():
            self.add_error("feedback", "Explica qué debe corregir el creador.")
        return data
