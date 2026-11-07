from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from content.access import owns_revision
from learning.models import Enrollment, Notification

from . import tests as fixtures
from .bolt11 import requested_msat
from .gateway import ProviderStatus, ProviderUnavailable
from .gifts import redeem_gift
from .models import Coupon, Entitlement, Gift, Invoice, OrderLine, Purchase, Refund, Tip
from .orders import (
    order_snapshot_valid,
    quote_direct_order,
    quote_selection,
    reserve_direct_order,
)
from .pricing import upgrade_credit
from .refunds import approve_refund, refund_blocker, reject_refund, request_refund
from .services import ensure_emitted, settle
from .tips import check_tip, create_tip

# 150 sats in BOLT11 amount notation; only the human-readable part is read.
INVOICE_150 = "lnbc1500n1pjtestqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"


class PayingGateway(fixtures.FakeGateway):
    def __init__(self):
        super().__init__()
        self.payments = []

    def pay(self, payment_request):
        self.payments.append(payment_request)
        return "b" * 64


@override_settings(COMMERCE_PAYMENT_MODE="fake", ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class FeatureFixture(TestCase):
    setUp = fixtures.CommerceJourneyTests.setUp
    activate = fixtures.CommerceJourneyTests.activate
    invoice = fixtures.CommerceJourneyTests.invoice
    pay = fixtures.CommerceJourneyTests.pay

    def paid(self, invoice):
        invoice = ensure_emitted(invoice, self.gateway)
        return settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))

    def direct(self, offer, buyer=None, **options):
        buyer = buyer or self.student
        message = options.pop("gift_message", "")
        quote = quote_direct_order(buyer, offer.pk, **options)
        return reserve_direct_order(buyer, offer.pk, request_key=quote["request_key"], token=quote["token"], gift_message=message)

    def coupon(self, code="LANZA", **fields):
        now = timezone.now()
        values = {"creator": self.creator, "code": code, "percent_off": 20, "starts_at": now - timedelta(minutes=1),
                  "expires_at": now + timedelta(days=1), "max_uses": 5}
        values.update(fields)
        if "amount_off_sats" in fields:
            values["percent_off"] = None
        return Coupon.objects.create(**values)


class UpgradeCreditTests(FeatureFixture):
    def test_earlier_lesson_is_credited_and_only_missing_content_is_sold(self):
        self.pay(self.individual)
        self.assertEqual(upgrade_credit(self.student, self.bundle), 70)
        invoice = self.paid(self.direct(self.bundle))
        line = invoice.order.lines.get()
        self.assertEqual((invoice.amount_sats, line.credit_sats, line.amount_sats), (80, 70, 80))
        self.assertNotIn(self.records[1].content_id, {item["resource_id"] for item in line.inventory})
        self.assertEqual(invoice.status, "paid")
        for record in self.records[1:]:
            self.assertTrue(owns_revision(self.student, record.content_id))
        self.assertTrue(owns_revision(self.student, self.resource.pk))
        self.assertEqual(upgrade_credit(self.student, self.bundle), 0)

    def test_credit_never_takes_the_package_below_one_sat(self):
        self.pay(self.individual)
        self.pay(self.second_offer)
        quote = quote_direct_order(self.student, self.bundle.pk)
        self.assertTrue(quote["can_checkout"])
        self.assertEqual((quote["total_sats"], quote["credit_total_sats"]), (1, 149))

    def test_tampered_credit_line_fails_snapshot_and_grants_nothing(self):
        self.pay(self.individual)
        invoice = ensure_emitted(self.direct(self.bundle), self.gateway)
        self.assertTrue(order_snapshot_valid(invoice))
        OrderLine._base_manager.filter(order=invoice.order).update(credit_sats=60)
        invoice.refresh_from_db()
        self.assertFalse(order_snapshot_valid(invoice))
        settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))
        self.assertFalse(owns_revision(self.student, self.records[2].content_id))

    def test_package_bought_after_credit_quote_changes_the_fingerprint(self):
        self.pay(self.individual)
        quote = quote_direct_order(self.student, self.bundle.pk)
        self.pay(self.file_offer)
        with self.assertRaises(ValidationError):
            reserve_direct_order(self.student, self.bundle.pk, request_key=quote["request_key"], token=quote["token"])


