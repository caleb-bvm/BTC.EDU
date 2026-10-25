from django import forms

from .models import LearningPath


class PathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = ("title", "summary", "description", "bundle_percent", "published")
        labels = {"title": "Título", "summary": "Resumen", "description": "Qué lograrás al terminar",
                  "bundle_percent": "Descuento del paquete (%)", "published": "Publicar la ruta"}
        help_texts = {"summary": "Una o dos frases para la tarjeta de la ruta.",
                      "bundle_percent": "Entre 0 y 50. Con 0, cada curso se compra por separado.",
                      "published": "Necesita al menos dos cursos y uno obligatorio."}
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
            errors.append(f"La nota de «{course.title}» admite hasta 240 caracteres.")
        chosen.append({"course": course, "order": order if order > 0 else 999, "optional": data.get(f"opcional-{course.pk}") == "on", "note": note[:240]})
    chosen.sort(key=lambda item: (item["order"], item["course"].title))
    return chosen, errors
