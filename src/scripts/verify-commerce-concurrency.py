"""Exercise independent SQLite connections against a shared temporary file."""
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def run():
    with tempfile.TemporaryDirectory(prefix="commerce-concurrency-", dir=ROOT / ".local") as temporary:
        os.environ["DJANGO_SETTINGS_MODULE"] = "platform_config.settings"
        os.environ["DJANGO_DB_PATH"] = str(Path(temporary) / "platform.sqlite3")
        import django
        django.setup()
        from demo_commerce import seed
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        from django.db import connections
        from django.test import override_settings

        from commerce.gateway import ProviderStatus
        from commerce.models import Entitlement, Invoice, PaymentEvidence, Purchase
        from commerce.services import reserve_invoice, settle
        from learning.models import Enrollment, LessonProgress
        from learning.services import StaleProgress, enroll, save_progress

        with override_settings(MEDIA_ROOT=Path(temporary) / "media"):
            call_command("migrate", verbosity=0)
            data = seed()
            def parallel(function):
                barrier = Barrier(2)
                def worker(number):
                    connections.close_all()
                    try:
                        barrier.wait(timeout=10)
                        return function(number)
                    finally:
                        connections.close_all()
                with ThreadPoolExecutor(max_workers=2) as executor:
                    return list(executor.map(worker, range(2)))
            try:
                ids = parallel(lambda number: reserve_invoice(get_user_model().objects.get(pk=data.student.pk), data.bundle.pk).pk)
                assert ids[0] == ids[1] and Invoice.objects.count() == 1
                bundle = Invoice.objects.get(pk=ids[0])
                single = reserve_invoice(data.student, data.individual.pk)
                Invoice.objects.filter(pk=bundle.pk).update(payment_hash="a" * 64, issue_state="ready")
                Invoice.objects.filter(pk=single.pk).update(payment_hash="b" * 64, issue_state="ready")
                outcomes = parallel(lambda number: settle(bundle.pk if number == 0 else single.pk,
                    ProviderStatus(True, 150000 if number == 0 else 70000, "a" * 64 if number == 0 else "b" * 64)).status)
                assert sorted(outcomes) == ["failed", "paid"]
                assert Purchase.objects.count() == 1 and PaymentEvidence.objects.count() == 2
                winning = Invoice.objects.get(status="paid")
                parallel(lambda number: settle(winning.pk, ProviderStatus(True, winning.amount_sats * 1000, winning.payment_hash)))
                assert Purchase.objects.count() == 1
                assert Entitlement.objects.count() in (1, 4)
                enrollment = enroll(data.student, data.version)
                def progress(number):
                    try:
                        save_progress(get_user_model().objects.get(pk=data.student.pk), enrollment.pk, data.records[0].pk, 0, "complete" if number == 0 else "position")
                        return "saved"
                    except StaleProgress:
                        return "stale"
                outcomes = parallel(progress)
                assert sorted(outcomes) == ["saved", "stale"]
                assert Enrollment.objects.get(pk=enrollment.pk).revision == 1
                assert LessonProgress.objects.filter(enrollment=enrollment).count() <= 1
                print("OK: dos conexiones SQLite en archivo: reserva única, pagos solapados, confirmaciones repetidas y avance concurrente sin sobrescritura.")
            finally:
                connections.close_all()


if __name__ == "__main__":
    run()
