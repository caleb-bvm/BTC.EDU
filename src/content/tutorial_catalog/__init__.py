"""Original tutorials and curated resources, one file per category; external sources remain attributed."""
import json
from pathlib import Path

from content.reading import video_embed

ROOT = Path(__file__).resolve().parent
CATALOG_FILES = ("bitcoin.json", "ciberseguridad.json", "datos-ia.json", "desarrollo-software.json", "infraestructura.json", "creacion.json")
TUTORIAL_SUPPORT = (
    "Guía de autoestudio con pasos comprobables y fuentes oficiales. "
    "No incluye tutorías ni revisión personal de tu resultado."
)
RESOURCE_SUPPORT = (
    "Recurso de consulta para usar a tu ritmo. "
    "No incluye tutorías ni revisión personal."
)
# free: every step is open; freemium: the first step is open and the rest are sold; paid: every step is sold.
ACCESS_MODELS = ("free", "freemium", "paid")
RESOURCE_KINDS = ("video", "material", "reference")
LEVELS = ("beginner", "intermediate", "advanced")
ACTIVITIES = ("understand", "design", "execute")


def tutorial_steps(tutorial):
    """Access per step: freemium opens only the first one."""
    model = tutorial["access"]
    return [{**step, "free": model == "free" or (model == "freemium" and position == 0)}
            for position, step in enumerate(tutorial["steps"])]


def check_tutorial(item):
    name = item["title"]
    if item["access"] not in ACCESS_MODELS:
        raise ValueError(f"{name}: modalidad de acceso desconocida.")
    if (item["access"] == "free") == bool(item.get("price")):
        raise ValueError(f"{name}: solo los tutoriales con pasos de pago llevan precio.")
    if item["level"] not in LEVELS or not 5 <= item["minutes"] <= 45:
        raise ValueError(f"{name}: nivel o duración fuera de rango.")
    if not 3 <= len(item["steps"]) <= 6:
        raise ValueError(f"{name}: un tutorial tiene entre tres y seis pasos.")
    for step in item["steps"]:
        if step["activity"] not in ACTIVITIES or not step["sources"]:
            raise ValueError(f"{step['title']}: actividad o fuentes incompletas.")
        if len(step["body"].split()) < 110:
            raise ValueError(f"{step['title']}: el paso necesita al menos 110 palabras.")


def check_resource(item):
    name = item["title"]
    if item["kind"] not in RESOURCE_KINDS:
        raise ValueError(f"{name}: formato desconocido.")
    if item["kind"] == "video" and (not video_embed(item["video_url"]) or not item["video_author"].strip()):
        raise ValueError(f"{name}: el video necesita un enlace de YouTube y su autor.")
    if item["kind"] == "material":
        if item["access"] not in ("free", "paid") or (item["access"] == "paid") != bool(item.get("price")):
            raise ValueError(f"{name}: acceso o precio inconsistentes.")
        if not item["document"]["sections"] or not item["sources"]:
            raise ValueError(f"{name}: el material necesita contenido y fuentes.")
    if item["kind"] == "reference" and not item["source_url"].startswith("https://"):
        raise ValueError(f"{name}: la referencia necesita un enlace HTTPS.")


def load_catalog():
    tutorials, resources = [], []
    for filename in CATALOG_FILES:
        data = json.loads((ROOT / filename).read_text(encoding="utf-8"))
        tutorials.extend(data["tutorials"])
        resources.extend(data["resources"])
    for items in (tutorials, resources):
        if len({item["slug"] for item in items}) != len(items) or len({item["title"] for item in items}) != len(items):
            raise ValueError("Hay identificadores o títulos repetidos.")
    for item in tutorials:
        check_tutorial(item)
    for item in resources:
        check_resource(item)
    return tutorials, resources


def step_body(step):
    """Keep references inside the protected revision, as in the complete courses."""
    return step["body"].strip() + "\n\nPara profundizar\n" + "\n".join(
        f"{source['title']}: {source['url']}" for source in step["sources"]
    )
