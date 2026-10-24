"""Publish the original Creation and Technology collections via normal services."""
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from commerce.offers import create_offer, review_offer, submit_offer
from content.course_catalog import (
    CREATOR_EMAIL,
    REVIEWER_EMAIL,
    SUPPORT,
    load_catalog,
    teaching_body,
)
from content.models import Category, Chapter, Course, Lesson, Topic
from creators.models import CreatorProfile
from creators.services import decide, submit
from learning.models import (
    CertificateDraft,
    PracticeDraft,
    PracticeIntake,
    QuizDraft,
    VersionPractice,
)


def approved_offer(creator, reviewer, target, title, amount):
    offer = create_offer(creator, target, title, amount)
    submit_offer(creator, offer)
    review_offer(reviewer, offer, True, "Precio editorial inicial; no validado con compradores.")
    return offer


@transaction.atomic
def publish_collection(catalog):
    users = get_user_model().objects
    creator, created = users.get_or_create(
        email=CREATOR_EMAIL, account_type="creator", defaults={"first_name": "BTC.EDU"},
    )
    if created:
        creator.set_unusable_password()
        creator.save(update_fields=["password"])
        CreatorProfile.objects.create(
            user=creator, display_name="BTC.EDU · Creación y Tecnología",
            bio="Recorridos originales de autoestudio con prácticas, soluciones y fuentes atribuidas. "
                "Los videos externos son complementos de sus autores. Sin tutorías personales incluidas.",
            specialty="Fotografía, edición de video, desarrollo web y Python", status="approved",
        )
    if not creator.is_active or not CreatorProfile.objects.filter(user=creator, status="approved").exists():
        raise CommandError("El perfil editorial debe estar activo y aprobado.")
    reviewer, created = users.get_or_create(email=REVIEWER_EMAIL, account_type="admin")
    if not created and (reviewer.has_usable_password() or reviewer.is_active or reviewer.is_staff):
        raise CommandError("La identidad reservada de revisión está en uso.")
    reviewer.set_unusable_password()
    reviewer.is_active = reviewer.is_staff = True
    reviewer.save(update_fields=["password", "is_active", "is_staff"])
    reviewer.user_permissions.set(Permission.objects.filter(
        content_type__app_label__in=["content", "creators", "commerce"],
        codename__in=["change_course", "change_submission", "change_offer"],
    ))
    added = 0
    for item in catalog:
        if Course.objects.filter(creator=creator, title=item["title"]).exists():
            continue
        category, _ = Category.objects.get_or_create(
            slug=item["category"]["slug"], defaults={"name": item["category"]["name"]},
        )
        topic, _ = Topic.objects.get_or_create(
            slug=item["topic"]["slug"], defaults={"name": item["topic"]["name"], "category": category},
        )
        if topic.category_id != category.pk:
            raise CommandError(f"La subcategoría {topic} pertenece a otra categoría; no se modifica.")
        course = Course.objects.create(
            creator=creator, title=item["title"], description=item["description"] + "\n\n" + SUPPORT,
            objective=item["objective"], requirements=item["requirements"], topic=topic,
            level=item["level"], estimated_minutes=item["minutes"],
        )
        lessons = []
        for chapter_position, data in enumerate(item["chapters"], 1):
            chapter = Chapter.objects.create(
                course=course, title=data["title"], description=data["description"],
                position=chapter_position, status="published",
            )
            for position, data in enumerate(data["lessons"], 1):
                lesson = Lesson.objects.create(
                    chapter=chapter, position=position, title=data["title"], description=data["description"],
                    learning_outcome=data["outcome"], requirements=item["requirements"],
                    activity_kind=data["activity"], public_preview=data["preview"], support_scope=SUPPORT,
                    body=teaching_body(data), access_type="paid", status="published",
                )
                lessons.append(lesson)
                if data.get("quiz"):
                    quiz = QuizDraft(
                        lesson=lesson, title=data["quiz"]["title"], questions=data["quiz"]["questions"],
                        enabled=True, required=True, pass_mark=75, max_attempts=5, feedback="submitted",
                    )
                    quiz.full_clean()
                    quiz.save()
                if data.get("practice"):
                    project = data["practice"]
                    criteria = [criterion if isinstance(criterion, str) else
                                f"{criterion['label']}: {criterion['description']}" for criterion in project["criteria"]]
                    practice = PracticeDraft(
                        lesson=lesson, title=project["title"], instructions=project["instructions"],
                        criteria=criteria, enabled=True,
                    )
                    practice.full_clean()
                    practice.save()
        certificate = CertificateDraft.objects.create(course=course, enabled=True)
        certificate.required_lessons.set(lessons)
        submission = submit(course, creator)
        decide(submission, reviewer, True,
               "Publicación editorial autorizada por el usuario. Contenido original con fuentes primarias; "
               "comprobación de estructura y acceso. Revisión independiente por especialistas pendiente.")
        version = submission.course_version
        # Autoestudio: no se vende un plazo de revisión sin un educador asignado.
        for practice in VersionPractice.objects.filter(lesson__chapter__version=version):
            PracticeIntake.objects.create(practice=practice, accepting=False)
        lesson_price = (item["price"] + 7) // 8
        for chapter in version.chapters.all():
            for lesson in chapter.lessons.select_related("content"):
                approved_offer(creator, reviewer, f"lesson:{lesson.pk}", lesson.content.title, lesson_price)
            approved_offer(creator, reviewer, f"chapter:{chapter.pk}", chapter.title, lesson_price * 3)
        approved_offer(creator, reviewer, f"course:{version.pk}", item["title"], item["price"])
        added += 1
    reviewer.is_active = reviewer.is_staff = False
    reviewer.save(update_fields=["is_active", "is_staff"])
    reviewer.user_permissions.clear()
    return added


class Command(BaseCommand):
    help = "Publica cuatro cursos completos de pago en Creación y Tecnología, sin sustituir cursos existentes."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Comprueba el contenido y muestra el inventario sin escribir.")

    def handle(self, *args, **options):
        try:
            catalog = load_catalog()
        except (OSError, KeyError, ValueError) as exc:
            raise CommandError(f"Catálogo incompleto: {exc}") from exc
        if options["dry_run"]:
            for item in catalog:
                count = sum(len(chapter["lessons"]) for chapter in item["chapters"])
                self.stdout.write(f"{item['title']}: {len(item['chapters'])} capítulos, {count} lecciones; {item['price']} sats.")
            return
        missing = [item for item in catalog if not Course.objects.filter(
            creator__email=CREATOR_EMAIL, creator__account_type="creator", title=item["title"],
        ).exists()]
        if not missing:
            self.stdout.write("Cursos añadidos: 0. El catálogo ya está cargado; no se modificó ningún curso.")
            return
        database = settings.DATABASES["default"]
        source = Path(database["NAME"])
        if database["ENGINE"] != "django.db.backends.sqlite3" or not source.is_file():
            raise CommandError("La carga requiere una base SQLite existente para respaldarla.")
        directory = settings.BASE_DIR / ".local" / "backups"
        directory.mkdir(parents=True, exist_ok=True)
        backup = directory / f"before-complete-courses-{datetime.now():%Y%m%d-%H%M%S-%f}.sqlite3"
        with sqlite3.connect(source) as origin, sqlite3.connect(backup) as destination:
            origin.backup(destination)
        origin.close()
        destination.close()
        self.stdout.write(f"Respaldo local: {backup}")
        count = publish_collection(missing)
        self.stdout.write(self.style.SUCCESS(f"Cursos añadidos: {count}. Lecciones de pago, evaluaciones, proyectos y ofertas publicados."))
