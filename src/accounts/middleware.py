from datetime import timedelta

from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import AccountSession


class AccountSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.account_type in ("student", "creator") and request.session.session_key:
            now = timezone.now()
            key = request.session.session_key
            # Do not store user agents, IPs, cookies or other tracking identifiers.
            agent = request.META.get("HTTP_USER_AGENT", "")
            browser = "Firefox" if "Firefox" in agent else "Edge" if "Edg/" in agent else "Chrome" if "Chrome" in agent else "Safari" if "Safari" in agent else "Navegador"
            session, _ = AccountSession.objects.get_or_create(session_key=key, defaults={"user": request.user, "browser": browser})
            if session.user_id != request.user.pk:
                AccountSession.objects.filter(pk=session.pk).update(user=request.user, created_at=now, ended_at=None)
            elif session.last_seen_at < now - timedelta(minutes=10):
                AccountSession.objects.filter(pk=session.pk).update(last_seen_at=now)
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated and request.method == "POST" and request.POST.get("account_id", str(request.user.pk)) != str(request.user.pk):
            return render(request, "accounts/session_changed.html", status=403)
        if not request.user.is_authenticated or request.user.account_type != "creator":
            return None
        profile = getattr(request.user, "creator_profile", None)
        if not profile or profile.status != "suspended":
            return None
        name = request.resolver_match.url_name or ""
        account_routes = {"creator-account"} | {f"creator-account-{suffix}" for suffix in ("photo", "security", "password", "email", "verify", "preferences", "sessions", "support", "export", "close", "switch")}
        auth_routes = {"creator-password-reset", "creator-password-reset-done", "creator-password-reset-confirm", "creator-password-reset-complete", "creator-application", "creator-login", "creator-logout", "login", "logout", "student-signup", "account-email-confirm", "account-restore"}
        if name in account_routes | auth_routes | {"notifications", "notification-read", "notifications-read-all", "account-session-context"}:
            return None
        if name == "account-avatar" and view_kwargs.get("pk") == request.user.pk:
            return None
        if request.method in ("GET", "HEAD"):
            return redirect("creator-application")
        return HttpResponseForbidden("Tu cuenta de creador está suspendida. Consulta el estado y solicita una revisión desde tu perfil de creador.")
