"""Publish the original tutorials and curated resources via the normal review services."""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.course_catalog import CREATOR_EMAIL, unit_price
from content.course_catalog import load_catalog as course_catalog
from content.management.commands.load_complete_courses import (
    approved_offer,
    backup_database,
    close_review,
    editorial_team,
)
from content.models import (
    Category,
    Chapter,
    Course,
    CourseKind,
    ExternalReference,
    Lesson,
    Material,
    PublicationStatus,
    Topic,
    VersionLesson,
    Video,
)
from content.tutorial_catalog import (
    RESOURCE_SUPPORT,
    TUTORIAL_SUPPORT,
    load_catalog,
    step_body,
    tutorial_steps,
)
from content.tutorial_catalog.pdf import render_material
from creators.services import decide, submit
from media.models import Asset

APPROVAL = ("Publicación editorial autorizada por el usuario. Contenido original o curado con fuentes atribuidas; "
            "comprobación de estructura y acceso. Revisión independiente por especialistas pendiente.")
MODELS = {"video": Video, "material": Material, "reference": ExternalReference}


def topic_for(slug):
    """Use the subcategory of the complete courses, creating it from their catalog on a fresh database."""
    topic = Topic.objects.select_related("category").filter(slug=slug).first()
    if topic is None:
        item = next((item for item in course_catalog() if item["topic"]["slug"] == slug), None)
        if item is None:
            raise CommandError(f"La subcategoría «{slug}» no existe en el catálogo.")
        category, _ = Category.objects.get_or_create(slug=item["category"]["slug"], defaults={"name": item["category"]["name"]})
        topic = Topic.objects.create(slug=slug, name=item["topic"]["name"], category=category)
    if topic.category_id is None:
        raise CommandError(f"La subcategoría «{slug}» no tiene categoría.")
    return topic


def publish_tutorial(item, creator, reviewer):
    course = Course.objects.create(
        creator=creator, kind=CourseKind.TUTORIAL, title=item["title"],
        description=item["description"] + "\n\n" + TUTORIAL_SUPPORT, objective=item["objective"],
        requirements=item["requirements"], topic=topic_for(item["topic"]), level=item["level"],
        estimated_minutes=item["minutes"],
    )
    chapter = Chapter.objects.create(course=course, title="Pasos", description=item["objective"], position=1, status="published")
    for position, step in enumerate(tutorial_steps(item), 1):
        Lesson.objects.create(
            chapter=chapter, position=position, title=step["title"], description=step["description"],
            learning_outcome=step["outcome"], requirements=item["requirements"], activity_kind=step["activity"],
            public_preview=step["preview"], support_scope=TUTORIAL_SUPPORT, body=step_body(step),
            access_type="free" if step["free"] else "paid", status="published",
        )
    submission = submit(course, creator)
    decide(submission, reviewer, True, APPROVAL)
    version = submission.course_version
    if item["access"] != "free":
        paid = list(VersionLesson.objects.filter(chapter__version=version, content__access_type="paid").select_related("content"))
        lesson_price = unit_price(item["price"], len(paid))
        for lesson in paid:
            approved_offer(creator, reviewer, f"lesson:{lesson.pk}", lesson.content.title, lesson_price)
        approved_offer(creator, reviewer, f"course:{version.pk}", item["title"], item["price"])


def publish_resource(item, creator, reviewer):
    topic = topic_for(item["topic"])
    if item["kind"] == "reference":
        ExternalReference.objects.create(
            title=item["title"], description=item["description"], topic=topic,
            source_name=item["source_name"], source_url=item["source_url"], status=PublicationStatus.PUBLISHED,
        )
        return
    values = {
        "creator": creator, "title": item["title"], "description": item["description"], "topic": topic,
        "learning_outcome": item["outcome"], "requirements": item["requirements"], "activity_kind": item["activity"],
        "public_preview": item["preview"], "support_scope": RESOURCE_SUPPORT,
    }
    if item["kind"] == "video":
        resource = Video.objects.create(**values, access_type="free", video_url=item["video_url"], video_author=item["video_author"])
    else:
        pdf = render_material(item, topic.category.name)
        asset = Asset(creator=creator, file=SimpleUploadedFile(f"{item['slug']}.pdf", pdf, content_type="application/pdf"))
        asset.save()
        resource = Material.objects.create(**values, access_type=item["access"], pending_asset=asset)
    submission = submit(resource, creator)
    decide(submission, reviewer, True, APPROVAL)
    if item["kind"] == "material" and item["access"] == "paid":
        approved_offer(creator, reviewer, f"resource:{submission.resource_version.pk}", item["title"], item["price"])


def exists(kind, item):
    if kind == "tutorial":
        return Course.objects.filter(creator__email=CREATOR_EMAIL, title=item["title"]).exists()
    if item["kind"] == "reference":
        return ExternalReference.objects.filter(source_url=item["source_url"]).exists()
    return MODELS[item["kind"]].objects.filter(creator__email=CREATOR_EMAIL, title=item["title"]).exists()


@transaction.atomic
def publish_catalog(tutorials, resources):
    creator, reviewer = editorial_team()
    for item in tutorials:
        publish_tutorial(item, creator, reviewer)
    for item in resources:
        publish_resource(item, creator, reviewer)
    close_review(reviewer)


class Command(BaseCommand):
    help = "Publica los tutoriales y recursos de cada categoría sin sustituir contenido existente."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Comprueba el contenido y muestra el inventario sin escribir.")

    def handle(self, *args, **options):
        try:
            tutorials, resources = load_catalog()
        except (OSError, KeyError, ValueError) as exc:
            raise CommandError(f"Catálogo incompleto: {exc}") from exc
        if options["dry_run"]:
            for item in tutorials:
                price = "gratis" if item["access"] == "free" else f"{item['access']}, {item['price']} sats"
                self.stdout.write(f"Tutorial · {item['title']}: {len(item['steps'])} pasos, ~{item['minutes']} min; {price}.")
            for item in resources:
                self.stdout.write(f"{item['kind'].capitalize()} · {item['title']}.")
            return
        tutorials = [item for item in tutorials if not exists("tutorial", item)]
        resources = [item for item in resources if not exists("resource", item)]
        if not tutorials and not resources:
            self.stdout.write("Tutoriales y recursos añadidos: 0. El catálogo ya está cargado.")
            return
        backup = backup_database("before-tutorials-resources")
        self.stdout.write(f"Respaldo local: {backup}")
        publish_catalog(tutorials, resources)
        self.stdout.write(self.style.SUCCESS(f"Tutoriales añadidos: {len(tutorials)}. Recursos añadidos: {len(resources)}."))
