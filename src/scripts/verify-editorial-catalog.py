"""Verifica el catálogo en una copia SQLite; no registra visitas en la base principal."""
import os
import sqlite3
import sys
import tempfile
from contextlib import ExitStack
from io import StringIO
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SRC))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform_config.settings")

import django  # noqa: E402
from django.conf import settings  # noqa: E402

source = settings.DATABASES["default"]["NAME"]
with tempfile.TemporaryDirectory(prefix="verify-editorial-") as temporary, ExitStack() as cleanup:
    database = Path(temporary) / "catalog.sqlite3"
    with sqlite3.connect(source) as origin, sqlite3.connect(database) as destination:
        origin.backup(destination)
    origin.close()
    destination.close()
    settings.DATABASES["default"]["NAME"] = database
    django.setup()
    from django.core.management import call_command
    from django.db import connections
    from django.test import Client
    from django.urls import reverse

    from accounts.models import User
    from commerce.models import Offer
    from content.editorial_catalog import CATALOG
    from content.models import Course, CourseVersion, Lesson, ResourceVersion
    from creators.models import Submission
    from learning.models import VersionCertificatePolicy, VersionQuiz

    cleanup.callback(connections.close_all)

    output = StringIO()
    models = [Course, CourseVersion, Lesson, ResourceVersion, Offer, Submission]
    before = [model.objects.count() for model in models]
    call_command("load_editorial_catalog", stdout=output)
    call_command("load_editorial_catalog", stdout=output)
    assert before == [model.objects.count() for model in models], "La recarga duplicó registros"
    client = Client(HTTP_HOST="localhost")
    for name in ["courses", "explore", "course-selector"]:
        assert client.get(reverse(name)).status_code == 200, name
    free = paid = 0
    for item in CATALOG:
        course = Course.objects.get(creator__email="editorial@btc-edu.invalid", title=item["title"])
        version = course.current_version
        assert version.sealed and version.published_at
        response = client.get(reverse("course-detail", args=[course.pk]))
        assert response.status_code == 200 and item["title"] in response.content.decode()
        entries = [entry for chapter in version.chapters.all() for entry in chapter.lessons.select_related("content")]
        assert len(entries) == 4
        policy = VersionCertificatePolicy.objects.get(version=version)
        assert set(policy.required_lesson_ids) == {entry.pk for entry in entries}
        quiz = VersionQuiz.objects.get(lesson=entries[-1])
        from learning.quizzes import validate_questions
        validate_questions(quiz.questions)
        for entry in entries:
            response = client.get(reverse("version-lesson", args=[course.pk, version.number, entry.pk]))
            body = response.content.decode()
            if entry.content.access_type == "free":
                assert response.status_code == 200
                assert "Solución y comprobación" in body
                free += 1
            else:
                assert response.status_code == 403
                assert "Solución y comprobación" not in body, "Texto pagado expuesto"
                assert "Esta lección requiere una compra" in body
                assert Offer.objects.filter(lesson=entry, status="active", amount_sats=50).exists()
                paid += 1
        if item["price"]:
            assert Offer.objects.filter(course_version=version, kind="course", status="active", amount_sats=120).count() == 1
    reviewer = User.objects.get(email="revision-editorial@btc-edu.invalid", account_type="admin")
    assert not reviewer.is_active and not reviewer.is_staff and not reviewer.has_usable_password()
    assert not reviewer.user_permissions.exists()
    assert free == 15 and paid == 9
    print("OK: 6 cursos, 24 lecciones, 6 evaluaciones y 6 políticas de certificado.")
    print("OK: catálogo, selector, 6 fichas y 24 lecciones por HTTP; 15 gratis y 9 protegidas.")
    print("OK: 12 ofertas activas; recarga repetida sin duplicados; revisión sin acceso de login.")
    connections.close_all()
