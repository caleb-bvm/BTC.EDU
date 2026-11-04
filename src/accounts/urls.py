"""Student password reset and account settings routes."""
from .recovery import recovery_patterns
from .settings_urls import settings_patterns

urlpatterns = [*recovery_patterns(), *settings_patterns()]
