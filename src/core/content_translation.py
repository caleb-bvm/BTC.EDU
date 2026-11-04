"""Translations of BTC.EDU's own catalog (titles, summaries, outcomes), kept apart from the interface.

Spanish is the source language. The `content` catalog maps the published Spanish text to
its translation; text without a translation, including what educators write, is shown as written.
"""
import gettext as gettext_module
from functools import lru_cache

from django.conf import settings
from django.utils import translation
from django.utils.functional import lazy

DOMAIN = "content"


@lru_cache(maxsize=None)
def _catalog(language):
    return gettext_module.translation(DOMAIN, localedir=str(settings.BASE_DIR / "locale"), languages=[language], fallback=True)


def content_language():
    return (translation.get_language() or settings.LANGUAGE_CODE).split("-")[0]


def translate_content(text):
    if text is not None and hasattr(text, "_meta"):
        text = str(text)  # Categories and topics render through their name.
    if not text or not isinstance(text, str):
        return text
    language = content_language()
    if language == settings.LANGUAGE_CODE:
        return text
    catalog = _catalog(language)
    translated = catalog.gettext(text)
    if translated == text and "\n\n" in text:
        # Loaders join a catalog description with a fixed note; translate each paragraph.
        translated = "\n\n".join(catalog.gettext(part) for part in text.split("\n\n"))
    return translated


def is_translated(text):
    """True when the text is already in the active language (source language or translated)."""
    return not text or content_language() == settings.LANGUAGE_CODE or translate_content(text) != text


translate_content_lazy = lazy(translate_content, str)


def without_language_prefix(path):
    """`/en/cursos/` → `/cursos/`, so route checks work for every language."""
    for code, _name in settings.LANGUAGES:
        prefix = f"/{code}/"
        if code != settings.LANGUAGE_CODE and path.startswith(prefix):
            return path[len(prefix) - 1:]
    return path
