from django.conf import settings
from django.core.checks import Tags, Warning, register


@register(Tags.security, deploy=True)
def account_delivery_configuration(app_configs, **kwargs):
    issues = []
    if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
        issues.append(Warning("El correo de cuenta utiliza un backend local; no confirma entrega a un buzón real.", id="accounts.W001"))
    elif settings.EMAIL_HOST in ("localhost", "127.0.0.1") or settings.DEFAULT_FROM_EMAIL.endswith("@localhost"):
        issues.append(Warning("Verifica el proveedor SMTP y el remitente antes de abrir registros públicos.", id="accounts.W002"))
    return issues
