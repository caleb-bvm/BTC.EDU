"""Community UI preview using a disposable database and synthetic accounts."""
import json
import os
import sys
import tempfile
from pathlib import Path
from uuid import uuid4
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="community-preview-", dir=ROOT / ".local") as directory:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        os.environ["DJANGO_DEBUG"] = "true"
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        from django.core.management import call_command
        from django.core.wsgi import get_wsgi_application

        from content.models import Chapter, Course, Lesson
        from content.publication import publish_course
        from creators.models import CreatorProfile
        from learning.community import post_message, report_message
        from learning.services import enroll

        call_command("migrate", verbosity=0)
        users = get_user_model().objects
        creator = users.create_user("creator@community.invalid", password="CommunityQA_42!", account_type="creator", first_name="Ana")
        CreatorProfile.objects.create(user=creator, display_name="Ana López", status="approved")
        student = users.create_user("student@community.invalid", password="CommunityQA_42!", first_name="Lucía")
        admin = users.create_superuser("admin@community.invalid", password="CommunityQA_42!")
        course = Course.objects.create(creator=creator, title="Fundamentos de micropagos", description="Aprende y comparte")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        Lesson.objects.create(chapter=chapter, title="Introducción", body="Texto educativo", status="published")
        version = publish_course(course, admin)
        enroll(student, version)
        root = post_message(student, version, "¿Cómo explicarías la diferencia entre comprar una lección y comprar el curso completo?", uuid4())
        post_message(creator, version, "Una lección permite resolver una necesidad concreta. Revisa siempre los materiales incluidos antes de elegir.", uuid4(), root.pk)
        report_message(student, root.pk, "Reporte de prueba para recorrer la moderación")
        metadata = {"directory": directory, "version": version.pk, "thread": root.pk}
        (ROOT / ".local/community-preview.json").write_text(json.dumps(metadata), encoding="utf-8")
        print("Vista temporal: http://127.0.0.1:8019/aprendizaje/comunidad/", flush=True)
        print(json.dumps(metadata), flush=True)
        with make_server("127.0.0.1", 8019, StaticFilesHandler(get_wsgi_application())) as server:
            server.serve_forever()


if __name__ == "__main__":
    run()
