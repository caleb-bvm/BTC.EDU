from django.db.models import Prefetch, Q
from django.urls import reverse

from .models import (
    AccessType,
    Chapter,
    Course,
    Lesson,
    Material,
    PublicationStatus,
    Video,
)


def course_tree(preview=False):
    chapters = Chapter.objects.order_by("position", "pk")
    lessons = Lesson.objects.defer("body").order_by("position", "pk")
    if not preview:
        chapters = chapters.filter(status=PublicationStatus.PUBLISHED)
        lessons = lessons.filter(status=PublicationStatus.PUBLISHED)
    return chapters.prefetch_related(
        Prefetch("lessons", queryset=lessons, to_attr="visible_lessons")
    )


def course_summary(course):
    lessons = [
        lesson
        for chapter in course.visible_chapters
        for lesson in chapter.visible_lessons
    ]
    free = sum(lesson.access_type == AccessType.FREE for lesson in lessons)
    paid = len(lessons) - free
    label = (
        "Gratis + lecciones de pago"
        if free and paid
        else "Lecciones de pago"
        if paid
        else "Gratis"
        if free
        else "Temario en preparación"
    )
    return {
        "lessons": lessons,
        "free_count": free,
        "paid_count": paid,
        "access_label": label,
    }


def catalog_context(params):
    categories = {
        "todos": "Todo",
        "cursos": "Cursos",
        "videos": "Videos",
        "materiales": "Materiales",
    }
    category = params.get("tipo", "todos")
    if category not in categories:
        category = "todos"
    access = params.get("acceso", "todos")
    if access not in ("todos", "gratis", "pago"):
        access = "todos"
    query = params.get("q", "").strip()[:200]
    cards = []
    for kind, model, label in (
        ("cursos", Course, "Curso"),
        ("videos", Video, "Video"),
        ("materiales", Material, "Material"),
    ):
        if category not in ("todos", kind):
            continue
        items = model.objects.filter(status=PublicationStatus.PUBLISHED).select_related(
            "creator"
        )
        if query:
            items = items.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if model == Course:
            items = items.prefetch_related(
                Prefetch("chapters", queryset=course_tree(), to_attr="visible_chapters")
            )
        for item in items:
            summary = course_summary(item) if model == Course else None
            free = (
                summary["free_count"] > 0
                if summary
                else item.access_type == AccessType.FREE
            )
            paid = (
                summary["paid_count"] > 0
                if summary
                else item.access_type == AccessType.PAID
            )
            if (access == "gratis" and not free) or (access == "pago" and not paid):
                continue
            creator = item.creator.get_full_name().strip() or "Creador de BTC.EDU"
            url = (
                reverse("course-detail", args=[item.pk])
                if summary
                else reverse("resource-detail", args=[kind, item.pk])
            )
            cards.append(
                {
                    "item": item,
                    "kind": label,
                    "creator": creator,
                    "url": url,
                    "summary": summary,
                    "access_label": summary["access_label"]
                    if summary
                    else item.get_access_type_display(),
                }
            )
    cards.sort(
        key=lambda card: (card["item"].title.casefold(), card["kind"], card["item"].pk)
    )
    return {
        "category": category,
        "categories": categories,
        "access_filter": access,
        "query": query,
        "cards": cards,
        "filtered": bool(query or access != "todos"),
    }
