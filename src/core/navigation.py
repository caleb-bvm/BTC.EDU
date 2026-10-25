"""Stable global destinations and section navigation outside the sidebar."""
from urllib.parse import urlencode

from django.urls import reverse

CATALOG_MENU = [
    ("courses", "Cursos", "book"), ("tutorials", "Tutoriales", "steps"),
    ("resources", "Recursos", "file"), ("learning-paths", "Rutas", "route"),
]
MEMBERSHIP_LINK = ("membership", "Membresía", "ticket")
CATALOG_DESTINATIONS = {"cursos": "courses", "tutoriales": "tutorials", "recursos": "resources"}
STUDENT_MENU = [
    *CATALOG_MENU, MEMBERSHIP_LINK, ("workspace", "Mi aprendizaje", "book"),
    ("purchases", "Compras", "bag"), ("community-spaces", "Comunidad", "people"),
]
CREATOR_MENU = [
    ("creator-dashboard", "Mi estudio", "home"), ("creator-content", "Contenido", "file"),
    ("creator-questions", "Alumnos", "people"), ("community-spaces", "Comunidad", "chat"),
    ("creator-analytics", "Ventas", "chart"),
]
SECTION_MENUS = {
    "learning": [("workspace", "Mi aprendizaje"), ("student-questions", "Mis preguntas"), ("student-practices", "Prácticas")],
    "payments": [("purchases", "Historial de compras"), ("cart", "Carrito"), ("student-tips", "Propinas")],
    "community": [("community-spaces", "Comunidades de cursos"), ("members", "Personas")],
    "studio": [("creator-content", "Todo el contenido"), ("creator-files", "Biblioteca de archivos")],
    "teaching": [("creator-questions", "Preguntas"), ("creator-results", "Evaluaciones"), ("creator-practices", "Entregas")],
    "sales": [("creator-analytics", "Actividad"), ("creator-offers", "Ofertas y precios"), ("creator-coupons", "Cupones"), ("creator-tips", "Propinas")],
}
SECTION_LABELS = {
    "learning": "Secciones de Mi aprendizaje", "payments": "Secciones de Compras",
    "community": "Secciones de Comunidad", "studio": "Secciones de Contenido",
    "teaching": "Secciones de Alumnos", "sales": "Secciones de Ventas",
}


def discovery_section(parameters):
    section = parameters.get("seccion") or (
        "recursos" if parameters.get("tipo") in {"videos", "materiales", "referencias"}
        else "tutoriales" if parameters.get("tipo") == "tutoriales" else "cursos")
    return section if section in CATALOG_DESTINATIONS else "cursos"


