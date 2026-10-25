from django import template
from django.templatetags.static import static

register = template.Library()

# Integrated course illustrations, not separately sold stock photographs.
# License and individual source pages are also recorded in investigación y requisitos.
PHOTOS = {
    "fotografia": {"file": "fotografia", "author": "Marek Pospíšil", "url": "https://unsplash.com/photos/man-holding-iphone-WLBqJn2I6cQ"},
    "edicion-video": {"file": "edicion-video", "author": "André Eusébio", "url": "https://unsplash.com/photos/a-person-edits-video-on-a-computer-25OWIrAtGMM"},
    "desarrollo-web": {"file": "desarrollo-web", "author": "Emile Perron", "url": "https://unsplash.com/photos/macbook-pro-showing-programming-language-xrVDYZRGdw4"},
    "programacion": {"file": "programacion-python", "author": "Chris Ried", "url": "https://unsplash.com/photos/a-computer-screen-with-a-bunch-of-code-on-it-ieic5Tq8YMk"},
}

# Original SVG illustrations drawn for BTC.EDU, one per subcategory; they need no credit.
ILLUSTRATIONS = {
    "bases-de-datos", "analisis-datos", "inteligencia-artificial", "ciberseguridad", "seguridad-aplicaciones",
    "respuesta-incidentes", "redes", "linux-sistemas", "devops-contenedores", "git-colaboracion", "apis-backend",
    "diseno-ui-ux", "modelado-3d", "nodos-mineria", "lightning",
}


@register.simple_tag
def content_cover(topic_slug="", kind="", resource=None):
    if resource or kind in ("video", "material", "videos", "materiales"):
        filename = "cover-stack.svg"
    elif topic_slug in PHOTOS:
        filename = f"courses/{PHOTOS[topic_slug]['file']}.jpg"
    elif topic_slug in ILLUSTRATIONS:
        filename = f"courses/{topic_slug}.svg"
    elif kind in ("tutorial", "tutoriales") or topic_slug == "lightning":
        filename = "cover-tools.svg"
    elif topic_slug == "seguridad":
        filename = "cover-stack.svg"
    else:
        filename = "cover-circuit.svg"
    return static(f"images/{filename}")


@register.simple_tag
def course_photo(topic_slug=""):
    return PHOTOS.get(topic_slug)
