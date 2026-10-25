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


class SavedItem(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    resource = models.ForeignKey("content.ResourceVersion", on_delete=models.PROTECT, null=True, blank=True)
    reference = models.ForeignKey("content.ExternalReference", on_delete=models.PROTECT, null=True, blank=True)
    course_version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField(max_length=200)
    source_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-pk")
        constraints = [
            models.CheckConstraint(condition=(models.Q(resource__isnull=False, reference__isnull=True, course_version__isnull=True)
                                               | models.Q(resource__isnull=True, reference__isnull=False, course_version__isnull=True)
                                               | models.Q(resource__isnull=True, reference__isnull=True, course_version__isnull=False)), name="saved_item_one_target"),
            models.UniqueConstraint(fields=("student", "resource"), name="unique_saved_resource"),
            models.UniqueConstraint(fields=("student", "reference"), name="unique_saved_reference"),
            models.UniqueConstraint(fields=("student", "course_version"), name="unique_saved_course_version"),
        ]


class SavedCollection(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    normalized_name = models.CharField(max_length=180)
    items = models.ManyToManyField(SavedItem, related_name="collections", blank=True)

    class Meta:
        ordering = ("name", "pk")
        constraints = [models.UniqueConstraint(fields=("student", "normalized_name"), name="unique_student_collection_name")]


class PracticeRules(models.Model):
    title = models.CharField("Título", max_length=200)
    instructions = models.TextField("Qué debe entregar el estudiante", max_length=10000)
    criteria = models.JSONField(default=list)
    review_days = models.PositiveSmallIntegerField("Plazo previsto de revisión (días naturales)", default=7, validators=[MinValueValidator(1), MaxValueValidator(30)])

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if not self.title.strip() or not self.instructions.strip():
            raise ValidationError("Completa el título y las instrucciones de la práctica.")
        if not isinstance(self.criteria, list) or not 1 <= len(self.criteria) <= 12 or any(not isinstance(c, str) or not c.strip() or len(c) > 300 for c in self.criteria):
            raise ValidationError("Define entre 1 y 12 criterios claros, de hasta 300 caracteres cada uno.")


class PracticeDraft(PracticeRules):
    lesson = models.OneToOneField("content.Lesson", on_delete=models.CASCADE, related_name="practice_draft")
    enabled = models.BooleanField("Incluir práctica en la próxima versión", default=True)
    revision = models.PositiveIntegerField(default=0)


class VersionPractice(FrozenRecord, PracticeRules):
    lesson = models.OneToOneField("content.VersionLesson", on_delete=models.PROTECT, related_name="practice")

    def clean(self):
        super().clean()
        if self.lesson.chapter.version.sealed:
            raise ValidationError("No se pueden añadir prácticas a una versión sellada.")


class PracticeIntake(models.Model):
    practice = models.OneToOneField(VersionPractice, on_delete=models.PROTECT, related_name="intake")
    accepting = models.BooleanField(default=True)
    revision = models.PositiveIntegerField(default=0)


def practice_upload_path(instance, filename):
    from pathlib import PurePath
    return f"practice-deliveries/{uuid.uuid4().hex}{PurePath(filename).suffix.lower()}"


class PracticeDelivery(FrozenRecord):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name="practice_deliveries")
    practice = models.ForeignKey(VersionPractice, on_delete=models.PROTECT, related_name="deliveries")
    number = models.PositiveIntegerField()
    request_key = models.UUIDField()
    body = models.TextField(blank=True, max_length=10000)
    project_url = models.URLField(blank=True, max_length=500)
    attachment = models.FileField(upload_to=practice_upload_path, blank=True)
    attachment_name = models.CharField(max_length=200, blank=True)
    attachment_size = models.PositiveIntegerField(default=0)
    attachment_sha256 = models.CharField(max_length=64, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField()

    class Meta:
        ordering = ("submitted_at", "pk")
        constraints = [
            models.UniqueConstraint(fields=("enrollment", "practice", "number"), name="unique_practice_delivery_number"),
            models.UniqueConstraint(fields=("enrollment", "request_key"), name="unique_practice_delivery_request"),
        ]

    def clean(self):
        super().clean()
        if self.enrollment.version_id != self.practice.lesson.chapter.version_id:
            raise ValidationError("La entrega no corresponde a esta inscripción.")
        if not (self.body.strip() or self.project_url or self.attachment):
            raise ValidationError("Añade una solución, un enlace o un archivo.")

    @property
    def state(self):
        review = getattr(self, "review", None)
        return review.outcome if review else "pending"

    @property
    def state_label(self):
        return {"pending": "En revisión", "changes": "Cambios solicitados", "accepted": "Aprobada"}[self.state]

    @property
    def overdue(self):
        return self.state == "pending" and self.due_at < timezone.now()


class PracticeReview(FrozenRecord):
    delivery = models.OneToOneField(PracticeDelivery, on_delete=models.PROTECT, related_name="review")
    educator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    outcome = models.CharField(max_length=10, choices=(("accepted", "Aprobar entrega"), ("changes", "Solicitar cambios")))
    feedback = models.TextField(max_length=5000)
    met_criteria = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def clean(self):
        super().clean()
        if self.educator_id != self.delivery.practice.lesson.chapter.version.course.creator_id:
            raise ValidationError("Solo el educador de esta práctica puede revisarla.")
        criteria = self.delivery.practice.criteria
        if not isinstance(self.met_criteria, list) or any(type(i) is not int or i < 0 or i >= len(criteria) for i in self.met_criteria) or len(set(self.met_criteria)) != len(self.met_criteria):
            raise ValidationError("Revisa los criterios seleccionados.")
        if not self.feedback.strip():
            raise ValidationError("Explica el resultado y el siguiente paso para el estudiante.")
        if self.outcome == "accepted" and set(self.met_criteria) != set(range(len(criteria))):
            raise ValidationError("Para aprobar, la entrega debe cumplir todos los criterios.")


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
    category = models.CharField(max_length=12, default="service", choices=(("service", "Cuenta y revisiones"), ("questions", "Preguntas"), ("community", "Comunidad")))

    class Meta:
        ordering = ("-created_at", "-pk")


class CommunityPost(FrozenRecord):
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT)
    lesson = models.ForeignKey("content.VersionLesson", on_delete=models.PROTECT, null=True, blank=True, related_name="community_posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="replies")
    body = models.TextField(max_length=2000)
    request_key = models.UUIDField()
    hidden = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.lesson_id and self.lesson.chapter.version_id != self.version_id:
            raise ValidationError("La conversación debe pertenecer a una lección de esta versión.")
        if self.parent_id and (self.parent.parent_id or self.parent.version_id != self.version_id or self.parent.lesson_id != self.lesson_id):
            raise ValidationError("La respuesta debe conservar la versión y lección de su conversación.")

    class Meta:
        ordering = ("created_at", "pk")
        permissions = [("moderate_community", "Moderar comunidades de todos los cursos")]
        constraints = [models.UniqueConstraint(fields=("author", "request_key"), name="unique_community_post_request")]


class CommunitySubscription(models.Model):
    thread = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name="subscriptions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("thread", "user"), name="unique_community_subscription")]


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


class CertificateTimestamp(models.Model):
    """OpenTimestamps proof of a certificate fingerprint; it grows as calendars confirm it."""
    certificate = models.OneToOneField(Certificate, on_delete=models.PROTECT, related_name="timestamp")
    proof = models.BinaryField()
    calendars = models.JSONField(default=list)
    submitted_at = models.DateTimeField()
    checked_at = models.DateTimeField(null=True, blank=True)
    bitcoin_height = models.PositiveIntegerField(null=True, blank=True)


class CourseReview(models.Model):
    class Basis(models.TextChoices):
        PURCHASE = "purchase", "Compra verificada"
        COMPLETED = "completed", "Curso completado"

    course = models.ForeignKey("content.Course", on_delete=models.PROTECT, related_name="reviews")
    version = models.ForeignKey("content.CourseVersion", on_delete=models.PROTECT, related_name="reviews")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="course_reviews")
    rating = models.PositiveSmallIntegerField("valoración", validators=[MinValueValidator(1), MaxValueValidator(5)])
    body = models.TextField("reseña", max_length=2000, blank=True)
    basis = models.CharField(max_length=12, choices=Basis)
    hidden = models.BooleanField("oculta por moderación", default=False)
    reply = models.TextField("respuesta del educador", max_length=1000, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-pk")
        constraints = [models.UniqueConstraint(fields=("course", "student"), name="unique_course_review"),
                       models.CheckConstraint(condition=models.Q(rating__gte=1, rating__lte=5), name="review_rating_bounds")]

    def clean(self):
        if self.version_id and self.course_id and self.version.course_id != self.course_id:
            raise ValidationError("La reseña debe corresponder a una versión del curso.")


class PracticeShowcase(models.Model):
    """A student's explicit permission to show an approved practice in the course gallery."""
    delivery = models.OneToOneField(PracticeDelivery, on_delete=models.PROTECT, related_name="showcase")
    public = models.BooleanField(default=True)
    hidden = models.BooleanField("oculta por moderación", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.delivery_id and self.delivery.state != "accepted":
            raise ValidationError("Solo se pueden mostrar prácticas aprobadas.")


BUNDLE_MAX_PERCENT = 50


class LearningPath(models.Model):
    # Without an educator the path is editorial: BTC.EDU may combine published courses from anyone.
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
                                related_name="learning_paths", verbose_name="educador")
    title = models.CharField("título", max_length=200)
    slug = models.SlugField("identificador", unique=True)
    summary = models.CharField("resumen", max_length=240)
    description = models.TextField("descripción", blank=True)
    published = models.BooleanField("publicada", default=False)
    position = models.PositiveIntegerField("orden", default=1)
    bundle_percent = models.PositiveSmallIntegerField("descuento del paquete (%)", default=0, validators=[MaxValueValidator(BUNDLE_MAX_PERCENT)],
                                                      help_text="Con 0, los cursos se compran solo por separado.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("position", "pk")
        verbose_name = "ruta de aprendizaje"
        verbose_name_plural = "rutas de aprendizaje"
        constraints = [models.CheckConstraint(condition=models.Q(bundle_percent__lte=BUNDLE_MAX_PERCENT), name="path_bundle_percent_bounds")]

    def __str__(self):
        return self.title

    @property
    def author_name(self):
        profile = getattr(self.creator, "creator_profile", None) if self.creator_id else None
        return profile.display_name if profile else "BTC.EDU"


class PathCourse(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="steps")
    course = models.ForeignKey("content.Course", on_delete=models.PROTECT, related_name="path_steps", verbose_name="curso o tutorial")
    position = models.PositiveIntegerField("orden", default=1)
    note = models.CharField("por qué en este paso", max_length=240, blank=True)
    # The path is a recommended trail: an optional step never blocks the credential.
    optional = models.BooleanField("opcional", default=False)

    class Meta:
        ordering = ("position", "pk")
        verbose_name = "paso de la ruta"
        verbose_name_plural = "pasos de la ruta"
        constraints = [models.UniqueConstraint(fields=("path", "course"), name="unique_path_course"),
                       models.UniqueConstraint(fields=("path", "position"), name="unique_path_position")]


class PathCompletion(models.Model):
    """Credential for a finished path, built from the course certificates it requires."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.ForeignKey(LearningPath, on_delete=models.PROTECT, related_name="completions")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="path_completions")
    student_name = models.CharField(max_length=150)
    path_title = models.CharField(max_length=200)
    evidence = models.JSONField(default=list)
    issued_at = models.DateTimeField(default=timezone.now, editable=False)
    fingerprint = models.CharField(max_length=64, editable=False)
    public = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("path", "student"), name="unique_path_completion")]

    def save(self, *args, **kwargs):
        if self._state.adding:
            from .paths import path_digest
            self.fingerprint = path_digest(self)
        else:
            original = type(self).objects.get(pk=self.pk)
            if any(getattr(self, name) != getattr(original, name) for name in ("path_id", "student_id", "student_name", "path_title", "evidence", "issued_at", "fingerprint")):
                raise ValidationError("La credencial conserva sus datos de emisión.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Las credenciales no se eliminan.")
