from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from commerce.bundles import bundle_quote, reserve_path_order
from commerce.gateway import ProviderStatus
from commerce.models import Coupon, Entitlement, OrderLine
from commerce.offers import create_offer, review_offer, submit_offer
from commerce.orders import order_snapshot_valid
from commerce.services import ensure_emitted, settle
from commerce.tests import FakeGateway
from content.models import Chapter, Course, Lesson
from content.publication import publish_course
from content.testing import EDUCATION_FIXTURE
from creators.models import CreatorProfile

from .models import LearningPath, PathCourse
from .paths import issue_path_credential, path_progress, save_creator_path
from .services import enroll, save_progress


@override_settings(COMMERCE_PAYMENT_MODE="fake", ACCOUNT_REQUIRE_VERIFIED_EMAIL=False, SECURE_SSL_REDIRECT=False)
class LearningPathTests(TestCase):
    def setUp(self):
        users = get_user_model().objects
        self.creator = users.create_user("paths.creator@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=self.creator, display_name="Educadora", status="approved")
        self.admin = users.create_superuser("paths.admin@example.invalid")
        self.student = users.create_user("paths.student@example.invalid")
        self.sold = [self.sold_course(f"Curso {index}", price) for index, price in enumerate((1000, 2000, 3000), 1)]
        self.path = LearningPath.objects.create(title="Ruta de prueba", slug="ruta-prueba", summary="Resumen", published=True, bundle_percent=20)
        for position, (course, _, _) in enumerate(self.sold, 1):
            PathCourse.objects.create(path=self.path, course=course, position=position, optional=position == 3)

    def approve(self, target, title, amount, creator=None):
        offer = create_offer(creator or self.creator, target, title, amount)
        submit_offer(creator or self.creator, offer)
        return review_offer(self.admin, offer, True)

    def sold_course(self, title, price, creator=None):
        creator = creator or self.creator
        course = Course.objects.create(creator=creator, title=title, description="Descripción", status="published", estimated_minutes=90)
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Gratis", body="Texto", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="De pago", body="Texto", access_type="paid", status="published", position=2)
        version = publish_course(course, self.admin)
        lesson = version.chapters.first().lessons.get(position=2)
        self.approve(f"lesson:{lesson.pk}", f"{title} · lección", price // 2, creator)
        return course, version, self.approve(f"course:{version.pk}", title, price, creator)

    def complete(self, version):
        enrollment = enroll(self.student, version)
        for revision, record in enumerate(version.chapters.first().lessons.order_by("position")):
            Entitlement.objects.get_or_create(buyer=self.student, resource=record.content)
            save_progress(self.student, enrollment.pk, record.pk, revision, "complete")

    def test_bundle_discounts_each_missing_course_and_grants_access(self):
        quote = bundle_quote(self.student, self.path)
        self.assertEqual((quote["list_total_sats"], quote["discount_total_sats"], quote["total_sats"]), (6000, 1200, 4800))
        self.assertTrue(quote["can_checkout"])
        invoice = reserve_path_order(self.student, self.path, quote["token"], quote["request_key"])
        self.assertEqual((invoice.amount_sats, invoice.title), (4800, "Ruta · Ruta de prueba"))
        self.assertEqual(set(OrderLine.objects.values_list("path_id", flat=True)), {self.path.pk})
        self.assertTrue(order_snapshot_valid(invoice))
        self.assertEqual(reserve_path_order(self.student, self.path, quote["token"], quote["request_key"]).pk, invoice.pk)
        invoice = ensure_emitted(invoice, FakeGateway())
        settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))
        self.assertEqual(Entitlement.objects.filter(buyer=self.student, resource__access_type="paid").count(), 3)

    def test_bundle_skips_owned_courses_and_needs_two_to_buy(self):
        _, version, _ = self.sold[0]
        Entitlement.objects.create(buyer=self.student, resource=version.chapters.first().lessons.get(position=2).content)
        quote = bundle_quote(self.student, self.path)
        self.assertEqual([line["offer"].pk for line in quote["lines"]], [self.sold[1][2].pk, self.sold[2][2].pk])
        _, version, _ = self.sold[1]
        Entitlement.objects.create(buyer=self.student, resource=version.chapters.first().lessons.get(position=2).content)
        self.assertFalse(bundle_quote(self.student, self.path)["can_checkout"])
        self.path.bundle_percent = 0
        self.path.save()
        self.assertFalse(bundle_quote(AnonymousUser(), self.path)["can_checkout"])

    def test_changed_discount_invalidates_the_review(self):
        quote = bundle_quote(self.student, self.path)
        LearningPath.objects.filter(pk=self.path.pk).update(bundle_percent=30)
        self.path.refresh_from_db()
        with self.assertRaises(ValidationError):
            reserve_path_order(self.student, self.path, quote["token"], quote["request_key"])
        other = LearningPath.objects.create(title="Otra", slug="otra", summary="Otra", published=True, bundle_percent=20)
        with self.assertRaises(PermissionDenied):
            reserve_path_order(self.student, other, quote["token"], quote["request_key"])

    def test_checkout_page_hides_coupons_and_reserves_the_bundle(self):
        Coupon.objects.create(creator=self.creator, code="RUTA", percent_off=50, starts_at="2026-01-01T00:00Z", expires_at="2099-01-01T00:00Z", max_uses=5)
        page = self.client.get(reverse("learning-path", args=[self.path.slug]))
        self.assertContains(page, "Paquete de la ruta")
        self.assertContains(page, "4800")
        self.client.force_login(self.student)
        review = self.client.get(reverse("path-checkout", args=[self.path.slug]) + "?cupon=RUTA")
        self.assertNotContains(review, 'name="cupon"')
        self.assertContains(review, "Paquete de la ruta · 20&nbsp;%")
        selection = review.context["selection"]
        response = self.client.post(reverse("path-checkout", args=[self.path.slug]), {"token": selection["token"], "request_key": selection["request_key"]})
        line = OrderLine.objects.first()
        self.assertRedirects(response, reverse("invoice-detail", args=[line.order.invoice.pk]), fetch_redirect_response=False)
        self.assertIsNone(line.coupon_id)

    def test_optional_steps_never_block_the_credential(self):
        for course, version, _ in self.sold[:2]:
            self.complete(version)
        progress = path_progress(self.student, self.path)
        self.assertEqual((progress["required_finished"], progress["required_total"], progress["percentage"], progress["eligible"]), (2, 2, 100, True))
        self.assertEqual(progress["next"]["course"].pk, self.sold[2][0].pk)
        completion = issue_path_credential(self.student, self.path, "Ana")
        self.assertEqual(len(completion.evidence), 2)
        self.assertNotIn("optional", str(completion.evidence))

    def test_suggestion_follows_the_last_finished_step(self):
        self.complete(self.sold[1][1])
        self.assertEqual(path_progress(self.student, self.path)["next"]["course"].pk, self.sold[2][0].pk)
        enroll(self.student, self.sold[0][1])
        self.assertEqual(path_progress(self.student, self.path)["next"]["course"].pk, self.sold[0][0].pk)

    def test_creators_curate_only_their_published_courses(self):
        other = get_user_model().objects.create_user("paths.other@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=other, display_name="Otra", status="approved")
        foreign, _, _ = self.sold_course("Ajeno", 500, other)
        steps = [{"course": course, "optional": False, "note": ""} for course, _, _ in self.sold[:2]]
        fields = {"title": "Mi ruta", "summary": "Corta", "description": "", "bundle_percent": 10, "published": True}
        path = save_creator_path(self.creator, LearningPath(), fields, steps)
        self.assertEqual((path.creator_id, path.slug, path.steps.count()), (self.creator.pk, "mi-ruta", 2))
        with self.assertRaises(ValidationError):
            save_creator_path(self.creator, LearningPath(), fields, steps + [{"course": foreign, "optional": False, "note": ""}])
        with self.assertRaises(ValidationError):
            save_creator_path(self.creator, LearningPath(), fields, [{**step, "optional": True} for step in steps])
        with self.assertRaises(PermissionDenied):
            save_creator_path(other, path, fields, [])

    def test_studio_form_orders_steps_and_marks_optional(self):
        self.client.force_login(self.creator)
        first, second, third = (course for course, _, _ in self.sold)
        response = self.client.post(reverse("creator-path-new"), {
            "title": "Ruta del estudio", "summary": "Resumen", "description": "", "bundle_percent": "15", "published": "on",
            f"curso-{third.pk}": "on", f"orden-{third.pk}": "1", f"curso-{first.pk}": "on", f"orden-{first.pk}": "2",
            f"opcional-{first.pk}": "on", f"nota-{first.pk}": "  Repaso   breve ", f"orden-{second.pk}": "3"})
        path = LearningPath.objects.get(slug="ruta-del-estudio")
        self.assertRedirects(response, reverse("creator-path", args=[path.pk]), fetch_redirect_response=False)
        self.assertEqual([(step.course_id, step.optional, step.note) for step in path.steps.all()],
                         [(third.pk, False, ""), (first.pk, True, "Repaso breve")])
        self.assertContains(self.client.get(reverse("creator-paths")), "Ruta del estudio")
        stranger = get_user_model().objects.create_user("paths.third@example.invalid", account_type="creator")
        CreatorProfile.objects.create(user=stranger, display_name="Tercera", status="approved")
        self.client.force_login(stranger)
        self.assertEqual(self.client.get(reverse("creator-path", args=[path.pk])).status_code, 404)
