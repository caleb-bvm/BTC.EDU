"""Installable web app: manifest, a root-scoped service worker and an offline page."""
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.http import require_GET


@require_GET
def manifest(request):
    icons = [{"src": static("images/icons/icon-192.png"), "sizes": "192x192", "type": "image/png"},
             {"src": static("images/icons/icon-512.png"), "sizes": "512x512", "type": "image/png"},
             {"src": static("images/icons/maskable-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]
    response = JsonResponse({
        "name": "BTC.EDU", "short_name": "BTC.EDU", "lang": "es",
        "description": "Cursos, videos y materiales. Elige lo que quieres aprender.",
        "start_url": "/mi-espacio/", "scope": "/", "display": "standalone",
        "background_color": "#000000", "theme_color": "#000000", "icons": icons,
    }, content_type="application/manifest+json", json_dumps_params={"ensure_ascii": False})
    response["Cache-Control"] = "public, max-age=3600"
    return response


@require_GET
def service_worker(request):
    script = (settings.BASE_DIR / "static/js/sw.js").read_text(encoding="utf-8")
    response = HttpResponse(script, content_type="application/javascript; charset=utf-8")
    response["Cache-Control"] = "no-cache"
    response["Service-Worker-Allowed"] = "/"
    return response


@require_GET
def offline(request):
    # Cached by the service worker for every account, so it renders without the session.
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser()
    response = render(request, "core/offline.html")
    response["Cache-Control"] = "no-cache"
    return response
