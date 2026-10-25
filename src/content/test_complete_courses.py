from copy import deepcopy
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from commerce.gateway import ProviderStatus
from commerce.membership import check_membership, create_membership_payment
from commerce.models import Entitlement, MembershipPlan, Offer
from commerce.services import ensure_emitted, reserve_invoice, settle
from commerce.tests import FakeGateway
from creators.models import Submission
from learning.assessment_services import save_attempt, start_attempt
from learning.certificates import completion_status, issue_certificate
from learning.models import PracticeIntake, VersionPractice, VersionQuiz
from learning.quizzes import validate_questions
from learning.services import enroll, save_progress

from .course_catalog import CREATOR_EMAIL, REVIEWER_EMAIL, access_model, load_catalog
from .management.commands.load_complete_courses import publish_collection
from .models import (
    Category,
    Course,
    CourseVersion,
    Lesson,
    ResourceVersion,
    Topic,
    VersionLesson,
)
from .reading import reading_sections, video_embed
from .templatetags.course_media import PHOTOS


class CourseReadingTests(SimpleTestCase):
    def test_code_preserves_indentation_blank_lines_and_escapes_html(self):
        code = 'def total():\n    value = "<script>alert(1)</script>"\n\n    return value'
        body = f"Explicación\n\nEjemplo\n\n```python\n{code}\n```\n\nPráctica\n\nModifica la función.\n\nSolución y comprobación\n\nRetorna el valor."
        sections = reading_sections(body)
        blocks = [block for section in sections for block in section["blocks"] if block["code"]]
        self.assertEqual(blocks[0]["text"], code)
        self.assertEqual([section["kind"] for section in sections], ["text", "example", "practice", "solution"])
        rendered = render_to_string("content/_reading.html", {"reading_sections": sections})
        self.assertIn('    value = &quot;&lt;script&gt;', rendered)
        self.assertNotIn("<script>alert", rendered)
        self.assertIn('<details class="reading-solution">', rendered)

    def test_video_players_accept_only_youtube_and_keep_links_as_fallback(self):
        allowed = "https://www.youtube.com/watch?v=EFv9ubbZLKw"
        self.assertEqual(video_embed(allowed), "https://www.youtube-nocookie.com/embed/EFv9ubbZLKw")
        for url in ("https://youtube.com.evil.test/watch?v=EFv9ubbZLKw", "https://example.com/iframe", "javascript:alert(1)"):
            self.assertEqual(video_embed(url), "")
        sections = reading_sections(f"Video complementario\nFoco de teclado\n{allowed}\n\nPara profundizar\nDocumentación.")
        rendered = render_to_string("content/_reading.html", {"reading_sections": sections})
        self.assertIn('src="https://www.youtube-nocookie.com/embed/EFv9ubbZLKw"', rendered)
        self.assertIn(allowed, rendered)


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_REQUIRE_VERIFIED_EMAIL=False)
class CompleteCoursesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.catalog = load_catalog()
        publish_collection(cls.catalog)
        cls.student = get_user_model().objects.create_user(
            "catalog-student@example.invalid", account_type="student",
        )

    def courses(self):
        return Course.objects.filter(creator__email=CREATOR_EMAIL).select_related("current_version", "topic__category")

    def buy(self, offer):
        invoice = ensure_emitted(reserve_invoice(self.student, offer.pk), FakeGateway())
        return settle(invoice.pk, ProviderStatus(True, invoice.amount_sats * 1000, invoice.payment_hash))

    def by_model(self, model):
        titles = {item["title"] for item in self.catalog if access_model(item) == model}
        return self.courses().filter(title__in=titles)

    def course_offer(self, course):
        return Offer.objects.filter(kind="course", course_version=course.current_version, status="active").first()

    def grant(self, course):
        """Open a course through its own access model: a course offer or the membership."""
        offer = self.course_offer(course)
        if offer:
            return self.buy(offer)
        payment = create_membership_payment(self.student, MembershipPlan.objects.get(active=True))
        return check_membership(payment, FakeGateway(), simulate=True)

    def test_original_content_has_complete_curricula_and_valid_module_assessments(self):
        count = len(self.catalog)
        self.assertEqual(self.courses().count(), count)
        self.assertEqual(Lesson.objects.filter(chapter__course__in=self.courses()).count(), 12 * count)
        for course in self.courses():
            version = course.current_version
            self.assertTrue(version.sealed and version.published_at)
            self.assertEqual(version.chapters.count(), 4)
            self.assertEqual(VersionQuiz.objects.filter(lesson__chapter__version=version).count(), 4)
            self.assertEqual(VersionPractice.objects.filter(lesson__chapter__version=version).count(), 1)
            self.assertEqual(len(version.certificate_policy.required_lesson_ids), 12)
        for quiz in VersionQuiz.objects.filter(lesson__chapter__version__course__in=self.courses()):
            validate_questions(quiz.questions)
            self.assertEqual(len(quiz.questions), 4)
            self.assertTrue(quiz.required)
        self.assertEqual(Submission.objects.filter(course__in=self.courses(), status="approved").count(), count)

    def test_catalog_offers_paid_freemium_and_membership_courses(self):
        for model in ("paid", "freemium", "membership"):
            self.assertTrue(self.by_model(model).exists(), model)
        self.assertEqual(set(self.by_model("membership").values_list("membership", flat=True)), {True})
        self.assertFalse(self.courses().exclude(pk__in=self.by_model("membership")).filter(membership=True).exists())
        self.assertTrue(MembershipPlan.objects.filter(active=True).exists())

    def test_access_follows_each_model_and_every_cover_is_credited(self):
        freemium = set(self.by_model("freemium").values_list("pk", flat=True))
        for course in self.courses():
            response = self.client.get(reverse("course-detail", args=[course.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "/static/images/courses/")
            credited = course.topic.slug in PHOTOS
            self.assertEqual("Unsplash" in response.content.decode(), credited, course.title)
            model = "membership" if course.membership else "freemium" if course.pk in freemium else "paid"
            lessons = VersionLesson.objects.filter(chapter__version=course.current_version).select_related("content")
            self.assertEqual(any(lesson.content.access_type == "free" for lesson in lessons), model != "paid", course.title)
            for lesson in lessons:
                response = self.client.get(reverse("version-lesson", args=[course.pk, 1, lesson.pk]))
                if lesson.content.access_type == "free":
                    self.assertEqual(response.status_code, 200)
                    self.assertTrue(response.context["body"])
                    continue
                self.assertEqual(response.status_code, 403)
                self.assertIsNone(response.context["body"])
                self.assertEqual(response.context["reading_sections"], [])
                self.assertNotContains(response, 'youtube-nocookie.com/embed/', status_code=403)
                if model == "membership":
                    self.assertEqual(response.context["offers"], [])
                    self.assertContains(response, "Incluido en la membresía", status_code=403)
                else:
                    self.assertEqual(len(response.context["offers"]), 3)

    def test_course_purchase_unlocks_exact_inventory_and_other_courses_stay_locked(self):
        self.client.force_login(self.student)
        course = self.by_model("paid").first()
        self.buy(self.course_offer(course))
        self.assertEqual(Entitlement.objects.filter(buyer=self.student).count(), 12)
        for lesson in VersionLesson.objects.filter(chapter__version=course.current_version):
            response = self.client.get(reverse("version-lesson", args=[course.pk, 1, lesson.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["body"])
        other = self.by_model("paid").exclude(pk=course.pk).first()
        lesson = VersionLesson.objects.filter(chapter__version=other.current_version).first()
        self.assertEqual(self.client.get(reverse("version-lesson", args=[other.pk, 1, lesson.pk])).status_code, 403)

    def test_individual_purchase_unlocks_one_lesson_and_offers_match_the_catalog(self):
        course = self.by_model("paid").first()
        lesson = VersionLesson.objects.filter(chapter__version=course.current_version).first()
        self.buy(Offer.objects.get(kind="lesson", lesson=lesson, status="active"))
        self.assertEqual(set(Entitlement.objects.filter(buyer=self.student).values_list("resource_id", flat=True)), {lesson.content_id})
        sold = [item for item in self.catalog if access_model(item) != "membership"]
        paid_lessons = sum(1 for item in sold for chapter in item["chapters"] for entry in chapter["lessons"] if not entry.get("free"))
        paid_chapters = sum(1 for item in sold for chapter in item["chapters"] if not all(entry.get("free") for entry in chapter["lessons"]))
        offers = Offer.objects.filter(creator__email=CREATOR_EMAIL, status="active")
        self.assertEqual(offers.filter(kind="course").count(), len(sold))
        self.assertEqual(offers.filter(kind="chapter").count(), paid_chapters)
        self.assertEqual(offers.filter(kind="lesson").count(), paid_lessons)
        for item in sold:
            self.assertEqual(self.course_offer(self.courses().get(title=item["title"])).amount_sats, item["price"])

    def test_membership_opens_its_courses_but_not_paid_ones(self):
        self.client.force_login(self.student)
        course = self.by_model("membership").first()
        detail = self.client.get(reverse("course-detail", args=[course.pk]), follow=True)
        self.assertContains(detail, "Incluido en la membresía")
        self.assertNotContains(detail, "Gratis + lecciones de pago")
        self.grant(course)
        for lesson in VersionLesson.objects.filter(chapter__version=course.current_version):
            self.assertEqual(self.client.get(reverse("version-lesson", args=[course.pk, 1, lesson.pk])).status_code, 200)
        paid = self.by_model("paid").first()
        lesson = VersionLesson.objects.filter(chapter__version=paid.current_version).first()
        self.assertEqual(self.client.get(reverse("version-lesson", args=[paid.pk, 1, lesson.pk])).status_code, 403)

    def test_quizzes_and_progress_allow_completion_certificate_for_every_course(self):
        for course in self.courses():
            self.grant(course)
            enrollment = enroll(self.student, course.current_version)
            self.assertFalse(completion_status(enrollment)["eligible"])
            for quiz in VersionQuiz.objects.filter(lesson__chapter__version=course.current_version):
                attempt = start_attempt(self.student, enrollment.pk, quiz.pk)
                answers = {str(index): question["correct"] for index, question in enumerate(quiz.questions)}
                attempt = save_attempt(self.student, attempt.pk, answers, 0, submit=True)
                self.assertTrue(attempt.passed)
            for lesson in VersionLesson.objects.filter(chapter__version=course.current_version):
                enrollment = save_progress(self.student, enrollment.pk, lesson.pk, enrollment.revision, "complete")
            self.assertTrue(completion_status(enrollment)["eligible"])
            certificate = issue_certificate(self.student, enrollment.pk, "Estudiante del catálogo")
            self.assertEqual(certificate.enrollment_id, enrollment.pk)

    def test_projects_do_not_promise_personal_review_when_intake_is_closed(self):
        self.client.force_login(self.student)
        course = self.by_model("paid").first()
        self.buy(self.course_offer(course))
        practice = VersionPractice.objects.get(lesson__chapter__version=course.current_version)
        self.assertFalse(PracticeIntake.objects.get(practice=practice).accepting)
        response = self.client.get(reverse("student-practice", args=[practice.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no incluye revisión personal")
        self.assertNotContains(response, "Revisión prevista")

    def test_repeat_load_keeps_existing_versions_and_reviewer_disabled(self):
        models = (Course, CourseVersion, Lesson, ResourceVersion, Offer, Submission)
        before = [model.objects.count() for model in models]
        call_command("load_complete_courses", stdout=StringIO())
        self.assertEqual(publish_collection(self.catalog), 0)
        self.assertEqual(before, [model.objects.count() for model in models])
        reviewer = get_user_model().objects.get(email=REVIEWER_EMAIL)
        self.assertFalse(reviewer.is_active or reviewer.is_staff or reviewer.has_usable_password())
        self.assertFalse(reviewer.user_permissions.exists())

    def test_conflicting_taxonomy_rolls_back_whole_publication(self):
        candidate = deepcopy(self.catalog[0])
        candidate["title"] += " nueva edición"
        category = Category.objects.exclude(slug=candidate["category"]["slug"]).first()
        Topic.objects.filter(slug=candidate["topic"]["slug"]).update(category=category)
        before = Course.objects.count()
        with self.assertRaises(CommandError):
            publish_collection([candidate])
        self.assertEqual(Course.objects.count(), before)
        self.assertFalse(get_user_model().objects.get(email=REVIEWER_EMAIL).is_active)
