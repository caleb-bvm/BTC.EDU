from urllib.parse import urlencode

from django.urls import reverse

MENUS = {
    "catalog": ("Explorar", [("courses", "Cursos"), ("tutorials", "Tutoriales"), ("resources", "Recursos")]),
    "learning": ("Mi aprendizaje", [("workspace", "Mi aprendizaje"), ("certificates", "Certificados"), ("student-questions", "Mis preguntas")]),
    "payments": ("Compras", [("purchases", "Compras y facturas"), ("workspace", "Mi aprendizaje")]),
    "community": ("Comunidad", [("community-spaces", "Conversaciones"), ("members", "Personas"), ("notifications", "Notificaciones")]),
    "account": ("Mi cuenta", [("student-account", "Resumen"), ("student-profile", "Perfil de estudiante"), ("student-account-security", "Acceso")]),
    "auth": ("Acceso de estudiantes", [("login", "Entrar"), ("student-signup", "Crear cuenta"), ("student-password-reset", "Recuperar acceso")]),
    "studio": ("Tu contenido", [("creator-dashboard", "Mi contenido"), ("creator-files", "Biblioteca de archivos"), ("creator-offers", "Ofertas y precios")]),
    "teaching": ("Tus alumnos", [("creator-questions", "Preguntas de alumnos"), ("creator-analytics", "Estadísticas")]),
    "creator-account": ("Mi cuenta", [("creator-account", "Resumen"), ("creator-application", "Perfil de creador"), ("creator-account-security", "Acceso")]),
}


def contextual_navigation(request):
    """Choose navigation by resolved route, independently of catalog filters."""
    route = request.resolver_match.url_name if request.resolver_match else ""
    route = route or ""
    user = request.user
    creator = user.is_authenticated and user.account_type == "creator"
    creator_ready = creator and getattr(getattr(user, "creator_profile", None), "status", None) == "approved"
    signed_in = user.is_authenticated
    selected = route
    context = "catalog"
    if route.startswith("community-") or route in {"members", "member-profile", "notifications", "notification-read"}:
        context = "community"
        selected = "community-spaces" if route.startswith("community-") else "members" if route == "member-profile" else "notifications" if route == "notification-read" else route
    elif route in {"offer-detail", "checkout", "purchases"} or route.startswith("invoice-"):
        context, selected = "payments", "purchases"
    elif route == "student-profile" or route.startswith("student-account"):
        context = "account"
        selected = "student-account-security" if route.endswith(("security", "password", "email", "sessions", "export", "close")) else "student-profile" if route == "student-profile" else "student-account"
    elif route in {"login", "student-signup"} or route.startswith("student-password-reset"):
        context = "auth"
        selected = "student-password-reset" if route.startswith("student-password-reset") else route
    elif route == "workspace" or route.startswith(("certificate-", "quiz-", "student-question")) or route in {"certificates", "purchased-resource"}:
        context = "learning"
        selected = "certificates" if route.startswith("certificate-") else "student-questions" if route.startswith("student-question") else "workspace" if route.startswith("quiz-") or route == "purchased-resource" else route
    elif route in {"course-detail", "course-version", "lesson-detail", "version-lesson"}:
        context = "course"
    elif route.startswith("creator-") or route == "offer-review":
        context = "creator-account" if route == "creator-application" or route.startswith("creator-account") else "teaching" if route.startswith(("creator-question", "creator-quiz", "creator-certificate")) or route == "creator-analytics" else "studio"
        selected = "creator-questions" if route.startswith("creator-question") else "creator-analytics" if route.startswith("creator-quiz") or route == "creator-certificate-policy" else "creator-offers" if route in {"creator-offer", "offer-review"} else "creator-files" if route == "creator-file" else route if context == "creator-account" else "creator-dashboard" if context == "studio" and route not in {"creator-files", "creator-offers"} else route
        if route.startswith("creator-account"):
            selected = "creator-account-security" if route.endswith(("security", "password", "email", "sessions", "export", "close")) else "creator-account"
    elif route == "course-selector":
        selected = "courses"
    elif route in {"resource-detail", "reference-detail"}:
        selected = "resources"

    title, entries = MENUS.get(context, ("Tu recorrido", []))
    if creator and context == "account":
        title, entries = MENUS["creator-account"]
    if creator and context == "payments":
        entries = [("creator-offers", "Ofertas y precios")]
    if not signed_in and context in {"learning", "payments", "community", "account"}:
        entries = [("login", "Entrar"), ("courses", "Explorar cursos")]
    if creator and context == "studio" and getattr(getattr(user, "creator_profile", None), "status", None) != "approved":
        title, entries = MENUS["creator-account"]
        context, selected = "creator-account", "creator-application"
    if creator and not creator_ready and context == "community":
        entries = [("members", "Personas"), ("notifications", "Notificaciones")]

    def links(items):
        result = []
        for name, label in items:
            url = reverse(name)
            if context == "auth" and name in {"login", "student-signup"} and request.GET.get("next"):
                url += "?" + urlencode({"next": request.GET["next"]})
            result.append({"url": url, "label": label, "current": name == selected,
                           "notifications": name == "notifications"})
        return result

    switches = []
    if context != "catalog":
        switches.append(("courses", "Explorar"))
    if signed_in:
        destination = "creator-dashboard" if creator and getattr(getattr(user, "creator_profile", None), "status", None) == "approved" else "creator-application" if creator else "workspace"
        if context not in ({"studio", "teaching", "creator-account"} if creator else {"learning"}):
            switches.append((destination, "Mi estudio" if creator else "Mi aprendizaje"))
        if context != "community" and (not creator or creator_ready):
            switches.append(("community-spaces", "Comunidad"))
        if context not in {"account", "creator-account"}:
            switches.append(("creator-account" if creator else "student-account", "Mi cuenta"))
        if creator_ready and context == "studio":
            switches.append(("creator-questions", "Tus alumnos"))
    elif context != "auth":
        switches.append(("login", "Entrar"))
    if creator and getattr(getattr(user, "creator_profile", None), "status", None) == "suspended":
        context, title = "creator-account", "Tu cuenta"
        entries = [("creator-application", "Estado de mi cuenta"), ("creator-account", "Mi cuenta"), ("creator-account-support", "Ayuda y revisión"), ("notifications", "Notificaciones")]
        switches = []
    return {"sidebar_context": context, "sidebar_title": title,
            "sidebar_links": links(entries), "sidebar_switches": links(switches)}
