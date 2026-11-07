"""Messages shown by the JavaScript files; base.html passes their translation to `btcT()`."""
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext, gettext_noop

MESSAGES = [
    gettext_noop("Cerrar menú principal"), gettext_noop("Abrir menú principal"),
    gettext_noop("No pudimos actualizar el catálogo. Tus filtros siguen aquí; vuelve a intentarlo."),
    gettext_noop("Se perdió la conexión. Conservamos tus filtros; vuelve a buscar cuando recuperes conexión."),
    gettext_noop("No pudimos comprobar el pago. Usa Actualizar estado para volver a intentarlo."),
    gettext_noop("Cambios sin guardar"), gettext_noop("Sin cambios pendientes"),
    gettext_noop("La sesión o cuenta cambió. Vuelve a entrar y reintenta; tus cambios siguen aquí."),
    gettext_noop("No se pudo guardar. Conservamos tus cambios para reintentar."),
    gettext_noop("No pudimos confirmar el guardado. Tus cambios siguen aquí; recarga tu cuenta en otra pestaña para comprobarlo."),
    gettext_noop("Corrige los campos indicados y vuelve a guardar."),
    gettext_noop("La sesión o cuenta cambió. Entra con esta cuenta en otra pestaña y vuelve a guardar; tus cambios siguen aquí."),
    gettext_noop("Se perdió la conexión. Tus cambios siguen aquí; vuelve a intentarlo cuando regrese."),
    gettext_noop("Elige una foto JPG, PNG o WebP de hasta 3 MB."),
    gettext_noop("Ajusta la posición y el acercamiento. La vista previa muestra el recorte que se guardará."),
    gettext_noop("No pudimos leer la foto. Elige otro archivo."),
    gettext_noop("Añadiendo…"),
    gettext_noop("No pudimos añadir esta selección. Revisa la opción y vuelve a intentar."),
    gettext_noop(" artículo"), gettext_noop(" artículos"),
    gettext_noop("La sesión cambió. Revisa tu cuenta en otra pestaña y vuelve a intentar."),
    gettext_noop("No pudimos conectar. Conservamos tu selección; vuelve a intentar añadirla."),
    gettext_noop("Factura copiada."), gettext_noop("Seleccionamos la factura. Usa la opción de copiar de tu dispositivo."),
    gettext_noop("Cargando archivo…"),
    gettext_noop("La sesión o cuenta cambió. Entra con esta cuenta en otra pestaña y reintenta; el archivo sigue seleccionado."),
    gettext_noop("Corrige el archivo y vuelve a intentarlo"),
    gettext_noop("Tu sesión venció. Abre Entrar en otra pestaña y reintenta; el archivo sigue seleccionado."),
    gettext_noop("No se pudo guardar. Conservamos tu selección para reintentar."),
    gettext_noop("Se perdió la conexión. Reintenta con el archivo seleccionado."),
    gettext_noop("Revisa los campos indicados. Tus cambios siguen aquí."),
    gettext_noop("Corrige los campos y vuelve a guardar."),
    gettext_noop("La versión enviada se guardó. Tus cambios posteriores siguen aquí; revisa el borrador antes de volver a guardar."),
    gettext_noop("Tu sesión o cuenta cambió. Entra en otra pestaña y reintenta; tus cambios siguen aquí."),
    gettext_noop("No pudimos confirmar el guardado. Tus cambios siguen aquí; vuelve a intentarlo."),
    gettext_noop("Salir de lectura enfocada ↙"), gettext_noop("Enfocar lectura ↗"),
    gettext_noop("Guardando tu avance…"),
    gettext_noop("Tu sesión cambió. Vuelve a entrar para guardar el avance."),
    gettext_noop("No pudimos guardar. Comprueba tu sesión y vuelve a intentarlo."),
    gettext_noop("No pudimos guardar. Reintenta desde esta lección."),
    gettext_noop("Completada"), gettext_noop("{completed} de {total}"),
    gettext_noop("Estás aquí"), gettext_noop("Por estudiar"),
    gettext_noop("No pudimos conectar para guardar. Reintenta desde esta lección."),
    gettext_noop("Disponible sin conexión ✓"), gettext_noop("Guardar sin conexión"),
    gettext_noop("No se pudo guardar. Inténtalo con conexión."),
    gettext_noop("El máximo es 20 preguntas. Puedes editar o eliminar las existentes."),
    gettext_noop("Marcada para revisar"), gettext_noop("Marcar para revisar"),
    gettext_noop("Revisar y entregar →"), gettext_noop("Siguiente →"),
    gettext_noop("Respondiste todo. Revisa las preguntas marcadas si quieres cambiar algo."),
    gettext_noop("Respondiste todas las preguntas. Puedes cambiar cualquier respuesta o entregar el intento."),
    gettext_noop("Sin responder"), gettext_noop("Sin guardar"),
    gettext_noop("Recarga el intento para recuperar las respuestas guardadas."),
    gettext_noop("Revisa tu conexión. Tus respuestas siguen en esta página."),
    gettext_noop("Nueva pregunta"), gettext_noop("Carrito, "),
    gettext_noop("Activar modo claro"), gettext_noop("Activar modo oscuro"),
    gettext_noop("☾ Oscuro"), gettext_noop("☀ Claro"),
]


def js_text(request):
    """Translations for the active language; Spanish pages need none."""
    if (translation.get_language() or settings.LANGUAGE_CODE).split("-")[0] == settings.LANGUAGE_CODE:
        return {"js_text": None}
    return {"js_text": {message: gettext(message) for message in MESSAGES}}
