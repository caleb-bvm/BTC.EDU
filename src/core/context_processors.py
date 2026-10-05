from django.conf import settings


def academy_preview(request):
    return {"academy_preview": getattr(settings, "ACADEMY_PREVIEW", False),
            "payment_test_environment": settings.COMMERCE_SIMULATION}
