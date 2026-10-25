from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from content.models import Material
from content.publication import publish_course, publish_resource
from content.testing import EDUCATION_FIXTURE

from . import tests as fixtures
from .cart import GUEST_KEY, PENDING_KEY, UNDO_KEY, add_item, cart_summary
from .gateway import ProviderStatus, ProviderUnavailable
from .models import Cart, CartItem, Entitlement, Invoice, Offer, Order
from .orders import quote_order, reserve_order
from .services import ensure_emitted, settle


@override_settings(COMMERCE_PAYMENT_MODE="fake", ACCOUNT_REQUIRE_VERIFIED_EMAIL=False,
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CartJourneyTests(TestCase):
    setUp = fixtures.CommerceJourneyTests.setUp
    activate = fixtures.CommerceJourneyTests.activate
    invoice = fixtures.CommerceJourneyTests.invoice
    pay = fixtures.CommerceJourneyTests.pay

    def add(self, offer=None, client=None, **data):
        return (client or self.client).post(reverse("cart-add", args=[(offer or self.individual).pk]), data)

    def review(self, direct=None, **query):
        return self.client.get(reverse("direct-checkout", args=[direct.pk]) if direct else reverse("cart-checkout"), query)

    def pay_review(self, response, direct=None, **extra):
        quote = response.context["selection"]
        payload = {"token": quote["token"], "request_key": quote["request_key"], **extra}
        if direct:
            payload["leccion"] = response.context["selected_lesson_id"]
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            return self.client.post(reverse("direct-checkout", args=[direct.pk]) if direct else reverse("cart-checkout"), payload)

    def login_visitor(self, visitor):
        self.student.set_password("Cart-journey-34718!")
        self.student.save(update_fields=("password",))
        return visitor.post(reverse("login"), {"username": self.student.email, "password": "Cart-journey-34718!",
                                                "next": reverse("cart-checkout")})

    def test_reading_empty_carts_creates_no_selection_and_grants_no_access(self):
        guest = Client()
        self.assertEqual(guest.get(reverse("cart")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cart")).status_code, 200)
        request = RequestFactory().get(reverse("cart"))
        request.user, request.session = AnonymousUser(), {}
        self.assertEqual(cart_summary(request)["cart_count"], 0)
        self.assertFalse(Cart.objects.exists())
        self.assertFalse(Entitlement.objects.exists())
        self.assertFalse(Invoice.objects.exists())

    def test_guest_add_is_idempotent_and_preserves_explicit_lesson_without_rights(self):
        guest = Client()
        for _ in range(2):
            response = guest.post(reverse("cart-add", args=[self.individual.pk]), {"leccion": self.records[1].pk,
                                  "next": "https://outside.invalid/"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["cart_count"], 1)
            self.assertEqual(response.json()["redirect"], reverse("cart"))
        cart = Cart.objects.get(pk=guest.session[GUEST_KEY])
        self.assertIsNone(cart.buyer_id)
        self.assertEqual(cart.items.get().return_lesson_id, self.records[1].pk)
        self.assertFalse(Entitlement.objects.exists())
        self.assertFalse(Order.objects.exists())

    def test_foreign_origin_and_unavailable_offer_cannot_be_added(self):
        response = self.add(leccion=self.records[2].pk)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CartItem.objects.exists())
        Offer.objects.filter(pk=self.individual.pk).update(status="archived")
        self.add()
        self.assertFalse(CartItem.objects.exists())

    def test_mutations_require_post_csrf_and_student_role(self):
        self.assertEqual(self.client.get(reverse("cart-add", args=[self.individual.pk])).status_code, 405)
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.student)
        self.assertEqual(secure.post(reverse("cart-add", args=[self.individual.pk])).status_code, 403)
        self.client.force_login(self.creator)
        self.assertEqual(self.add().status_code, 403)
        self.assertEqual(self.client.get(reverse("cart")).status_code, 403)
        self.assertEqual(self.client.post(reverse("direct-checkout", args=[self.individual.pk])).status_code, 403)

    def test_guest_checkout_cannot_reserve_an_order_and_direct_get_is_read_only(self):
        guest = Client()
        self.add(client=guest)
        response = guest.post(reverse("cart-checkout"), {"token": "invented"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        preview = guest.get(reverse("direct-checkout", args=[self.individual.pk]))
        self.assertContains(preview, "Entrar y continuar")
        self.assertEqual(preview.context["selection"]["token"], "")
        self.assertFalse(Invoice.objects.exists())
        self.assertFalse(Entitlement.objects.exists())

    def test_get_does_not_merge_guest_choice_and_login_returns_to_checkout_with_selection(self):
        visitor = Client()
        self.add(client=visitor)
        guest_id = visitor.session[GUEST_KEY]
        visitor.force_login(self.student)
        self.assertEqual(visitor.get(reverse("cart")).context["selection"]["lines"], [])
        self.assertIsNone(Cart.objects.get(pk=guest_id).buyer_id)
        visitor.logout()
        self.add(client=visitor)
        fresh_guest_id = visitor.session[GUEST_KEY]
        response = self.login_visitor(visitor)
        self.assertEqual(response.url, reverse("cart-checkout"))
        self.assertEqual(Cart.objects.get(pk=fresh_guest_id).buyer_id, self.student.pk)
        self.assertNotIn(GUEST_KEY, visitor.session)
        self.assertEqual(visitor.get(reverse("cart")).context["selection"]["total_sats"], 70)

    def test_login_merges_duplicate_offers_and_keeps_both_distinct_selections(self):
        self.add(leccion=self.records[1].pk)
        own = Cart.objects.get(buyer=self.student)
        visitor = Client()
        self.add(client=visitor)
        self.add(self.file_offer, client=visitor)
        self.login_visitor(visitor)
        self.assertEqual(set(own.items.values_list("offer_id", flat=True)), {self.individual.pk, self.file_offer.pk})
        self.assertEqual(own.items.get(offer=self.individual).return_lesson_id, self.records[1].pk)
        self.assertNotIn(GUEST_KEY, visitor.session)

    def test_identity_switch_cannot_read_remove_or_mutate_previous_account_cart(self):
        self.add()
        own = Cart.objects.get(buyer=self.student)
        item = own.items.get()
        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(reverse("cart")), self.individual.title)
        self.assertEqual(self.client.post(reverse("cart-remove", args=[item.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("cart-add", args=[self.file_offer.pk]), {"account_id": self.student.pk}).status_code, 403)
        self.assertTrue(own.items.filter(pk=item.pk).exists())
        with self.assertRaises(PermissionDenied):
            add_item(self.other, own, self.file_offer.pk)

    def test_guest_marker_cannot_expose_a_persistent_buyer_cart(self):
        self.add()
        cart = Cart.objects.get(buyer=self.student)
        guest = Client()
        session = guest.session
        session[GUEST_KEY] = str(cart.pk)
        session.save()
        self.assertNotContains(guest.get(reverse("cart")), self.individual.title)
        self.assertIsNotNone(Cart.objects.get(pk=cart.pk).buyer_id)

    def test_remove_and_undo_restore_once_without_creating_permissions(self):
        self.add(leccion=self.records[1].pk)
        cart = Cart.objects.get(buyer=self.student)
        item = cart.items.get()
        self.client.post(reverse("cart-remove", args=[item.pk]))
        self.assertFalse(cart.items.exists())
        key = self.client.session[UNDO_KEY]["key"]
        for _ in range(2):
            self.client.post(reverse("cart-undo"), {"key": key})
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.get().return_lesson_id, self.records[1].pk)
        self.assertNotIn(UNDO_KEY, self.client.session)
        self.assertFalse(Entitlement.objects.exists())

    def test_nested_overlap_is_explicit_and_blocks_checkout_until_user_removes_one(self):
        self.add()
        self.add(self.bundle)
        response = self.client.get(reverse("cart"))
        self.assertFalse(response.context["selection"]["can_checkout"])
        self.assertContains(response, "más de una oferta")
        self.assertEqual(response.context["selection"]["eligible_total_sats"], 70)
        failed = self.client.post(reverse("cart-checkout"), {"token": "", "request_key": ""})
        self.assertEqual(failed.status_code, 409)
        self.assertFalse(Order.objects.exists())
        cart = Cart.objects.get(buyer=self.student)
        self.client.post(reverse("cart-remove", args=[cart.items.get(offer=self.individual).pk]))
        self.assertTrue(self.review().context["selection"]["can_checkout"])

    def test_owned_and_partial_diagnostics_do_not_count_already_owned_content_as_charge(self):
        self.add(self.bundle)
        self.pay(self.individual)
        partial = self.client.get(reverse("cart"))
        # A partly owned package is completed for the difference, never charged again.
        self.assertTrue(partial.context["selection"]["can_checkout"])
        self.assertEqual(partial.context["selection"]["total_sats"], 80)
        self.assertEqual(partial.context["selection"]["credit_total_sats"], 70)
        self.assertContains(partial, "Reconocemos 70 sats")
        Entitlement.objects.get_or_create(buyer=self.student, resource=self.records[2].content)
        Entitlement.objects.get_or_create(buyer=self.student, resource=self.resource)
        owned = self.client.get(reverse("cart"))
        self.assertContains(owned, "Ya adquirido")
        self.assertEqual(owned.context["selection"]["eligible_total_sats"], 0)
        self.assertNotContains(owned, 'class="cart-item-price">150 <small>sats</small>')

    def test_replaced_price_is_preserved_for_review_and_never_substituted_silently(self):
        self.add()
        new = self.activate(f"lesson:{self.records[1].pk}", "Texto actualizado", 95)
        response = self.client.get(reverse("cart"))
        self.assertFalse(response.context["selection"]["can_checkout"])
        self.assertContains(response, self.individual.title)
        self.assertContains(response, "Revisar opción actual")
        self.assertContains(response, reverse("offer-detail", args=[new.pk]))
        self.assertEqual(CartItem.objects.get().offer_id, self.individual.pk)

    def test_direct_review_of_replaced_option_returns_to_current_option(self):
        new = self.activate(f"lesson:{self.records[1].pk}", "Texto actualizado", 95)
        response = self.review(direct=self.individual)
        self.assertFalse(response.context["selection"]["can_checkout"])
        self.assertEqual(response.context["return_url"], reverse("offer-detail", args=[new.pk]))
        self.assertContains(response, "Revisar opciones")
        self.assertFalse(Order.objects.exists())

    def test_direct_post_requires_signed_review_and_ignores_posted_price(self):
        missing = self.client.post(reverse("direct-checkout", args=[self.individual.pk]), {"amount_sats": "1"})
        self.assertEqual(missing.status_code, 409)
        self.assertFalse(Order.objects.exists())
        review = self.review(direct=self.individual, leccion=self.records[1].pk)
        response = self.pay_review(review, direct=self.individual, amount_sats="1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Invoice.objects.get().amount_sats, 70)
        self.assertFalse(Entitlement.objects.exists())

    def test_direct_purchase_preserves_general_cart_and_token_retry_returns_same_invoice(self):
        self.add(self.file_offer)
        cart = Cart.objects.get(buyer=self.student)
        review = self.review(direct=self.individual, leccion=self.records[1].pk)
        first = self.pay_review(review, direct=self.individual)
        second = self.pay_review(review, direct=self.individual)
        self.assertEqual(first.url, second.url)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(cart.items.get().offer_id, self.file_offer.pk)
        self.assertIsNone(Order.objects.get().cart_id)

    def test_expired_direct_order_reviews_successor_and_keeps_original_snapshot(self):
        review = self.review(direct=self.bundle, leccion=self.records[1].pk)
        self.pay_review(review, direct=self.bundle)
        original = Invoice.objects.get()
        Invoice.objects.filter(pk=original.pk).update(expires_at=timezone.now() - timedelta(seconds=1))
        successor = self.activate(f"course:{self.version.pk}", "Precio actualizado", 180)
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            detail = self.client.get(reverse("invoice-detail", args=[original.pk]))
        expected = reverse("direct-checkout", args=[successor.pk]) + f"?leccion={self.records[1].pk}"
        self.assertEqual(detail.context["retry_url"], expected)
        self.assertContains(detail, expected)
        current = self.client.get(expected)
        self.assertEqual(current.context["selection"]["total_sats"], 180)
        self.assertEqual(current.context["selection"]["lines"][0]["return_lesson_id"], self.records[1].pk)
        original.refresh_from_db()
        line = original.order.lines.get()
        self.assertEqual((original.status, original.amount_sats, line.offer_id, line.amount_sats),
                         ("expired", 150, self.bundle.pk, 150))
        self.assertEqual(line.return_lesson_id, self.records[1].pk)
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertFalse(Entitlement.objects.exists())

    def test_direct_retry_revalidates_origin_when_successor_has_another_version(self):
        review = self.review(direct=self.bundle, leccion=self.records[1].pk)
        self.pay_review(review, direct=self.bundle)
        original = Invoice.objects.get()
        settle(original.pk, ProviderStatus(False, 150000, original.payment_hash, True))
        self.lesson.body = "Texto de una nueva versión"
        self.lesson.save()
        current_version = publish_course(self.course, self.admin)
        for lesson in current_version.chapters.first().lessons.select_related("content"):
            if lesson.content.access_type == "paid":
                self.activate(f"lesson:{lesson.pk}", f"Texto vigente {lesson.pk}", 70)
        successor = self.activate(f"course:{current_version.pk}", "Nueva versión", 190)
        with patch("commerce.services.LNbitsGateway", return_value=self.gateway):
            detail = self.client.get(reverse("invoice-detail", args=[original.pk]))
        expected = reverse("direct-checkout", args=[successor.pk])
        self.assertEqual(detail.context["retry_url"], expected)
        current = self.client.get(expected)
        self.assertIsNone(current.context["selection"]["lines"][0]["return_lesson_id"])
        self.assertEqual(current.context["selection"]["lines"][0]["course_version"].pk, current_version.pk)
        self.assertEqual(original.order.lines.get().return_lesson_id, self.records[1].pk)
        self.assertEqual(Invoice.objects.count(), 1)
        self.assertFalse(Entitlement.objects.exists())

    def test_cart_author_fallback_does_not_publish_private_name(self):
        self.add()
        self.creator.first_name = "Nombre privado del autor"
        self.creator.save(update_fields=("first_name",))
        self.creator.creator_profile.delete()
        response = self.client.get(reverse("cart"))
        self.assertEqual(response.context["selection"]["lines"][0]["creator_name"], "Educador")
        self.assertNotContains(response, "Nombre privado del autor")
        review = self.review(direct=self.individual)
        self.assertContains(review, f"El acceso se añadirá a tu cuenta: <strong>{self.student.email}</strong>")

    def test_changed_cart_or_price_requires_a_new_review_without_invoice(self):
        self.add()
        review = self.review()
        self.add(self.file_offer)
        changed = self.pay_review(review)
        self.assertEqual(changed.status_code, 409)
        self.assertFalse(Invoice.objects.exists())
        fresh = self.review()
        Offer.objects.filter(pk=self.individual.pk).update(amount_sats=99)
        repriced = self.pay_review(fresh)
        self.assertEqual(repriced.status_code, 409)
        self.assertFalse(Order.objects.exists())
        self.assertContains(repriced, 'class="cart-item-price">99 <small>sats</small>', status_code=409)

    def test_payment_keeps_new_cart_items_and_replay_survives_cart_changes(self):
        self.add()
        cart = Cart.objects.get(buyer=self.student)
        review = self.review()
        first = self.pay_review(review)
        invoice = Invoice.objects.get()
        self.add(self.file_offer)
        replay = self.pay_review(review)
        self.assertEqual(replay.url, first.url)
        self.assertEqual(Invoice.objects.count(), 1)
        settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))
        self.assertEqual(list(cart.items.values_list("offer_id", flat=True)), [self.file_offer.pk])
        self.assertTrue(Entitlement.objects.filter(buyer=self.student, resource=self.records[1].content).exists())
        self.assertFalse(Entitlement.objects.filter(buyer=self.student, resource=self.resource).exists())

    def test_provider_failure_retains_same_reserved_invoice_for_recovery(self):
        self.add()
        review = self.review()
        with patch("commerce.cart_views.ensure_emitted", side_effect=ProviderUnavailable("offline")):
            first = self.client.post(reverse("cart-checkout"), {"token": review.context["selection"]["token"],
                                     "request_key": review.context["selection"]["request_key"]})
        self.assertEqual(first.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        second = self.pay_review(review)
        self.assertEqual(first.url, second.url)
        self.assertEqual(Invoice.objects.count(), 1)

    def test_pending_payment_is_linked_in_cart_before_another_checkout(self):
        self.add()
        quote = quote_order(self.student, Cart.objects.get(buyer=self.student))
        invoice = ensure_emitted(reserve_order(self.student, Cart.objects.get(buyer=self.student), quote["token"]), self.gateway)
        response = self.client.get(reverse("cart"))
        self.assertFalse(response.context["selection"]["can_checkout"])
        self.assertContains(response, reverse("invoice-detail", args=[invoice.pk]))
        self.assertContains(response, "Consultar pago pendiente")

    def test_saving_for_later_removes_only_after_successful_bookmark(self):
        self.add(self.bundle)
        cart = Cart.objects.get(buyer=self.student)
        item = cart.items.get()
        from learning.models import SavedItem
        self.client.post(reverse("cart-save", args=[item.pk]))
        self.assertFalse(cart.items.exists())
        self.assertTrue(SavedItem.objects.filter(student=self.student, course_version=self.version).exists())
        self.add(self.file_offer)
        item = cart.items.get()
        with patch("learning.bookmarks.save_item", side_effect=PermissionDenied):
            self.client.post(reverse("cart-save", args=[item.pk]))
        self.assertTrue(cart.items.filter(pk=item.pk).exists())
        self.assertFalse(Entitlement.objects.exists())

    def test_capacity_limit_preserves_visitor_choice_until_explicit_merge_has_room(self):
        cart = Cart.objects.create(buyer=self.student)
        for number in range(20):
            material = Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, title=f"Material {number}",
                         description="Material para el límite de selección", access_type="paid", pending_asset=self.resource.asset)
            resource = publish_resource(material, self.admin)
            offer = self.activate(f"resource:{resource.pk}", f"Material {number}", 1)
            add_item(self.student, cart, offer.pk)
        rejected = self.add()
        self.assertEqual(rejected.status_code, 302)
        self.assertEqual(cart.items.count(), 20)
        visitor = Client()
        self.add(client=visitor)
        guest_id = visitor.session[GUEST_KEY]
        guest_item = Cart.objects.get(pk=guest_id).items.get()
        self.login_visitor(visitor)
        self.assertIn(PENDING_KEY, visitor.session)
        self.assertEqual(cart.items.count(), 20)
        self.assertTrue(CartItem.objects.filter(pk=guest_item.pk, cart_id=guest_id).exists())
        self.assertContains(visitor.get(reverse("cart")), "Lo que elegiste como visitante")
        visitor.post(reverse("cart-remove", args=[cart.items.first().pk]))
        visitor.post(reverse("cart-merge"), {"items": [str(guest_item.pk)]})
        self.assertEqual(cart.items.count(), 20)
        self.assertEqual(CartItem.objects.get(pk=guest_item.pk).cart_id, cart.pk)
        self.assertNotIn(PENDING_KEY, visitor.session)
