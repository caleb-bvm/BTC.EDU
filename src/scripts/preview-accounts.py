"""Disposable account UX preview. Never writes to the project's database."""
import os
import sys
import tempfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="accounts-preview-", dir=ROOT / ".local") as directory:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        os.environ["DJANGO_DEBUG"] = "true"
        os.environ["DJANGO_EMAIL_BACKEND"] = "django.core.mail.backends.filebased.EmailBackend"
        os.environ["EMAIL_FILE_PATH"] = str(Path(directory) / "mail")
        import django
        from django.conf import settings

        settings.MEDIA_ROOT = Path(directory) / "media"
        settings.SESSION_COOKIE_NAME = "accounts_preview_session"
        settings.CSRF_COOKIE_NAME = "accounts_preview_csrf"
        settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
        django.setup()
        from django.contrib.auth import get_user_model
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.management import call_command
        from django.db import connections
        from django.utils import timezone
        from PIL import Image, ImageDraw

        from accounts.avatars import normalize_avatar, update_avatar
        from creators.application_service import review_application
        from creators.models import CreatorProfile
        from learning.support import notify

        try:
            call_command("migrate", verbosity=0)
            users = get_user_model().objects
            student = users.create_user("persona@accounts.invalid", "StudentQA_42!", first_name="Lucía", display_name="Lucía", bio="Quiero entender Bitcoin y practicar paso a paso.", interests="Bitcoin, Lightning", learning_goal="Aprender a reconocer una factura Lightning.")
            creator = users.create_user("persona@accounts.invalid", "CreatorQA_42!", account_type="creator", email_verified_at=timezone.now())
            reviewer = users.create_superuser("review@accounts.invalid", "ReviewQA_42!")
            profile = CreatorProfile.objects.create(user=creator, display_name="Daniel Rivera", bio="Explico Bitcoin con ejemplos cercanos y ejercicios prácticos.", specialty="Bitcoin y Lightning")
            review_application(profile, reviewer, "approved", "")
            suspended = users.create_user("suspendido@accounts.invalid", "CreatorQA_42!", account_type="creator")
            review_application(CreatorProfile.objects.create(user=suspended, display_name="Perfil en revisión", bio="Educación", specialty="Bitcoin"), reviewer, "suspended", "Necesitamos revisar la información sobre los derechos del contenido. Puedes solicitar una revisión desde Ayuda.")
            for user, color in ((student, "#eec7ab"), (creator, "#aac7bd")):
                # Abstract synthetic shapes for UI QA, without real people's photos.
                image = Image.new("RGB", (480, 320), color)
                draw = ImageDraw.Draw(image)
                draw.ellipse((175, 55, 285, 165), fill="#354941")
                draw.rounded_rectangle((125, 180, 335, 350), radius=70, fill="#354941")
                stream = BytesIO()
                image.save(stream, "PNG")
                update_avatar(user, normalize_avatar(SimpleUploadedFile("qa.png", stream.getvalue())))
            notify(student, "question:preview", "Tu pregunta sobre facturas tiene una respuesta", "/cuenta/ajustes/")
            print("Vista temporal: http://127.0.0.1:8036/cuenta/ajustes/", flush=True)
            print("Estudiante: persona@accounts.invalid / StudentQA_42!", flush=True)
            print("Creador: persona@accounts.invalid / CreatorQA_42!", flush=True)
            print("Suspendido: suspendido@accounts.invalid / CreatorQA_42!", flush=True)
            call_command("runserver", "127.0.0.1:8036", use_reloader=False)
        finally:
            connections.close_all()


if __name__ == "__main__":
    run()
