from datetime import datetime, time, timedelta

from django import forms
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Sum
from django.utils import timezone

from commerce.models import Entitlement, Invoice, Purchase
from content.models import CourseVersion, VersionLesson
from creators.models import Submission
from learning.models import (
    Certificate,
    Enrollment,
    LessonQuestion,
    QuizAttempt,
)

from .models import ActivityEvent


class PeriodForm(forms.Form):
    start = forms.DateField(label="Desde", widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))
    end = forms.DateField(label="Hasta", widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))

    def clean(self):
        values = super().clean()
        if "start" in values and "end" in values and (values["start"] > values["end"] or (values["end"] - values["start"]).days > 366):
            raise forms.ValidationError("Elige un intervalo ordenado de hasta 366 días.")
        return values


def ratio(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator, "percent": round(100 * numerator / denominator, 1) if denominator else None}


def dashboard_data(start, end, creator=None):
    tz = timezone.get_current_timezone()
    lower = timezone.make_aware(datetime.combine(start, time.min), tz)
    upper = timezone.make_aware(datetime.combine(end + timedelta(days=1), time.min), tz)
    window = {"created_at__gte": lower, "created_at__lt": upper}
    invoices = Invoice.objects.filter(**window, buyer__account_type="student", buyer__is_staff=False)
    purchases = Purchase.objects.filter(invoice__buyer__account_type="student", invoice__buyer__is_staff=False)
    enrollments = Enrollment.objects.filter(**window, student__account_type="student", student__is_staff=False)
    events = ActivityEvent.objects.filter(**window)
    versions = CourseVersion.objects.filter(sealed=True, published_at__isnull=False)
    submissions = Submission.objects.filter(**window)
    if creator:
        invoices = invoices.filter(offer__creator=creator)
        purchases = purchases.filter(invoice__offer__creator=creator)
        enrollments = enrollments.filter(version__course__creator=creator)
        events = events.filter(creator=creator)
        versions = versions.filter(course__creator=creator)
        submissions = submissions.filter(creator=creator)
    paid = invoices.filter(purchase__isnull=False)
    paid_ids = set(paid.values_list("pk", flat=True))
    invoice_count = invoices.count()
    buyers = set(paid.values_list("buyer_id", flat=True))
    repeat_buyers = purchases.filter(invoice__buyer_id__in=buyers).values("invoice__buyer_id").annotate(total=Count("pk")).filter(total__gte=2).count()
    rights = Entitlement.objects.filter(created_at__gte=lower, created_at__lt=upper, buyer__account_type="student", buyer__is_staff=False)
    if creator:
        rights = rights.filter(resource__creator=creator)
    # One permission per learner/resource, regardless of bundled offers or repeated opens.
    rights_data = list(rights.values_list("buyer_id", "resource_id", "created_at"))
    opens = ActivityEvent.objects.filter(kind="purchased_content_opened", created_at__lt=timezone.now())
    if creator:
        opens = opens.filter(creator=creator)
    acquired_at = {(buyer, resource): acquired for buyer, resource, acquired in rights_data}
    opened_pairs = {(actor, resource) for actor, resource, occurred in opens.filter(actor_id__in={item[0] for item in rights_data}, resource_id__in={item[1] for item in rights_data}).values_list("actor_id", "resource_id", "created_at")
                    if (actor, resource) in acquired_at and occurred >= acquired_at[(actor, resource)]}
    viewed_pairs = set(events.filter(kind="offer_viewed").values_list("session_id", "offer_id"))
    created_pairs = set(events.filter(kind="invoice_created").values_list("session_id", "offer_id"))
    observed = list(ActivityEvent.objects.filter(kind="invoice_created", invoice_id__in=paid_ids).values_list("actor_id", "session_id", "invoice__purchase__created_at"))
    returns = list(ActivityEvent.objects.filter(kind="library_viewed", actor_id__in=buyers).values_list("actor_id", "session_id", "created_at"))
    returning = {buyer for buyer, purchase_session, created in observed for actor, library_session, returned in returns if buyer == actor and library_session != purchase_session and returned > created}
    tracked_buyers = {buyer for buyer, _, _ in observed}
    attempts = QuizAttempt.objects.filter(enrollment__in=enrollments, submitted_at__isnull=False)
    questions = LessonQuestion.objects.filter(**window)
    if creator:
        questions = questions.filter(enrollment__version__course__creator=creator)
    response_times = []
    answered = 0
    for question in questions.select_related("enrollment__version__course").prefetch_related("replies"):
        answer = next((reply for reply in question.replies.all() if reply.author_id == question.enrollment.version.course.creator_id), None)
        if answer:
            answered += 1
            response_times.append((answer.created_at - question.created_at).total_seconds() / 3600)
    completed = 0
    rows = []
    for version in versions.order_by("-published_at", "-pk"):
        cohort = enrollments.filter(version=version)
        total = VersionLesson.objects.filter(chapter__version=version).count()
        finished = cohort.annotate(done=Count("completed_lessons")).filter(done=total).count() if total else 0
        completed += finished
        if cohort.exists() or not creator:
            rows.append({"version": version, "enrolled": cohort.count(), "completion": ratio(finished, cohort.count()),
                         "certificates": Certificate.objects.filter(enrollment__in=cohort).count()})
    latency = paid.aggregate(value=Avg(ExpressionWrapper(F("purchase__created_at") - F("created_at"), output_field=DurationField())))["value"]
    first_event = ActivityEvent.objects.filter(creator=creator).order_by("created_at").first() if creator else ActivityEvent.objects.order_by("created_at").first()
    return {"invoice_count": invoice_count, "paid_count": len(paid_ids), "pending_count": invoices.filter(status="pending").count(),
            "failed_count": invoices.filter(status="failed").count(), "expired_count": invoices.filter(status="expired").count(),
            "payment_completion": ratio(len(paid_ids), invoice_count), "volume": paid.aggregate(total=Sum("amount_sats"))["total"] or 0,
            "buyer_count": len(buyers), "repeat_purchase": ratio(repeat_buyers, len(buyers)),
            "request_conversion": ratio(len(viewed_pairs & created_pairs), len(viewed_pairs)),
            "opening": ratio(len(opened_pairs), len(rights_data)), "library_return": ratio(len(returning), len(tracked_buyers)),
            "untracked_buyers": len(buyers - tracked_buyers), "enrolled_count": enrollments.count(), "course_completion": ratio(completed, enrollments.count()),
            "attempt_approval": ratio(attempts.filter(passed=True).count(), attempts.count()),
            "student_approval": ratio(attempts.filter(passed=True).values("enrollment_id").distinct().count(), attempts.values("enrollment_id").distinct().count()),
            "certificates_count": Certificate.objects.filter(enrollment__in=enrollments).count(),
            "question_count": questions.count(), "answered_count": answered, "answer_hours": round(sum(response_times) / len(response_times), 1) if response_times else None,
            "submissions": submissions.count(), "published_submissions": submissions.filter(status="approved").count(),
            "latency_seconds": round(latency.total_seconds(), 1) if latency else None,
            "first_event_at": first_event.created_at if first_event else None, "rows": rows,
            "recent_invoices": invoices.select_related("offer", "offer__course_version").order_by("-created_at")[:20],
            "offer_views": events.filter(kind="offer_viewed").count(), "content_opens": events.filter(kind__in=("free_content_opened", "purchased_content_opened")).count()}
