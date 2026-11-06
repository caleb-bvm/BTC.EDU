"""Languages a course or resource can be written in.

Only the interface is translated; each course is shown in the language its educator
writes it in. The list reuses Django's language names, which Django already translates.
"""
import unicodedata

from django.conf import global_settings
from django.utils.functional import lazy
from django.utils.translation import get_language, gettext

DEFAULT_CONTENT_LANGUAGE = "es"
LANGUAGE_FIELD_MAX_LENGTH = 15

# Django's Spanish catalog uses a few uncommon names; these are the usual ones.
SPANISH_NAMES = {
    "af": "Afrikáans", "az": "Azerí", "gd": "Gaélico escocés", "kab": "Cabileño", "km": "Jemer",
    "lb": "Luxemburgués", "tk": "Turcomano", "udm": "Udmurto",
}


def _language_name(code, name):
    if (get_language() or "").startswith("es") and code in SPANISH_NAMES:
        return SPANISH_NAMES[code]
    return gettext(name)


_lazy_name = lazy(_language_name, str)

CONTENT_LANGUAGES = [
    (code, _lazy_name(code, name))
    for code, name in global_settings.LANGUAGES
    if "-" not in code or code in ("zh-hans", "zh-hant")
]
_NAMES = dict(CONTENT_LANGUAGES)


def language_name(code):
    """Name of a content language in the current interface language."""
    return str(_NAMES.get(code, code))


def _sort_key(choice):
    text = unicodedata.normalize("NFKD", str(choice[1]))
    return "".join(char for char in text if not unicodedata.combining(char)).casefold()


def sorted_language_choices():
    """Choices sorted by their name in the current interface language."""
    return sorted(CONTENT_LANGUAGES, key=_sort_key)
