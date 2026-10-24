from urllib.parse import parse_qsl, urlencode

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from content.catalog import catalog_context

from .navigation import discovery_section


def discovery_links(context, request):
    """Conserva el contexto de búsqueda al abrir una ficha."""
    for card in context["all_cards"]:
        card["url"] += "?" + urlencode({"volver": request.get_full_path()})
    if request.user.is_authenticated and request.user.is_active and request.user.account_type == "student":
        from django.db.models import Count

        from learning.models import Enrollment
        version_ids = [card["item"].current_version_id for card in context["all_cards"] if card["summary"]]
        enrollments = Enrollment.objects.filter(student=request.user, version_id__in=version_ids).annotate(done=Count("completed_lessons", distinct=True), total=Count("version__chapters__lessons", distinct=True))
        progress = {item.version_id: {"done": item.done, "total": item.total, "percentage": round(item.done * 100 / item.total) if item.total else 0} for item in enrollments}
        for card in context["all_cards"]:
            if card["summary"]:
                card["learning"] = progress.get(card["item"].current_version_id)
    return context


def category_navigation(context):
    params = {"seccion": context["explore_section"]} if context.get("explore_section") else {}
    url = context["catalog_url"]
    context["category_index_url"] = url + ("?" + urlencode(params) if params else "")
    context["all_catalog_url"] = url + "?" + urlencode({**params, "vista": "todos"})
    selection = {"categoria": context["category_filter"]} if context["category_filter"] else {}
    if context["topic_filter"] and not context["topic_missing"]:
        if "categoria" not in dict(parse_qsl(context["filter_query"])):
            selection.pop("categoria", None)
        selection["tema"] = context["topic_filter"]
    context["clear_filters_url"] = (url + "?" + urlencode({**params, **selection})
                                    if context["selected_category"] and not context["category_missing"] else context["all_catalog_url"])
    for card in context["category_cards"]:
        card["url"] = url + "?" + urlencode({**params, "categoria": card["slug"]})
    subcategory_params = dict(parse_qsl(context["filter_query"]))
    subcategory_params.pop("tema", None)
    context["all_subcategories_url"] = url + "?" + urlencode({**params, **subcategory_params, "categoria": context["category_filter"]})
    if context["selected_category"] and context["category_filter"] == context["uncategorized_topic"] and (
        (context["unassigned_count"] and context["subcategory_cards"]) or context["topic_filter"] == context["uncategorized_topic"]
    ):
        context["subcategory_cards"].append({"name": "Sin subcategoría", "slug": context["uncategorized_topic"], "count": context["unassigned_count"]})
    for card in context["subcategory_cards"]:
        card["url"] = url + "?" + urlencode({**params, **subcategory_params, "categoria": context["category_filter"], "tema": card["slug"]})
    return filter_navigation(context)


def filter_navigation(context):
    params = dict(parse_qsl(context["filter_query"]))
    if context.get("category_browsing"):
        params["vista"] = "todos"
    labels = {
        "q": f'«{context["query"]}»' if context["query"] else "",
        "nivel": dict(context["levels"]).get(context["level_filter"], ""),
        "acceso": {"gratis": "Con contenido gratis", "pago": "Con contenido de pago"}.get(context["access_filter"], ""),
        "tipo": context["categories"].get(context["category"], "") if context["category"] != "todos" else "",
    }
    chips = []
    for key, label in labels.items():
        if not label:
            continue
        remaining = {name: value for name, value in params.items() if name != key}
        chips.append({"label": label, "url": context["catalog_url"] + ("?" + urlencode(remaining) if remaining else "")})
    context["active_filter_chips"] = chips
    return context


def home(request):
    context = {"active": "home", "catalog_url": reverse("explore"), "section": "cursos",
               "section_label": "Cursos", "explore_section": "cursos",
               **catalog_context({}, "cursos", browse_categories=True)}
    return render(request, "core/home.html", category_navigation(context))


def explore(request):
    section = discovery_section(request.GET)
    labels = {"cursos": "Cursos", "tutoriales": "Tutoriales", "recursos": "Recursos"}
    context = {"active": "explore", "section": section, "section_label": labels[section],
               "page_title": labels[section], "page_intro": {"cursos": "Un recorrido completo, a tu ritmo.", "tutoriales": "Guías para resolver una tarea, paso a paso.", "recursos": "Videos, materiales y fuentes para seguir explorando."}[section],
               "catalog_url": reverse("explore"), "explore_section": section,
               **discovery_links(catalog_context(request.GET, section, browse_categories=True), request)}
    category_navigation(context)
    template = "core/_catalog.html" if request.headers.get("HX-Request") == "true" else "core/explore.html"
    return render(request, template, context)


@require_GET
def academy_catalog(request, section):
    titles = {"cursos": ("Cursos", "Cursos", "Un recorrido completo, a tu ritmo."), "tutoriales": ("Tutoriales", "Tutoriales", "Guías para resolver una tarea, paso a paso."), "recursos": ("Recursos", "Recursos", "Videos, materiales y fuentes para seguir explorando.")}
    label, title, intro = titles[section]
    names = {"cursos": "courses", "tutoriales": "tutorials", "recursos": "resources"}
    context = {"active": names[section], "section": section, "section_label": label, "page_title": title, "page_intro": intro, "catalog_url": reverse(names[section]), **discovery_links(catalog_context(request.GET, section, browse_categories=True), request)}
    category_navigation(context)
    template = "core/_catalog.html" if request.headers.get("HX-Request") == "true" else "core/explore.html"
    return render(request, template, context)


@require_GET
def course_selector(request):
    context = discovery_links(catalog_context(request.GET, "cursos"), request)
    cards = context["all_cards"]
    selected = next((card for card in cards if str(card["item"].pk) == request.GET.get("curso")), None)
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
        topic_params["categoria"] = topic.category.slug if topic.category_id else context["uncategorized_topic"]
        topic_links.append((topic, topic_params.urlencode()))
    all_params = request.GET.copy()
    for field in ("curso", "tema", "categoria", "pagina"):
        all_params.pop(field, None)
    return render(request, "core/selector.html", filter_navigation({**context, "active": "courses", "selector": True, "selected": selected, "level_groups": ordered_groups, "topic_links": topic_links, "all_topic_query": all_params.urlencode(), "catalog_url": reverse("course-selector")}))


def creators(request):
    return render(request, "core/creators.html", {"active": "creators"})


@login_required
def workspace(request):
    if request.user.account_type != "student":
        return redirect_to_login(request.get_full_path(), reverse("login"))
    from learning.views import library
    return library(request)


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
