from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.models import Course
from learning.models import LearningPath, PathCourse

BUNDLE_PERCENT = 15

# Editorial paths: title, summary, goal and steps as (course title, optional, why this step).
PATHS = [
    ("bitcoin-y-lightning", "Bitcoin y Lightning: de cero a cobrar",
     "Entiende Bitcoin, protege tus claves y cobra con Lightning en un negocio.",
     "Al terminar sabrás cómo se mueve una transacción, cómo respaldar una wallet y cómo emitir y conciliar cobros con Lightning.",
     [("Bitcoin desde cero: unidades, red y transacciones", False, "Unidades, red y transacciones: la base de los demás pasos."),
      ("Wallets y autocustodia: claves, respaldo y recepción", False, "Antes de recibir pagos, aprende a proteger tus claves."),
      ("Lightning desde cero: canales, rutas y liquidez", False, "Canales, rutas y liquidez explican por qué un pago llega o falla."),
      ("Facturas Lightning: del QR a la confirmación", False, "Lee una factura y confirma el pago antes de entregar."),
      ("Opera tu propio nodo Bitcoin: Bitcoin Core paso a paso", True, "Verifica la red por tu cuenta con un nodo propio."),
      ("Cobros con Lightning para negocios: del mostrador a la contabilidad", False, "Lleva lo aprendido al mostrador y a la contabilidad.")]),
    ("desarrollo-con-lightning", "Desarrollo con Lightning",
     "Integra pagos Lightning en una aplicación, del laboratorio al acceso por compra.",
     "Al terminar podrás montar un laboratorio con LNbits, emitir facturas desde código y entregar contenido solo después del pago.",
     [("Lightning desde cero: canales, rutas y liquidez", False, "El modelo de canales y rutas con el que trabajará tu código."),
      ("Facturas Lightning: del QR a la confirmación", False, "La factura es la interfaz entre tu aplicación y el pago."),
      ("LNbits: organiza un laboratorio de micropagos", False, "Un laboratorio local para probar pagos sin riesgo."),
      ("Contenido con micropagos: compra, acceso y versiones", False, "Conecta el pago con el acceso y las versiones del contenido."),
      ("APIs REST con Python y FastAPI: diseña, prueba y protege tu backend", True, "Diseña el backend que expone esos pagos.")]),
    ("backend-con-python", "Backend con Python",
     "Del primer script a una API publicada en un servidor Linux.",
     "Al terminar habrás automatizado tareas con Python, versionado tu código y publicado una API en un servidor.",
     [("Python práctico: automatiza reportes con CSV", False, "Sintaxis y archivos con un problema real: reportes en CSV."),
      ("Git y GitHub: control de versiones para trabajar en equipo", False, "Versiona desde el principio y trabaja con otras personas."),
      ("APIs REST con Python y FastAPI: diseña, prueba y protege tu backend", False, "Diseña, prueba y protege tu primer backend."),
      ("Linux para servidores: terminal, permisos, servicios y SSH", False, "Terminal, permisos y SSH para operar donde vive tu API."),
      ("Docker y contenedores: empaqueta, ejecuta y despliega aplicaciones", True, "Empaqueta la API para desplegarla igual en cualquier servidor.")]),
    ("analisis-de-datos", "Análisis de datos",
     "Consulta, limpia y comunica los datos de un negocio con SQL y Python.",
     "Al terminar podrás responder preguntas de negocio con SQL y pandas, y presentar resultados verificables.",
     [("Python práctico: automatiza reportes con CSV", False, "Las bases de Python que usarás con pandas."),
      ("SQL desde cero con SQLite: consulta y analiza las ventas de un negocio", False, "Consulta las ventas directamente en la base de datos."),
      ("Análisis de datos con Python y pandas: limpia, resume y comunica", False, "Limpia, resume y comunica los datos."),
      ("IA generativa en el trabajo: instrucciones claras y resultados verificables", True, "Usa IA para acelerar el análisis y verifica sus resultados.")]),
    ("ciberseguridad", "Ciberseguridad",
     "Protege cuentas y aplicaciones, y responde cuando algo falla.",
     "Al terminar sabrás reducir riesgos personales, revisar una aplicación web con OWASP Top 10 y coordinar la respuesta a un incidente.",
     [("Fundamentos de ciberseguridad: protege tus cuentas, dispositivos y datos", False, "Cuentas, dispositivos y datos: los hábitos que los demás pasos suponen."),
      ("Redes desde cero: direcciones IP, DNS y diagnóstico de conexiones", True, "Sáltalo si ya dominas IP y DNS; ayuda a leer registros y ataques."),
      ("Seguridad de aplicaciones web: OWASP Top 10:2025 en la práctica", False, "Los riesgos más comunes de una aplicación web y cómo evitarlos."),
      ("Respuesta a incidentes de seguridad: detecta, contén y aprende", False, "Detecta, contén y aprende de un incidente.")]),
    ("infraestructura", "Infraestructura",
     "Redes, servidores Linux y contenedores para operar servicios propios.",
     "Al terminar podrás diagnosticar conexiones, administrar un servidor y desplegar servicios en contenedores, incluido un nodo Bitcoin.",
     [("Redes desde cero: direcciones IP, DNS y diagnóstico de conexiones", False, "Direcciones, DNS y diagnóstico: lo primero cuando algo no conecta."),
      ("Linux para servidores: terminal, permisos, servicios y SSH", False, "Administra el servidor donde correrán tus servicios."),
      ("Docker y contenedores: empaqueta, ejecuta y despliega aplicaciones", False, "Despliega servicios repetibles con contenedores."),
      ("Opera tu propio nodo Bitcoin: Bitcoin Core paso a paso", True, "Aplica lo aprendido operando un nodo propio.")]),
]


class Command(BaseCommand):
    help = "Publica las rutas editoriales de BTC.EDU sin modificar rutas existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        titles = {title for *_, steps in PATHS for title, _, _ in steps}
        courses = {course.title: course for course in Course.objects.filter(title__in=titles, status="published", current_version__isnull=False)}
        missing = sorted(titles - courses.keys())
        if missing:
            raise CommandError("Faltan cursos publicados: " + "; ".join(missing))
        added = 0
        for position, (slug, title, summary, description, steps) in enumerate(PATHS, 1):
            if LearningPath.objects.filter(slug=slug).exists():
                continue
            path = LearningPath.objects.create(slug=slug, title=title, summary=summary, description=description, position=position,
                                               bundle_percent=BUNDLE_PERCENT, published=True)
            PathCourse.objects.bulk_create([PathCourse(path=path, course=courses[course], position=index, optional=optional, note=note)
                                            for index, (course, optional, note) in enumerate(steps, 1)])
            added += 1
        self.stdout.write(f"Rutas añadidas: {added} de {len(PATHS)}.")
