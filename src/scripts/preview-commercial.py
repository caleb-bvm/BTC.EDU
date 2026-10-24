"""Commercial localhost UX review, using disposable data and an offline gateway."""
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="commercial-preview-", dir=ROOT / ".local") as directory:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        os.environ["DJANGO_DEBUG"] = "true"
        import django
        from django.conf import settings

        settings.MEDIA_ROOT = Path(directory) / "media"
        settings.COMMERCE_SIMULATION = True
        settings.COMMERCE_PAYMENT_MODE = "fake"
        settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL = False
        settings.SESSION_COOKIE_NAME = "commercial_preview_session"
        settings.CSRF_COOKIE_NAME = "commercial_preview_csrf"
        settings.TEMPLATES[0]["APP_DIRS"] = False
        settings.TEMPLATES[0]["OPTIONS"]["loaders"] = [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ]
        django.setup()
        from django.core.management import call_command
        from django.db import connections

        from commerce.gateway import ProviderInvoice, ProviderStatus
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
            from django.contrib.auth import get_user_model
            from django.core.files.uploadedfile import SimpleUploadedFile

            from commerce.offers import create_offer, review_offer, submit_offer
            from content.models import Material
            from creators.models import CreatorProfile
            from creators.services import submit as send_content
            from media.models import Asset
            teacher = get_user_model().objects.create_user("beatriz@demo.invalid", account_type="creator", first_name="Beatriz")
            teacher.set_password("OverhaulQA_42!")
            teacher.save(update_fields=("password",))
            CreatorProfile.objects.create(user=teacher, status="approved", display_name="Beatriz Hernández", specialty="Herramientas de estudio", bio="Prepara actividades y materiales para organizar el aprendizaje.")
            asset = Asset.objects.create(creator=teacher, file=SimpleUploadedFile("plan-de-estudio.txt", b"Plan de estudio: objetivo, recursos, practica y repaso.", content_type="text/plain"))
            guide = Material.objects.create(creator=teacher, title="Planifica tu semana de estudio", description="Una plantilla breve para organizar objetivos y sesiones.", access_type="paid", pending_asset=asset, **EDUCATION_FIXTURE)
            decide(send_content(guide, teacher), data.reviewer, True)
            guide.refresh_from_db()
            file_sale = create_offer(teacher, f"resource:{guide.revision_id}", "Plan de estudio · plantilla", 40)
            submit_offer(teacher, file_sale)
            review_offer(data.reviewer, file_sale, True)
            tutorial2 = Course.objects.create(creator=teacher, kind="tutorial", title="Organiza una práctica guiada", description="Define un resultado y comprueba tu progreso con dos pasos.", objective="Preparar una práctica con un resultado verificable.", requirements="Una tarea concreta para estudiar.")
            chapter2 = Chapter.objects.create(course=tutorial2, title="Tu práctica", status="published")
            for index, title in enumerate(("Define tu resultado", "Comprueba lo aprendido"), 1):
                Lesson.objects.create(chapter=chapter2, title=title, description="Un paso para preparar y revisar tu práctica.", body="Escribe el resultado que quieres obtener, prepara una actividad y contrasta la solución.", status="published", access_type="paid", position=index, **EDUCATION_FIXTURE)
            publication = send_content(tutorial2, teacher)
            decide(publication, data.reviewer, True)
            for record in publication.course_version.chapters.first().lessons.all():
                item = create_offer(teacher, f"lesson:{record.pk}", record.content.title, 30)
                submit_offer(teacher, item)
                review_offer(data.reviewer, item, True)
            tutorial_sale = create_offer(teacher, f"course:{publication.course_version.pk}", "Práctica guiada · tutorial completo", 60)
            submit_offer(teacher, tutorial_sale)
            review_offer(data.reviewer, tutorial_sale, True)
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
                print("Revisión comercial: http://127.0.0.1:8031/", flush=True)
                print("Estudiante: lucia@demo.invalid / OverhaulQA_42!", flush=True)
                print("Educador: ana@demo.invalid / OverhaulQA_42!", flush=True)
                print("Revisión: revision@demo.invalid / OverhaulQA_42!", flush=True)
                print(f"Ofertas para revisar: curso {data.bundle.pk}, tutorial {tutorial_sale.pk}, material {file_sale.pk}", flush=True)
                print(f"Lección objetivo: http://127.0.0.1:8031/cursos/{data.course.pk}/versiones/{data.version.number}/lecciones/{data.records[1].pk}/", flush=True)
                call_command("runserver", "127.0.0.1:8031", use_reloader=False)
        finally:
            connections.close_all()


if __name__ == "__main__":
    run()
