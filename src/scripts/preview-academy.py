"""Vista local con registros temporales, separada de la base del usuario."""
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

preview_file = tempfile.NamedTemporaryFile(prefix="academy-preview-", suffix=".sqlite3", dir=SRC_ROOT / ".local", delete=False)
preview_path = Path(preview_file.name).resolve()
preview_file.close()
settings.DATABASES["default"]["NAME"] = preview_path
settings.ACADEMY_PREVIEW = True
settings.TEMPLATES[0]["APP_DIRS"] = False
settings.TEMPLATES[0]["OPTIONS"]["loaders"] = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.db import connections  # noqa: E402

from content.models import (  # noqa: E402
    AccessType,
    Chapter,
    Course,
    CourseKind,
    CourseLevel,
    ExternalReference,
    Lesson,
    Material,
    PublicationStatus,
    Topic,
    Video,
)


def populate():
    creator = get_user_model().objects.create_user("preview@example.invalid", first_name="Equipo", last_name="BTC.EDU")
    topics = {name: Topic.objects.create(name=name, slug=slug) for name, slug in (("Bitcoin", "bitcoin"), ("Seguridad", "seguridad"), ("Desarrollo", "desarrollo"))}
    examples = (
        ("Bitcoin desde sus fundamentos", "Bitcoin", CourseLevel.BEGINNER, 90, "Comprende las ideas que hacen posible Bitcoin y construye una base para seguir aprendiendo.", False),
        ("Tu primera wallet", "Bitcoin", CourseLevel.BEGINNER, 60, "Conoce cómo se organiza una wallet y los conceptos que necesitas antes de dar tus primeros pasos.", False),
        ("Un nodo, paso a paso", "Bitcoin", CourseLevel.INTERMEDIATE, 120, "Explora la estructura de un nodo y las herramientas para entender cómo participa en la red.", True),
        ("Cuida tu entorno digital", "Seguridad", CourseLevel.BEGINNER, 75, "Organiza tus hábitos de seguridad y reconoce situaciones que requieren más cuidado.", False),
        ("Privacidad por diseño", "Seguridad", CourseLevel.INTERMEDIATE, 110, "Analiza cómo tomar decisiones de privacidad al construir y utilizar herramientas digitales.", True),
        ("Construye con Python", "Desarrollo", CourseLevel.BEGINNER, 180, "Aprende las piezas de un programa y practica con pequeñas herramientas que puedes ampliar.", False),
    )
    for title, topic, level, minutes, description, mixed in examples:
        course = Course.objects.create(creator=creator, title=title, description=description, topic=topics[topic], level=level, estimated_minutes=minutes, objective="Comprender los conceptos principales y aplicarlos en una actividad práctica.", requirements="Curiosidad, un navegador y tiempo para practicar.", status=PublicationStatus.PUBLISHED)
        chapter = Chapter.objects.create(course=course, title="Una base para empezar", status=PublicationStatus.PUBLISHED)
        for position, lesson_title in enumerate(("El punto de partida", "Conecta las piezas", "Llévalo a la práctica"), 1):
            Lesson.objects.create(chapter=chapter, position=position, title=lesson_title, description="Construye sobre lo que ya sabes y explora una idea a la vez.", body="Esta es una lección de demostración para revisar la lectura de BTC.EDU.\n\nAprender empieza con observar las piezas: qué hace cada una, cómo se relacionan y qué decisiones puedes tomar con ellas.\n\nTómate un momento para escribir lo que esperas aprender. Vuelve a esa pregunta cuando termines este recorrido.\n\nEstos registros son temporales y no forman parte del catálogo real.", access_type=AccessType.PAID if mixed and position == 3 else AccessType.FREE, status=PublicationStatus.PUBLISHED)
    for title, topic, level in (("Prepara tu espacio de trabajo", "Desarrollo", CourseLevel.BEGINNER), ("Organiza una copia de seguridad", "Seguridad", CourseLevel.BEGINNER), ("Lee la información de tu nodo", "Bitcoin", CourseLevel.INTERMEDIATE)):
        tutorial = Course.objects.create(creator=creator, title=title, description="Una guía práctica para completar una tarea y entender cada decisión del recorrido.", kind=CourseKind.TUTORIAL, topic=topics[topic], level=level, estimated_minutes=20, objective="Completar una tarea práctica siguiendo los pasos.", status=PublicationStatus.PUBLISHED)
        chapter = Chapter.objects.create(course=tutorial, title="Paso a paso", status=PublicationStatus.PUBLISHED)
        Lesson.objects.create(chapter=chapter, title="Antes de empezar", body="Contenido temporal para revisar cómo se lee un tutorial.", status=PublicationStatus.PUBLISHED)
    Video.objects.create(creator=creator, title="Las piezas de una red", description="Ficha temporal de un video. La reproducción todavía no está disponible.", topic=topics["Bitcoin"], status=PublicationStatus.PUBLISHED)
    Material.objects.create(creator=creator, title="Guía de práctica", description="Ficha temporal de un material. La descarga todavía no está disponible.", topic=topics["Desarrollo"], status=PublicationStatus.PUBLISHED)
    ExternalReference.objects.create(title="Referencia de lectura", description="Ejemplo temporal de una fuente externa curada.", source_name="Fuente de demostración", source_url="https://example.org/", topic=topics["Seguridad"], status=PublicationStatus.PUBLISHED)


try:
    call_command("migrate", verbosity=0)
    populate()
    print("Vista previa: http://127.0.0.1:8012/cursos/ — datos temporales, sin contenido en tu base.", flush=True)
    call_command("runserver", "127.0.0.1:8012", use_reloader=False)
finally:
    connections.close_all()
    preview_path.unlink(missing_ok=True)
