"""Independent, disposable preview with real FakeWallet invoices and no passwords."""
# Django model imports must follow setup against the temporary database.
# ruff: noqa: E402
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
preview_dir = tempfile.TemporaryDirectory(prefix="commerce-preview-", dir=ROOT / ".local")
preview_path = Path(preview_dir.name).resolve()
assert preview_path.is_relative_to((ROOT / ".local").resolve())
os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
os.environ["DJANGO_DB_PATH"] = str(preview_path / "platform.sqlite3")

import django

django.setup()

from demo_commerce import seed
from django.conf import settings
from django.contrib.auth import login, logout
from django.core.management import call_command
from django.db import connections
from django.http import HttpResponseRedirect

from commerce.services import ensure_emitted, reserve_invoice, simulate_payment
from learning.models import Enrollment
from learning.services import save_progress

settings.MEDIA_ROOT = preview_path / "media"
settings.ACADEMY_PREVIEW = True
settings.SESSION_COOKIE_NAME = "commerce_preview_session"
settings.CSRF_COOKIE_NAME = "commerce_preview_csrf"
settings.SESSION_COOKIE_SECURE = False
settings.CSRF_COOKIE_SECURE = False
settings.SECURE_SSL_REDIRECT = False
settings.MIDDLEWARE.append("__main__.PreviewRoles")
roles = {}


class PreviewRoles:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        role = request.GET.get("vista")
        if role == "publico":
            logout(request)
            return HttpResponseRedirect(request.path)
        if role in roles:
            login(request, roles[role], backend="accounts.backends.AccountBackend")
            return HttpResponseRedirect(request.path)
        return self.get_response(request)


try:
    call_command("migrate", verbosity=0)
    data = seed()
    roles.update(estudiante=data.student, pendiente=data.other, creador=data.creator, revisor=data.reviewer)
    paid = ensure_emitted(reserve_invoice(data.student, data.bundle.pk))
    paid = simulate_payment(data.student, paid)
    enrollment = Enrollment.objects.get(student=data.student, version=data.version)
    save_progress(data.student, enrollment.pk, data.records[0].pk, 0, "complete")
    pending = ensure_emitted(reserve_invoice(data.other, data.bundle.pk))
    print("Vista temporal: http://127.0.0.1:8014/cursos/1/", flush=True)
    print("Biblioteca: http://127.0.0.1:8014/mi-espacio/?vista=estudiante", flush=True)
    print(f"Factura pendiente: http://127.0.0.1:8014/facturas/{pending.pk}/?vista=pendiente", flush=True)
    print(f"Compra confirmada: http://127.0.0.1:8014/facturas/{paid.pk}/?vista=estudiante", flush=True)
    print("Ofertas: http://127.0.0.1:8014/crear/ofertas/?vista=creador", flush=True)
    call_command("runserver", "127.0.0.1:8014", use_reloader=False)
finally:
    connections.close_all()
    preview_dir.cleanup()
