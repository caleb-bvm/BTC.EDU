"""Task-oriented presentation of a creator's editable work, without publication writes."""
from django.urls import reverse

from content.education import EDUCATION_FIELDS
from content.models import Course, Material, VersionLesson, Video
from learning.models import CertificateDraft

from .models import Submission

COURSE_FIELDS = ("title", "description", "objective", "requirements", "kind", "topic_id", "level", "estimated_minutes")
UNIT_FIELDS = ("title", "description", *EDUCATION_FIELDS, "access_type", "body")
QUIZ_FIELDS = ("title", "pass_mark", "max_attempts", "wait_minutes", "required", "feedback", "questions")


def course_sections(course, selected="informacion"):
    if not course.pk:
        return []
    home = reverse("creator-course", args=[course.pk])
    return [{"key": key, "label": label, "url": url, "active": selected == key} for key, label, url in (
        ("informacion", "Información", home + "?seccion=informacion"),
        ("temario", "Temario", home + "?seccion=temario"),
        ("evaluaciones", "Evaluaciones", home + "?seccion=evaluaciones"),
        ("certificado", "Certificado", reverse("creator-certificate-policy", args=[course.pk])),
        ("publicacion", "Publicación", home + "?seccion=publicacion"),
        ("precio", "Acceso y precio", home + "?seccion=precio"),
    )]


def form_groups(form):
    if form.__class__.__name__ == "LessonForm":
        groups = (
            ("Sobre la lección", ("title", "description")),
            ("Aprendizaje y acompañamiento", EDUCATION_FIELDS),
            ("Contenido", ("body",)),
            ("Videos y materiales", ("resources",)),
            ("Acceso y ubicación", ("access_type", "position", "status")),
        )
    elif form.__class__.__name__ in ("ResourceForm", "MaterialForm"):
        groups = (
            ("Sobre el recurso", ("title", "description", "topic")),
            ("Aprendizaje y acompañamiento", EDUCATION_FIELDS),
            ("Archivo y accesibilidad", ("new_file", "pending_asset", "new_subtitles", "pending_subtitles", "transcript")),
            ("Acceso", ("access_type",)),
        )
    elif form.__class__.__name__ == "CourseForm":
        groups = (
            ("Presentación", ("title", "kind", "description")),
            ("Resultado y requisitos", ("objective", "requirements")),
            ("Descubrimiento", ("topic", "level", "estimated_minutes")),
        )
    else:
        return []
    return [{"title": title, "fields": [form[name] for name in names if name in form.fields]} for title, names in groups]


def course_requirements(course):
    """Point at actual publication blockers; the publication service remains authoritative."""
    checks = []
    home = reverse("creator-course", args=[course.pk])
    info_ok = bool(course.title.strip() and course.description.strip())
    checks.append({"label": "Título y descripción", "ready": info_ok, "url": home + "?seccion=informacion", "action": "Completar información"})
    chapters = list(course.chapters.all())
    included = [chapter for chapter in chapters if chapter.status == "published"]
    lessons = [lesson for chapter in included for lesson in chapter.lessons.all() if lesson.status == "published"]
    structure_ok = bool(included) and all(any(lesson.status == "published" for lesson in chapter.lessons.all()) for chapter in included)
    checks.append({"label": "Capítulos con lecciones incluidas", "ready": structure_ok, "url": home + "?seccion=temario", "action": "Organizar temario"})
    for lesson in lessons:
        checks.append({"label": lesson.title + ": contenido y ficha educativa", "ready": bool(lesson.body.strip()) and all(getattr(lesson, name).strip() for name in EDUCATION_FIELDS), "url": reverse("creator-lesson", args=[lesson.chapter_id, lesson.pk]), "action": "Completar lección"})
        quiz = getattr(lesson, "quiz_draft", None)
        if quiz and quiz.enabled:
            checks.append({"label": lesson.title + ": evaluación", "ready": bool(quiz.questions), "url": reverse("creator-quiz", args=[lesson.pk]), "action": "Revisar evaluación"})
    certificate = CertificateDraft.objects.filter(course=course).first()
    if certificate and certificate.enabled:
        required = list(certificate.required_lessons.select_related("chapter"))
        checks.append({"label": "Lecciones requeridas para el certificado", "ready": bool(required) and all(lesson.status == "published" and lesson.chapter.status == "published" for lesson in required), "url": reverse("creator-certificate-policy", args=[course.pk]), "action": "Ajustar certificado"})
    return checks


