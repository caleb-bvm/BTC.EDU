"""Read-only learning navigation shared by the course and personal library."""
from django.urls import reverse

from content.access import content_access

from .models import Enrollment, VersionQuiz


def continuation(lessons, completed, last_id, accessible):
    """Resume unfinished work, then the next accessible lesson, then review."""
    def identifier(item):
        return getattr(item, "version_record", item).pk

    pending = [item for item in lessons if identifier(item) in accessible and identifier(item) not in completed]
    last_index = next((index for index, item in enumerate(lessons) if identifier(item) == last_id), -1)
    if last_index >= 0 and lessons[last_index] in pending:
        return lessons[last_index]
    following = [item for item in lessons[last_index + 1:] if item in pending]
    if pending:
        return following[0] if following else pending[0]
    if lessons and all(identifier(item) in completed for item in lessons):
        return next((item for item in lessons if identifier(item) in accessible), None)
    return None


def library_journey(user, enrollment):
    """Attach version-specific progress and the next accessible step to a card."""
    version = enrollment.version
    lessons = [lesson for chapter in version.chapters.all() for lesson in chapter.lessons.all()]
    completed = {item.lesson_id for item in enrollment.completed_lessons.all()}
    first = continuation(lessons, completed, enrollment.last_lesson_id,
                         {lesson.pk for lesson in lessons if content_access(user, lesson).allowed})
    enrollment.is_complete = bool(lessons and len(completed) == len(lessons))
    enrollment.open_label = "Ver opciones de acceso" if not first else "Repasar" if enrollment.is_complete else "Continuar" if enrollment.last_lesson_id or completed else "Empezar"
    enrollment.open_url = reverse("version-lesson", args=[version.course_id, version.number, first.pk]) if first else reverse("course-version", args=[version.course_id, version.number])
    enrollment.lesson_count = len(lessons)
    enrollment.completed_count = len(completed)
    enrollment.percentage = round(len(completed) * 100 / len(lessons)) if lessons else 0
    enrollment.retired = version.course.status == "archived" or version.course.current_version_id != version.pk
    enrollment.next_title = first.content.title if first else "Revisa las opciones de acceso"
    enrollment.state_label = "Completado" if enrollment.is_complete else "En curso" if enrollment.last_lesson_id or completed else "Por empezar"
    enrollment.can_continue = bool(first and not enrollment.is_complete)
    enrollment.needs_access = bool(lessons and not first and not enrollment.is_complete)
    enrollment.remaining_count = len(lessons) - len(completed)
    # One segment per lesson, scaled down to 24 so long courses keep a legible track.
    segments = min(len(lessons), 24)
    filled = round(len(completed) * segments / len(lessons)) if lessons else 0
    enrollment.segments = [index < filled for index in range(segments)]
    return enrollment


def course_learning_context(user, course, version=None, current_id=None):
    lessons = [item for chapter in course.visible_chapters for item in chapter.visible_lessons]
    student = user.is_authenticated and user.is_active and user.account_type == "student"
    enrollment = Enrollment.objects.filter(student=user, version=version).first() if student and version else None
    completed = set(enrollment.completed_lessons.values_list("lesson_id", flat=True)) if enrollment else set()
    quizzes = dict(VersionQuiz.objects.filter(lesson__chapter__version=version).values_list("lesson_id", "required")) if version else {}
    accessible = set()
    for number, lesson in enumerate(lessons, 1):
        record = getattr(lesson, "version_record", lesson)
        lesson.learning_id = record.pk
        lesson.learning_number = number
        lesson.learning_allowed = content_access(user, record).allowed
        lesson.learning_completed = record.pk in completed
        lesson.learning_current = record.pk == current_id
        lesson.learning_quiz = record.pk in quizzes
        lesson.learning_required_quiz = quizzes.get(record.pk, False)
        lesson.learning_state = "Completada" if lesson.learning_completed else "Por estudiar" if lesson.learning_allowed else "Requiere acceso"
        if lesson.learning_allowed:
            accessible.add(record.pk)
    for chapter in course.visible_chapters:
        chapter.learning_completed = sum(item.learning_completed for item in chapter.visible_lessons)
        chapter.learning_current = any(item.learning_current for item in chapter.visible_lessons)
    target = continuation(lessons, completed, enrollment.last_lesson_id if enrollment else None, accessible)
    total = len(lessons)
    done = sum(item.learning_completed for item in lessons)
    all_done = bool(total and done == total)
    content_kind = "tutorial" if (version.kind if version else course.kind) == "tutorial" else "curso"
    action = "Repasar" if all_done else "Continuar" if enrollment and (done or enrollment.last_lesson_id) else "Empezar"
    label = f"{action} {content_kind}"
    if not target:
        label = "Ver opciones de acceso"
    return {"journey": {"enrollment": enrollment, "target": target, "label": label,
                         "completed": done, "total": total, "percentage": round(done * 100 / total) if total else 0,
                         "all_done": all_done, "locked": total - len(accessible)},
            "enrolled": bool(enrollment)}
