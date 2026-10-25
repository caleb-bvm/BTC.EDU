import importlib

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.models.deletion import ProtectedError
from django.test import TestCase, TransactionTestCase

from creators.forms import CourseForm, MaterialForm, ResourceForm

from .management.commands.load_editorial_catalog import editorial_topic
from .models import Category, Topic
from .testing import CATEGORY_SLUGS


class TaxonomyFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.actor = get_user_model().objects.create_user("taxonomy@forms.invalid", account_type="creator")
        cls.bitcoin, _ = Category.objects.get_or_create(slug="bitcoin", defaults={"name": "Bitcoin"})
        cls.infrastructure = Category.objects.get(slug="infraestructura")
        cls.foundation, _ = Topic.objects.get_or_create(slug="bitcoin", defaults={"name": "Fundamentos de Bitcoin", "category": cls.bitcoin})
        cls.networks, _ = Topic.objects.get_or_create(slug="redes", defaults={"name": "Redes", "category": cls.infrastructure})
        cls.custom = Topic.objects.create(name="Tema propio", slug="tema-propio")

    def test_course_and_resource_choices_group_subcategories_and_validate_the_topic(self):
        for form in (CourseForm(), ResourceForm(actor=self.actor), MaterialForm(actor=self.actor)):
            with self.subTest(form=type(form).__name__):
                field = form.fields["topic"]
                self.assertEqual(field.label, "Subcategoría")
                self.assertIn('<optgroup label="Bitcoin y Lightning">', str(form["topic"]))
                self.assertIn('<optgroup label="Infraestructura y nube">', str(form["topic"]))
                self.assertIn('<optgroup label="Otros temas">', str(form["topic"]))
                groups = dict(list(field.choices)[1:])
                self.assertIn((self.foundation.pk, self.foundation.name), groups["Bitcoin y Lightning"])
                self.assertIn((self.networks.pk, self.networks.name), groups["Infraestructura y nube"])
                self.assertIn((self.custom.pk, self.custom.name), groups["Otros temas"])
                self.assertEqual(field.clean(str(self.networks.pk)), self.networks)
                self.assertIsNone(field.clean(""))
                with self.assertRaises(ValidationError):
                    field.clean("99999999")

    def test_course_form_saves_a_subcategory_and_keeps_it_selected(self):
        form = CourseForm(data={"title": "Aprende redes", "kind": "course", "topic": self.networks.pk})
        self.assertTrue(form.is_valid(), form.errors)
        course = form.save(commit=False)
        course.creator = self.actor
        course.save()
        self.assertEqual(course.topic_id, self.networks.pk)
        self.assertIn(f'value="{self.networks.pk}" selected', str(CourseForm(instance=course)["topic"]))

    def test_category_delete_is_protected_and_image_defaults_cover_new_categories(self):
        with self.assertRaises(ProtectedError):
            self.bitcoin.delete()
        for slug in CATEGORY_SLUGS:
            self.assertEqual(Category(slug=slug).category_image, f"images/categories/{slug}.svg")
        self.assertEqual(Category(slug="otra").category_image, "images/categories/general.svg")
        self.assertEqual(Category(slug="otra", artwork="desarrollo").category_image, "images/categories/desarrollo.svg")


class TaxonomyEditorialImportTests(TestCase):
    def test_import_reuses_a_recognized_name_with_a_custom_slug_and_preserves_its_category(self):
        bitcoin = Category.objects.get(slug="bitcoin")
        infrastructure = Category.objects.get(slug="infraestructura")
        original = Topic.objects.get(slug="bitcoin")
        original.slug = "mis-bitcoin"
        original.category = infrastructure
        original.save(update_fields=["slug", "category"])
        item = {"slug": "bitcoin", "topic": "Bitcoin"}
        count = Topic.objects.count()

        imported = editorial_topic(item, bitcoin)
        self.assertEqual((imported.pk, imported.slug, imported.category_id), (original.pk, "mis-bitcoin", infrastructure.pk))
        self.assertEqual(Topic.objects.count(), count)
        self.assertFalse(Topic.objects.filter(slug="bitcoin").exists())

        imported.category = None
        imported.save(update_fields=["category"])
        imported = editorial_topic(item, bitcoin)
        self.assertEqual((imported.pk, imported.slug, imported.category_id), (original.pk, "mis-bitcoin", bitcoin.pk))
        self.assertEqual(editorial_topic(item, bitcoin).pk, original.pk)
        self.assertEqual(Topic.objects.count(), count)


