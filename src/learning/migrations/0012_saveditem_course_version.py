import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0011_classify_notifications"),
        ("content", "0004_courseversion_published_at_alter_chapter_status_and_more"),
    ]
    operations = [
        migrations.RemoveConstraint(model_name="saveditem", name="saved_item_one_target"),
        migrations.AddField(
            model_name="saveditem", name="course_version",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="content.courseversion"),
        ),
        migrations.AddConstraint(
            model_name="saveditem",
            constraint=models.CheckConstraint(
                condition=(models.Q(resource__isnull=False, reference__isnull=True, course_version__isnull=True)
                           | models.Q(resource__isnull=True, reference__isnull=False, course_version__isnull=True)
                           | models.Q(resource__isnull=True, reference__isnull=True, course_version__isnull=False)),
                name="saved_item_one_target",
            ),
        ),
        migrations.AddConstraint(
            model_name="saveditem",
            constraint=models.UniqueConstraint(fields=("student", "course_version"), name="unique_saved_course_version"),
        ),
    ]
