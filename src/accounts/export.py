from django.utils import timezone


def account_data(user):
    from commerce.models import Invoice
    from creators.models import Submission
    from learning.models import Certificate, Enrollment, QuizAttempt, SavedItem

    fields = ("id", "email", "account_type", "first_name", "last_name", "display_name", "bio", "interests", "learning_goal", "website", "profile_public", "email_verified_at", "date_joined")
    data = {"exported_at": timezone.now(), "account": {key: getattr(user, key) for key in fields},
            "preferences": {"questions": user.notify_questions, "community": user.notify_community},
            "history": list(user.accountevent_set.values("kind", "detail", "created_at")),
            "support": list(user.accountsupportrequest_set.values("id", "kind", "body", "status", "response", "created_at", "reviewed_at"))}
    if user.account_type == "student":
        enrollments = Enrollment.objects.filter(student=user)
        data["enrollments"] = list(enrollments.values("id", "version_id", "version__title", "last_lesson_id", "created_at", "updated_at"))
        data["completed_lessons"] = list(user.enrollment_set.filter(pk__in=enrollments).values("id", "completed_lessons__lesson_id", "completed_lessons__completed_at"))
        data["invoices"] = list(Invoice.objects.filter(buyer=user).values("id", "title", "amount_sats", "status", "created_at"))
        data["assessments"] = list(QuizAttempt.objects.filter(enrollment__student=user).values("id", "quiz_id", "passed", "score", "submitted_at"))
        data["certificates"] = list(Certificate.objects.filter(enrollment__student=user).values("id", "student_name", "issued_at"))
        data["saved_items"] = list(SavedItem.objects.filter(student=user).values("id", "title", "resource_id", "reference_id", "source_url", "created_at"))
    else:
        profile = getattr(user, "creator_profile", None)
        data["creator_profile"] = {key: getattr(profile, key) for key in ("display_name", "bio", "specialty", "website", "status", "feedback", "reviewed_at")} if profile else None
        data["submissions"] = list(Submission.objects.filter(creator=user).values("id", "status", "feedback", "created_at", "reviewed_at"))
    return data
