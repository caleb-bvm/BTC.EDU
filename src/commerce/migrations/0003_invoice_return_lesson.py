import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("commerce", "0002_remove_invoice_one_pending_invoice_per_offer_and_more"),
        ("content", "0004_courseversion_published_at_alter_chapter_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="return_lesson",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name="purchase_returns", to="content.versionlesson"),
        ),
    ]
