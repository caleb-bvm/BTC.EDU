"""Carga explícita, transaccional e idempotente del catálogo editorial."""
import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from commerce.offers import create_offer, review_offer, submit_offer
from content.editorial_catalog import CATALOG
from content.models import Category, Chapter, Course, Lesson, Topic
from creators.models import CreatorProfile
from creators.services import decide, submit
from learning.models import CertificateDraft, QuizDraft


def editorial_topic(item, category):
    topic_name = {"bitcoin": "Fundamentos de Bitcoin", "seguridad": "Seguridad y autocustodia"}.get(item["slug"], item["topic"])
    topic = Topic.objects.filter(slug=item["slug"]).first()
    if topic is None:
        topic = Topic.objects.filter(name__in=(topic_name, item["topic"])).order_by("pk").first()
    if topic is None:
        topic, _ = Topic.objects.get_or_create(slug=item["slug"], defaults={"name": topic_name, "category": category})
    if topic.category_id is None:
        topic.category = category
        topic.save(update_fields=["category"])
    return topic


class Command(BaseCommand):
    help = "Publica seis cursos de Bitcoin y Lightning sin modificar cursos existentes."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Muestra inventario sin escribir.")

    def handle(self, *args, **options):
        if options["dry_run"]:
            for item in CATALOG:
                self.stdout.write(f"{item['title']}: {len(item['lessons'])} lecciones; {item['price'] or 'Gratis'}")
            return
        db = settings.DATABASES["default"]
        if db["ENGINE"] != "django.db.backends.sqlite3" or not Path(db["NAME"]).is_file():
            raise CommandError("La carga requiere SQLite existente para crear respaldo.")
        source = Path(db["NAME"])
        backup = source.with_name(f"{source.stem}-before-editorial-{datetime.now():%Y%m%d-%H%M%S-%f}.sqlite3")
        with sqlite3.connect(source) as origin, sqlite3.connect(backup) as destination:
            origin.backup(destination)
        origin.close()
        destination.close()
        self.stdout.write(f"Respaldo: {backup}")
        with transaction.atomic():
            users = get_user_model().objects
            creator, created = users.get_or_create(email="editorial@btc-edu.invalid", account_type="creator",
                                                 defaults={"first_name": "BTC.EDU"})
            if created:
                creator.set_unusable_password()
                creator.save(update_fields=["password"])
                CreatorProfile.objects.create(user=creator, display_name="BTC.EDU",
                                              bio="Material introductorio de Bitcoin y Lightning con ejercicios guiados.",
                                              specialty="Bitcoin y Lightning", status="approved")
            if not creator.is_active or not CreatorProfile.objects.filter(user=creator, status="approved").exists():
                raise CommandError("El perfil editorial existente debe estar activo y aprobado.")
            reviewer, created = users.get_or_create(email="revision-editorial@btc-edu.invalid", account_type="admin")
            if not created and (reviewer.has_usable_password() or reviewer.is_active or reviewer.is_staff):
                raise CommandError("La identidad reservada de revisión ya está en uso.")
            reviewer.set_unusable_password()
            reviewer.is_active = True
            reviewer.is_staff = True
            reviewer.save(update_fields=["password", "is_active", "is_staff"])
            reviewer.user_permissions.set(Permission.objects.filter(
                content_type__app_label__in=["content", "creators", "commerce"],
                codename__in=["change_course", "change_submission", "change_offer"]))
            added = 0
            bitcoin, _ = Category.objects.get_or_create(slug="bitcoin", defaults={"name": "Bitcoin"})
            for item in CATALOG:
                if Course.objects.filter(creator=creator, title=item["title"]).exists():
                    continue
                topic = editorial_topic(item, bitcoin)
                course = Course.objects.create(creator=creator, title=item["title"], description=item["description"],
                                               objective=item["objective"], requirements=item["requirements"],
                                               topic=topic, level="beginner", estimated_minutes=item["minutes"])
                lessons = []
                for index, title in enumerate(item["chapters"]):
                    chapter = Chapter.objects.create(course=course, title=title, position=index + 1, status="published")
                    for offset, data in enumerate(item["lessons"][index * 2:index * 2 + 2]):
                        position = index * 2 + offset
                        entry = Lesson.objects.create(chapter=chapter, title=data["title"],
                                                      description="Lee la explicación, resuelve la práctica y compara tu respuesta.",
                                                      body=data["body"] + f"\n\nPara profundizar\n{item['source']}",
                                                      position=offset + 1, status="published",
                                                      access_type="paid" if item["price"] and position else "free",
                                                      learning_outcome=data["learning_outcome"], requirements=item["requirements"],
                                                      activity_kind=data["activity_kind"], public_preview=data["public_preview"],
                                                      support_scope="Practica con el ejemplo y compara tu respuesta con la solución. Las preguntas y conversaciones se mantienen dentro de la plataforma, sin un plazo de respuesta garantizado.")
                        lessons.append(entry)
                prompt, answers, explanation = item["question"]
                quiz = QuizDraft(lesson=lessons[-1], title="Comprueba lo aprendido", enabled=True, pass_mark=100,
                                 questions=[dict(prompt=prompt, multiple=False, options=answers, correct=[0], explanation=explanation)])
                quiz.full_clean()
                quiz.save()
                policy = CertificateDraft.objects.create(course=course, enabled=True)
                policy.required_lessons.set(lessons)
                submission = submit(course, creator)
                decide(submission, reviewer, True, "Carga editorial solicitada; revisión educativa externa pendiente.")
                version = submission.course_version
                if item["price"]:
                    for chapter in version.chapters.all():
                        for entry in chapter.lessons.select_related("content"):
                            if entry.content.access_type == "paid":
                                self.offer(creator, reviewer, f"lesson:{entry.pk}", entry.content.title, 50)
                    self.offer(creator, reviewer, f"course:{version.pk}", item["title"], item["price"])
                added += 1
            reviewer.is_active = False
            reviewer.is_staff = False
            reviewer.save(update_fields=["is_active", "is_staff"])
            reviewer.user_permissions.clear()
        self.stdout.write(self.style.SUCCESS(f"Cursos añadidos: {added}. Cursos existentes conservados."))

    @staticmethod
    def offer(creator, reviewer, target, title, amount):
        offer = create_offer(creator, target, title, amount)
        submit_offer(creator, offer)
        review_offer(reviewer, offer, True)
