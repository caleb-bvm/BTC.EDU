from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from commerce.catalog import public_version, version_owned
from commerce.services import require_student, reserve_writer

from .models import Enrollment


def enrolled(user, version):
    return user.is_authenticated and user.is_active and user.account_type == "student" and Enrollment.objects.filter(student=user, version=version).exists()


def can_visit_version(user, version):
    if not version.published_at:
        return False
    return public_version(version) or version_owned(user, version) or enrolled(user, version)


@transaction.atomic
def enroll(actor, version):
    require_student(actor)
    reserve_writer(actor.pk)
    actor.refresh_from_db()
    require_student(actor)
    version.refresh_from_db()
    if not version.sealed or not can_visit_version(actor, version):
        raise PermissionDenied("Esta versión no está disponible para tu cuenta.")
    if version.course.status not in ("published", "archived"):
        raise ValidationError("Este curso no está disponible para estudiar.")
    enrollment, _ = Enrollment.objects.get_or_create(student=actor, version=version)
    return enrollment
