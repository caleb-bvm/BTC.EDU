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
        from datetime import timedelta

        from demo_commerce import seed
        from django.contrib.auth import get_user_model
        from django.core.exceptions import ValidationError
        from django.core.management import call_command
        from django.db import connections
        from django.test import override_settings
        from django.utils import timezone

        from commerce.gateway import ProviderStatus
        from commerce.models import (
            Cart,
            CartItem,
            Entitlement,
            Invoice,
            Order,
            PaymentEvidence,
            Purchase,
        )
        from commerce.orders import inventory_for, quote_order, reserve_order
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
                try:
                    reserve_invoice(data.student, data.individual.pk)
                    raise AssertionError("Se permitió una reserva solapada nueva")
                except ValidationError:
                    pass
                # Historical invoices issued before the new prevention must also
                # preserve both payment evidence records without duplicate access.
                single = Invoice.objects.create(buyer=data.student, offer=data.individual, logical_key=data.individual.logical_key,
                                                title=data.individual.title, amount_sats=data.individual.amount_sats,
                                                inventory=inventory_for(data.individual), expires_at=timezone.now() + timedelta(minutes=15))
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
                # A second buyer exercises one grouped order across independent
                # connections; repeated submission/confirmation remains singular.
                cart = Cart.objects.create(buyer=data.other)
                CartItem.objects.create(cart=cart, offer=data.individual, return_lesson=data.records[1])
                CartItem.objects.create(cart=cart, offer=data.second, return_lesson=data.records[2])
                quote = quote_order(data.other, cart)
                order_ids = parallel(lambda number: reserve_order(get_user_model().objects.get(pk=data.other.pk),
                                     Cart.objects.get(pk=cart.pk), quote["token"], quote["request_key"]).pk)
                assert order_ids[0] == order_ids[1] and Order.objects.count() == 1
                grouped = Invoice.objects.get(pk=order_ids[0])
                Invoice.objects.filter(pk=grouped.pk).update(payment_hash="c" * 64, issue_state="ready")
                parallel(lambda number: settle(grouped.pk, ProviderStatus(True, grouped.amount_sats * 1000, "c" * 64)))
                assert Purchase.objects.filter(invoice_id=grouped.pk).count() == 1
                assert Entitlement.objects.filter(buyer=data.other).count() == 2
                assert CartItem.objects.filter(cart=cart).count() == 0
                assert Cart.objects.get(pk=cart.pk).revision == 1
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
                # Legacy and grouped paths compete for the same paid revision.
                contender = get_user_model().objects.create_user("reservation-concurrency@example.invalid")
                contender_cart = Cart.objects.create(buyer=contender)
                CartItem.objects.create(cart=contender_cart, offer=data.file_offer)
                contender_quote = quote_order(contender, contender_cart)
                def race_reservations(number):
                    actor = get_user_model().objects.get(pk=contender.pk)
                    try:
                        if number == 0:
                            return reserve_invoice(actor, data.file_offer.pk).pk
                        return reserve_order(actor, Cart.objects.get(pk=contender_cart.pk), contender_quote["token"]).pk
                    except ValidationError:
                        return "blocked"
                reserved = parallel(race_reservations)
                assert reserved.count("blocked") == 1
                assert Invoice.objects.filter(buyer=contender).count() == 1
                print("OK: dos conexiones SQLite: reserva única, legado/carrito sin solapamientos, pedido/pago repetido único, derechos y limpieza atómica, avance sin sobrescritura.")
            finally:
                connections.close_all()


if __name__ == "__main__":
    run()
