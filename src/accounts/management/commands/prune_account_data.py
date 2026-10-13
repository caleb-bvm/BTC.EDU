import re
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import AccessAttempt, AccountMail, User


class Command(BaseCommand):
    help = "Retira fotos sin referencias de más de un día y contenido de correos vencidos."

    def handle(self, *args, **options):
        now = timezone.now()
        storage = User._meta.get_field("avatar").storage
        references = set(User.objects.exclude(avatar="").values_list("avatar", flat=True))
        removed = 0
        try:
            _, files = storage.listdir("account-avatars")
        except OSError:
            files = []
        for filename in files:
            if not re.fullmatch(r"[0-9a-f]{32}\.webp", filename):
                continue
            name = "account-avatars/" + filename
            if name in references:
                continue
            try:
                if storage.get_modified_time(name) < now - timedelta(days=1):
                    # One generated filename within the fixed avatar directory;
                    # no recursive deletion or paths supplied by a request.
                    storage.delete(name)
                    removed += 1
            except OSError:
                continue
        AccountMail.objects.filter(expires_at__lt=now).exclude(body="").update(body="")
        AccessAttempt.objects.filter(window_started_at__lt=now - timedelta(days=2)).delete()
        self.stdout.write(f"Fotos sin referencias retiradas: {removed}.")
