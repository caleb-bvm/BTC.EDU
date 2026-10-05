from django.conf import settings
from django.db import models


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    last_lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT, null=True, blank=True, related_name="+")
    revision = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("student", "version"), name="unique_student_course_version")]

    def __str__(self):
        return f"{self.student} · {self.version}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="completed_lessons")
    lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("enrollment", "lesson"), name="unique_completed_enrollment_lesson")]
