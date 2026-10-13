import django.db.models.deletion
from django.db import migrations, models


def retain_current_resource_topics(apps, schema_editor):
    """Capture the existing classification; older revisions have no recoverable topic."""
    revisions = apps.get_model("content", "ResourceVersion")
    database = schema_editor.connection.alias
    for name, kind in (("Video", "video"), ("Material", "material")):
        model = apps.get_model("content", name)
        current = model.objects.using(database).exclude(revision_id=None)
        for revision_id, topic_id in current.values_list("revision_id", "topic_id").iterator():
            revisions.objects.using(database).filter(pk=revision_id, kind=kind).update(topic_id=topic_id)


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0004_courseversion_published_at_alter_chapter_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="resourceversion",
            name="topic",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                related_name="+", to="content.topic",
            ),
        ),
        migrations.RunPython(retain_current_resource_topics, migrations.RunPython.noop),
    ]
