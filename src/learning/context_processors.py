from .models import Notification


def notification_count(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return {}
    return {"notification_unread_count": Notification.objects.filter(recipient=request.user, read_at__isnull=True).count()}
