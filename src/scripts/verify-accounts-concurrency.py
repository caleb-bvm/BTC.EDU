"""Account operations across independent SQLite connections, with synthetic data."""
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="accounts-concurrency-", dir=ROOT / ".local") as directory:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(directory) / "platform.sqlite3")
        import django
        django.setup()
        from django.contrib.auth import get_user_model
        from django.core.exceptions import PermissionDenied, ValidationError
        from django.core.management import call_command
        from django.db import connections
        from django.test import RequestFactory, override_settings

        from accounts.models import AccountEvent
        from accounts.security import (
            action_token,
            change_password,
            close_account,
            confirm_action,
            request_email_action,
        )
        from creators.application_service import review_application
        from creators.models import CreatorApplicationEvent, CreatorProfile

        def parallel(operation):
            barrier = Barrier(2)
            def worker(number):
                connections.close_all()
                try:
                    barrier.wait(timeout=10)
                    return operation(number)
                finally:
                    connections.close_all()
            with ThreadPoolExecutor(max_workers=2) as executor:
                return list(executor.map(worker, range(2)))

        with override_settings(ACCOUNT_SEND_EMAIL=False, ACCOUNT_REQUIRE_VERIFIED_EMAIL=False, MEDIA_ROOT=Path(directory) / "media", PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"]):
            try:
                call_command("migrate", verbosity=0)
                users = get_user_model().objects
                student = users.create_user("same@concurrency.invalid", "StudentQA_42!")
                creator = users.create_user("same@concurrency.invalid", "CreatorQA_42!", account_type="creator")
                admin = users.create_superuser("review@concurrency.invalid", "ReviewQA_42!")
                action = request_email_action(RequestFactory().get("/", HTTP_HOST="127.0.0.1"), student, "verify")
                def confirm(number):
                    try:
                        confirm_action(action_token(action))
                        return "confirmed"
                    except ValidationError:
                        return "rejected"
                assert sorted(parallel(confirm)) == ["confirmed", "rejected"]
                assert AccountEvent.objects.filter(user=student, kind="email_verified").count() == 1
                profile = CreatorProfile.objects.create(user=creator, display_name="Docente", bio="Educación", specialty="Bitcoin")
                def review(number):
                    try:
                        review_application(profile, admin, "approved" if number else "changes", "Revisar presentación" if not number else "", expected_revision=0)
                        return "saved"
                    except ValidationError:
                        return "stale"
                assert sorted(parallel(review)) == ["saved", "stale"]
                assert CreatorApplicationEvent.objects.filter(profile=profile).count() == 1
                student.refresh_from_db()
                stale = users.get(pk=student.pk)
                close_account(student)
                try:
                    change_password(stale, "StudentQA_42!", "UpdatedQA_42!")
                    raise AssertionError("A stale password request must not reactivate the account.")
                except (PermissionDenied, ValidationError):
                    pass
                student.refresh_from_db()
                assert not student.is_active and student.check_password("StudentQA_42!")
                creator.refresh_from_db()
                assert creator.is_active and creator.check_password("CreatorQA_42!")
                print("OK: confirmación simultánea única, revisión concurrente sin sobrescritura, contraseña obsoleta rechazada tras desactivación y cuentas independientes.")
            finally:
                connections.close_all()


if __name__ == "__main__":
    run()
