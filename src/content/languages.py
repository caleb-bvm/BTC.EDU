"""Languages a course or resource can be written in.

Only the interface is translated; each course is shown in the language its educator
writes it in. The list reuses Django's language names, which Django already translates.
"""
import unicodedata

from django.conf import global_settings
from django.utils.translation import gettext_lazy

DEFAULT_CONTENT_LANGUAGE = "es"
LANGUAGE_FIELD_MAX_LENGTH = 15

CONTENT_LANGUAGES = [
    (code, gettext_lazy(name))
    for code, name in global_settings.LANGUAGES
    if "-" not in code or code in ("zh-hans", "zh-hant")
]


def _sort_key(choice):
    text = unicodedata.normalize("NFKD", str(choice[1]))
    return "".join(char for char in text if not unicodedata.combining(char)).casefold()


def sorted_language_choices():
    """Choices sorted by their name in the current interface language."""
    return sorted(CONTENT_LANGUAGES, key=_sort_key)
