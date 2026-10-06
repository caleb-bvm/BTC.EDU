"""Configuración local y de despliegue, sin secretos en el repositorio."""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import dotenv_values, load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".local/commerce.env")
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise ImproperlyConfigured("Configura DJANGO_SECRET_KEY en src/.env.")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "accounts", "core", "content", "media", "creators", "commerce", "learning",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "platform_config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "core.context_processors.academy_preview",
    ]},
}]
WSGI_APPLICATION = "platform_config.wsgi.application"
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["accounts.backends.AccountBackend"]
# SQLite es el motor elegido para esta etapa local.
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.getenv("DJANGO_DB_PATH", str(BASE_DIR / ".local/platform.sqlite3")),
    "OPTIONS": {"timeout": 20},
}}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "es"
TIME_ZONE = "America/El_Salvador"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / ".local/staticfiles"
# No existe ruta pública de MEDIA: los contenidos de pago tendrán entrega autorizada.
MEDIA_ROOT = BASE_DIR / ".local/private-media"
CONTENT_MAX_UPLOAD_BYTES = 256 * 1024 * 1024
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/cuenta/entrar/"
LOGIN_REDIRECT_URL = "/mi-espacio/"
LOGOUT_REDIRECT_URL = "/"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# Only local, fictitious payments are supported by this integration.
COMMERCE_SIMULATION = os.getenv("COMMERCE_SIMULATION", "false").lower() == "true"
LNBITS_URL = os.getenv("LNBITS_URL", "http://127.0.0.1:5000")
_commerce_private = dotenv_values(BASE_DIR / ".local/commerce.env")
LNBITS_INVOICE_KEY = os.getenv("LNBITS_INVOICE_KEY") or _commerce_private.get("LNBITS_INVOICE_KEY", "")
LNBITS_PAYER_KEY = os.getenv("LNBITS_PAYER_KEY") or _commerce_private.get("LNBITS_PAYER_KEY", "")
LNBITS_ADMIN_TOKEN = os.getenv("LNBITS_ADMIN_TOKEN") or _commerce_private.get("LNBITS_ADMIN_TOKEN", "")
