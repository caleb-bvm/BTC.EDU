"""Keep the English catalogs in step with the Spanish source text.

  manage.py translations extract   # update locale/*/django.po and content.po, keep translations
  manage.py translations compile   # build the .mo files Django loads
  manage.py translations status    # count missing or placeholder-mismatched entries
"""
import importlib
import json
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.translation_files import (
    Entry,
    extract_python,
    extract_template,
    placeholders,
    read_po,
    write_mo,
    write_po,
)

HEADER = (
    "Project-Id-Version: BTC.EDU\n"
    "Language: {language}\n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=UTF-8\n"
    "Content-Transfer-Encoding: 8bit\n"
    "Plural-Forms: nplurals=2; plural=(n != 1);\n"
)
# Catalog fields shown as titles, summaries or outcomes. Lesson bodies, quizzes and sources stay in Spanish.
CONTENT_FIELDS = {"title", "name", "description", "objective", "requirements", "outcome", "preview",
                  "learning_outcome", "public_preview", "summary", "goal", "reason"}
SKIPPED = {"sources", "videos", "quiz", "practice", "projects", "document", "body", "question", "url", "slug", "video_url", "source_url"}


# Texts the loaders write directly (catalog creator profile, tutorial chapter, editorial units).
LOADER_TEXTS = (
    "Recorridos originales de autoestudio con prácticas, soluciones y fuentes atribuidas. "
    "Los videos externos son complementos de sus autores. Sin tutorías personales incluidas.",
    "Cursos originales de tecnología: software, datos, ciberseguridad, infraestructura, diseño y Bitcoin",
    "Material introductorio de Bitcoin y Lightning con ejercicios guiados.",
    "Lee la explicación, resuelve la práctica y compara tu respuesta.",
    "Practica con el ejemplo y compara tu respuesta con la solución. Las preguntas y conversaciones "
    "se mantienen dentro de la plataforma, sin un plazo de respuesta garantizado.",
    "Pasos",
)


def tracked_files(suffix):
    output = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", f"*{suffix}"],
                            cwd=settings.BASE_DIR, capture_output=True, text=True, check=True).stdout
    return [path for path in output.splitlines()
            if "test" not in path.rsplit("/", 1)[-1] and "/migrations/" not in path and not path.startswith("scripts/")]


def interface_messages():
    found = {}
    sources = [(path, extract_template) for path in tracked_files(".html") + tracked_files(".txt") if path.startswith(("templates/", ))]
    sources += [(path, extract_python) for path in tracked_files(".py")]
    for relative, extractor in sources:
        for fields, reference in extractor(settings.BASE_DIR / relative, relative):
            key = (fields.get("context"), fields["msgid"], "plural" in fields)
            entry = found.setdefault(key, Entry(msgid=fields["msgid"], context=fields.get("context"), plural=fields.get("plural")))
            entry.references.append(reference)
    return found


def _collect(value, found, reference, field=""):
    if isinstance(value, dict):
        for key, item in value.items():
            if key not in SKIPPED:
                _collect(item, found, reference, key)
            elif key in ("quiz", "practice") and isinstance(item, dict) and item.get("title"):
                # Quiz and practice titles appear in progress and certificate pages.
                _collect(item["title"], found, reference, "title")
    elif isinstance(value, (list, tuple)):
        for item in value:
            _collect(item, found, reference, field)
    elif isinstance(value, str) and field in CONTENT_FIELDS and value.strip():
        found.setdefault((None, value, False), Entry(msgid=value)).references.append(reference)


