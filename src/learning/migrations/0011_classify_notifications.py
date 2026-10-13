from django.db import migrations


def classify(apps, schema_editor):
    Notification = apps.get_model("learning", "Notification")
    for prefix, category in (("question:", "questions"), ("reply:", "questions"),
                             ("community-reply:", "community"), ("community-lesson:", "community")):
        Notification.objects.filter(event_key__startswith=prefix).update(category=category)


class Migration(migrations.Migration):
    dependencies = [("learning", "0010_saveditem")]
    operations = [migrations.RunPython(classify, migrations.RunPython.noop)]
