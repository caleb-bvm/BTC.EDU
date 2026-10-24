from django import forms

from .catalog import target_choices


class OfferForm(forms.Form):
    target = forms.ChoiceField(label="Qué incluye", choices=())
    title = forms.CharField(label="Nombre de la oferta", max_length=200)
    amount_sats = forms.IntegerField(label="Precio en sats", min_value=1, max_value=100000,
        help_text="Para cambiar el precio después, prepara una nueva oferta. Las facturas pendientes conservarán el importe original.")

    def __init__(self, *args, actor, course=None, resource=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target"].choices = [("", "Elige un contenido publicado")] + target_choices(actor, course, resource)
        self.fields["target"].help_text = "Solo aparece contenido publicado que puedes ofrecer. El precio y las inclusiones se revisan antes de la venta."
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


class CouponForm(forms.Form):
    code = forms.RegexField(label="Código", regex=r"^[A-Za-z0-9-]{4,24}$", max_length=24,
                            help_text="Entre 4 y 24 letras, números o guiones. Los estudiantes lo escriben al revisar su compra.",
                            error_messages={"invalid": "Usa entre 4 y 24 letras, números o guiones."})
    kind = forms.ChoiceField(label="Tipo de descuento", choices=(("percent", "Porcentaje"), ("amount", "Cantidad en sats")))
    value = forms.IntegerField(label="Descuento", min_value=1, max_value=100000,
                               help_text="Hasta 90 % o 100 000 sats. Cada artículo conserva al menos 1 sat.")
    course = forms.ChoiceField(label="Aplica a", required=False, choices=())
    starts_at = forms.DateTimeField(label="Desde", widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"))
    expires_at = forms.DateTimeField(label="Vence", widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"))
    max_uses = forms.IntegerField(label="Usos disponibles", min_value=1, max_value=10000, initial=50,
                                  help_text="Cuenta los pedidos pagados o pendientes que usan el cupón.")

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        from .pricing import coupon_scope_choices
        self.fields["course"].choices = coupon_scope_choices(actor)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean(self):
        data = super().clean()
        if data.get("kind") == "percent" and data.get("value") and data["value"] > 90:
            self.add_error("value", "El porcentaje máximo es 90 %.")
        if data.get("starts_at") and data.get("expires_at") and data["expires_at"] <= data["starts_at"]:
            self.add_error("expires_at", "La fecha de vencimiento debe ser posterior al inicio.")
        return data


class TipForm(forms.Form):
    amount = forms.IntegerField(label="Importe en sats", min_value=10, max_value=100000, initial=500)
    message = forms.CharField(label="Mensaje para el educador", required=False, max_length=280,
                              widget=forms.Textarea(attrs={"rows": 3, "maxlength": 280}),
                              help_text="Opcional. Solo lo lee el educador.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RefundForm(forms.Form):
    reason = forms.CharField(label="Motivo", min_length=10, max_length=1000, widget=forms.Textarea(attrs={"rows": 4}))
    payment_request = forms.CharField(label="Factura Lightning para recibir el reembolso", max_length=2000,
                                      widget=forms.Textarea(attrs={"rows": 3, "spellcheck": "false", "autocomplete": "off"}))

    def __init__(self, *args, amount=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_request"].help_text = f"Crea en tu wallet una factura por exactamente {amount} sats y pégala aquí."
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RefundDecisionForm(forms.Form):
    decision = forms.ChoiceField(label="Decisión", choices=(("approve", "Aprobar y pagar"), ("reject", "Rechazar")))
    note = forms.CharField(label="Nota para el estudiante", required=False, max_length=500, widget=forms.Textarea(attrs={"rows": 3}))
    payment_hash = forms.RegexField(label="Hash del pago confirmado", regex=r"^[a-fA-F0-9]{64}$", required=False,
                                    help_text="Solo para cerrar un reembolso por conciliar que ya consta en la wallet.")

    def clean(self):
        data = super().clean()
        if data.get("decision") == "reject" and not data.get("note", "").strip():
            self.add_error("note", "Explica por qué no procede el reembolso.")
        return data
