from django.db import migrations, models

# The former «Tecnología» areas become categories; subcategory slugs are kept so old links still work.
# Optional trailing names recognize a subcategory renamed here or saved with another slug.
CATEGORIES = (
    ("bitcoin", "Bitcoin y Lightning", "Bitcoin, Lightning, autocustodia y desarrollo de pagos.", "bitcoin", (
        ("bitcoin", "Fundamentos de Bitcoin", "Conoce los principios, las transacciones y el funcionamiento de Bitcoin."),
        ("lightning", "Lightning", "Comprende canales, rutas, liquidez y pagos Lightning."),
        ("seguridad", "Seguridad y autocustodia", "Protege claves, respaldos y hábitos de uso de Bitcoin."),
        ("desarrollo-lightning", "Desarrollo Lightning", "Crea aplicaciones e integraciones para pagos con Lightning."),
        ("nodos-mineria", "Nodos y minería", "Opera un nodo, valida la cadena y entiende cómo funciona la minería."),
    )),
    ("desarrollo-software", "Desarrollo de software", "Programación, aplicaciones web y móviles, APIs y prácticas de ingeniería.", "desarrollo-software", (
        ("programacion", "Programación", "Fundamentos, lenguajes y resolución de problemas con código."),
        ("desarrollo-web", "Desarrollo web", "Interfaces, servidores y aplicaciones para la web."),
        ("desarrollo-movil", "Desarrollo móvil", "Diseño y desarrollo de aplicaciones para dispositivos móviles."),
        ("apis-backend", "APIs y backend", "Servicios, APIs y lógica de servidor para aplicaciones."),
        ("git-colaboracion", "Git y colaboración", "Control de versiones, revisión de código y trabajo en equipo."),
        ("pruebas-calidad", "Pruebas y calidad", "Pruebas automatizadas, depuración y calidad del software."),
    )),
    ("datos-ia", "Datos e inteligencia artificial", "Bases de datos, análisis, aprendizaje automático e IA aplicada.", "datos-ia", (
        ("bases-de-datos", "Bases de datos", "Modelado, consultas y administración de datos."),
        ("analisis-datos", "Análisis de datos", "Limpieza, exploración y visualización de datos para tomar decisiones."),
        ("aprendizaje-automatico", "Aprendizaje automático", "Modelos predictivos: preparación de datos, entrenamiento y evaluación."),
        ("inteligencia-artificial", "Inteligencia artificial", "Conceptos y uso práctico de herramientas de inteligencia artificial."),
    )),
    ("ciberseguridad", "Ciberseguridad", "Protección de sistemas, redes, aplicaciones y datos.", "ciberseguridad", (
        ("ciberseguridad", "Fundamentos de ciberseguridad", "Amenazas, controles y hábitos para proteger sistemas y datos.", "Ciberseguridad"),
        ("seguridad-aplicaciones", "Seguridad de aplicaciones", "Vulnerabilidades comunes, desarrollo seguro y revisión de código."),
        ("hacking-etico", "Hacking ético", "Pruebas de penetración autorizadas y análisis de vulnerabilidades."),
        ("respuesta-incidentes", "Respuesta a incidentes", "Detección, análisis y recuperación ante incidentes de seguridad."),
    )),
    ("infraestructura", "Infraestructura y nube", "Hardware, redes, sistemas operativos, nube y DevOps.", "infraestructura", (
        ("hardware-pc", "Hardware de PC", "Componentes, montaje, mantenimiento y diagnóstico de computadoras."),
        ("redes", "Redes", "Conectividad, protocolos y administración de redes."),
        ("linux-sistemas", "Linux y sistemas", "Uso y administración de sistemas operativos y servidores."),
        ("computacion-nube", "Computación en la nube", "Servicios, despliegue y control de costos en plataformas de nube."),
        ("devops-contenedores", "DevOps y contenedores", "Contenedores, automatización e integración y entrega continuas."),
    )),
    ("creacion", "Diseño y creación digital", "Diseño de interfaces, fotografía, video, 3D y producción de contenido digital.", "creacion", (
        ("diseno-ui-ux", "Diseño UI/UX", "Investigación, experiencia de usuario e interfaces digitales."),
        ("adobe-photoshop", "Adobe Photoshop", "Edición de imágenes y composición digital con Adobe Photoshop."),
        ("adobe-lightroom", "Adobe Lightroom", "Organización, revelado y edición fotográfica con Adobe Lightroom."),
        ("adobe-premiere", "Adobe Premiere Pro", "Edición y montaje de video con Adobe Premiere Pro."),
        ("fotografia", "Fotografía", "Composición, iluminación, captura y edición de fotografías."),
        ("creacion-contenido", "Creación de contenido", "Planificación y producción de contenidos para medios digitales."),
        ("modelado-3d", "Modelado y animación 3D", "Creación de modelos, escenas y animaciones tridimensionales."),
    )),
)
PREVIOUS_DEFAULTS = {
    "bitcoin": ("Bitcoin", "Bitcoin, Lightning y autocustodia."),
    "creacion": ("Creación", "Diseño, fotografía, video y producción de contenido digital."),
}
RETIRED = "tecnologia"


