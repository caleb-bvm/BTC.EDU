"""Exercise independent SQLite connections against disposable community data."""
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="community-concurrency-", dir=ROOT / ".local") as directory:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        from django.core.exceptions import PermissionDenied, ValidationError
        from django.core.management import call_command
        from django.db import connections

        from content.models import Chapter, Course, Lesson, VersionLesson
        from content.publication import publish_course
        from content.testing import EDUCATION_FIXTURE
        from creators.models import CreatorProfile
        from learning.community import (
            follow_thread,
            moderate,
            post_message,
            report_message,
        )
        from learning.models import (
            CommunityDecision,
            CommunityPost,
            CommunityReport,
            CommunitySubscription,
            Notification,
        )
        from learning.services import enroll

        call_command("migrate", verbosity=0)
        users = get_user_model().objects
        creator = users.create_user("creator@community-race.invalid", account_type="creator")
        CreatorProfile.objects.create(user=creator, display_name="Docente", status="approved")
        student = users.create_user("student@community-race.invalid")
        admin = users.create_superuser("admin@community-race.invalid")
        course = Course.objects.create(creator=creator, title="Comunidad", description="Concurrencia")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Lección", body="Texto", status="published")
        version = publish_course(course, admin)
        enroll(student, version)

        def parallel(function):
            barrier = Barrier(2)
            def worker(index):
                connections.close_all()
                try:
                    barrier.wait(timeout=10)
                    return function(index)
                finally:
                    connections.close_all()
            with ThreadPoolExecutor(max_workers=2) as executor:
                return list(executor.map(worker, range(2)))

        def actor(user):
            return users.get(pk=user.pk)

        def reply_or_suspend(index, root):
            try:
                if index:
                    moderate(actor(creator), version, "suspend", "Pausa", student_id=student.pk)
                else:
                    post_message(actor(student), version, "Respuesta concurrente", uuid4(), root.pk)
                return "accepted"
            except (PermissionDenied, ValidationError):
                return "blocked"

        try:
            key = uuid4()
            posts = parallel(lambda index: post_message(actor(student), version, "Tema", key).pk)
            assert posts[0] == posts[1] and CommunityPost.objects.count() == 1
            reports = parallel(lambda index: report_message(actor(student), posts[0], "Revisar").pk)
            assert reports[0] == reports[1] and CommunityReport.objects.count() == 1
            parallel(lambda index: moderate(actor(creator), version, "hide", "Revisión", posts[0]))
            assert CommunityDecision.objects.count() == 1
            root = post_message(actor(creator), version, "Otro tema", uuid4())
            parallel(lambda index: follow_thread(actor(student), root.pk, True))
            assert CommunitySubscription.objects.filter(thread=root, user=student).count() == 1
            parallel(lambda index: reply_or_suspend(index, root))
            before = CommunityPost.objects.count()
            try:
                post_message(actor(student), version, "Tras suspensión", uuid4(), root.pk)
                raise AssertionError("Suspended participant was allowed to write")
            except PermissionDenied:
                pass
            assert CommunityPost.objects.count() == before
            moderate(actor(creator), version, "restore", "Continuar pruebas", student_id=student.pk)
            lesson = VersionLesson.objects.get(chapter__version=version)
            lesson_key = uuid4()
            lesson_posts = parallel(lambda index: post_message(actor(student), version, "Duda de lección", lesson_key, lesson_id=lesson.pk).pk)
            assert lesson_posts[0] == lesson_posts[1]
            assert Notification.objects.filter(event_key=f"community-lesson:{lesson_posts[0]}").count() == 1
            reply_key = uuid4()
            replies = parallel(lambda index: post_message(actor(creator), version, "Respuesta de lección", reply_key, lesson_posts[0]).pk)
            assert replies[0] == replies[1]
            assert CommunityPost.objects.get(pk=replies[0]).lesson_id == lesson.pk
            assert Notification.objects.filter(event_key=f"community-reply:{replies[0]}").count() == 1
            print("OK: publicaciones y reportes únicos, moderación y seguimiento sin duplicados, suspensión aplicada y comentarios/respuestas de lección con avisos únicos en conexiones SQLite independientes.")
        finally:
            connections.close_all()


if __name__ == "__main__":
    run()
