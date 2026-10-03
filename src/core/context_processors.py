from django.conf import settings


def academy_preview(request):
    return {"academy_preview": getattr(settings, "ACADEMY_PREVIEW", False)}
