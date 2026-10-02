from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .access import content_access
from .models import (
    AccessType,
    Chapter,
    Course,
    Lesson,
    Material,
    PublicationStatus,
    Video,
)


class ContentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user("creator@example.com")
        cls.other = get_user_model().objects.create_user("other@example.com", is_staff=True)
        cls.course = Course.objects.create(title="Curso de prueba", creator=cls.creator, status=PublicationStatus.PUBLISHED)
        cls.chapter = Chapter.objects.create(title="Capítulo", course=cls.course, status=PublicationStatus.PUBLISHED)
        cls.lesson = Lesson.objects.create(title="Lección", chapter=cls.chapter, body="Texto protegido", status=PublicationStatus.PUBLISHED)

    def test_published_free_lesson_is_delivered_without_login(self):
        response = self.client.get(reverse("lesson-content", args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["body"], "Texto protegido")
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_paid_lesson_denies_anonymous_and_other_creator(self):
        self.lesson.access_type = AccessType.PAID
        self.lesson.save()
        url = reverse("lesson-content", args=[self.lesson.pk])
        for user in (None, self.other):
            with self.subTest(user=user):
                if user:
                    self.client.force_login(user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)
                self.assertNotContains(response, self.lesson.body, status_code=403)

    def test_unpublished_ancestor_hides_lesson(self):
        for item in (self.course, self.chapter, self.lesson):
            with self.subTest(model=type(item).__name__):
                item.status = PublicationStatus.DRAFT
                item.save()
                response = self.client.get(reverse("lesson-content", args=[self.lesson.pk]))
                self.assertEqual(response.status_code, 404)
                self.assertNotContains(response, self.lesson.body, status_code=404)
                item.status = PublicationStatus.PUBLISHED
                item.save()

    def test_owner_can_preview_draft_paid_lesson(self):
        self.course.status = PublicationStatus.DRAFT
        self.course.save()
        self.lesson.access_type = AccessType.PAID
        self.lesson.save()
        self.client.force_login(self.creator)
        response = self.client.get(reverse("lesson-content", args=[self.lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["access"], "creator_preview")
        self.assertFalse(content_access(self.other, self.lesson).allowed)

    def test_inactive_owner_has_no_preview(self):
        self.creator.is_active = False
        self.course.status = PublicationStatus.DRAFT
        self.course.save()
        self.assertFalse(content_access(self.creator, self.lesson).allowed)

    def test_free_lesson_does_not_inherit_paid_sibling(self):
        Lesson.objects.create(title="Extra", chapter=self.chapter, position=2, access_type=AccessType.PAID, status=PublicationStatus.PUBLISHED)
        self.assertTrue(content_access(AnonymousUser(), self.lesson).allowed)

    def test_standalone_resources_follow_publication_and_access(self):
        for model in (Video, Material):
            with self.subTest(model=model.__name__):
                resource = model.objects.create(title="Ficha", creator=self.creator)
                self.assertFalse(content_access(AnonymousUser(), resource).allowed)
                resource.status = PublicationStatus.PUBLISHED
                self.assertTrue(content_access(AnonymousUser(), resource).allowed)
                resource.access_type = AccessType.PAID
                self.assertFalse(content_access(self.other, resource).allowed)

    def test_positions_are_unique_within_parent(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Chapter.objects.create(title="Duplicado", course=self.course, position=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Lesson.objects.create(title="Duplicada", chapter=self.chapter, position=1)

    def test_content_endpoint_only_accepts_get_and_handles_missing_lesson(self):
        self.assertEqual(self.client.post(reverse("lesson-content", args=[self.lesson.pk])).status_code, 405)
        self.assertEqual(self.client.get(reverse("lesson-content", args=[999999])).status_code, 404)

    def test_admin_content_requires_staff(self):
        self.client.force_login(self.creator)
        self.assertEqual(self.client.get(reverse("admin:content_course_changelist")).status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("admin:content_course_changelist")).status_code, 403)
