"""Template helpers for the bilingual interface; loaded as builtins in settings."""
from django import template
from django.conf import settings
from django.urls import translate_url
from django.utils import translation
from django.utils.translation import gettext

from core.content_translation import is_translated, translate_content

register = template.Library()


@register.filter(name="tr")
def tr(value):
    """Translate BTC.EDU's own catalog text; anything else is returned as written.

    Stored notices keep the text of the language they were created in, so known
    interface messages are looked up in the interface catalog as well.
    """
    translated = translate_content(value)
    if translated == value and isinstance(value, str) and value:
        translated = gettext(value)
    return translated


@register.filter
def source_lang(value):
    """Return the source language when the text has no translation, for the lang attribute."""
    return "" if is_translated(value) else settings.LANGUAGE_CODE


@register.simple_tag(takes_context=True)
def language_options(context):
    request = context.get("request")
    # Path only: query strings may carry return addresses that must not be echoed.
    path = request.path if request else "/"
    current = translation.get_language()
    return [{"code": code, "name": name, "current": code == current, "url": translate_url(path, code)}
            for code, name in settings.LANGUAGES]
