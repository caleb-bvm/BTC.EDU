"""Learning UI review with editorial content and disposable synthetic progress."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="learning-preview-", dir=ROOT / ".local") as directory:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        os.environ["DJANGO_DEBUG"] = "true"
        import django
        from django.conf import settings

        settings.TEMPLATES[0]["APP_DIRS"] = False
        settings.TEMPLATES[0]["OPTIONS"]["loaders"] = ["django.template.loaders.filesystem.Loader", "django.template.loaders.app_directories.Loader"]
        settings.SESSION_COOKIE_NAME = "learning_preview_session"
        settings.CSRF_COOKIE_NAME = "learning_preview_csrf"
        django.setup()
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        from django.db import connections

        from content.editorial_catalog import CATALOG
        from content.models import Course
        from learning.assessment_services import save_attempt, start_attempt
        from learning.models import VersionQuiz
        from learning.services import enroll, save_progress

        try:
            call_command("migrate", verbosity=0)
            call_command("load_editorial_catalog", verbosity=0)
            student = get_user_model().objects.create_user("student@learning.invalid", password="LearningQA_42!", first_name="Lucía", display_name="Lucía")
            for index in (0, 1, 2, 3):
                version = Course.objects.get(title=CATALOG[index]["title"]).current_version
                enrollment = enroll(student, version)
                lessons = [lesson for chapter in version.chapters.all() for lesson in chapter.lessons.select_related("content")]
                if index == 0:
                    save_progress(student, enrollment.pk, lessons[0].pk, 0, "complete")
                    save_progress(student, enrollment.pk, lessons[1].pk, 1, "position")
                elif index == 1:
                    for revision, lesson in enumerate(lessons):
                        quiz = VersionQuiz.objects.filter(lesson=lesson).first()
                        if quiz:
                            attempt = start_attempt(student, enrollment.pk, quiz.pk)
                            save_attempt(student, attempt.pk, {str(i): question["correct"] for i, question in enumerate(quiz.questions)}, 0, submit=True)
                        save_progress(student, enrollment.pk, lesson.pk, revision, "complete")
                elif index == 3:
                    save_progress(student, enrollment.pk, lessons[0].pk, 0, "complete")
            print("Vista temporal: http://127.0.0.1:8020/mi-espacio/", flush=True)
            print("Cuenta sintética: student@learning.invalid / LearningQA_42!", flush=True)
            call_command("runserver", "127.0.0.1:8020", use_reloader=False)
        finally:
            connections.close_all()


if __name__ == "__main__":
    run()
