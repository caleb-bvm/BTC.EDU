from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from content.catalog import catalog_context


def discovery_links(context, request):
    """Conserva el contexto de búsqueda al abrir una ficha."""
    for card in context["all_cards"]:
        card["url"] += "?" + urlencode({"volver": request.get_full_path()})
    return context


def home(request):
    return render(request, "core/home.html", {"active": "home", "catalog_url": reverse("courses"), **catalog_context({}, "cursos")})


def explore(request):
    context = {"active": "courses", "catalog_url": reverse("explore"), "page_title": "Explorar todo", **discovery_links(catalog_context(request.GET), request)}
    template = "core/_catalog.html" if request.headers.get("HX-Request") == "true" else "core/explore.html"
    return render(request, template, context)


@require_GET
def academy_catalog(request, section):
    titles = {"cursos": ("Cursos", "Encuentra tu siguiente paso.", "Un recorrido completo, a tu ritmo."), "tutoriales": ("Tutoriales", "De la idea a la práctica.", "Guías para resolver una tarea, paso a paso."), "recursos": ("Recursos", "Amplía tu perspectiva.", "Videos, materiales y fuentes para seguir explorando.")}
    label, title, intro = titles[section]
    names = {"cursos": "courses", "tutoriales": "tutorials", "recursos": "resources"}
    context = {"active": names[section], "section": section, "section_label": label, "page_title": title, "page_intro": intro, "catalog_url": reverse(names[section]), **discovery_links(catalog_context(request.GET, section), request)}
    template = "core/_catalog.html" if request.headers.get("HX-Request") == "true" else "core/explore.html"
    return render(request, template, context)


@require_GET
def course_selector(request):
    context = discovery_links(catalog_context(request.GET, "cursos"), request)
    cards = context["all_cards"]
    selected = next((card for card in cards if str(card["item"].pk) == request.GET.get("curso")), None)
    if selected is None and cards:
        selected = cards[0]
    level_groups = {}
    for card in cards:
        level_groups.setdefault(card["item"].get_level_display() or "Nivel por definir", []).append(card)
    ordered_groups = [(label, level_groups[label]) for _, label in context["levels"] if label in level_groups]
    if "Nivel por definir" in level_groups:
        ordered_groups.append(("Nivel por definir", level_groups["Nivel por definir"]))
    topic_links = []
    for topic in context["topics"]:
        topic_params = request.GET.copy()
        topic_params.pop("curso", None)
        topic_params.pop("pagina", None)
        topic_params["tema"] = topic.slug
        topic_links.append((topic, topic_params.urlencode()))
    all_params = request.GET.copy()
    for field in ("curso", "tema", "pagina"):
        all_params.pop(field, None)
    return render(request, "core/selector.html", {**context, "active": "courses", "selector": True, "selected": selected, "level_groups": ordered_groups, "topic_links": topic_links, "all_topic_query": all_params.urlencode(), "catalog_url": reverse("course-selector")})


def creators(request):
    return render(request, "core/creators.html", {"active": "creators"})


@login_required
def workspace(request):
    if request.user.account_type != "student":
        return redirect_to_login(request.get_full_path(), reverse("login"))
    return render(request, "core/workspace.html", {"active": "workspace"})


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
