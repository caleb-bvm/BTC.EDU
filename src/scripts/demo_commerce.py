"""Sample content exclusively for temporary demonstrations and integration checks."""
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from commerce.offers import create_offer, review_offer, submit_offer
from content.models import Chapter, Course, Lesson, LessonResource, Material
from creators.models import CreatorProfile
from creators.services import decide, submit
from media.models import Asset


def seed():
    users = get_user_model().objects
    creator = users.create_user("ana@demo.invalid", first_name="Ana", last_name="López", account_type="creator")
    reviewer = users.create_superuser("revision@demo.invalid")
    student = users.create_user("lucia@demo.invalid", first_name="Lucía")
    other = users.create_user("segundo@demo.invalid")
    CreatorProfile.objects.create(user=creator, display_name="Ana López", bio="Aprende a preparar y comprobar un flujo de micropagos de prueba.", specialty="Tecnología", status="approved")
    course = Course.objects.create(creator=creator, title="Construye tu primer flujo de micropagos", description="Una guía práctica para crear una factura de prueba, comprobar el pago y organizar los accesos de tu proyecto.", objective="Comprender la factura, el estado del pago y el acceso concedido.", requirements="Conocer la navegación básica de una aplicación web.", level="beginner", estimated_minutes=45)
    chapter = Chapter.objects.create(course=course, title="De la factura al aprendizaje", status="published")
    free = Lesson.objects.create(chapter=chapter, title="Antes de empezar", description="Conoce el recorrido y el entorno de simulación.", body="Trabajaremos con pagos ficticios. Una factura pendiente no concede acceso: la aplicación debe confirmar el estado desde el servidor.", status="published", position=1)
    lesson = Lesson.objects.create(chapter=chapter, title="Preparar una factura", description="Define el precio y conserva lo incluido.", body="La factura reúne un precio, una lista concreta de contenidos y un plazo. Estos datos permanecen iguales aunque el creador publique otra oferta. Consulta el estado antes de repetir una operación que no respondió.", status="published", access_type="paid", position=2)
    Lesson.objects.create(chapter=chapter, title="Confirmar y conservar el acceso", description="Abre el contenido después del pago confirmado.", body="La confirmación del proveedor permite registrar la compra. Cada derecho apunta a la revisión adquirida: estudiar una versión nueva requiere una decisión explícita. Una confirmación repetida conserva la compra original.", status="published", access_type="paid", position=3)
    asset = Asset.objects.create(creator=creator, file=SimpleUploadedFile("guia-del-recorrido.txt", "Guía de demostración\n1. Preparar factura\n2. Comprobar pago\n3. Abrir contenido adquirido\n".encode(), content_type="text/plain"))
    material = Material.objects.create(creator=creator, title="Guía del recorrido de compra", description="Una lista de pasos para comprobar tu implementación de prueba.", access_type="paid", pending_asset=asset)
    material_submission = submit(material, creator)
    decide(material_submission, reviewer, True)
    material.refresh_from_db()
    LessonResource.objects.create(lesson=lesson, resource=material.revision)
    submission = submit(course, creator)
    decide(submission, reviewer, True)
    version = submission.course_version
    version.refresh_from_db()
    records = list(version.chapters.first().lessons.select_related("content"))
    def offer(target, title, price):
        item = create_offer(creator, target, title, price)
        submit_offer(creator, item)
        return review_offer(reviewer, item, True)
    individual = offer(f"lesson:{records[1].pk}", "Preparar una factura · texto", 70)
    second = offer(f"lesson:{records[2].pk}", "Confirmar y conservar el acceso · texto", 80)
    file_offer = offer(f"resource:{material.revision_id}", "Guía del recorrido · material", 30)
    bundle = offer(f"course:{version.pk}", "Curso completo · micropagos", 150)
    chapter_offer = offer(f"chapter:{records[0].chapter_id}", "De la factura al aprendizaje · capítulo", 150)
    return SimpleNamespace(creator=creator, reviewer=reviewer, student=student, other=other, course=course, free=free, lesson=lesson,
                           material=material, version=version, records=records, individual=individual, second=second, file_offer=file_offer, bundle=bundle, chapter_offer=chapter_offer)
