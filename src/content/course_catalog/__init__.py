"""Original learning paths sold as paid, freemium or membership courses; external sources remain attributed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_FILES = ("creacion.json", "web.json", "python.json", "datos-ia.json", "ciberseguridad.json", "infraestructura.json", "software.json", "diseno.json", "bitcoin.json")
CREATOR_EMAIL = "colecciones@btc-edu.invalid"
REVIEWER_EMAIL = "revision-colecciones@btc-edu.invalid"
SUPPORT = (
    "Estudio a tu ritmo con ejercicios, soluciones y evaluaciones automáticas. "
    "Los videos y fuentes externos son complementos gratuitos de sus autores; "
    "la compra corresponde al recorrido y al material original de BTC.EDU. "
    "No incluye tutorías ni revisión personal del proyecto."
)
# paid: every lesson is sold; freemium: free lessons first, the rest sold;
# membership: opened by the membership plan, with free lessons as a sample.
ACCESS_MODELS = ("paid", "freemium", "membership")
MEMBERSHIP_PLAN = {
    "name": "Membresía mensual", "amount_sats": 5000, "days": 30,
    "description": "Acceso a todos los cursos de la membresía durante 30 días.",
}


def access_model(course):
    return course.get("access", "paid")


def load_catalog():
    courses = []
    for filename in CATALOG_FILES:
        courses.extend(json.loads((ROOT / filename).read_text(encoding="utf-8")))
    if len({item["slug"] for item in courses}) != len(courses):
        raise ValueError("Hay identificadores de curso repetidos.")
    for course in courses:
        model = access_model(course)
        if model not in ACCESS_MODELS:
            raise ValueError(f"{course['title']}: modalidad de acceso desconocida.")
        if (model != "membership" and course["price"] <= 0) or not course["sources"]:
            raise ValueError(f"{course['title']}: necesita precio y fuentes.")
        chapters = course["chapters"]
        if len(chapters) < 4 or any(len(chapter["lessons"]) < 3 for chapter in chapters):
            raise ValueError(f"{course['title']}: temario incompleto.")
        free = [lesson.get("free", False) for chapter in chapters for lesson in chapter["lessons"]]
        if model == "paid" and any(free):
            raise ValueError(f"{course['title']}: un curso de pago no tiene lecciones gratuitas.")
        if model == "freemium" and not (any(free) and not all(free)):
            raise ValueError(f"{course['title']}: un curso freemium combina lecciones gratuitas y de pago.")
        if model == "membership" and all(free):
            raise ValueError(f"{course['title']}: un curso de membresía necesita lecciones incluidas en el plan.")
        for chapter in chapters:
            if not any(lesson.get("quiz") for lesson in chapter["lessons"]):
                raise ValueError(f"{chapter['title']}: falta evaluación.")
            for lesson in chapter["lessons"]:
                if len(lesson["body"].split()) < 250 or not lesson["sources"]:
                    raise ValueError(f"{lesson['title']}: contenido o fuentes insuficientes.")
    return courses


def unit_price(course_price, paid_lessons):
    """Buying every paid lesson separately costs about 1.5 times the full course."""
    return -(-course_price * 3 // (2 * paid_lessons))


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
