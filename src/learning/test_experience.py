import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from content.models import Course
from content.publication import publish_course
from scripts.demo_commerce import seed

from .models import Enrollment
from .services import enroll, save_progress


class LearningExperienceTests(TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        settings = override_settings(MEDIA_ROOT=directory.name, SECURE_SSL_REDIRECT=False)
        settings.enable()
        self.addCleanup(settings.disable)
        self.data = seed()
        self.client.force_login(self.data.student)
        self.enrollment = enroll(self.data.student, self.data.version)
        self.course_url = reverse("course-version", args=[self.data.course.pk, self.data.version.number])

    def test_course_and_library_resume_same_accessible_unfinished_lesson(self):
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "position")
        course = self.client.get(self.course_url)
        library = self.client.get(reverse("workspace"))
        target = course.context["journey"]["target"]
        self.assertEqual(target.version_record.pk, self.data.records[0].pk)
        self.assertIn(target.detail_url, library.context["resume"].open_url)
        self.assertContains(course, "Continuar curso")
        self.assertEqual(course.context["journey"]["completed"], 0)

    def test_finishing_only_free_sample_does_not_resume_locked_content(self):
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "complete")
        course = self.client.get(self.course_url)
        self.assertIsNone(course.context["journey"]["target"])
        self.assertContains(course, "Ver opciones de acceso")
        self.assertContains(self.client.get(reverse("workspace")), "Ver acceso")
        self.assertEqual(course.context["journey"]["locked"], 2)

    def test_start_enrolls_once_and_opens_free_lesson_without_marking_complete(self):
        self.client.force_login(self.data.other)
        endpoint = reverse("enrollment-create", args=[self.data.version.pk])
        expected = reverse("version-lesson", args=[self.data.course.pk, self.data.version.number, self.data.records[0].pk])
        for _ in range(2):
            self.assertRedirects(self.client.post(endpoint, {"start": "1"}), expected)
        enrollment = Enrollment.objects.get(student=self.data.other, version=self.data.version)
        self.assertFalse(enrollment.completed_lessons.exists())

    def test_requested_locked_or_foreign_lesson_cannot_override_start(self):
        endpoint = reverse("enrollment-create", args=[self.data.version.pk])
        for lesson in [self.data.records[1].pk, -1, "invalid"]:
            response = self.client.post(endpoint, {"start": "1", "lesson": lesson})
            self.assertIn(f"/lecciones/{self.data.records[0].pk}/", response.url)

    def test_locked_reader_exposes_no_body_or_practice_and_keeps_navigation(self):
        url = reverse("version-lesson", args=[self.data.course.pk, self.data.version.number, self.data.records[1].pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertNotContains(response, self.data.records[1].content.body, status_code=403)
        self.assertEqual(response.context["reading_sections"], [])
        self.assertContains(response, "Lecciones del curso", status_code=403)
        self.assertNotContains(response, "data-progress-form", status_code=403)

    def test_archived_enrolled_course_keeps_version_specific_resume(self):
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "position")
        publish_course(self.data.course, self.data.reviewer)
        Course.objects.filter(pk=self.data.course.pk).update(status="archived")
        response = self.client.get(self.course_url)
        target = response.context["journey"]["target"]
        self.assertIn(f"/versiones/{self.data.version.number}/", target.detail_url)
        self.client.force_login(self.data.other)
        self.assertEqual(self.client.get(self.course_url).status_code, 404)

    def test_library_filters_preserve_global_counts_and_classify_unstarted(self):
        endpoint = reverse("workspace")
        self.assertEqual(self.client.get(endpoint, {"estado": "por-empezar"}).context["enrollments"].paginator.count, 1)
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "position")
        active = self.client.get(endpoint, {"estado": "en-curso"})
        self.assertEqual(active.context["enrollments"].paginator.count, 1)
        empty = self.client.get(endpoint, {"estado": "completados", "q": "no existe"})
        self.assertEqual(empty.context["enrollments"].paginator.count, 0)
        self.assertEqual(empty.context["learning_stats"]["courses"], 1)
        self.assertContains(empty, "No hay cursos con estos filtros")

    def test_started_course_is_featured_before_a_newer_unstarted_course(self):
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "position")
        new = publish_course(self.data.course, self.data.reviewer)
        enroll(self.data.student, new)
        response = self.client.get(reverse("workspace"))
        self.assertEqual(response.context["resume"].version_id, self.data.version.pk)

    def test_continuation_is_independent_of_filtered_courses(self):
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "position")
        filtered = self.client.get(reverse("workspace"), {"seccion": "cursos", "q": "no coincide"})
        self.assertEqual(filtered.context["enrollments"].paginator.count, 0)
        self.assertEqual(filtered.context["resume"].version_id, self.data.version.pk)
        continuation_page = self.client.get(reverse("workspace"), {"seccion": "continuar"})
        self.assertContains(continuation_page, filtered.context["resume"].open_url)
        self.assertContains(continuation_page, "Continuar lección")
        self.assertFalse(self.enrollment.completed_lessons.exists())

    def test_learning_sections_are_separate_and_unknown_section_has_safe_fallback(self):
        resources = self.client.get(reverse("workspace"), {"seccion": "recursos"})
        self.assertEqual(resources.context["learning_section"], "recursos")
        self.assertContains(resources, "Tus recursos")
        self.assertNotContains(resources, 'id="workspace-courses-heading"')
        saved = self.client.get(reverse("workspace"), {"seccion": "guardados"})
        self.assertContains(saved, 'id="mis-guardados"')
        self.assertNotContains(saved, 'id="workspace-resources-heading"')
        fallback = self.client.get(reverse("workspace"), {"seccion": "desconocida"})
        self.assertEqual(fallback.context["learning_section"], "continuar")
        self.assertContains(fallback, 'aria-labelledby="resume-heading"')

    def test_catalog_shows_only_the_current_students_progress(self):
        save_progress(self.data.student, self.enrollment.pk, self.data.records[0].pk, 0, "complete")
        response = self.client.get(reverse("courses"), {"vista": "todos"})
        self.assertContains(response, "1 de 3 completadas")
        self.client.force_login(self.data.other)
        self.assertNotContains(self.client.get(reverse("courses"), {"vista": "todos"}), "1 de 3 completadas")

    def test_catalog_price_identifies_full_course_instead_of_cheaper_lesson(self):
        response = self.client.get(reverse("courses"), {"vista": "todos"})
        card = response.context["cards"][0]
        self.assertEqual(card["price"], self.data.bundle.amount_sats)
        self.assertEqual(card["price_label"], "Curso completo")
        self.assertContains(response, "150 sats")
        self.assertNotContains(response, "Desde")
