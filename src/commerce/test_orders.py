import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone

from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile
from learning.models import Enrollment

from . import tests as fixtures
from .gateway import ProviderStatus, ProviderUnavailable
from .models import (
    Cart,
    CartItem,
    Entitlement,
    EntitlementSource,
    Invoice,
    Order,
    OrderLine,
    PaymentEvidence,
    Purchase,
)
from .offers import archive_offer, create_offer, review_offer, submit_offer
from .orders import (
    quote_direct_order,
    quote_order,
    quote_selection,
    reserve_direct_order,
    reserve_order,
)
from .services import ensure_emitted, reconcile, reserve_invoice, settle


@override_settings(COMMERCE_PAYMENT_MODE="fake", ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class GroupedOrderTests(TestCase):
    setUp = fixtures.CommerceJourneyTests.setUp
    activate = fixtures.CommerceJourneyTests.activate
    invoice = fixtures.CommerceJourneyTests.invoice
    pay = fixtures.CommerceJourneyTests.pay
    lesson_url = fixtures.CommerceJourneyTests.lesson_url

    def cart(self, offers=None, buyer=None):
        cart = Cart.objects.create(buyer=buyer or self.student)
        for offer in offers or [self.individual, self.second_offer]:
            CartItem.objects.create(cart=cart, offer=offer, return_lesson=offer.lesson if offer.lesson_id else None)
        return cart

    def reserve(self, cart):
        quote = quote_order(self.student, cart)
        return reserve_order(self.student, cart, quote["token"], quote["request_key"])

    def paid(self, invoice):
        invoice = ensure_emitted(invoice, self.gateway)
        return settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))

    def another_educator(self):
        seller = get_user_model().objects.create_user("second.seller@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=seller, display_name="Otra docente", status="approved")
        course = Course.objects.create(creator=seller, title="Otro tutorial", description="Un tutorial", kind="tutorial")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Otro aprendizaje", body="Contenido distinto", access_type="paid", status="published")
        version = publish_course(course, self.admin)
        lesson = version.chapters.first().lessons.first()
        def active(target, title, amount):
            offer = create_offer(seller, target, title, amount)
            submit_offer(seller, offer)
            return review_offer(self.admin, offer, True)
        active(f"lesson:{lesson.pk}", "Otra lección", 100)
        return active(f"course:{version.pk}", "Otro tutorial completo", 200), version

    def test_multiple_educators_one_invoice_total_and_atomic_access(self):
        other_offer, other_version = self.another_educator()
        cart = self.cart([self.bundle, other_offer])
        quote = quote_order(self.student, cart)
        self.assertTrue(quote["can_checkout"])
        self.assertEqual(quote["total_sats"], 350)
        invoice = reserve_order(self.student, cart, quote["token"], quote["request_key"])
        self.assertIsNone(invoice.offer_id)
        self.assertEqual(invoice.amount_sats, 350)
        self.assertEqual(invoice.title, "Pedido · 2 artículos")
        self.assertEqual(invoice.order.lines.count(), 2)
        self.assertEqual(set(invoice.order.lines.values_list("creator_id", flat=True)), {self.creator.pk, other_offer.creator_id})
        self.assertTrue(invoice.order.sealed)
        self.assertFalse(Purchase.objects.exists())
        self.assertFalse(Entitlement.objects.exists())
        self.paid(invoice)
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(PaymentEvidence.objects.count(), 1)
        self.assertEqual(Entitlement.objects.count(), 5)
        self.assertEqual(EntitlementSource.objects.count(), 5)
        self.assertEqual(set(Enrollment.objects.values_list("version_id", flat=True)), {self.version.pk, other_version.pk})
        self.assertEqual(CartItem.objects.count(), 0)
        cart.refresh_from_db()
        self.assertEqual(cart.revision, 1)

    def test_lesson_optional_paid_file_and_tutorial_can_share_order(self):
        other_offer, _ = self.another_educator()
        cart = self.cart([self.individual, self.file_offer, other_offer])
        invoice = self.reserve(cart)
        self.assertEqual(invoice.amount_sats, 300)
        self.assertEqual(invoice.title, "Pedido · 3 artículos")
        self.paid(invoice)
        self.assertTrue(Entitlement.objects.filter(buyer=self.student, resource=self.records[1].content).exists())
        self.assertTrue(Entitlement.objects.filter(buyer=self.student, resource=self.resource).exists())
        self.assertEqual(invoice.order.lines.get(offer=self.individual).return_lesson_id, self.records[1].pk)

    def test_duplicate_and_package_overlap_have_no_token_or_charge(self):
        for selection in ([{"offer_id": self.individual.pk}, {"offer_id": self.individual.pk}],
                          [{"offer_id": self.bundle.pk}, {"offer_id": self.individual.pk}]):
            quote = quote_selection(self.student, selection)
            self.assertIn("selection_overlap", {issue["code"] for issue in quote["conflicts"]})
            self.assertFalse(quote["can_checkout"])
            self.assertEqual(quote["token"], "")
        cart = self.cart([self.bundle, self.individual])
        with self.assertRaises(ValidationError):
            reserve_order(self.student, cart, "not-a-token")
        self.assertFalse(Order.objects.exists())
        self.assertFalse(Invoice.objects.exists())

    def test_existing_rights_reject_owned_and_credit_partial_packages(self):
        self.pay(self.individual)
        quote = quote_selection(self.student, [{"offer_id": self.individual.pk}, {"offer_id": self.bundle.pk}])
        codes = {issue["code"] for issue in quote["conflicts"]}
        self.assertIn("owned", codes)
        self.assertNotIn("partial", codes)
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.individual.pk)
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertFalse(Order.objects.exists())

    def test_pending_legacy_blocks_grouped_overlap_but_not_unrelated_content(self):
        legacy = self.invoice(self.individual)
        quote = quote_direct_order(self.student, self.bundle.pk)
        issue = next(issue for issue in quote["conflicts"] if issue["code"] == "pending_overlap")
        self.assertEqual(issue["invoice_id"], str(legacy.pk))
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.bundle.pk)
        separate = reserve_direct_order(self.student, self.second_offer.pk)
        self.assertTrue(separate.order_id)

    def test_grouped_pending_blocks_legacy_overlaps(self):
        order_invoice = reserve_direct_order(self.student, self.bundle.pk)
        with self.assertRaisesMessage(ValidationError, "pago pendiente"):
            reserve_invoice(self.student, self.individual.pk)
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertEqual(Invoice.objects.get().pk, order_invoice.pk)

    def test_unknown_emission_blocks_new_order_even_after_local_expiry(self):
        invoice = reserve_direct_order(self.student, self.individual.pk)
        with patch.object(self.gateway, "create", side_effect=ProviderUnavailable("unknown")):
            with self.assertRaises(ProviderUnavailable):
                ensure_emitted(invoice, self.gateway)
        Invoice.objects.filter(pk=invoice.pk).update(status="expired", expires_at=timezone.now() - timedelta(seconds=1))
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.bundle.pk)
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertFalse(Purchase.objects.exists())

    def test_expired_issued_requires_reconciliation_before_new_quote(self):
        invoice = ensure_emitted(reserve_direct_order(self.student, self.individual.pk), self.gateway)
        Invoice.objects.filter(pk=invoice.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.individual.pk)
        reconcile(invoice, self.gateway)
        replacement = reserve_direct_order(self.student, self.individual.pk)
        self.assertNotEqual(invoice.pk, replacement.pk)

    def test_observed_payment_after_expiry_preserves_review_and_blocks_repayment(self):
        invoice = ensure_emitted(reserve_direct_order(self.student, self.individual.pk), self.gateway)
        observed = invoice.expires_at + timedelta(seconds=1)
        result = settle(invoice.pk, ProviderStatus(True, 70000, invoice.payment_hash), observed_at=observed)
        self.assertEqual((result.status, result.incident), ("expired", "payment_time_unknown"))
        self.assertEqual(result.evidence.observed_at, observed)
        self.assertFalse(Purchase.objects.exists())
        self.assertFalse(Entitlement.objects.exists())
        with self.assertRaises(ValidationError):
            reserve_invoice(self.student, self.individual.pk)
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.individual.pk)

    def test_signed_review_binds_user_cart_revision_origin_and_price(self):
        cart = self.cart()
        quote = quote_order(self.student, cart)
        with self.assertRaises(PermissionDenied):
            reserve_order(self.other, cart, quote["token"])
        with self.assertRaises(ValidationError):
            reserve_order(self.student, cart, quote["token"] + "modified")
        CartItem.objects.filter(cart=cart, offer=self.individual).update(return_lesson=None)
        with self.assertRaises(ValidationError):
            reserve_order(self.student, cart, quote["token"])
        CartItem.objects.filter(cart=cart, offer=self.individual).update(return_lesson=self.records[1])
        Cart.objects.filter(pk=cart.pk).update(revision=1)
        with self.assertRaises(ValidationError):
            reserve_order(self.student, cart, quote["token"])
        self.assertFalse(Order.objects.exists())

    def test_retired_or_replaced_offer_requires_review_without_price_mutation(self):
        quote = quote_direct_order(self.student, self.individual.pk)
        replacement = self.activate(f"lesson:{self.records[1].pk}", "Precio actual", 90)
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.individual.pk, token=quote["token"])
        invoice = reserve_direct_order(self.student, replacement.pk)
        self.assertEqual(invoice.amount_sats, 90)
        self.assertEqual(self.individual.amount_sats, 70)

    def test_quote_expiry_requires_fresh_review(self):
        quote = quote_direct_order(self.student, self.individual.pk)
        with patch("django.core.signing.time.time", return_value=timezone.now().timestamp() + 1000):
            with self.assertRaisesMessage(ValidationError, "venció"):
                reserve_direct_order(self.student, self.individual.pk, token=quote["token"])
        self.assertFalse(Invoice.objects.exists())

    def test_consumed_quote_returns_original_after_cart_and_offer_changes(self):
        cart = self.cart()
        quote = quote_order(self.student, cart)
        invoice = reserve_order(self.student, cart, quote["token"], quote["request_key"])
        self.paid(invoice)
        archive_offer(self.creator, self.individual)
        CartItem.objects.create(cart=cart, offer=self.file_offer)
        Cart.objects.filter(pk=cart.pk).update(revision=8)
        with patch("django.core.signing.time.time", return_value=timezone.now().timestamp() + 1000):
            retried = reserve_order(self.student, cart, quote["token"], quote["request_key"])
        self.assertEqual(retried.pk, invoice.pk)
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().offer_id, self.file_offer.pk)

    def test_direct_consumed_request_is_stable_and_cannot_retarget(self):
        quote = quote_direct_order(self.student, self.individual.pk, self.records[1].pk)
        invoice = reserve_direct_order(self.student, self.individual.pk, self.records[1].pk, quote["request_key"], quote["token"])
        self.assertEqual(reserve_direct_order(self.student, self.individual.pk, self.records[1].pk, quote["request_key"], quote["token"]).pk, invoice.pk)
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.second_offer.pk, None, quote["request_key"], quote["token"])
        self.assertEqual(Order.objects.count(), 1)

    def test_confirming_order_preserves_new_or_recreated_cart_items(self):
        cart = self.cart()
        invoice = self.reserve(cart)
        original = cart.items.get(offer=self.individual)
        original.delete()
        replacement = CartItem.objects.create(cart=cart, offer=self.individual, return_lesson=self.records[1])
        extra = CartItem.objects.create(cart=cart, offer=self.file_offer)
        Cart.objects.filter(pk=cart.pk).update(revision=5)
        self.paid(invoice)
        self.assertEqual(set(cart.items.values_list("pk", flat=True)), {replacement.pk, extra.pk})
        cart.refresh_from_db()
        self.assertEqual(cart.revision, 6)

    def test_direct_buy_does_not_mutate_cart(self):
        cart = self.cart([self.file_offer])
        original_ids = list(cart.items.values_list("pk", flat=True))
        invoice = reserve_direct_order(self.student, self.individual.pk)
        self.paid(invoice)
        self.assertEqual(list(cart.items.values_list("pk", flat=True)), original_ids)
        cart.refresh_from_db()
        self.assertEqual(cart.revision, 0)

    def test_wrong_amount_or_corrupted_snapshot_grants_none_of_the_order(self):
        cart = self.cart()
        invoice = ensure_emitted(self.reserve(cart), self.gateway)
        settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000 - 1, invoice.payment_hash))
        self.assertFalse(Entitlement.objects.exists())
        self.assertFalse(Purchase.objects.exists())
        self.assertEqual(CartItem.objects.count(), 2)
        other = reserve_direct_order(self.other, self.file_offer.pk)
        other = ensure_emitted(other, self.gateway)
        OrderLine._base_manager.filter(order=other.order).update(amount_sats=1)
        failed = settle(other.pk, ProviderStatus(True, other.amount_sats * 1000, other.payment_hash))
        self.assertEqual(failed.incident, "inventory_mismatch")
        self.assertFalse(Entitlement.objects.exists())

    def test_repeated_confirmation_has_one_purchase_and_no_duplicate_sources(self):
        invoice = self.paid(self.reserve(self.cart()))
        settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))
        settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(EntitlementSource.objects.count(), 2)
        self.assertEqual(PaymentEvidence.objects.count(), 1)

    def test_malformed_inventory_keeps_payment_evidence_and_grants_nothing(self):
        invoice = ensure_emitted(self.reserve(self.cart()), self.gateway)
        Invoice.objects.filter(pk=invoice.pk).update(inventory=[{"resource_id": self.records[1].content_id}])
        failed = settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))
        self.assertEqual(failed.incident, "inventory_mismatch")
        self.assertEqual(PaymentEvidence.objects.get(invoice=invoice).resolution, "inventory_mismatch")
        self.assertFalse(Purchase.objects.exists())
        self.assertFalse(Entitlement.objects.exists())
        self.assertEqual(CartItem.objects.count(), 2)

    def test_order_and_sealed_lines_are_immutable(self):
        invoice = self.reserve(self.cart())
        order = invoice.order
        order.amount_sats = 1
        with self.assertRaises(ValidationError):
            order.save()
        line = order.lines.first()
        line.title = "Otra cosa"
        with self.assertRaises(ValidationError):
            line.save()
        with self.assertRaises(ValidationError):
            OrderLine.objects.create(order=order, offer=self.file_offer, creator=self.creator, title="Extra", amount_sats=30,
                                     logical_key=self.file_offer.logical_key, inventory=[{"resource_id": self.resource.pk}], position=3)

    def test_invoice_requires_exactly_one_legacy_or_order_target(self):
        invoice = self.reserve(self.cart())
        for fields in ({"offer": self.individual, "order": invoice.order}, {"offer": None, "order": None}):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Invoice.objects.create(buyer=self.student, logical_key=str(uuid.uuid4()), title="Invalid", amount_sats=1,
                                       inventory=[], expires_at=timezone.now(), **fields)

    def test_guest_can_review_without_creating_payment_or_signed_token(self):
        quote = quote_direct_order(AnonymousUser(), self.individual.pk)
        self.assertTrue(quote["can_checkout"])
        self.assertEqual((quote["token"], quote["request_key"]), ("", ""))
        with self.assertRaises(PermissionDenied):
            reserve_direct_order(AnonymousUser(), self.individual.pk)
        self.assertFalse(Order.objects.exists())

    def test_limit_and_invalid_origin_do_not_create_orders(self):
        quote = quote_selection(self.student, [{"offer_id": self.individual.pk}] * 21)
        self.assertIn("limit", {item["code"] for item in quote["conflicts"]})
        quote = quote_direct_order(self.student, self.individual.pk, self.records[2].pk)
        self.assertIn("invalid_origin", {item["code"] for item in quote["conflicts"]})
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.individual.pk, "https://example.invalid")
        self.assertFalse(Order.objects.exists())

    def test_telemetry_is_per_offer_once_and_does_not_inflate_order_total(self):
        from core.models import ActivityEvent
        cart = self.cart()
        quote = quote_order(self.student, cart)
        session = uuid.uuid4()
        invoice = reserve_order(self.student, cart, quote["token"], activity_session=session)
        reserve_order(self.student, cart, quote["token"], activity_session=session)
        events = ActivityEvent.objects.filter(invoice=invoice, kind="invoice_created")
        self.assertEqual(events.count(), 2)
        self.assertEqual(set(events.values_list("offer_id", flat=True)), {self.individual.pk, self.second_offer.pk})
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertEqual(invoice.amount_sats, 150)
