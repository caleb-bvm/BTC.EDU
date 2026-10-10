import hashlib
import json
from datetime import UTC

import django.utils.timezone
from django.db import migrations, models


def backfill_fingerprints(apps, schema_editor):
    Certificate = apps.get_model("learning", "Certificate")
    database = schema_editor.connection.alias
    for certificate in Certificate.objects.using(database).select_related("enrollment__version").iterator():
        def canonical(value):
            return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        record = {
            "schema": "btc.edu.certificate.v1",
            "id": str(certificate.pk),
            "student_name": certificate.student_name,
            "course_title": certificate.course_title,
            "creator_name": certificate.creator_name,
            "version": certificate.enrollment.version.number,
            "issued_at": certificate.issued_at.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z"),
            "evidence_sha256": hashlib.sha256(canonical(certificate.evidence)).hexdigest(),
        }
        Certificate.objects.using(database).filter(pk=certificate.pk).update(fingerprint=hashlib.sha256(canonical(record)).hexdigest())


class Migration(migrations.Migration):
    dependencies = [("learning", "0004_certificate_certificatedraft_certificaterevocation_and_more")]
    operations = [
        migrations.AddField(model_name="certificate", name="fingerprint", field=models.CharField(default="", editable=False, max_length=64), preserve_default=False),
        migrations.AlterField(model_name="certificate", name="issued_at", field=models.DateTimeField(default=django.utils.timezone.now, editable=False)),
        migrations.RunPython(backfill_fingerprints, migrations.RunPython.noop),
    ]