def contextual_navigation(request):
    route = (request.resolver_match.url_name or "") if request.resolver_match else ""
    user = request.user
    signed_in = user.is_authenticated
    creator = signed_in and user.account_type == "creator"
    status = getattr(getattr(user, "creator_profile", None), "status", None) if creator else None
    ready = creator and status == "approved"
    requested_next = request.POST.get("next", "") if request.method == "POST" else request.GET.get("next", "")
    context, selected = "catalog", route
    primary = CATALOG_DESTINATIONS[discovery_section(request.GET)] if route == "explore" else route if route in {"courses", "tutorials", "resources"} else "courses"
    if route.startswith("community-") or route in {"members", "member-profile"}:
        context, primary = "community", "community-spaces"
        selected = "members" if route == "member-profile" else "community-spaces" if route.startswith("community-") else route
    elif route in {"notifications", "notification-read", "notifications-read-all"}:
        context, selected, primary = "notifications", "notifications", ""
    elif route in {"offer-detail", "checkout", "purchases", "direct-checkout", "refund-request", "gift-detail", "student-tips"} or route.startswith(("invoice-", "cart", "tip-")):
        context, primary = "payments", "purchases"
        selected = ("cart" if route.startswith("cart") or route == "direct-checkout" else "student-tips" if route == "student-tips" or route.startswith("tip-")
                    else "purchases" if route in {"purchases", "refund-request", "gift-detail"} or route.startswith("invoice-") else "")
    elif route == "student-profile" or route.startswith("student-account"):
        context, primary = "account", ""
        selected = "student-account-security" if route.endswith(("security", "password", "email", "sessions", "verify")) else "student-profile" if route == "student-profile" else "student-account"
    elif route in {"login", "student-signup"} or route.startswith("student-password-reset"):
        context, primary = "auth", "login"
        selected = "student-password-reset" if route.startswith("student-password-reset") else route
    elif route == "workspace" or route.startswith(("certificate-", "quiz-", "student-question", "student-practice")) or route in {"certificates", "purchased-resource", "question-create", "path-credential"}:
        context, primary = "learning", "workspace"
        selected = "certificates" if route.startswith("certificate-") or route == "certificates" else "student-questions" if route.startswith("student-question") or route == "question-create" else "student-practices" if route.startswith("student-practice") else "workspace"
    elif route in {"learning-paths", "learning-path"}:
        selected, primary = "learning-paths", "learning-paths"
    elif route == "membership" or route.startswith("membership-"):
        selected, primary = "membership", "membership"
    elif route in {"course-detail", "course-version", "lesson-detail", "version-lesson", "course-gallery"}:
        # Enrollment is already available in the rendered course context. The
        # shared navigation template uses it to highlight Mi aprendizaje without
        # querying the same enrollment again from this context processor.
        context, primary = "course", "courses"
    elif route == "creators":
        primary = "creators"
    elif route == "creator-public-profile":
        context, selected, primary = "catalog", "", ""
    elif route.startswith("creator-") or route in {"offer-review", "refund-review"}:
        if route == "creator-application" or route.startswith("creator-account"):
            context, primary = "creator-account", ""
            selected = "creator-account-security" if route.endswith(("security", "password", "email", "sessions", "verify")) else "creator-application" if route == "creator-application" else "creator-account"
        elif route == "creator-analytics" or route in {"creator-offers", "creator-offer", "offer-review", "refund-review", "creator-coupons", "creator-tips"}:
            context, primary = "sales", "creator-analytics"
            selected = route if route in {"creator-analytics", "creator-coupons", "creator-tips"} else "creator-offers"
        elif route.startswith(("creator-question", "creator-practice-delivery")) or route in {"creator-results", "creator-quiz-results", "creator-quiz-grant", "creator-practices", "creator-practice-intake"}:
            context, primary = "teaching", "creator-questions"
            selected = "creator-questions" if route.startswith("creator-question") else "creator-practices" if route.startswith("creator-practice") else "creator-results"
        else:
            context, primary = "studio", "creator-dashboard" if route == "creator-dashboard" else "creator-content"
            selected = "creator-files" if route in {"creator-files", "creator-file"} else "creator-content"
    elif route in {"resource-detail", "reference-detail"}:
        selected, primary = "resources", "resources"
    elif route == "course-selector":
        selected = "courses"

    account = "creator-account" if creator else "student-account"
    destination = "creator-dashboard" if ready else "creator-application" if creator else "workspace" if signed_in else "home"

    def links(entries, current):
        output = []
        for entry in entries:
            name, label, *icons = entry
            url = reverse(name)
            output.append({"url": url, "label": label, "current": name == current,
                           "name": name, "icon": icons[0] if icons else "", "notifications": name == "notifications"})
        return output

    if ready:
        entries = CREATOR_MENU
    elif creator:
        entries = [("creator-application", "Estado de mi cuenta", "file")]
        primary = "creator-application" if route == "creator-application" else primary
        context = "creator-account" if context in {"studio", "teaching", "sales"} else context
    elif signed_in:
        entries = STUDENT_MENU
    else:
        entries = [*CATALOG_MENU, MEMBERSHIP_LINK, ("creators", "Enseñar", "people")]
    section_entries = SECTION_MENUS.get(context, [])
    if context == "learning" and not (route.startswith(("student-question", "student-practice")) or route == "question-create"):
        section_entries = []
    if context == "studio" and route not in {"creator-content", "creator-files", "creator-file"}:
        section_entries = []
    if creator and not ready:
        section_entries = []
    return {
        "sidebar_context": context, "sidebar_title": "Mi estudio" if creator else "BTC.EDU",
        "sidebar_links": links(entries, primary), "sidebar_switches": [],
        "sidebar_secondary_links": links(CATALOG_MENU, primary) if creator and status != "suspended" else [],
        "sidebar_local_links": [],
        "section_navigation_links": links(section_entries, selected),
        "section_navigation_label": SECTION_LABELS.get(context, "Secciones"),
        "navigation_account_url": reverse(account), "navigation_home_url": reverse(destination),
        "navigation_account_current": context in {"account", "creator-account"} and route != "creator-application",
        "navigation_notifications_current": context == "notifications",
        "navigation_cart_current": route.startswith("cart"),
        "navigation_creator": creator, "navigation_creator_ready": ready,
        "navigation_learning_url": reverse(destination),
        "navigation_signin_url": reverse("creator-login") if route == "creators" or route.startswith("creator-") and route != "creator-public-profile" else reverse("login") + "?" + urlencode({"next": requested_next or (reverse("workspace") if context == "auth" else request.get_full_path())}),
    }
