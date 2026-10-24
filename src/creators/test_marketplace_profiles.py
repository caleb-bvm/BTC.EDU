import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from content.models import Chapter, Course, Lesson, Material
from content.publication import publish_course, publish_resource
from content.testing import EDUCATION_FIXTURE
from media.models import Asset

from .models import CreatorProfile


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_REQUIRE_VERIFIED_EMAIL=False,
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class MarketplaceProfileTests(TestCase):
    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        users = get_user_model().objects
        self.creator = users.create_user("PRIVATE_AUTHOR_EMAIL@profiles.invalid", account_type="creator", first_name="NOMBRE_PRIVADO")
        self.other = users.create_user("OTHER_PRIVATE_EMAIL@profiles.invalid", account_type="creator")
        self.admin = users.create_superuser("admin@profiles.invalid")
        for person, label in ((self.creator, "Educador público"), (self.other, "Otro educador")):
            CreatorProfile.objects.create(user=person, display_name=label, bio="Presentación pública.", specialty="Tecnología", status="approved")
        self.course = self.make_course(self.creator, "Curso publicado")
        self.tutorial = self.make_course(self.creator, "Tutorial publicado", kind="tutorial")
        self.foreign = self.make_course(self.other, "CONTENIDO_AJENO")
        asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("guia.txt", b"Archivo privado"))
        self.material = Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, title="Material publicado", description="Ficha pública", pending_asset=asset, access_type="paid", transcript="TRANSCRIPCION_PROTEGIDA")
        publish_resource(self.material, self.admin)
        self.profile_url = reverse("creator-public-profile", args=[self.creator.pk])

    def make_course(self, creator, title, kind="course"):
        course = Course.objects.create(creator=creator, title=title, kind=kind, description="Información pública")
        chapter = Chapter.objects.create(course=course, title="Inicio", status="published")
        Lesson.objects.create(**EDUCATION_FIXTURE, chapter=chapter, title="Unidad", body="Texto", status="published")
        publish_course(course, self.admin)
        return course

    def test_author_links_use_only_public_profile_and_do_not_expose_private_identity(self):
        for path in (reverse("courses") + "?vista=todos", reverse("tutorials") + "?vista=todos", reverse("course-detail", args=[self.course.pk]), reverse("resource-detail", args=["materiales", self.material.pk])):
            page = self.client.get(path)
            self.assertContains(page, self.profile_url)
            self.assertContains(page, "Educador público")
            self.assertNotContains(page, self.creator.email)
            self.assertNotContains(page, "NOMBRE_PRIVADO")
        self.assertNotContains(self.client.get(self.profile_url), self.creator.email)

    def test_storefront_filters_owner_and_uses_published_metadata(self):
        self.course.title = "BORRADOR_NO_PUBLICADO"
        self.course.description = "DESCRIPCION_PRIVADA"
        self.course.save()
        page = self.client.get(self.profile_url)
        self.assertContains(page, "Curso publicado")
        self.assertContains(page, "Tutorial publicado")
        self.assertContains(page, "Material publicado")
        for private in ("BORRADOR_NO_PUBLICADO", "DESCRIPCION_PRIVADA", "CONTENIDO_AJENO", "TRANSCRIPCION_PROTEGIDA"):
            self.assertNotContains(page, private)
        tutorials = self.client.get(self.profile_url, {"tipo": "tutoriales", "q": "publicado"})
        self.assertEqual(tutorials.context["result_count"], 1)
        self.assertContains(tutorials, "Tutorial publicado")
        self.assertNotContains(tutorials, "Curso publicado")
        self.assertNotContains(tutorials, "Material publicado")

    def test_email_visibility_and_suspension_gate_profile_links_and_endpoint(self):
        with override_settings(ACCOUNT_REQUIRE_VERIFIED_EMAIL=True):
            self.assertEqual(self.client.get(self.profile_url).status_code, 404)
            self.assertNotContains(self.client.get(reverse("courses") + "?vista=todos"), self.profile_url)
            self.creator.email_verified_at = timezone.now()
            self.creator.save(update_fields=("email_verified_at",))
            self.assertEqual(self.client.get(self.profile_url).status_code, 200)
            self.assertContains(self.client.get(reverse("courses") + "?vista=todos"), self.profile_url)
        CreatorProfile.objects.filter(user=self.creator).update(status="suspended")
        self.assertEqual(self.client.get(self.profile_url).status_code, 404)
        self.assertNotContains(self.client.get(reverse("courses") + "?vista=todos"), self.profile_url)
