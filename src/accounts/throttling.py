"""Bound credential and email requests without storing emails or IP addresses."""
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import AccessAttempt


class AccessThrottled(Exception):
    pass


@transaction.atomic
def consume(request, account_type, purpose, email=""):
    if not settings.ACCOUNT_THROTTLE_ENABLED:
        return
    now = timezone.now()
    minutes = 15 if purpose == "login" else 60
    limit = 12 if purpose == "login" else 6
    values = [(f"{purpose}:account:{account_type}:{email.strip().lower()}", limit),
              (f"{purpose}:origin:{request.META.get('REMOTE_ADDR', '')}", limit * 5)]
    for value, maximum in values:
        key = salted_hmac("accounts.access-limit", value).hexdigest()
        # A neutral write reserves SQLite's writer before reading the counter.
        AccessAttempt.objects.filter(key=key).update(count=F("count"))
        attempt, _ = AccessAttempt.objects.get_or_create(key=key, defaults={"window_started_at": now})
        if now - attempt.window_started_at >= timedelta(minutes=minutes):
            attempt.window_started_at, attempt.count = now, 0
        if attempt.count >= maximum:
            # Return the rejection after the transaction commits so prior counters
            # stay bounded and no successful reservation is accidentally rolled back.
            return False
        attempt.count += 1
        attempt.save(update_fields=("count", "window_started_at"))
    return True


def allow(request, account_type, purpose, email=""):
    if consume(request, account_type, purpose, email) is False:
        raise AccessThrottled("Has realizado varios intentos. Espera unos minutos y vuelve a intentarlo.")
