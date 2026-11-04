from django import forms
from django.utils.translation import gettext, gettext_lazy

from .models import LearningPath


class PathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ("title", "summary", "description", "bundle_percent", "published")
        labels = {"title": gettext_lazy("Título"), "summary": gettext_lazy("Resumen"), "description": gettext_lazy("Qué lograrás al terminar"),
                  "bundle_percent": gettext_lazy("Descuento del paquete (%)"), "published": gettext_lazy("Publicar la ruta")}
        help_texts = {"summary": gettext_lazy("Una o dos frases para la tarjeta de la ruta."),
                      "bundle_percent": gettext_lazy("Entre 0 y 50. Con 0, cada curso se compra por separado."),
                      "published": gettext_lazy("Necesita al menos dos cursos y uno obligatorio.")}
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


def parse_steps(data, courses):
    """Selected courses with their order, optional flag and note, from one row per own course."""
    chosen, errors = [], []
    for course in courses:
        if data.get(f"curso-{course.pk}") != "on":
            continue
        try:
            order = int(data.get(f"orden-{course.pk}") or 0)
        except ValueError:
            order = 0
        note = " ".join(str(data.get(f"nota-{course.pk}", "")).split())
        if len(note) > 240:
            errors.append((gettext('La nota de «%(title)s» admite hasta 240 caracteres.') % {"title": course.title}))
        chosen.append({"course": course, "order": order if order > 0 else 999, "optional": data.get(f"opcional-{course.pk}") == "on", "note": note[:240]})
    chosen.sort(key=lambda item: (item["order"], item["course"].title))
    return chosen, errors
