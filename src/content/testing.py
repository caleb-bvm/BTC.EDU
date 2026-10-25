"""Educational metadata for synthetic test and preview units only."""
EDUCATION_FIXTURE = {
    "learning_outcome": "Explicar el ejemplo de esta unidad de prueba.",
    "requirements": "Sin conocimientos previos para este ejemplo.",
    "activity_kind": "understand",
    "public_preview": "Muestra pública del ejemplo de prueba.",
    "support_scope": "Consulta la explicación y la solución del ejemplo.",
}

CATEGORY_SLUGS = ("bitcoin", "desarrollo-software", "datos-ia", "ciberseguridad", "infraestructura", "creacion")


def category_counts(counts):
    """Expected catalog counts: every configured category is listed, even when empty."""
    return {**dict.fromkeys(CATEGORY_SLUGS, 0), **counts}
