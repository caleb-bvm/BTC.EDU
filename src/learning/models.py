import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

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


class CertificateDraft(models.Model):
    course = models.OneToOneField("content.Course", on_delete=models.CASCADE, related_name="certificate_draft")
    enabled = models.BooleanField("Ofrecer certificado de finalización", default=False)
    required_lessons = models.ManyToManyField("content.Lesson", blank=True)
    revision = models.PositiveIntegerField(default=0)


class VersionCertificatePolicy(FrozenRecord):
    version = models.OneToOneField("content.CourseVersion", on_delete=models.PROTECT, related_name="certificate_policy")
    required_lesson_ids = models.JSONField(default=list)

    def clean(self):
        from content.models import VersionLesson
        ids = self.required_lesson_ids
        if (self.version.sealed or not isinstance(ids, list) or not ids
                or any(type(value) is not int for value in ids) or len(ids) != len(set(ids))
                or VersionLesson.objects.filter(chapter__version=self.version, pk__in=ids).count() != len(ids)):
            raise ValidationError("El certificado requiere lecciones incluidas en esta versión sin sellar.")


class Certificate(FrozenRecord):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.PROTECT, related_name="certificate")
    student_name = models.CharField(max_length=150)
    course_title = models.CharField(max_length=200)
    creator_name = models.CharField(max_length=200)
    evidence = models.JSONField(default=dict)
    issued_at = models.DateTimeField(default=timezone.now, editable=False)
    fingerprint = models.CharField(max_length=64, editable=False)

    def save(self, *args, **kwargs):
        if self._state.adding:
            from .certificate_integrity import certificate_digest
            self.fingerprint = certificate_digest(self)
        return super().save(*args, **kwargs)


class CertificateSharing(models.Model):
    certificate = models.OneToOneField(Certificate, on_delete=models.PROTECT, related_name="sharing")
    public = models.BooleanField(default=False)


class CertificateRevocation(FrozenRecord):
    certificate = models.OneToOneField(Certificate, on_delete=models.PROTECT, related_name="revocation")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)


class LessonQuestion(FrozenRecord):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="questions")
    lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT)
    body = models.TextField(max_length=2000)
    request_key = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("enrollment", "request_key"), name="unique_student_question_request")]


class QuestionReply(FrozenRecord):
    question = models.ForeignKey(LessonQuestion, on_delete=models.PROTECT, related_name="replies")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    body = models.TextField(max_length=2000)
    request_key = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "pk")
        constraints = [models.UniqueConstraint(fields=("question", "author", "request_key"), name="unique_question_reply_request")]


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="notifications")
    event_key = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at", "-pk")


class CommunityPost(FrozenRecord):
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="replies")
    body = models.TextField(max_length=2000)
    request_key = models.UUIDField()
    hidden = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "pk")
        permissions = [("moderate_community", "Moderar comunidades de todos los cursos")]
        constraints = [models.UniqueConstraint(fields=("author", "request_key"), name="unique_community_post_request")]


class CommunityReport(FrozenRecord):
    post = models.ForeignKey(CommunityPost, on_delete=models.PROTECT, related_name="reports")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.CharField(max_length=500)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("post", "reporter"), name="unique_community_report")]


class CommunitySuspension(models.Model):
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("version", "student"), name="unique_community_suspension")]


class CommunityDecision(FrozenRecord):
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    post = models.ForeignKey(CommunityPost, null=True, blank=True, on_delete=models.PROTECT)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="community_decisions")
    action = models.CharField(max_length=12, choices=(("hide", "Ocultar"), ("show", "Mostrar"), ("close", "Cerrar"), ("open", "Reabrir"), ("dismiss", "Descartar reportes"), ("suspend", "Suspender escritura"), ("restore", "Restablecer escritura")))
    reason = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
