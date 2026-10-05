"""Estudio de creador con cuentas y almacenamiento temporales, solo en localhost."""
import os
import sys
import tempfile
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SRC_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform_config.settings")

import django  # noqa: E402
from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402

preview_dir = tempfile.TemporaryDirectory(prefix="creator-preview-", dir=SRC_ROOT / ".local")
settings.DATABASES["default"]["NAME"] = Path(preview_dir.name) / "preview.sqlite3"
settings.MEDIA_ROOT = Path(preview_dir.name) / "media"
settings.DEBUG = True
settings.SECURE_SSL_REDIRECT = False
settings.SESSION_COOKIE_SECURE = False
settings.CSRF_COOKIE_SECURE = False
settings.SESSION_COOKIE_NAME = "creator_preview_session"
settings.CSRF_COOKIE_NAME = "creator_preview_csrf"
settings.ACADEMY_PREVIEW = True
settings.MIDDLEWARE.append("__main__.PreviewCreatorMiddleware")
django.setup()

from django.contrib.auth import get_user_model, login  # noqa: E402
from django.core.files.uploadedfile import SimpleUploadedFile  # noqa: E402
from django.db import connections  # noqa: E402

from content.models import (  # noqa: E402
    Chapter,
    Course,
    Lesson,
    LessonResource,
    Material,
    Topic,
    Video,
)
from content.publication import publish_course, publish_resource  # noqa: E402
from creators.models import CreatorProfile  # noqa: E402
from creators.services import decide, submit  # noqa: E402
from media.models import Asset  # noqa: E402


class PreviewCreatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Quick role selection is explicit and exists only in this temporary
        # process. Ordinary login, logout and registration remain testable.
        role = request.GET.get("vista")
        if role in ("creador", "revisor"):
            email = "reviewer@example.invalid" if role == "revisor" else "creator@example.invalid"
            actor = get_user_model().objects.get(email=email)
            if request.user.pk != actor.pk:
                login(request, actor, backend="accounts.backends.AccountBackend")
        return self.get_response(request)


def populate():
    creator = get_user_model().objects.create_user("creator@example.invalid", first_name="Ana", last_name="López", account_type="creator")
    reviewer = get_user_model().objects.create_superuser("reviewer@example.invalid")
    CreatorProfile.objects.create(user=creator, display_name="Ana López", bio="Enseño tecnología con ejercicios y explicaciones paso a paso.", specialty="Bitcoin y desarrollo", status="approved")
    topic = Topic.objects.create(name="Bitcoin", slug="bitcoin")
    clip = Asset.objects.create(creator=creator, file=SimpleUploadedFile("video-de-prueba.mp4", (SRC_ROOT / "media/fixtures/white.mp4").read_bytes(), content_type="video/mp4"))
    captions = Asset.objects.create(creator=creator, file=SimpleUploadedFile("subtitulos.vtt", b"WEBVTT\n\n00:00.000 --> 00:05.000\nContenido temporal de prueba.\n", content_type="text/vtt"))
    guide = Asset.objects.create(creator=creator, file=SimpleUploadedFile("guia-de-practica.txt", b"Guia temporal: escribe tu objetivo y prepara una practica.", content_type="text/plain"))
    video = Video.objects.create(creator=creator, title="Una idea, paso a paso", description="Video temporal para comprobar carga, revisión y reproducción.", pending_asset=clip, pending_subtitles=captions, transcript="Esta es una transcripción de prueba.")
    material = Material.objects.create(creator=creator, title="Guía de práctica", description="Ejercicio temporal para acompañar la primera lección.", pending_asset=guide)
    for resource in (video, material):
        publish_resource(resource, reviewer)
    course = Course.objects.create(creator=creator, title="Bitcoin desde sus fundamentos", description="Comprende las piezas principales de Bitcoin y practica a tu ritmo.", objective="Explicar los conceptos básicos y relacionarlos con un ejemplo.", requirements="Curiosidad y un navegador.", topic=topic, level="beginner", estimated_minutes=90)
    chapter = Chapter.objects.create(course=course, title="Una base para empezar", status="published")
    lesson = Lesson.objects.create(chapter=chapter, title="El punto de partida", body="Antes de empezar, escribe lo que quieres aprender.\n\nObserva cada pieza y explica con tus palabras cómo se relaciona con las demás.", status="published")
    for position, resource in enumerate((video, material), 1):
        LessonResource.objects.create(lesson=lesson, resource=resource.revision, position=position)
    publish_course(course, reviewer)
    course.description = "Una nueva edición con práctica guiada y recursos reutilizables."
    course.save()
    submit(course, creator)
    draft = Course.objects.create(creator=creator, kind="tutorial", title="Prepara tu entorno de desarrollo", description="Completa una tarea concreta, paso a paso.")
    draft_chapter = Chapter.objects.create(course=draft, title="Primeros pasos", status="published")
    Lesson.objects.create(chapter=draft_chapter, title="Revisa tus herramientas", body="Comprueba tu navegador y organiza tus archivos de práctica.", status="published")
    returned = submit(draft, creator)
    decide(returned, reviewer, False, "Explica qué herramientas necesita el alumno antes de comenzar.")
    submit(video, creator)


try:
    call_command("migrate", verbosity=0)
    populate()
    print("Vista temporal: http://127.0.0.1:8013/para-creadores/ — ?vista=revisor / ?vista=creador ofrece entrada rápida solo en esta demostración.", flush=True)
    call_command("runserver", "127.0.0.1:8013", use_reloader=False)
finally:
    connections.close_all()
    preview_dir.cleanup()
