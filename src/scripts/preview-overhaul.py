"""Integrated localhost UX review, using disposable data and an offline gateway."""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="overhaul-preview-", dir=ROOT / ".local") as directory:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        os.environ["DJANGO_DEBUG"] = "true"
        import django
        from django.conf import settings

        settings.MEDIA_ROOT = Path(directory) / "media"
        settings.COMMERCE_SIMULATION = True
        settings.COMMERCE_PAYMENT_MODE = "fake"
        settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL = False
        settings.SESSION_COOKIE_NAME = "overhaul_preview_session"
        settings.CSRF_COOKIE_NAME = "overhaul_preview_csrf"
        settings.TEMPLATES[0]["APP_DIRS"] = False
        settings.TEMPLATES[0]["OPTIONS"]["loaders"] = [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ]
        django.setup()
        from django.core.management import call_command
        from django.db import connections

        from commerce.gateway import ProviderInvoice, ProviderStatus
        from commerce.services import ensure_emitted, reserve_invoice
        from content.editorial_catalog import CATALOG
        from content.models import Chapter, Course, Lesson
        from content.testing import EDUCATION_FIXTURE
        from creators.services import decide, submit
        from learning.assessment_services import save_attempt, start_attempt
        from learning.models import VersionQuiz
        from learning.services import enroll, save_progress
        from learning.support import post_question, reply_question
        from scripts.demo_commerce import seed

        class OfflineGateway:
            def __init__(self):
                self.paid = set()

            def create(self, invoice):
                return ProviderInvoice(invoice.pk.hex * 2, "lnbcrt1" + invoice.pk.hex * 5)

            recover = create

            def status(self, invoice):
                return ProviderStatus(invoice.pk in self.paid, invoice.amount_sats * 1000, invoice.payment_hash)

            def simulate(self, invoice):
                self.paid.add(invoice.pk)

            def close(self):
                pass

        try:
            call_command("migrate", verbosity=0)
            data = seed()
            call_command("load_editorial_catalog", verbosity=0)
            for user in (data.student, data.other, data.creator, data.reviewer):
                user.set_password("OverhaulQA_42!")
                user.save(update_fields=("password",))
            for index in range(4):
                course = Course.objects.get(title=CATALOG[index]["title"])
                enrollment = enroll(data.student, course.current_version)
                lessons = list(course.current_version.chapters.first().lessons.all())
                if index == 0:
                    save_progress(data.student, enrollment.pk, lessons[0].pk, 0, "complete")
                    save_progress(data.student, enrollment.pk, lessons[1].pk, 1, "position")
                if index == 1:
                    all_lessons = [lesson for chapter in course.current_version.chapters.all() for lesson in chapter.lessons.all()]
                    for revision, lesson in enumerate(all_lessons):
                        quiz = VersionQuiz.objects.filter(lesson=lesson).first()
                        if quiz:
                            attempt = start_attempt(data.student, enrollment.pk, quiz.pk)
                            save_attempt(data.student, attempt.pk, {str(i): q["correct"] for i, q in enumerate(quiz.questions)}, 0, submit=True)
                        save_progress(data.student, enrollment.pk, lesson.pk, revision, "complete")
            enrollment = enroll(data.student, data.version)
            save_progress(data.student, enrollment.pk, data.records[0].pk, 0, "complete")
            question = post_question(data.student, data.records[0].pk, "¿Dónde encuentro lo que incluye cada compra?", uuid4())
            reply_question(data.creator, question.pk, "Consulta el detalle de la oferta antes de continuar.", uuid4())
            reply_question(data.student, question.pk, "¿Puedo comprar solo la lección que necesito?", uuid4())
            data.course.description += " Incluye una nueva práctica guiada."
            data.course.save(update_fields=("description",))
            submit(data.course, data.creator)
            tutorial = Course.objects.create(creator=data.creator, kind="tutorial", title="Organiza tu primera práctica", description="Un recorrido breve para preparar una actividad.")
            chapter = Chapter.objects.create(course=tutorial, title="Primeros pasos", status="published")
            Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Define un resultado", body="Escribe qué podrá hacer el estudiante después de la práctica.", status="published")
            decide(submit(tutorial, data.creator), data.reviewer, False, "Aclara los requisitos de la práctica.")
            gateway = OfflineGateway()
            with patch("commerce.services.LNbitsGateway", return_value=gateway):
                pending = ensure_emitted(reserve_invoice(data.student, data.individual.pk, return_lesson_id=data.records[1].pk))
                print("Revisión integrada: http://127.0.0.1:8030/", flush=True)
                print("Estudiante: lucia@demo.invalid / OverhaulQA_42!", flush=True)
                print("Educador: ana@demo.invalid / OverhaulQA_42!", flush=True)
                print("Revisión: revision@demo.invalid / OverhaulQA_42!", flush=True)
                print(f"Factura preparada: http://127.0.0.1:8030/facturas/{pending.pk}/", flush=True)
                print(f"Lección objetivo: http://127.0.0.1:8030/cursos/{data.course.pk}/versiones/{data.version.number}/lecciones/{data.records[1].pk}/", flush=True)
                call_command("runserver", "127.0.0.1:8030", use_reloader=False)
        finally:
            connections.close_all()


if __name__ == "__main__":
    run()
