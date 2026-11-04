"""Return student accounts to the learning page that requested authentication."""
from django.utils.http import url_has_allowed_host_and_scheme

from core.content_translation import without_language_prefix

STUDENT_PATHS = (
    "/explorar/", "/mi-espacio/", "/cuenta/perfil/", "/cursos/",
    "/tutoriales/", "/recursos/", "/referencias/", "/lecciones/",
    "/ofertas/", "/facturas/", "/aprendizaje/", "/personas/", "/creadores/",
    "/cuenta/ajustes/", "/carrito/", "/comprar/",
)


def student_destination(request, destination):
    if not destination or not url_has_allowed_host_and_scheme(
        destination, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return ""
    # Relative, known student destinations only; administration and studio stay separate.
    path = without_language_prefix(destination)
    return destination if path == "/" or path.startswith(STUDENT_PATHS) else ""