class CouponTests(FeatureFixture):
    def test_percent_coupon_discounts_only_matching_educator_content(self):
        self.coupon()
        quote = quote_selection(self.student, [{"offer_id": self.bundle.pk}], coupon_code=" lanza ")
        self.assertEqual((quote["total_sats"], quote["discount_total_sats"], quote["coupon_code"]), (120, 30, "LANZA"))
        invoice = self.paid(self.direct(self.bundle, coupon_code="LANZA"))
        line = invoice.order.lines.get()
        self.assertEqual((line.amount_sats, line.discount_sats, line.coupon.code), (120, 30, "LANZA"))
        self.assertTrue(order_snapshot_valid(invoice))

    def test_coupon_applies_after_credit_and_keeps_one_sat(self):
        self.coupon("GRANDE", amount_off_sats=500)
        self.pay(self.individual)
        quote = quote_direct_order(self.student, self.bundle.pk, coupon_code="GRANDE")
        self.assertEqual((quote["total_sats"], quote["credit_total_sats"], quote["discount_total_sats"]), (1, 70, 79))

    def test_unusable_codes_explain_and_never_block_buying(self):
        self.coupon("VIEJO", starts_at=timezone.now() - timedelta(days=3), expires_at=timezone.now() - timedelta(days=1))
        self.coupon("APAGADO", active=False)
        for code, message in (("NADA", "no existe"), ("VIEJO", "venció"), ("APAGADO", "no existe")):
            quote = quote_direct_order(self.student, self.bundle.pk, coupon_code=code)
            self.assertIn(message, quote["coupon_error"])
            self.assertTrue(quote["can_checkout"])
            self.assertEqual(quote["total_sats"], 150)

    def test_other_course_coupon_does_not_apply(self):
        from content.models import Course
        course = Course.objects.create(creator=self.creator, title="Otro curso", description="Otro")
        self.coupon("SOLOOTRO", course=course)
        quote = quote_direct_order(self.student, self.bundle.pk, coupon_code="SOLOOTRO")
        self.assertEqual(quote["coupon_error"], "Este cupón no aplica al contenido elegido.")
        self.assertEqual(quote["total_sats"], 150)

    def test_use_limit_and_one_paid_use_per_buyer(self):
        self.coupon(max_uses=1)
        self.paid(self.direct(self.individual, coupon_code="LANZA"))
        self.assertIn("Ya usaste", quote_direct_order(self.student, self.second_offer.pk, coupon_code="LANZA")["coupon_error"])
        self.assertIn("límite", quote_direct_order(self.other, self.second_offer.pk, coupon_code="LANZA")["coupon_error"])

    def test_coupon_conditions_are_frozen(self):
        coupon = self.coupon()
        coupon.percent_off = 50
        with self.assertRaises(ValidationError):
            coupon.save()

    def test_creator_page_creates_and_deactivates_coupons(self):
        self.client.force_login(self.creator)
        now = timezone.localtime()
        response = self.client.post(reverse("creator-coupons"), {
            "code": "abril-10", "kind": "amount", "value": 10, "course": "", "max_uses": 3,
            "starts_at": now.strftime("%Y-%m-%dT%H:%M"), "expires_at": (now + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M")})
        self.assertRedirects(response, reverse("creator-coupons"))
        coupon = Coupon.objects.get(code="ABRIL-10")
        self.client.post(reverse("creator-coupons"), {"action": "deactivate", "coupon": coupon.pk})
        coupon.refresh_from_db()
        self.assertFalse(coupon.active)


class GiftTests(FeatureFixture):
    def test_gift_grants_nothing_to_buyer_and_redeems_once(self):
        self.pay(self.individual)
        invoice = self.paid(self.direct(self.bundle, gift=True, gift_message="  Para ti,   suerte  "))
        self.assertEqual(invoice.status, "paid")
        gift = Gift.objects.get()
        self.assertEqual(invoice.order.gift_message, "Para ti, suerte")
        self.assertFalse(owns_revision(self.student, self.records[2].content_id))
        with self.assertRaises(ValidationError):
            redeem_gift(self.student, gift.token)
        redeem_gift(self.other, gift.token)
        for record in self.records[1:]:
            self.assertTrue(owns_revision(self.other, record.content_id))
        self.assertTrue(Enrollment.objects.filter(student=self.other, version=self.version).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.student, event_key=f"gift-redeemed:{gift.pk}").exists())
        third = get_user_model().objects.create_user("third@example.invalid")
        with self.assertRaises(ValidationError):
            redeem_gift(third, gift.token)

    def test_gift_page_shows_link_to_buyer_and_redeems_for_visitor(self):
        invoice = self.paid(self.direct(self.bundle, gift=True))
        gift = invoice.order.gift_card
        detail = self.client.get(reverse("invoice-detail", args=[invoice.pk]))
        self.assertContains(detail, reverse("gift-detail", args=[gift.token]))
        page = self.client.get(reverse("gift-detail", args=[gift.token]))
        self.assertContains(page, "Copiar enlace")
        self.client.logout()
        self.assertContains(self.client.get(reverse("gift-detail", args=[gift.token])), "Entrar para canjear")
        self.client.force_login(self.other)
        self.assertRedirects(self.client.post(reverse("gift-detail", args=[gift.token])), reverse("workspace"), fetch_redirect_response=False)
        self.assertTrue(owns_revision(self.other, self.resource.pk))
        self.assertEqual(self.client.get(reverse("gift-detail", args=["no-existe"])).status_code, 404)

    def test_pending_gift_does_not_reserve_buyer_content(self):
        ensure_emitted(self.direct(self.bundle, gift=True), self.gateway)
        quote = quote_direct_order(self.student, self.bundle.pk)
        self.assertTrue(quote["can_checkout"])


class TipTests(FeatureFixture):
    def test_tip_is_paid_notifies_educator_and_grants_no_access(self):
        tip = create_tip(self.student, self.creator, 500, " ¡Gracias! ", self.records[1])
        tip = check_tip(tip, self.gateway, simulate=True)
        self.assertEqual(tip.status, "paid")
        self.assertTrue(Notification.objects.filter(recipient=self.creator, event_key=f"tip:{tip.pk}").exists())
        self.assertFalse(Entitlement.objects.exists())
        self.client.force_login(self.creator)
        page = self.client.get(reverse("creator-tips"))
        self.assertContains(page, "¡Gracias!")
        self.assertContains(page, "500")

    def test_tip_limits_and_recipients(self):
        with self.assertRaises(ValidationError):
            create_tip(self.student, self.creator, 5)
        with self.assertRaises(PermissionDenied):
            create_tip(self.student, self.student, 100)
        with self.assertRaises(PermissionDenied):
            create_tip(self.creator, self.creator, 100)
        for _ in range(5):
            create_tip(self.student, self.creator, 100)
        with self.assertRaises(ValidationError):
            create_tip(self.student, self.creator, 100)

    def test_tip_pages_flow_with_silent_status_check(self):
        with patch("commerce.tips.LNbitsGateway", return_value=self.gateway):
            response = self.client.post(reverse("tip-create"), {"creador": self.creator.pk, "amount": 1000, "message": ""})
            tip = Tip.objects.get()
            self.assertRedirects(response, reverse("tip-detail", args=[tip.pk]), fetch_redirect_response=False)
            self.assertContains(self.client.get(reverse("tip-detail", args=[tip.pk])), reverse("tip-status", args=[tip.pk]))
            self.assertEqual(self.client.get(reverse("tip-status", args=[tip.pk])).json()["status"], "pending")
            self.client.post(reverse("tip-action", args=[tip.pk]), {"action": "pay"})
        tip.refresh_from_db()
        self.assertEqual(tip.status, "paid")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("tip-detail", args=[tip.pk])).status_code, 404)

    def test_provider_failure_keeps_one_tip_to_recover(self):
        tip = create_tip(self.student, self.creator, 100)
        class Down(fixtures.FakeGateway):
            def create(self, invoice):
                raise ProviderUnavailable("caído")
        with self.assertRaises(ProviderUnavailable):
            check_tip(tip, Down())
        tip.refresh_from_db()
        self.assertEqual(tip.issue_state, "unknown")
        tip = check_tip(tip, self.gateway)
        self.assertEqual(tip.issue_state, "ready")


