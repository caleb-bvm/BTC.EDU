from django.urls import path

from . import account_views as views


def settings_patterns(creator=False):
    prefix, name = ("cuenta/", "creator") if creator else ("ajustes/", "student")
    options = {"creator": creator}
    return [
        path(prefix, views.overview, options, name=f"{name}-account"),
        *[path(prefix + route + "/", view, options, name=f"{name}-account-{route_name}") for route, route_name, view in (
            ("foto", "photo", views.photo), ("acceso", "security", views.security),
            ("contrasena", "password", views.password), ("correo", "email", views.email),
            ("verificar", "verify", views.verify), ("avisos", "preferences", views.preferences),
            ("sesiones", "sessions", views.sessions), ("ayuda", "support", views.support),
            ("exportar", "export", views.export), ("desactivar", "close", views.close),
            ("cambiar-espacio", "switch", views.switch),
        )],
    ]
