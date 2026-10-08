from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from content.immutability import FrozenRecord

from .quizzes import validate_questions


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


class QuizRules(models.Model):
    title = models.CharField("título", max_length=200)
    pass_mark = models.PositiveSmallIntegerField("nota mínima", default=70, validators=[MaxValueValidator(100)])
    max_attempts = models.PositiveSmallIntegerField("intentos permitidos", default=3, validators=[MinValueValidator(1), MaxValueValidator(10)])
    wait_minutes = models.PositiveIntegerField("espera entre intentos (minutos)", default=0, validators=[MaxValueValidator(10080)])
    required = models.BooleanField("Exigir aprobación para completar la lección", default=True)
    feedback = models.CharField("mostrar soluciones", max_length=12, default="submitted", choices=(("submitted", "Al entregar cada intento"), ("passed", "Solo al aprobar")))
    questions = models.JSONField(default=list, blank=True)

    class Meta:
        abstract = True


class QuizDraft(QuizRules):
    lesson = models.OneToOneField("content.Lesson", on_delete=models.CASCADE, related_name="quiz_draft")
    enabled = models.BooleanField("Incluir evaluación en la próxima versión", default=True)
    revision = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.enabled or self.questions:
            validate_questions(self.questions)


class VersionQuiz(FrozenRecord, QuizRules):
    lesson = models.OneToOneField("content.VersionLesson", on_delete=models.PROTECT, related_name="quiz")

    def clean(self):
        if self.lesson.chapter.version.sealed:
            raise ValidationError("No se pueden añadir evaluaciones a una versión sellada.")
        validate_questions(self.questions)


class QuizAttempt(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="quiz_attempts")
    quiz = models.ForeignKey(VersionQuiz, on_delete=models.PROTECT, related_name="attempts")
    number = models.PositiveIntegerField()
    answers = models.JSONField(default=dict, blank=True)
    revision = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    correct_count = models.PositiveSmallIntegerField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("enrollment", "quiz", "number"), name="unique_quiz_attempt_number"),
            models.UniqueConstraint(fields=("enrollment", "quiz"), condition=models.Q(submitted_at__isnull=True), name="one_open_quiz_attempt"),
        ]


class ExtraQuizAttempt(FrozenRecord):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT)
    quiz = models.ForeignKey(VersionQuiz, on_delete=models.PROTECT)
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    # One grant for an exhausted allowance; retrying the same request is harmless.
    allowance_before = models.PositiveIntegerField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=("enrollment", "quiz", "allowance_before"), name="unique_extra_quiz_allowance")]