class TaxonomyMigrationTests(TransactionTestCase):
    def test_hierarchy_preserves_topic_identity_and_published_history_in_both_directions(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        previous = [node for node in latest if node[0] != "content"] + [("content", "0007_topic_category_presentation")]
        try:
            executor.migrate(previous)
            old = executor.loader.project_state(previous).apps
            topics = old.get_model("content", "Topic").objects
            topics.all().delete()
            bitcoin = topics.create(name="Bitcoin", slug="bitcoin", description="Descripción propia", artwork="lightning")
            security = topics.create(name="Seguridad", slug="seguridad")
            networks = topics.create(name="Redes", slug="mis-redes")
            custom = topics.create(name="Tema conservado", slug="tema-conservado")
            user = old.get_model("accounts", "User").objects.create(email="taxonomy@migration.invalid", password="!")
            course = old.get_model("content", "Course").objects.create(creator_id=user.pk, title="Curso conservado", topic_id=bitcoin.pk)
            version = old.get_model("content", "CourseVersion").objects.create(course_id=course.pk, number=1, title="Versión conservada", kind="course", topic_id=bitcoin.pk, creator_name="Docente", sealed=True)
            revision = old.get_model("content", "ResourceVersion").objects.create(creator_id=user.pk, kind="text", title="Revisión conservada", topic_id=security.pk)
            snapshots = {name: list(old.get_model("content", name).objects.values().order_by("pk")) for name in ("Course", "CourseVersion", "ResourceVersion")}

            MigrationExecutor(connection).migrate(latest)
            current = MigrationExecutor(connection).loader.project_state(latest).apps
            CategoryModel = current.get_model("content", "Category")
            TopicModel = current.get_model("content", "Topic")
            self.assertEqual(set(CategoryModel.objects.values_list("slug", flat=True)), set(CATEGORY_SLUGS))
            self.assertEqual(TopicModel.objects.get(pk=bitcoin.pk).name, "Fundamentos de Bitcoin")
            self.assertEqual(TopicModel.objects.get(pk=security.pk).name, "Seguridad y autocustodia")
            self.assertEqual(TopicModel.objects.get(pk=bitcoin.pk).description, "Descripción propia")
            self.assertEqual(TopicModel.objects.get(pk=bitcoin.pk).artwork, "lightning")
            self.assertEqual(TopicModel.objects.get(pk=networks.pk).slug, "mis-redes")
            self.assertEqual(TopicModel.objects.get(pk=networks.pk).category.slug, "infraestructura")
            self.assertIsNone(TopicModel.objects.get(pk=custom.pk).category_id)
            self.assertEqual(
                {slug: TopicModel.objects.filter(category__slug=slug).count() for slug in CATEGORY_SLUGS},
                {"bitcoin": 5, "desarrollo-software": 6, "datos-ia": 4, "ciberseguridad": 4, "infraestructura": 5, "creacion": 7},
            )
            self.assertEqual(current.get_model("content", "CourseVersion").objects.get(pk=version.pk).topic_id, bitcoin.pk)
            self.assertEqual(current.get_model("content", "ResourceVersion").objects.get(pk=revision.pk).topic_id, security.pk)
            before_repeat = list(TopicModel.objects.values().order_by("pk"))
            migration = importlib.import_module("content.migrations.0009_technology_categories")
            with connection.schema_editor() as editor:
                migration.reorganize_categories(current, editor)
            self.assertEqual(list(TopicModel.objects.values().order_by("pk")), before_repeat)
            for name, rows in snapshots.items():
                self.assertEqual(list(current.get_model("content", name).objects.values().order_by("pk")), rows)

            MigrationExecutor(connection).migrate(previous)
            old = MigrationExecutor(connection).loader.project_state(previous).apps
            self.assertEqual(old.get_model("content", "Topic").objects.count(), len(before_repeat))
            self.assertEqual(old.get_model("content", "Topic").objects.get(pk=networks.pk).slug, "mis-redes")
            for name, rows in snapshots.items():
                self.assertEqual(list(old.get_model("content", name).objects.values().order_by("pk")), rows)
        finally:
            MigrationExecutor(connection).migrate(latest)