def resource_requirements(item):
    return [
        {"label": "Título y descripción", "ready": bool(item.title.strip() and item.description.strip()), "url": "#id_title", "action": "Completar información"},
        {"label": "Resultado, requisitos, muestra y acompañamiento", "ready": all(getattr(item, field).strip() for field in EDUCATION_FIELDS), "url": "#id_learning_outcome", "action": "Completar ficha"},
        {"label": "Archivo seleccionado", "ready": bool(item.pending_asset_id), "url": "#id_new_file", "action": "Seleccionar archivo"},
    ]


def course_has_changes(course):
    version = course.current_version
    if not version or any(getattr(course, name) != getattr(version, name) for name in COURSE_FIELDS):
        return True
    chapters = [chapter for chapter in course.chapters.all() if chapter.status == "published"]
    frozen = list(version.chapters.prefetch_related("lessons__content", "lessons__attachments", "lessons__quiz"))
    if len(chapters) != len(frozen):
        return True
    for chapter, snapshot in zip(chapters, frozen):
        if any(getattr(chapter, field) != getattr(snapshot, field) for field in ("title", "description", "position")):
            return True
        lessons = [lesson for lesson in chapter.lessons.all() if lesson.status == "published"]
        stored = list(snapshot.lessons.all())
        if len(lessons) != len(stored):
            return True
        for lesson, record in zip(lessons, stored):
            if lesson.pk != record.source_lesson_id or lesson.position != record.position or any(getattr(lesson, name) != getattr(record.content, name) for name in UNIT_FIELDS):
                return True
            if [(a.position, a.resource_id) for a in lesson.attachments.all()] != [(a.position, a.resource_id) for a in record.attachments.all()]:
                return True
            draft_quiz = getattr(lesson, "quiz_draft", None)
            published_quiz = getattr(record, "quiz", None)
            enabled = bool(draft_quiz and draft_quiz.enabled)
            if enabled != bool(published_quiz) or enabled and any(getattr(draft_quiz, name) != getattr(published_quiz, name) for name in QUIZ_FIELDS):
                return True
    policy = getattr(version, "certificate_policy", None)
    draft = CertificateDraft.objects.filter(course=course).first()
    if bool(draft and draft.enabled) != bool(policy):
        return True
    if policy:
        source_ids = set(VersionLesson.objects.filter(chapter__version=version, pk__in=policy.required_lesson_ids).values_list("source_lesson_id", flat=True))
        if source_ids != set(draft.required_lessons.values_list("pk", flat=True)):
            return True
    return False


def content_cards(actor):
    submissions = list(Submission.objects.filter(creator=actor).select_related("course_version", "resource_version").order_by("-created_at", "-pk"))
    latest = {}
    for submission in submissions:
        key = ("course", submission.course_id) if submission.course_id else ("video", submission.video_id) if submission.video_id else ("material", submission.material_id)
        latest.setdefault(key, submission)
    cards = []
    courses = Course.objects.filter(creator=actor).select_related("current_version", "topic").prefetch_related("chapters__lessons__attachments", "chapters__lessons__quiz_draft")
    for model, kind in ((Course, "course"), (Video, "video"), (Material, "material")):
        items = courses if model is Course else model.objects.filter(creator=actor).select_related("revision", "topic")
        for item in items:
            snapshot = item.current_version if kind == "course" else item.revision
            submission = latest.get((kind, item.pk))
            if kind == "course":
                changed = course_has_changes(item)
                url = reverse("creator-course", args=[item.pk])
                label = item.get_kind_display()
            else:
                fields = ("title", "description", *EDUCATION_FIELDS, "topic_id", "access_type")
                changed = not snapshot or any(getattr(item, name) != getattr(snapshot, name) for name in fields) or item.transcript != snapshot.body or item.pending_asset_id != snapshot.asset_id or item.pending_subtitles_id != snapshot.subtitles_id
                url = reverse("creator-resource", args=["videos" if kind == "video" else "materiales", item.pk])
                label = "Video" if kind == "video" else "Material"
            state = "review" if submission and submission.status == "pending" else "changes" if submission and submission.status == "changes" else "draft" if changed else "published"
            cards.append({"item": item, "kind": item.kind if kind == "course" else kind, "type_label": label, "snapshot": snapshot, "changed": changed, "submission": submission, "state": state, "url": url, "updated_at": item.updated_at})
    return sorted(cards, key=lambda card: (card["updated_at"], card["item"].pk), reverse=True)
