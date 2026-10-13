"""Structure editorial plain text without accepting HTML or changing content."""
import re

SECTION_TITLES = {"Ejemplo": "example", "Práctica": "practice", "Solución y comprobación": "solution", "Para profundizar": "reference"}


def reading_sections(body):
    sections = []
    for paragraph in re.split(r"\n\s*\n", body or ""):
        lines = paragraph.strip().splitlines()
        if not lines:
            continue
        if lines[0] in SECTION_TITLES and len(lines) > 1:
            sections.append({"title": lines[0], "kind": SECTION_TITLES[lines[0]], "text": "\n".join(lines[1:])})
        elif sections and sections[-1]["kind"] != "text":
            sections[-1]["text"] += "\n\n" + paragraph.strip()
        else:
            sections.append({"title": "", "kind": "text", "text": paragraph.strip()})
    return sections