@override_settings(LNBITS_REFUND_KEY="refund-key")
class RefundTests(FeatureFixture):
    def test_bolt11_amount_reading(self):
        self.assertEqual(requested_msat(INVOICE_150), 150000)
        self.assertEqual(requested_msat("LIGHTNING:" + INVOICE_150.upper()), 150000)
        self.assertEqual(requested_msat("lnbc2500u1pjtest"), 250000000)
        self.assertIsNone(requested_msat("lnbcrt1500n1pjtest"))
        self.assertIsNone(requested_msat("lnbc1pjtest"))
        with override_settings(COMMERCE_PAYMENT_MODE="regtest"):
            self.assertEqual(requested_msat("lnbcrt1500n1pjtest"), 150000)

    def test_approved_refund_pays_and_ends_only_that_access(self):
        invoice = self.pay(self.bundle)
        with self.assertRaises(ValidationError):
            request_refund(self.student, invoice.pk, "No era lo que esperaba", "lnbc700n1pjtest")
        refund = request_refund(self.student, invoice.pk, "No era lo que esperaba", INVOICE_150)
        self.assertTrue(owns_revision(self.student, self.records[1].content_id))
        gateway = PayingGateway()
        refund = approve_refund(self.admin, refund, "Aprobado", gateway)
        self.assertEqual((refund.status, gateway.payments), ("refunded", [INVOICE_150]))
        self.assertFalse(owns_revision(self.student, self.records[1].content_id))
        self.assertEqual(Purchase.objects.count(), 1)
        self.assertEqual(Entitlement.objects.count(), 4)
        # Buying again restores access through a new purchase.
        self.paid(self.direct(self.individual))
        self.assertTrue(owns_revision(self.student, self.records[1].content_id))
        self.assertFalse(owns_revision(self.student, self.records[2].content_id))

    def test_refunded_purchase_is_not_credit(self):
        lesson = self.pay(self.individual)
        refund = request_refund(self.student, lesson.pk, "Lo compré por error", "lnbc700n1pjtest")
        approve_refund(self.admin, refund, "", PayingGateway())
        self.pay(self.second_offer)
        self.assertEqual(upgrade_credit(self.student, self.bundle), 80)

    def test_unknown_payout_keeps_access_for_review_and_rejection_needs_reason(self):
        invoice = self.pay(self.bundle)
        refund = request_refund(self.student, invoice.pk, "No funciona para mí", INVOICE_150)
        class Down(PayingGateway):
            def pay(self, payment_request):
                raise ProviderUnavailable("incierto")
        refund = approve_refund(self.admin, refund, "", Down())
        self.assertEqual(refund.status, "review")
        self.assertTrue(owns_revision(self.student, self.records[1].content_id))
        with self.assertRaises(ValidationError):
            reject_refund(self.admin, refund, " ")
        reject_refund(self.admin, refund, "El pago consta como no enviado; contáctanos.")
        refund.refresh_from_db()
        self.assertEqual(refund.status, "rejected")

    @override_settings(LNBITS_REFUND_KEY="")
    def test_unconfigured_refunds_are_never_marked_as_sent(self):
        invoice = self.pay(self.bundle)
        refund = request_refund(self.student, invoice.pk, "No era lo que esperaba", INVOICE_150)
        with self.assertRaises(ValidationError):
            approve_refund(self.admin, refund, "", PayingGateway())
        refund.refresh_from_db()
        self.assertEqual(refund.status, "requested")

    def test_window_certificate_credit_and_permissions_block_requests(self):
        invoice = self.pay(self.individual)
        with self.assertRaises(PermissionDenied):
            approve_refund(self.student, Refund(pk=invoice.pk), "")
        self.paid(self.direct(self.bundle))
        self.assertIn("crédito", refund_blocker(Invoice.objects.get(pk=invoice.pk), self.student))
        later = timezone.now() + timedelta(days=9)
        bundle_invoice = Invoice.objects.filter(order__isnull=False).get()
        self.assertIn("plazo", refund_blocker(bundle_invoice, self.student, now=later))

    def test_refund_page_and_review_page(self):
        invoice = self.pay(self.bundle)
        self.assertContains(self.client.get(reverse("invoice-detail", args=[invoice.pk])), reverse("refund-request", args=[invoice.pk]))
        response = self.client.post(reverse("refund-request", args=[invoice.pk]), {"reason": "No era el nivel que buscaba", "payment_request": INVOICE_150})
        self.assertRedirects(response, reverse("invoice-detail", args=[invoice.pk]), fetch_redirect_response=False)
        refund = Refund.objects.get()
        self.assertEqual(self.client.get(reverse("refund-review", args=[refund.pk])).status_code, 403)
        self.client.force_login(self.admin)
        with patch("commerce.refunds.LNbitsGateway", return_value=PayingGateway()):
            self.client.post(reverse("refund-review", args=[refund.pk]), {"decision": "approve", "note": ""})
        refund.refresh_from_db()
        self.assertEqual(refund.status, "refunded")


