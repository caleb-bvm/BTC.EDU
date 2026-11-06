"""System checks for the account mail configuration."""
from django.conf import settings
from django.core.checks import Tags, Warning, register


@register(Tags.security, deploy=True)
def account_delivery_configuration(app_configs, **kwargs):
    """Warn when account mail uses a local backend or an unverified SMTP sender."""
    issues = []
    if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
        issues.append(Warning("El correo de cuenta utiliza un backend local; no confirma entrega a un buzón real.", id="accounts.W001"))
    elif settings.EMAIL_HOST in ("localhost", "127.0.0.1") or settings.DEFAULT_FROM_EMAIL.endswith("@localhost"):
        issues.append(Warning("Verifica el proveedor SMTP y el remitente antes de abrir registros públicos.", id="accounts.W002"))
    return issues


@register(Tags.compatibility, deploy=True)
def legal_provider_configuration(app_configs, **kwargs):
    """Warn when the terms page cannot show who sells (consumer protection law, art. 21-A)."""
    missing = [field for field, value in settings.LEGAL_PROVIDER.items() if not value]
    if missing:
        return [Warning("Faltan datos del proveedor en los términos: " + ", ".join(missing) + ".",
                        hint="Define LEGAL_PROVIDER_NAME, _NIT, _ADDRESS, _PHONE y _EMAIL antes de cobrar con fondos reales.",
                        id="accounts.W003")]
    return []

