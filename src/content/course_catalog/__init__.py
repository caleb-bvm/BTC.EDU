"""Original, paid learning paths; external sources remain attributed references."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_FILES = ("creacion.json", "web.json", "python.json")
CREATOR_EMAIL = "colecciones@btc-edu.invalid"
REVIEWER_EMAIL = "revision-colecciones@btc-edu.invalid"
SUPPORT = (
    "Estudio a tu ritmo con ejercicios, soluciones y evaluaciones automáticas. "
    "Los videos y fuentes externos son complementos gratuitos de sus autores; "
    "la compra corresponde al recorrido y al material original de BTC.EDU. "
    "No incluye tutorías ni revisión personal del proyecto."
)


def load_catalog():
    courses = []
    for filename in CATALOG_FILES:
        courses.extend(json.loads((ROOT / filename).read_text(encoding="utf-8")))
    if len({item["slug"] for item in courses}) != len(courses):
        raise ValueError("Hay identificadores de curso repetidos.")
    for course in courses:
        if course["price"] <= 0 or not course["sources"]:
            raise ValueError(f"{course['title']}: necesita precio y fuentes.")
        chapters = course["chapters"]
        if len(chapters) < 4 or any(len(chapter["lessons"]) < 3 for chapter in chapters):
            raise ValueError(f"{course['title']}: temario incompleto.")
        for chapter in chapters:
            if not any(lesson.get("quiz") for lesson in chapter["lessons"]):
                raise ValueError(f"{chapter['title']}: falta evaluación.")
            for lesson in chapter["lessons"]:
                if len(lesson["body"].split()) < 250 or not lesson["sources"]:
                    raise ValueError(f"{lesson['title']}: contenido o fuentes insuficientes.")
    return courses


def teaching_body(lesson):
    """Keep references and optional videos inside the protected revision."""
    parts = [lesson["body"].strip()]
    if lesson.get("videos"):
        for video in lesson["videos"]:
            parts.append(f"Video complementario\n{video['title']}\n{video['url']}")
    parts.append("Para profundizar\n" + "\n".join(
        f"{source['title']}: {source['url']}" for source in lesson["sources"]
    ))
    return "\n\n".join(parts)
