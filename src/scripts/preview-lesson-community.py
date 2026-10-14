"""Review lesson conversations using a disposable database and synthetic accounts."""
import json
import os
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path
from uuid import uuid4
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="lesson-community-preview-", dir=ROOT / ".local") as directory, ExitStack() as cleanup:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        os.environ["DJANGO_DEBUG"] = "true"
        import django
        django.setup()
        from django.conf import settings
        settings.SESSION_COOKIE_NAME = "lesson_community_preview_session"
        settings.CSRF_COOKIE_NAME = "lesson_community_preview_csrf"
        from django.contrib.auth import get_user_model
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        from django.core.management import call_command
        from django.core.wsgi import get_wsgi_application
        from django.db import connections
        cleanup.callback(connections.close_all)

        from content.models import Chapter, Course, Lesson, VersionLesson
        from content.publication import publish_course
        from content.testing import EDUCATION_FIXTURE
        from creators.models import CreatorProfile
        from learning.community import post_message
        from learning.lesson_discussion import lesson_url
        from learning.services import enroll

        call_command("migrate", verbosity=0)
        users = get_user_model().objects
        creator = users.create_user("creator@lesson.invalid", password="LessonQA_42!", account_type="creator")
        CreatorProfile.objects.create(user=creator, display_name="Ana López", status="approved")
        student = users.create_user("student@lesson.invalid", password="LessonQA_42!", display_name="Lucía")
        peer = users.create_user("peer@lesson.invalid", password="LessonQA_42!", display_name="Luis")
        admin = users.create_superuser("admin@lesson.invalid", password="LessonQA_42!")
        course = Course.objects.create(creator=creator, title="Bitcoin a tu ritmo", description="Comprende cómo funcionan los pagos y comparte lo que aprendes.")
        chapter = Chapter.objects.create(course=course, title="Primeros pasos", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="¿Qué hace diferente a Bitcoin?", body="Bitcoin permite transferir valor entre personas.\n\nCada pago puede verificarse sin depender de una sola institución.\n\nAntes de avanzar, piensa en una situación en la que te gustaría pagar por un contenido específico.", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, position=2, title="Entender Lightning", body="Contenido protegido de la segunda lección.", access_type="paid", status="published")
        version = publish_course(course, admin)
        for user in (student, peer):
            enroll(user, version)
        lessons = list(VersionLesson.objects.filter(chapter__version=version))
        root = post_message(peer, version, "¿Cómo se comprueba un pago sin depender de un banco?", uuid4(), lesson_id=lessons[0].pk)
        post_message(creator, version, "La red verifica las reglas de la transacción. En la siguiente lección veremos cómo se relaciona esto con Lightning.", uuid4(), root.pk)
        metadata = {"directory": directory, "version": version.pk, "lesson_url": lesson_url(version, lessons[0].pk), "locked_url": lesson_url(version, lessons[1].pk), "thread": root.pk}
        (ROOT / ".local/lesson-community-preview.json").write_text(json.dumps(metadata), encoding="utf-8")
        print(json.dumps(metadata), flush=True)
        with make_server("127.0.0.1", 8021, StaticFilesHandler(get_wsgi_application())) as server:
            server.serve_forever()


if __name__ == "__main__":
    run()
