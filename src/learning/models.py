from django.conf import settings
from django.db import models


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("student", "version"), name="unique_student_course_version")]

    def __str__(self):
        return f"{self.student} · {self.version}"
