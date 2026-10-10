"""Serve the essential journey against a disposable database, never main data."""
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="essential-preview-", dir=ROOT / ".local") as directory:
        directory = Path(directory)
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(directory / "platform.sqlite3")
        os.environ["DJANGO_DEBUG"] = "true"
        import django
        django.setup()
        from django.conf import settings
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        from django.core.management import call_command
        from django.core.wsgi import get_wsgi_application

        from commerce.gateway import ProviderStatus
        from commerce.models import Invoice
        from commerce.services import reserve_invoice, settle
        from content.publication import publish_course
        from learning.assessment_services import save_attempt, start_attempt
        from learning.certificate_pdf import render_certificate
        from learning.certificates import issue_certificate
        from learning.models import CertificateDraft, CertificateSharing, QuizDraft
        from learning.services import enroll, save_progress
        from learning.support import post_question, reply_question
        from scripts.demo_commerce import seed

        settings.MEDIA_ROOT = directory / "media"
        call_command("migrate", verbosity=0)
        data = seed()
        for user in (data.student, data.creator, data.reviewer):
            user.set_password("EssentialQA_42!")
            user.save(update_fields=("password",))
        invoice = reserve_invoice(data.student, data.bundle.pk, activity_session=uuid4())
        Invoice.objects.filter(pk=invoice.pk).update(payment_hash="a" * 64, issue_state="ready")
        settle(invoice.pk, ProviderStatus(True, 150000, "a" * 64))
        policy = CertificateDraft.objects.create(course=data.course, enabled=True)
        policy.required_lessons.set(data.course.chapters.first().lessons.all())
        QuizDraft.objects.create(lesson=data.free, title="Comprueba tu recorrido", questions=[{"prompt": "¿Quién confirma el pago?", "multiple": False, "options": ["El servidor", "El navegador"], "correct": [0], "explanation": "La confirmación ocurre en el servidor."}])
        version = publish_course(data.course, data.reviewer)
        lessons = list(version.chapters.first().lessons.all())
        enrollment = enroll(data.student, version)
        attempt = start_attempt(data.student, enrollment.pk, lessons[0].quiz.pk)
        save_attempt(data.student, attempt.pk, {"0": [0]}, 0, submit=True)
        for index, lesson in enumerate(lessons):
            save_progress(data.student, enrollment.pk, lesson.pk, index, "complete")
        certificate = issue_certificate(data.student, enrollment.pk, "Lucía López")
        CertificateSharing.objects.filter(certificate=certificate).update(public=True)
        question = post_question(data.student, lessons[0].pk, "¿Puedo conservar mi avance si el curso publica otra versión?", uuid4())
        reply_question(data.creator, question.pk, "Sí. La inscripción y el avance permanecen vinculados a la versión que estudiaste. Puedes seguir repasando tu contenido adquirido.", uuid4())
        post_question(data.student, lessons[1].pk, "¿Dónde puedo consultar lo que incluye mi compra?", uuid4())
        (directory / "certificado.pdf").write_bytes(render_certificate(certificate))
        long = SimpleNamespace(course_title="Fundamentos de micropagos, publicación educativa y conservación de derechos históricos " * 2,
                               student_name="María José Álvarez " * 8, creator_name="Ana López", issued_at=certificate.issued_at,
                               enrollment=certificate.enrollment, pk=certificate.pk)
        (directory / "certificado-nombres-largos.pdf").write_bytes(render_certificate(long))
        metadata = {"directory": str(directory), "certificate": str(certificate.pk), "question": question.pk, "course": data.course.pk, "version": version.number}
        (ROOT / ".local/essential-preview.json").write_text(json.dumps(metadata), encoding="utf-8")
        print("Vista temporal: http://127.0.0.1:8018/", flush=True)
        print(json.dumps(metadata), flush=True)
        with make_server("127.0.0.1", 8018, StaticFilesHandler(get_wsgi_application())) as server:
            server.serve_forever()


if __name__ == "__main__":
    run()
