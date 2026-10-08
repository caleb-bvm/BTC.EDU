"""Loopback-only disposable assessment preview; never uses the primary database."""
# ruff: noqa: E402
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
temporary = tempfile.TemporaryDirectory(prefix="assessment-preview-", dir=ROOT / ".local")
preview_path = Path(temporary.name).resolve()
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

from creators.services import decide, submit
from learning.models import QuizDraft
from learning.services import enroll

settings.MEDIA_ROOT = preview_path / "media"
settings.ACADEMY_PREVIEW = True
settings.SESSION_COOKIE_NAME = "assessment_preview_session"
settings.CSRF_COOKIE_NAME = "assessment_preview_csrf"
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
    QuizDraft.objects.create(lesson=data.free, title="Comprueba el recorrido", max_attempts=2, questions=[
        {"prompt": "¿Cuándo se concede el acceso al contenido de pago?", "multiple": False, "options": ["Al crear una factura", "Cuando el servidor confirma el pago", "Al cerrar el navegador"], "correct": [1], "explanation": "La factura pendiente reserva las condiciones. El servidor comprueba el pago antes de conceder acceso."},
        {"prompt": "¿Qué debe conservar una factura? Selecciona todas las respuestas correctas.", "multiple": True, "options": ["El precio acordado", "Las revisiones incluidas", "La contraseña del alumno"], "correct": [0, 1], "explanation": "Precio y revisiones identifican lo comprado. La contraseña no forma parte de la factura."},
    ])
    submission = submit(data.course, data.creator)
    decide(submission, data.reviewer, True)
    version = submission.course_version
    version.refresh_from_db()
    enroll(data.student, version)
    roles.update(estudiante=data.student, creador=data.creator, revisor=data.reviewer)
    quiz = version.chapters.first().lessons.first().quiz
    print(f"Alumno: http://127.0.0.1:8015/aprendizaje/evaluaciones/{quiz.pk}/?vista=estudiante", flush=True)
    print(f"Editor: http://127.0.0.1:8015/crear/lecciones/{data.free.pk}/evaluacion/?vista=creador", flush=True)
    print(f"Revisión: http://127.0.0.1:8015/crear/revision/{submission.pk}/?vista=revisor", flush=True)
    call_command("runserver", "127.0.0.1:8015", use_reloader=False)
finally:
    connections.close_all()
    temporary.cleanup()
