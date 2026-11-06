"""Forms for offers, coupons, tips and refunds."""
from django import forms
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext, gettext_lazy

from .catalog import target_choices


class OfferForm(forms.Form):
    target = forms.ChoiceField(label=gettext_lazy("Qué incluye"), choices=())
    title = forms.CharField(label=gettext_lazy("Nombre de la oferta"), max_length=200)
    amount_sats = forms.IntegerField(label=gettext_lazy("Precio en sats"), min_value=1, max_value=100000,
        help_text=gettext_lazy("Para cambiar el precio después, prepara una nueva oferta. Las facturas pendientes conservarán el importe original."))

    def __init__(self, *args, actor, course=None, resource=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target"].choices = [("", gettext("Elige un contenido publicado"))] + target_choices(actor, course, resource)
        self.fields["target"].help_text = gettext("Solo aparece contenido publicado que puedes ofrecer. Un curso o capítulo necesita antes una oferta individual para cada lección de pago. El precio y las inclusiones se revisan antes de la venta.")
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class OfferReviewForm(forms.Form):
    decision = forms.ChoiceField(label=gettext_lazy("Decisión"), choices=(("approve", gettext_lazy("Aprobar oferta")), ("changes", gettext_lazy("Solicitar cambios"))))
    feedback = forms.CharField(label=gettext_lazy("Observaciones"), required=False, widget=forms.Textarea(attrs={"rows": 4}))

    def clean(self):
        data = super().clean()
        if data.get("decision") == "changes" and not data.get("feedback", "").strip():
            self.add_error("feedback", gettext("Explica qué debe corregir el creador."))
        return data


class CouponForm(forms.Form):
    code = forms.RegexField(label=gettext_lazy("Código"), regex=r"^[A-Za-z0-9-]{4,24}$", max_length=24,
                            help_text=gettext_lazy("Entre 4 y 24 letras, números o guiones. Los estudiantes lo escriben al revisar su compra."),
                            error_messages={"invalid": gettext_lazy("Usa entre 4 y 24 letras, números o guiones.")})
    kind = forms.ChoiceField(label=gettext_lazy("Tipo de descuento"), choices=(("percent", gettext_lazy("Porcentaje")), ("amount", gettext_lazy("Cantidad en sats"))))
    value = forms.IntegerField(label=gettext_lazy("Descuento"), min_value=1, max_value=100000,
                               help_text=gettext_lazy("Hasta 90 % o 100 000 sats. Cada artículo conserva al menos 1 sat."))
    course = forms.ChoiceField(label=gettext_lazy("Aplica a"), required=False, choices=())
    starts_at = forms.DateTimeField(label=gettext_lazy("Desde"), widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"))
    expires_at = forms.DateTimeField(label=gettext_lazy("Vence"), widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"))
    max_uses = forms.IntegerField(label=gettext_lazy("Usos disponibles"), min_value=1, max_value=10000, initial=50,
                                  help_text=gettext_lazy("Cuenta los pedidos pagados o pendientes que usan el cupón."))

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        from .pricing import coupon_scope_choices
        self.fields["course"].choices = coupon_scope_choices(actor)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean(self):
        data = super().clean()
        if data.get("kind") == "percent" and data.get("value") and data["value"] > 90:
            self.add_error("value", gettext("El porcentaje máximo es 90 %."))
        if data.get("starts_at") and data.get("expires_at") and data["expires_at"] <= data["starts_at"]:
            self.add_error("expires_at", gettext("La fecha de vencimiento debe ser posterior al inicio."))
        return data


class TipForm(forms.Form):
    amount = forms.IntegerField(label=gettext_lazy("Importe en sats"), min_value=10, max_value=100000, initial=500)
    message = forms.CharField(label=gettext_lazy("Mensaje para el educador"), required=False, max_length=280,
                              widget=forms.Textarea(attrs={"rows": 3, "maxlength": 280}),
                              help_text=gettext_lazy("Opcional. Solo lo lee el educador."))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RefundForm(forms.Form):
    kind = forms.ChoiceField(label=gettext_lazy("Qué ocurrió"), widget=forms.RadioSelect)
    reason = forms.CharField(label=gettext_lazy("Motivo"), min_length=10, max_length=1000, widget=forms.Textarea(attrs={"rows": 4}))
    payment_request = forms.CharField(label=gettext_lazy("Factura Lightning para recibir el reembolso"), max_length=2000,
                                      widget=forms.Textarea(attrs={"rows": 3, "spellcheck": "false", "autocomplete": "off"}))

    def __init__(self, *args, amount=0, claim=False, **kwargs):
        from .models import Refund
        super().__init__(*args, **kwargs)
        if claim:
            self.fields["kind"].choices = [choice for choice in Refund.Kind.choices if choice[0] != Refund.Kind.WITHDRAWAL]
            self.fields["reason"].label = gettext_lazy("Describe el problema")
        else:
            del self.fields["kind"]
            self.fields["reason"].required = False
            self.fields["reason"].min_length = None
            self.fields["reason"].validators = [validator for validator in self.fields["reason"].validators
                                                if not isinstance(validator, MinLengthValidator)]
            self.fields["reason"].widget.attrs.pop("minlength", None)
            self.fields["reason"].label = gettext_lazy("Motivo (opcional)")
        self.fields["payment_request"].help_text = (gettext('Crea en tu wallet una factura por exactamente %(amount)s sats y pégala aquí.') % {"amount": amount})
        for name, field in self.fields.items():
            if name != "kind":
                field.widget.attrs["class"] = "form-control"


class RefundDecisionForm(forms.Form):
    decision = forms.ChoiceField(label=gettext_lazy("Decisión"), choices=(("approve", gettext_lazy("Aprobar y pagar")), ("reject", gettext_lazy("Rechazar"))))
    note = forms.CharField(label=gettext_lazy("Nota para el estudiante"), required=False, max_length=500, widget=forms.Textarea(attrs={"rows": 3}))
    payment_hash = forms.RegexField(label=gettext_lazy("Hash del pago confirmado"), regex=r"^[a-fA-F0-9]{64}$", required=False,
                                    help_text=gettext_lazy("Solo para cerrar un reembolso por conciliar que ya consta en la wallet."))

    def clean(self):
        data = super().clean()
        if data.get("decision") == "reject" and not data.get("note", "").strip():
            self.add_error("note", gettext("Explica por qué no procede el reembolso."))
        return data
