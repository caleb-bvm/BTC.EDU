"""Loopback-only checkout demonstration with sample content and Polar invoices."""
# ruff: noqa: E402
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
temporary = tempfile.TemporaryDirectory(prefix="regtest-preview-", dir=ROOT / ".local")
preview = Path(temporary.name)
os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
os.environ["DJANGO_DB_PATH"] = str(preview / "platform.sqlite3")

import django

django.setup()

from demo_commerce import seed
from django.conf import settings
from django.contrib.auth import login
from django.core.management import call_command
from django.http import HttpResponseRedirect

from commerce.services import ensure_emitted, reserve_invoice

if settings.COMMERCE_PAYMENT_MODE != "regtest":
    raise SystemExit("Configura primero el comercio regtest.")
settings.MEDIA_ROOT = preview / "media"
settings.ACADEMY_PREVIEW = True
settings.SESSION_COOKIE_NAME = "regtest_preview_session"
settings.CSRF_COOKIE_NAME = "regtest_preview_csrf"
settings.SECURE_SSL_REDIRECT = False
settings.SESSION_COOKIE_SECURE = False
settings.CSRF_COOKIE_SECURE = False
settings.MIDDLEWARE.append("__main__.PreviewStudent")
student = None


class PreviewStudent:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.GET.get("vista") == "estudiante":
            login(request, student, backend="accounts.backends.AccountBackend")
            return HttpResponseRedirect(request.path)
        return self.get_response(request)


call_command("migrate", verbosity=0)
data = seed()
student = data.student
invoice = ensure_emitted(reserve_invoice(student, data.bundle.pk))
url = f"http://127.0.0.1:8016/facturas/{invoice.pk}/?vista=estudiante"
(ROOT / ".local/regtest-preview-url.txt").write_text(url, encoding="utf-8")
print("Compra de prueba: " + url, flush=True)
call_command("runserver", "127.0.0.1:8016", use_reloader=False)