def content_messages():
    from content import course_catalog, editorial_catalog, tutorial_catalog
    from learning.management.commands import load_learning_paths

    found = {}
    _collect(course_catalog.load_catalog(), found, "content/course_catalog")
    for filename in tutorial_catalog.CATALOG_FILES:
        _collect(json.loads((tutorial_catalog.ROOT / filename).read_text(encoding="utf-8")), found, f"content/tutorial_catalog/{filename}")
    for course in editorial_catalog.CATALOG:
        _collect({**course, "chapters": [{"title": title} for title in course["chapters"]]}, found, "content/editorial_catalog.py")
    paths = [{"title": title, "summary": summary, "goal": goal,
              "steps": [{"reason": reason} for _, _, reason in steps]} for _, title, summary, goal, steps in load_learning_paths.PATHS]
    _collect(paths, found, "learning/management/commands/load_learning_paths.py")
    categories = importlib.import_module("content.migrations.0009_technology_categories").CATEGORIES
    _collect([{"name": name, "description": description, "topics": [{"name": entry[1], "description": entry[2]} for entry in entries]}
              for _, name, description, _, entries in categories], found, "content/migrations/0009_technology_categories.py")
    # Fixed texts the loaders write next to each catalog entry.
    plan = course_catalog.MEMBERSHIP_PLAN
    fixed = [course_catalog.SUPPORT, plan["name"], plan["description"], tutorial_catalog.TUTORIAL_SUPPORT,
             tutorial_catalog.RESOURCE_SUPPORT, *LOADER_TEXTS]
    for text in fixed:
        found.setdefault((None, text, False), Entry(msgid=text)).references.append("loaders")
    return found


class Command(BaseCommand):
    help = "Extrae, compila o revisa las traducciones de la interfaz y del catálogo."

    def add_arguments(self, parser):
        parser.add_argument("action", choices=("extract", "compile", "status"))

    def catalogs(self):
        for code, _name in settings.LANGUAGES:
            if code != settings.LANGUAGE_CODE:
                for domain in ("django", "content"):
                    yield code, domain, settings.BASE_DIR / "locale" / code / "LC_MESSAGES" / f"{domain}.po"

    def handle(self, action, **options):
        getattr(self, action)()

    def extract(self):
        messages = {"django": interface_messages(), "content": content_messages()}
        for code, domain, path in self.catalogs():
            header, existing = read_po(path)
            previous = {entry.key: entry for entry in existing}
            entries = []
            for key, entry in sorted(messages[domain].items(), key=lambda item: (item[0][1].lower(), item[0][0] or "")):
                if key in previous:
                    old = previous[key]
                    entry.msgstr, entry.plural_strs, entry.fuzzy = old.msgstr, old.plural_strs, old.fuzzy
                entry.references = [] if domain == "content" else entry.references
                entries.append(entry)
            write_po(path, header or HEADER.format(language=code), entries)
            missing = sum(not entry.translated for entry in entries)
            dropped = len(set(previous) - set(messages[domain]))
            self.stdout.write(f"{path.relative_to(settings.BASE_DIR)}: {len(entries)} textos, {missing} sin traducir, {dropped} retirados.")

    def compile(self):
        for _code, _domain, path in self.catalogs():
            header, entries = read_po(path)
            if not entries:
                raise CommandError(f"{path} no existe; ejecuta primero «translations extract».")
            write_mo(path.with_suffix(".mo"), header, entries)
            self.stdout.write(f"{path.with_suffix('.mo').relative_to(settings.BASE_DIR)}: {sum(e.translated for e in entries)} de {len(entries)}.")

    def status(self):
        problems = 0
        for _code, _domain, path in self.catalogs():
            _header, entries = read_po(path)
            missing = [entry for entry in entries if not entry.translated]
            mismatched = [entry for entry in entries if entry.translated and entry.plural is None
                          and not set(placeholders(entry.msgstr)) <= set(placeholders(entry.msgid))]
            problems += len(mismatched)
            self.stdout.write(f"{path.relative_to(settings.BASE_DIR)}: {len(entries) - len(missing)} de {len(entries)} traducidos.")
            for entry in mismatched[:10]:
                self.stdout.write(f"  marcador ajeno al original: {entry.msgid[:70]!r}")
        if problems:
            raise CommandError(f"{problems} traducciones usan marcadores que no existen en el original.")