@override_settings(LNBITS_REFUND_KEY="refund-key")
class ConsumerClaimTests(FeatureFixture):
    """Refund rules reviewed against the consumer protection law and the notices educators receive."""

    def test_withdrawal_window_lasts_eight_days(self):
        invoice = self.pay(self.bundle)
        bought = invoice.purchase.created_at
        self.assertEqual(refund_blocker(invoice, self.student, now=bought + timedelta(days=8) - timedelta(minutes=1)), "")
        self.assertIn("plazo", refund_blocker(invoice, self.student, now=bought + timedelta(days=8, minutes=1)))

    def test_claims_ignore_window_and_credit_but_keep_basic_checks(self):
        lesson = self.pay(self.individual)
        self.paid(self.direct(self.bundle))
        lesson = Invoice.objects.get(pk=lesson.pk)
        later = timezone.now() + timedelta(days=60)
        self.assertTrue(refund_blocker(lesson, self.student, now=later))
        self.assertEqual(refund_blocker(lesson, self.student, now=later, claim=True), "")
        with self.assertRaises(ValidationError):
            request_refund(self.student, lesson.pk, "El video no carga en ningún navegador", "lnbc700n1pjtest", kind="otro")
        with self.assertRaises(ValidationError):
            request_refund(self.student, lesson.pk, "El video no carga en ningún navegador", "lnbc700n1pjtest")
        refund = request_refund(self.student, lesson.pk, "El video no carga en ningún navegador", "lnbc700n1pjtest", kind=Refund.Kind.DEFECTIVE)
        self.assertTrue(refund.is_claim)
        self.assertEqual(refund.respond_by, refund.created_at + timedelta(days=15))
        self.assertIn("Ya existe", refund_blocker(Invoice.objects.get(pk=lesson.pk), self.student, claim=True))
        refund.kind = Refund.Kind.WITHDRAWAL
        with self.assertRaises(ValidationError):
            refund.save()

    def test_claim_page_from_the_invoice(self):
        invoice = self.pay(self.bundle)
        claim_url = reverse("refund-claim", args=[invoice.pk])
        self.assertContains(self.client.get(reverse("invoice-detail", args=[invoice.pk])), claim_url)
        self.assertContains(self.client.get(claim_url), "Tiene errores o archivos dañados")
        response = self.client.post(claim_url, {"kind": "mismatch", "reason": "El temario no coincide con la ficha", "payment_request": INVOICE_150})
        self.assertRedirects(response, reverse("invoice-detail", args=[invoice.pk]), fetch_redirect_response=False)
        self.assertEqual(Refund.objects.get().kind, "mismatch")
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("refund-review", args=[Refund.objects.get().pk])), "No corresponde a lo ofrecido")

    def test_educator_hears_about_sales_and_refunds_without_student_data(self):
        invoice = self.pay(self.bundle)
        sale = Notification.objects.get(recipient=self.creator, event_key__startswith="sale:")
        self.assertIn(f"{invoice.amount_sats} sats", sale.title)
        self.assertNotIn(self.student.email, sale.title)
        refund = request_refund(self.student, invoice.pk, "No era el nivel que buscaba", INVOICE_150)
        self.assertTrue(Notification.objects.filter(recipient=self.creator, event_key__startswith=f"refund-requested:{refund.pk}").exists())
        approve_refund(self.admin, refund, "", PayingGateway())
        resolved = Notification.objects.get(recipient=self.creator, event_key__startswith=f"refund-resolved:{refund.pk}")
        self.assertIn("Reembolsamos", resolved.title)

    def test_sales_volume_leaves_out_refunded_purchases(self):
        from core.analytics import dashboard_data
        invoice = self.pay(self.bundle)
        today = timezone.localdate()
        self.assertEqual(dashboard_data(today, today, self.creator)["volume"], invoice.amount_sats)
        approve_refund(self.admin, request_refund(self.student, invoice.pk, "No era el nivel que buscaba", INVOICE_150), "", PayingGateway())
        data = dashboard_data(today, today, self.creator)
        self.assertEqual((data["volume"], data["refunded_volume"], data["sold_count"]), (0, invoice.amount_sats, 0))
        self.assertEqual(data["refunds"][0].reason, "No era el nivel que buscaba")
        self.client.force_login(self.creator)
        self.assertContains(self.client.get(reverse("creator-analytics")), "Reembolsos y reclamos")


