import tempfile
from collections import Counter
from copy import deepcopy

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from commerce.models import Offer

from .course_catalog import CREATOR_EMAIL
from .management.commands.load_tutorials_resources import publish_catalog
from .models import (
    Course,
    CourseKind,
    ExternalReference,
    Material,
    ResourceVersion,
    VersionLesson,
    Video,
)
from .tutorial_catalog import check_resource, check_tutorial, load_catalog
from .tutorial_catalog.pdf import render_material


class TutorialCatalogTests(SimpleTestCase):
    def test_each_category_has_five_tutorials_and_five_resources(self):
        tutorials, resources = load_catalog()
        self.assertEqual(len(tutorials), 30)
        self.assertEqual(len(resources), 30)
        self.assertEqual(Counter(item["access"] for item in tutorials), {"free": 12, "freemium": 12, "paid": 6})
        self.assertEqual(Counter(item["kind"] for item in resources), {"video": 12, "material": 12, "reference": 6})

    def test_checks_reject_inconsistent_prices_and_unattributed_videos(self):
        tutorials, resources = load_catalog()
        free = deepcopy(next(item for item in tutorials if item["access"] == "free"))
        free["price"] = 100
        with self.assertRaises(ValueError):
            check_tutorial(free)
        clip = deepcopy(next(item for item in resources if item["kind"] == "video"))
        clip["video_author"] = " "
        with self.assertRaises(ValueError):
            check_resource(clip)
        clip["video_author"], clip["video_url"] = "Autor", "https://example.com/video"
        with self.assertRaises(ValueError):
            check_resource(clip)

    def test_materials_render_as_pdf_with_their_sources(self):
        _, resources = load_catalog()
        material = next(item for item in resources if item["kind"] == "material")
        data = render_material(material, "Bitcoin y Lightning")
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertEqual(data, render_material(material, "Bitcoin y Lightning"))


@override_settings(SECURE_SSL_REDIRECT=False)
class PublishedTutorialsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = tempfile.TemporaryDirectory()
        cls.media = override_settings(MEDIA_ROOT=cls.files.name)
        cls.media.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.media.disable()
        cls.files.cleanup()

    @classmethod
    def setUpTestData(cls):
        cls.tutorials, cls.resources = load_catalog()
        publish_catalog(cls.tutorials, cls.resources)

    def tutorial(self, access):
        title = next(item["title"] for item in self.tutorials if item["access"] == access)
        return Course.objects.get(creator__email=CREATOR_EMAIL, kind=CourseKind.TUTORIAL, title=title)

    def test_catalog_is_published_with_offers_only_for_paid_steps(self):
        self.assertEqual(Course.objects.filter(kind=CourseKind.TUTORIAL, current_version__isnull=False).count(), 30)
        self.assertEqual(Video.objects.filter(status="published").count(), 12)
        self.assertEqual(Material.objects.filter(status="published").count(), 12)
        self.assertEqual(ExternalReference.objects.filter(status="published").count(), 6)
        free = self.tutorial("free").current_version
        self.assertFalse(Offer.objects.filter(course_version=free).exists())
        freemium = self.tutorial("freemium").current_version
        steps = list(VersionLesson.objects.filter(chapter__version=freemium).order_by("position").select_related("content"))
        self.assertEqual([step.content.access_type for step in steps], ["free"] + ["paid"] * (len(steps) - 1))
        self.assertTrue(Offer.objects.filter(course_version=freemium, status="active").exists())
        paid_materials = ResourceVersion.objects.filter(kind="material", access_type="paid")
        self.assertEqual(paid_materials.count(), 6)
        self.assertEqual(Offer.objects.filter(resource__in=paid_materials, status="active").count(), 6)

    def test_external_video_plays_from_youtube_with_credit_and_stays_free(self):
        video = Video.objects.filter(status="published").select_related("revision").first()
        response = self.client.get(reverse("resource-detail", args=["videos", video.pk]))
        self.assertContains(response, "https://www.youtube-nocookie.com/embed/")
        self.assertContains(response, f"Video de {video.revision.video_author} en YouTube.")
        revision = video.revision
        revision.pk, revision.access_type = None, "paid"
        with self.assertRaises(ValidationError):
            revision.full_clean()
