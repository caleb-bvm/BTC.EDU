"""Verify independent SQLite connections for starts, saves, submissions and grants."""
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="assessment-concurrency-", dir=ROOT / ".local") as temporary:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(temporary) / "platform.sqlite3")
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        from django.core.exceptions import ValidationError
        from django.core.management import call_command
        from django.db import connections

        from content.models import Chapter, Course, Lesson
        from content.publication import publish_course
        from creators.models import CreatorProfile
        from learning.assessment_services import (
            grant_attempt,
            save_attempt,
            start_attempt,
        )
        from learning.models import ExtraQuizAttempt, QuizAttempt, QuizDraft
        from learning.services import enroll

        call_command("migrate", verbosity=0)
        users = get_user_model().objects
        creator = users.create_user("creator@race.invalid", account_type="creator")
        student = users.create_user("student@race.invalid")
        reviewer = users.create_superuser("reviewer@race.invalid")
        CreatorProfile.objects.create(user=creator, display_name="Docente", status="approved")
        course = Course.objects.create(creator=creator, title="Concurrencia", description="Prueba")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        lesson = Lesson.objects.create(chapter=chapter, title="Lección", body="Texto", status="published")
        QuizDraft.objects.create(lesson=lesson, title="Evaluación", max_attempts=1, questions=[{"prompt": "Elige A", "multiple": False, "options": ["A", "B"], "correct": [0], "explanation": "A"}])
        version = publish_course(course, reviewer)
        quiz = version.chapters.first().lessons.first().quiz
        enrollment = enroll(student, version)

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
            ids = parallel(lambda index: start_attempt(users.get(pk=student.pk), enrollment.pk, quiz.pk).pk)
            assert ids[0] == ids[1] and QuizAttempt.objects.count() == 1

            def save(index):
                try:
                    save_attempt(users.get(pk=student.pk), ids[0], {"0": [index]}, 0)
                    return "saved"
                except ValidationError:
                    return "stale"
            assert sorted(parallel(save)) == ["saved", "stale"]
            attempt = QuizAttempt.objects.get(pk=ids[0])
            assert attempt.revision == 1
            # Two conflicting deliveries must observe the same first committed result.
            results = parallel(lambda index: save_attempt(users.get(pk=student.pk), attempt.pk, {"0": [index]}, 1, submit=True).score)
            assert results[0] == results[1]
            attempt.refresh_from_db()
            assert attempt.submitted_at and attempt.revision == 2
            grants = parallel(lambda index: grant_attempt(users.get(pk=creator.pk), enrollment.pk, quiz.pk, 1, "Intento adicional autorizado").pk)
            assert grants[0] == grants[1] and ExtraQuizAttempt.objects.count() == 1
            ids = parallel(lambda index: start_attempt(users.get(pk=student.pk), enrollment.pk, quiz.pk).pk)
            assert ids[0] == ids[1] and QuizAttempt.objects.count() == 2
            print("OK: conexiones SQLite independientes: inicio único, guardado obsoleto rechazado, entrega única y autorización adicional idempotente.")
        finally:
            connections.close_all()


if __name__ == "__main__":
    run()
