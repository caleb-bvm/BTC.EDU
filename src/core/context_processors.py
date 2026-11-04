"""Environment flags available to templates."""
from django.conf import settings


def academy_preview(request):
    """Flags for preview and simulated payment environments."""
    return {"academy_preview": getattr(settings, "ACADEMY_PREVIEW", False),
            "payment_test_environment": settings.COMMERCE_SIMULATION}
