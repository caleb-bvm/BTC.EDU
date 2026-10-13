"""Persist account mail before delivery and retry without logging private links."""
import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import AccountMail

logger = logging.getLogger(__name__)


def queue_mail(user, recipient, subject, body, action=None):
    from .security import state_digest
    mail = AccountMail.objects.create(user=user, recipient=recipient, subject=subject, body=body, action=action,
                                     state_digest=state_digest(user), expires_at=timezone.now() + timedelta(seconds=settings.ACCOUNT_EMAIL_TOKEN_TIMEOUT))
    if settings.ACCOUNT_SEND_EMAIL:
        transaction.on_commit(lambda: deliver_mail(mail.pk))
    return mail


def deliver_mail(pk):
    # Reserve a retry window before leaving the transaction for the SMTP call.
    # SMTP cannot guarantee exactly-once delivery if its response is lost.
    now = timezone.now()
    with transaction.atomic():
        claimed = AccountMail.objects.filter(pk=pk, status__in=("pending", "failed")).filter(
            models_due(now)
        ).update(next_attempt_at=now + timedelta(minutes=5), attempts=F("attempts") + 1)
        if not claimed:
            return False
        mail = AccountMail.objects.select_related("user", "action").get(pk=pk)
        from .security import state_digest
        if (mail.expires_at and mail.expires_at <= now or mail.action and mail.action.consumed_at
                or mail.state_digest and mail.state_digest != state_digest(mail.user)):
            AccountMail.objects.filter(pk=pk).update(status="cancelled", body="")
            return False
    try:
        sent = send_mail(mail.subject, mail.body, settings.DEFAULT_FROM_EMAIL, [mail.recipient], fail_silently=False)
        if sent != 1:
            raise RuntimeError("Mail backend did not accept the message")
    except Exception:
        AccountMail.objects.filter(pk=pk).update(status="failed")
        logger.warning("Account email delivery failed; queued for retry (%s).", pk)
        return False
    AccountMail.objects.filter(pk=pk).update(status="sent", sent_at=timezone.now(), next_attempt_at=None)
    return True


def models_due(now):
    from django.db.models import Q
    return Q(next_attempt_at__isnull=True) | Q(next_attempt_at__lte=now)
