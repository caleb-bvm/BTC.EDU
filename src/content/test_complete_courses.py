from copy import deepcopy
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from commerce.gateway import ProviderStatus
from commerce.models import Entitlement, Offer
from commerce.services import ensure_emitted, reserve_invoice, settle
from commerce.tests import FakeGateway
from creators.models import Submission
from learning.assessment_services import save_attempt, start_attempt
from learning.certificates import completion_status, issue_certificate
from learning.models import Enrollment, PracticeIntake, VersionPractice, VersionQuiz
from learning.quizzes import validate_questions
from learning.services import save_progress

from .course_catalog import CREATOR_EMAIL, REVIEWER_EMAIL, load_catalog
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

    def test_original_content_has_complete_curricula_and_valid_module_assessments(self):
        self.assertEqual(len(self.catalog), 4)
        self.assertEqual(self.courses().count(), 4)
        self.assertEqual(Lesson.objects.filter(chapter__course__in=self.courses()).count(), 48)
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
        self.assertEqual(Submission.objects.filter(course__in=self.courses(), status="approved").count(), 4)

    def test_every_lesson_is_locked_before_purchase_and_photos_are_visible(self):
        self.assertEqual(set(self.courses().values_list("topic__category__slug", flat=True)), {"creacion", "desarrollo-software"})
        for course in self.courses():
            response = self.client.get(reverse("course-detail", args=[course.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "/static/images/courses/")
            self.assertContains(response, "Unsplash")
            self.assertContains(response, '<details class="course-unit-offers">')
            self.assertNotContains(response, "Lee las lecciones gratis sin cuenta.")
            for lesson in VersionLesson.objects.filter(chapter__version=course.current_version).select_related("content"):
                self.assertEqual(lesson.content.access_type, "paid")
                url = reverse("version-lesson", args=[course.pk, 1, lesson.pk])
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)
                self.assertIsNone(response.context["body"])
                self.assertEqual(response.context["reading_sections"], [])
                self.assertNotContains(response, 'youtube-nocookie.com/embed/', status_code=403)
                self.assertEqual(len(response.context["offers"]), 3)

    def test_course_purchase_unlocks_exact_inventory_and_other_courses_stay_locked(self):
        self.client.force_login(self.student)
        course = self.courses().first()
        self.buy(Offer.objects.get(kind="course", course_version=course.current_version, status="active"))
        self.assertEqual(Entitlement.objects.filter(buyer=self.student).count(), 12)
        for lesson in VersionLesson.objects.filter(chapter__version=course.current_version):
            response = self.client.get(reverse("version-lesson", args=[course.pk, 1, lesson.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["body"])
        other = self.courses().exclude(pk=course.pk).first()
        lesson = VersionLesson.objects.filter(chapter__version=other.current_version).first()
        self.assertEqual(self.client.get(reverse("version-lesson", args=[other.pk, 1, lesson.pk])).status_code, 403)

    def test_individual_purchase_unlocks_one_lesson_and_preserves_other_units(self):
        course = self.courses().first()
        lesson = VersionLesson.objects.filter(chapter__version=course.current_version).first()
        self.buy(Offer.objects.get(kind="lesson", lesson=lesson, status="active"))
        self.assertEqual(set(Entitlement.objects.filter(buyer=self.student).values_list("resource_id", flat=True)), {lesson.content_id})
        self.assertEqual(Offer.objects.filter(creator__email=CREATOR_EMAIL, kind="course", status="active").count(), 4)
        self.assertEqual(Offer.objects.filter(creator__email=CREATOR_EMAIL, kind="chapter", status="active").count(), 16)
        self.assertEqual(Offer.objects.filter(creator__email=CREATOR_EMAIL, kind="lesson", status="active").count(), 48)

    def test_quizzes_and_progress_allow_completion_certificate_for_all_four_courses(self):
        for course in self.courses():
            self.buy(Offer.objects.get(kind="course", course_version=course.current_version, status="active"))
            enrollment = Enrollment.objects.get(student=self.student, version=course.current_version)
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
        course = self.courses().first()
        self.buy(Offer.objects.get(kind="course", course_version=course.current_version, status="active"))
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
