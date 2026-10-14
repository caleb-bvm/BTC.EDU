import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from commerce.models import Entitlement
from content.models import ExternalReference, Material, ResourceVersion
from content.testing import EDUCATION_FIXTURE
from media.models import Asset

from .bookmarks import save_item
from .models import SavedItem


@override_settings(SECURE_SSL_REDIRECT=False, ACCOUNT_SEND_EMAIL=False,
                   PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class BookmarkTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory(prefix="btc-edu-bookmarks-")
        self.settings_override = override_settings(MEDIA_ROOT=self.media.name)
        self.settings_override.enable()
        self.addCleanup(self.media.cleanup)
        self.addCleanup(self.settings_override.disable)
        users = get_user_model().objects
        self.student = users.create_user("student@bookmarks.invalid", "Learning-bookmarks-34718!")
        self.other = users.create_user("other@bookmarks.invalid", "Learning-bookmarks-34718!")
        self.creator = users.create_user("creator@bookmarks.invalid", account_type="creator")
        self.asset = Asset.objects.create(creator=self.creator, file=SimpleUploadedFile("exercise.txt", b"Protected practice"))
        self.resource = ResourceVersion.objects.create(**EDUCATION_FIXTURE, creator=self.creator, kind="material", title="Guía", access_type="free", asset=self.asset)
        self.item = Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, resource_key=self.resource.resource_key, title="Guía", description="Un ejercicio", status="published", revision=self.resource)
        self.reference = ExternalReference.objects.create(title="Fuente", description="Referencia", source_name="Documentación", source_url="https://example.org/docs", status="published")
        self.client.force_login(self.student)

    def test_free_bookmark_is_idempotent_and_grants_no_rights(self):
        one = save_item(self.student, "recurso", self.resource.pk, "save")
        two = save_item(self.student, "recurso", self.resource.pk, "save")
        self.assertEqual(one.pk, two.pk)
        self.assertEqual(SavedItem.objects.count(), 1)
        self.assertEqual(Entitlement.objects.count(), 0)
        self.assertContains(self.client.get(reverse("workspace")), "Guía")

    def test_resource_page_can_save_and_return_to_exact_page(self):
        url = reverse("resource-detail", args=["materiales", self.item.pk])
        self.assertContains(self.client.get(url), "Guardar para estudiar")
        response = self.client.post(reverse("bookmark-toggle", args=["recurso", self.resource.pk]), {"action": "save", "next": url})
        self.assertRedirects(response, url)
        self.assertContains(self.client.get(url), "Guardado")

    def test_paid_preview_can_be_bookmarked_but_file_stays_protected(self):
        paid = ResourceVersion.objects.create(**EDUCATION_FIXTURE, creator=self.creator, kind="material", title="De pago", access_type="paid", asset=self.asset)
        item = Material.objects.create(**EDUCATION_FIXTURE, creator=self.creator, resource_key=paid.resource_key, title="De pago", status="published", revision=paid)
        save_item(self.student, "recurso", paid.pk, "save")
        response = self.client.get(reverse("resource-file", args=["materiales", item.pk, 1, "archivo"]))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Entitlement.objects.filter(buyer=self.student).exists())

    def test_removing_bookmark_keeps_purchase_right(self):
        right = Entitlement.objects.create(buyer=self.student, resource=self.resource)
        save_item(self.student, "recurso", self.resource.pk, "save")
        save_item(self.student, "recurso", self.resource.pk, "remove")
        self.assertFalse(SavedItem.objects.exists())
        self.assertTrue(Entitlement.objects.filter(pk=right.pk).exists())

    def test_saved_item_is_private_and_stays_bound_to_revision(self):
        saved = save_item(self.student, "recurso", self.resource.pk, "save")
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("bookmark-open", args=[saved.pk])).status_code, 404)
        new = ResourceVersion.objects.create(**EDUCATION_FIXTURE, creator=self.creator, resource_key=self.resource.resource_key, number=2, kind="material", title="Guía nueva", access_type="free", asset=self.asset)
        # Editorial approval advances the pointer; normal draft saves deliberately
        # preserve it so the student's bookmark must retain its original revision.
        Material.objects.filter(pk=self.item.pk).update(revision=new)
        self.assertEqual(Material.objects.get(pk=self.item.pk).revision_id, new.pk)
        self.client.force_login(self.student)
        response = self.client.get(reverse("bookmark-open", args=[saved.pk]))
        self.assertContains(response, "ya no está disponible", msg_prefix=f"Destino observado: {getattr(response, 'url', '')}")
        saved.refresh_from_db()
        self.assertEqual(saved.resource_id, self.resource.pk)

    def test_reference_snapshot_and_filters_are_preserved(self):
        saved = save_item(self.student, "referencia", self.reference.pk, "save")
        self.reference.title = "Título actualizado"
        self.reference.status = "archived"
        self.reference.save(update_fields=("title", "status"))
        saved.refresh_from_db()
        self.assertEqual(saved.title, "Fuente")
        self.assertEqual(saved.source_url, "https://example.org/docs")
        self.assertContains(self.client.get(reverse("bookmark-open", args=[saved.pk])), "Consultar la fuente original")

    def test_unpublished_resource_and_wrong_account_are_denied(self):
        self.item.status = "draft"
        self.item.save(update_fields=("status",))
        with self.assertRaises(PermissionDenied):
            save_item(self.student, "recurso", self.resource.pk, "save")
        with self.assertRaises(PermissionDenied):
            save_item(self.creator, "referencia", self.reference.pk, "save")

    def test_save_requires_post_csrf_and_rejects_external_return(self):
        url = reverse("bookmark-toggle", args=["referencia", self.reference.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        secure = Client(enforce_csrf_checks=True)
        secure.force_login(self.student)
        self.assertEqual(secure.post(url, {"action": "save"}).status_code, 403)
        response = self.client.post(url, {"action": "save", "next": "https://outside.invalid"})
        self.assertRedirects(response, reverse("workspace"))
