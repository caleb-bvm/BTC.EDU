"""Verify independent connections for credentials and private message retries."""
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
    with tempfile.TemporaryDirectory(prefix="essential-concurrency-", dir=ROOT / ".local") as temporary:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(temporary) / "platform.sqlite3")
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        from django.db import connections

        from content.models import Chapter, Course, Lesson
        from content.publication import publish_course
        from creators.models import CreatorProfile
        from learning.certificates import issue_certificate
        from learning.models import (
            Certificate,
            CertificateDraft,
            LessonQuestion,
            Notification,
            QuestionReply,
        )
        from learning.services import enroll, save_progress
        from learning.support import post_question, reply_question

        call_command("migrate", verbosity=0)
        users = get_user_model().objects
        creator = users.create_user("creator@race.invalid", account_type="creator")
        student = users.create_user("student@race.invalid")
        admin = users.create_superuser("admin@race.invalid")
        CreatorProfile.objects.create(user=creator, status="approved", display_name="Docente")
        course = Course.objects.create(creator=creator, title="Certificados", description="Concurrencia")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        lesson = Lesson.objects.create(chapter=chapter, title="Lección", body="Texto", status="published")
        policy = CertificateDraft.objects.create(course=course, enabled=True)
        policy.required_lessons.add(lesson)
        version = publish_course(course, admin)
        record = version.chapters.first().lessons.first()
        enrollment = enroll(student, version)
        save_progress(student, enrollment.pk, record.pk, 0, "complete")

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

        try:
            ids = parallel(lambda index: issue_certificate(users.get(pk=student.pk), enrollment.pk, "Alumno").pk)
            assert ids[0] == ids[1] and Certificate.objects.count() == 1
            from learning.certificate_integrity import certificate_intact
            assert certificate_intact(Certificate.objects.get(pk=ids[0]))
            assert Notification.objects.filter(event_key=f"certificate:{ids[0]}").count() == 1
            key = uuid4()
            questions = parallel(lambda index: post_question(users.get(pk=student.pk), record.pk, "Pregunta", key).pk)
            assert questions[0] == questions[1] and LessonQuestion.objects.count() == 1
            key = uuid4()
            replies = parallel(lambda index: reply_question(users.get(pk=creator.pk), questions[0], "Respuesta", key).pk)
            assert replies[0] == replies[1] and QuestionReply.objects.count() == 1
            assert Notification.objects.filter(event_key=f"reply:{replies[0]}").count() == 1
            print("OK: certificado, pregunta, respuesta y avisos únicos ante solicitudes concurrentes con conexiones SQLite independientes.")
        finally:
            connections.close_all()


if __name__ == "__main__":
    run()