@override_settings(LNBITS_REFUND_KEY="refund-key")
class GiftRefundTests(FeatureFixture):
    def test_unredeemed_gift_is_refundable_and_its_link_stops_working(self):
        invoice = self.paid(self.direct(self.bundle, gift=True))
        gift = Gift.objects.get()
        self.assertEqual(refund_blocker(invoice, self.student), "")
        refund = request_refund(self.student, invoice.pk, "", INVOICE_150)
        self.assertEqual(refund.reason, "")
        with self.assertRaises(ValidationError):
            redeem_gift(self.other, gift.token)
        reject_refund(self.admin, refund, "El regalo se puede canjear de nuevo.")
        redeem_gift(self.other, gift.token)

    def test_redeemed_gift_is_not_refundable(self):
        invoice = self.paid(self.direct(self.bundle, gift=True))
        redeem_gift(self.other, Gift.objects.get().token)
        invoice = Invoice.objects.get(pk=invoice.pk)
        self.assertIn("canjeado", refund_blocker(invoice, self.student))
        self.assertIn("canjeado", refund_blocker(invoice, self.student, claim=True))

    def test_withdrawal_needs_no_reason_but_a_claim_does(self):
        invoice = self.pay(self.bundle)
        response = self.client.post(reverse("refund-request", args=[invoice.pk]), {"reason": "", "payment_request": INVOICE_150})
        self.assertRedirects(response, reverse("invoice-detail", args=[invoice.pk]), fetch_redirect_response=False)
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("refund-review", args=[Refund.objects.get().pk])), "no requiere justificación")
        from .refunds import valid_request
        self.assertEqual(valid_request("", INVOICE_150, 150)[0], "")
        with self.assertRaises(ValidationError):
            valid_request("corto", INVOICE_150, 150, claim=True)

    def test_admin_home_lists_open_requests_with_their_deadline(self):
        invoice = self.pay(self.bundle)
        refund = request_refund(self.student, invoice.pk, "", INVOICE_150)
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "1 solicitud de reembolso por responder.")
        self.assertContains(response, f"{timezone.localtime(refund.respond_by):%d/%m/%Y}")
        approve_refund(self.admin, refund, "", PayingGateway())
        self.assertNotContains(self.client.get(reverse("admin:index")), "por responder")
