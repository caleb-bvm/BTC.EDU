from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    AccessType,
    Chapter,
    Course,
    Lesson,
    Material,
    PublicationStatus,
    Video,
)


class LearningJourneyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = get_user_model().objects.create_user(
            "author@example.com", first_name="Ana", last_name="López"
        )
        cls.course = Course.objects.create(
            creator=cls.creator,
            title="Bitcoin desde cero",
            description="Comprende las bases",
            objective="Entender Bitcoin",
            requirements="Curiosidad",
            status=PublicationStatus.PUBLISHED,
        )
        cls.chapter = Chapter.objects.create(
            course=cls.course,
            title="Primeros pasos",
            status=PublicationStatus.PUBLISHED,
        )
        cls.free = Lesson.objects.create(
            chapter=cls.chapter,
            title="Introducción",
            body="Texto libre <script>alert(1)</script>",
            status=PublicationStatus.PUBLISHED,
        )
        cls.paid = Lesson.objects.create(
            chapter=cls.chapter,
            position=2,
            title="Profundiza",
            body="SECRETO DE PAGO",
            access_type=AccessType.PAID,
            status=PublicationStatus.PUBLISHED,
        )
        cls.draft = Lesson.objects.create(
            chapter=cls.chapter,
            position=3,
            title="LECCIÓN OCULTA",
            body="BORRADOR SECRETO",
        )

    def test_catalog_and_course_show_mixed_access_without_bodies_or_email(self):
        for url in ("/", "/explorar/", reverse("course-detail", args=[self.course.pk])):
            response = self.client.get(url)
            self.assertContains(response, self.course.title)
            self.assertContains(response, "Gratis + lecciones de pago")
            self.assertContains(response, "Ana López")
            for secret in (
                self.paid.body,
                self.free.body,
                self.draft.title,
                self.creator.email,
            ):
                self.assertNotContains(response, secret)

    def test_filters_search_and_htmx(self):
        self.assertContains(
            self.client.get("/explorar/?q=Bitcoin&acceso=gratis"), self.course.title
        )
        self.assertContains(
            self.client.get("/explorar/?acceso=pago"), self.course.title
        )
        self.assertNotContains(
            self.client.get("/explorar/?tipo=videos"), self.course.title
        )
        self.assertContains(
            self.client.get("/explorar/?q=inexistente"), "No encontramos coincidencias"
        )
        response = self.client.get(
            "/explorar/?q=Bitcoin&acceso=gratis", HTTP_HX_REQUEST="true"
        )
        self.assertContains(response, self.course.title)
        self.assertNotContains(response, "<html")
        self.assertContains(
            self.client.get("/explorar/?tipo=incorrecto&acceso=incorrecto"),
            self.course.title,
        )

    def test_reader_escapes_text_and_links_to_next_lesson(self):
        response = self.client.get(reverse("lesson-detail", args=[self.free.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, reverse("lesson-detail", args=[self.paid.pk]))
        self.assertNotContains(response, self.draft.title)
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_paid_reader_blocks_anonymous_and_staff(self):
        staff = get_user_model().objects.create_user("staff@example.com", is_staff=True)
        for user in (None, staff):
            if user:
                self.client.force_login(user)
            response = self.client.get(reverse("lesson-detail", args=[self.paid.pk]))
            self.assertContains(
                response, "Esta lección requiere una compra", status_code=403
            )
            self.assertNotContains(response, self.paid.body, status_code=403)
            self.assertIn("no-store", response.headers["Cache-Control"])

    def test_unpublished_ancestors_hide_pages_and_catalog(self):
        self.chapter.status = PublicationStatus.DRAFT
        self.chapter.save()
        self.assertNotContains(
            self.client.get(reverse("course-detail", args=[self.course.pk])),
            self.free.title,
        )
        self.assertEqual(
            self.client.get(reverse("lesson-detail", args=[self.free.pk])).status_code,
            404,
        )
        self.course.status = PublicationStatus.DRAFT
        self.course.save()
        self.assertNotContains(self.client.get("/explorar/"), self.course.title)
        self.assertEqual(
            self.client.get(
                reverse("course-detail", args=[self.course.pk])
            ).status_code,
            404,
        )

    def test_owner_preview_and_get_only(self):
        self.course.status = PublicationStatus.DRAFT
        self.course.save()
        self.client.force_login(self.creator)
        response = self.client.get(reverse("lesson-detail", args=[self.draft.pk]))
        self.assertContains(response, self.draft.body)
        self.assertContains(response, "Vista previa del creador")
        self.assertContains(
            self.client.get(reverse("course-detail", args=[self.course.pk])),
            self.draft.title,
        )
        self.assertNotContains(self.client.get("/explorar/"), self.course.title)
        for name, pk in (
            ("course-detail", self.course.pk),
            ("lesson-detail", self.free.pk),
        ):
            self.assertEqual(
                self.client.post(reverse(name, args=[pk])).status_code, 405
            )

    def test_standalone_cards_have_honest_information_pages(self):
        for kind, model in (("videos", Video), ("materiales", Material)):
            item = model.objects.create(
                creator=self.creator,
                title="Recurso independiente",
                status=PublicationStatus.PUBLISHED,
            )
            url = reverse("resource-detail", args=[kind, item.pk])
            self.assertContains(self.client.get(f"/explorar/?tipo={kind}"), url)
            self.assertContains(self.client.get(url), "ficha informativa")
            item.status = PublicationStatus.DRAFT
            item.save()
            self.assertEqual(self.client.get(url).status_code, 404)
