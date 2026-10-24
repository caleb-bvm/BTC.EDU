from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class SavedCourseMigrationTests(TransactionTestCase):
    def test_existing_resource_and_reference_rows_survive_extension(self):
        before = ("learning", "0011_classify_notifications")
        after = ("learning", "0012_saveditem_course_version")
        executor = MigrationExecutor(connection)
        try:
            executor.migrate([before])
            executor = MigrationExecutor(connection)
            old = executor.loader.project_state(list(executor.loader.applied_migrations)).apps
            User = old.get_model("accounts", "User")
            Resource = old.get_model("content", "ResourceVersion")
            Reference = old.get_model("content", "ExternalReference")
            Saved = old.get_model("learning", "SavedItem")
            student = User.objects.create(email="student@bookmark-migration.invalid", account_type="student")
            creator = User.objects.create(email="creator@bookmark-migration.invalid", account_type="creator")
            resource = Resource.objects.create(creator=creator, title="Recurso conservado", kind="text", access_type="free", body="Texto")
            reference = Reference.objects.create(title="Fuente original", source_name="Documentación", source_url="https://example.invalid/original", status="published")
            Saved.objects.create(student=student, resource=resource, title="Título al guardar")
            Saved.objects.create(student=student, reference=reference, title="Referencia guardada", source_url=reference.source_url)
            preserved = list(Saved.objects.order_by("pk").values("pk", "student_id", "resource_id", "reference_id", "title", "source_url", "created_at"))
            executor = MigrationExecutor(connection)
            executor.migrate([after])
            executor = MigrationExecutor(connection)
            new = executor.loader.project_state(list(executor.loader.applied_migrations)).apps
            Saved = new.get_model("learning", "SavedItem")
            self.assertEqual(list(Saved.objects.order_by("pk").values("pk", "student_id", "resource_id", "reference_id", "title", "source_url", "created_at")), preserved)
            self.assertFalse(Saved.objects.filter(course_version__isnull=False).exists())
            with self.assertRaises(IntegrityError), transaction.atomic():
                Saved.objects.create(student_id=student.pk, title="Sin objetivo")
            with self.assertRaises(IntegrityError), transaction.atomic():
                Saved.objects.create(student_id=student.pk, resource_id=resource.pk, reference_id=reference.pk, title="Dos objetivos")
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