def reorganize_categories(apps, schema_editor):
    Category = apps.get_model("content", "Category")
    Topic = apps.get_model("content", "Topic")
    database = schema_editor.connection.alias
    categories = Category.objects.using(database)
    topics = Topic.objects.using(database)
    for slug, name, description, artwork, entries in CATEGORIES:
        category = categories.filter(slug=slug).first()
        if category is None:
            category = categories.create(slug=slug, name=name, description=description, artwork=artwork)
        else:
            # Only the previous defaults are replaced; editorial changes made in the admin are kept.
            previous_name, previous_description = PREVIOUS_DEFAULTS.get(slug, (category.name, ""))
            changes = {"artwork": category.artwork or artwork}
            if category.name == previous_name and not categories.filter(name=name).exclude(pk=category.pk).exists():
                changes["name"] = name
            if category.description in ("", previous_description):
                changes["description"] = description
            categories.filter(pk=category.pk).update(**changes)
        for topic_slug, topic_name, topic_description, *aliases in entries:
            topic = topics.filter(slug=topic_slug).first()
            if topic is None:
                topic = topics.filter(name__in=(topic_name, *aliases)).order_by("pk").first()
            if topic is None:
                topics.create(slug=topic_slug, name=topic_name, description=topic_description, category=category)
                continue
            changes = {"category_id": category.pk, "description": topic.description or topic_description}
            if topic.name in aliases and not topics.filter(name=topic_name).exclude(pk=topic.pk).exists():
                changes["name"] = topic_name
            topics.filter(pk=topic.pk).update(**changes)
    retired = categories.filter(slug=RETIRED).first()
    if retired and not topics.filter(category=retired).exists():
        retired.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_category_hierarchy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='artwork',
            field=models.CharField(blank=True, choices=[('bitcoin', 'Bitcoin'), ('lightning', 'Lightning'), ('seguridad', 'Seguridad'), ('desarrollo', 'Desarrollo'), ('general', 'Aprendizaje'), ('tecnologia', 'Tecnología'), ('creacion', 'Creación'), ('desarrollo-software', 'Desarrollo de software'), ('datos-ia', 'Datos e inteligencia artificial'), ('ciberseguridad', 'Ciberseguridad'), ('infraestructura', 'Infraestructura y nube')], help_text='En blanco, se elige según la categoría; las categorías nuevas usan la imagen de aprendizaje.', max_length=20, verbose_name='imagen de la categoría'),
        ),
        # Reversing keeps the new taxonomy; courses and their versions never lose their subcategory.
        migrations.RunPython(reorganize_categories, migrations.RunPython.noop),
    ]
