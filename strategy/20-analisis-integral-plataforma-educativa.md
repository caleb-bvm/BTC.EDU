# Revisión integral de BTC.EDU

El diagnóstico siguiente conserva el estado observado durante la revisión. Después se iniciaron las implementaciones: el primer bloque resolvió registro, identidad pública y tema publicado de recursos. El estado vigente y las brechas restantes se mantienen en [Mejoras integrales](21-mejoras-integrales-btc-edu.md), con evidencia propia de cada entrega.

## Alcance y evidencia

Revisión realizada el 12 de octubre de 2026 sobre el espacio de desarrollo en `main`, con base Git `4000ed5` y cambios locales de perfiles, comunidad y catálogo editorial. La documentación se conserva en un worktree de `business/teorica`; el checkout principal y sus cambios concurrentes no se sustituyeron. Las referencias a archivos y funciones de código identifican la implementación analizada en `main`, no el código anterior de la rama documental.

Se revisaron rutas, modelos, reglas de autorización, servicios, plantillas, JavaScript, pruebas, documentación de producto y los dos originales de CUBO+. Se recorrieron inicio, catálogo, acceso, biblioteca, lección y comunidades en el navegador integrado con una base temporal. Comunidad y menú se observaron también a 390 × 844. El estudio, pagos, evaluaciones, certificados, preguntas y perfiles se contrastaron con su implementación y pruebas; no se afirma haber recorrido manualmente todos sus estados en navegador.

El repositorio estaba cambiando durante el análisis. Para hacer reproducible la regresión se conservó una instantánea de 341 archivos de `src`, excluyendo entornos, bases y secretos. Sobre esa copia pasaron **227 pruebas en 100,047 segundos**. La huella SHA-256 del manifiesto es `a34420a7479467f316a82923dc34726ddfe195aeace392bd8b62c6447f1eb834`. Una ejecución anterior sobre el checkout también pasó 227 pruebas. [Salida de la ejecución sobre la instantánea](evidencias/2026-10-12-pruebas-analisis-integral.txt).

Se hicieron comprobaciones adicionales con cuentas y contenidos sintéticos en otra base temporal. Sus resultados distinguen comportamientos presentes de brechas: la búsqueda comunitaria sí encuentra respuestas visibles; abrir un recurso gratuito no lo añade a la biblioteca; el registro pierde el destino; catálogo y perfil pueden mostrar nombres de creador diferentes; el tema de un recurso publicado cambia desde su borrador. [Resultados de las comprobaciones](evidencias/2026-10-12-comprobaciones-analisis-integral.json).

La base principal se consultó mediante SQLite en modo de solo lectura. Al cierre de esa consulta había seis cursos publicados, sin tutoriales, videos, materiales independientes ni referencias externas. Las nuevas migraciones de perfiles y seguimiento ya estaban aplicadas. No se añadieron contenidos, cuentas, compras, mensajes ni migraciones a esa base desde esta revisión. Las adiciones observadas durante el trabajo corresponden a cambios concurrentes.

No se hicieron entrevistas ni sesiones externas, una auditoría completa WCAG, pruebas de carga, una nueva compra contra LNbits o una prueba con fondos reales. Las conclusiones de experiencia son un diagnóstico de diseño e implementación. Las propuestas necesitan verificación y algunas requieren investigación con personas.

## Diagnóstico

BTC.EDU ya tiene componentes de una plataforma educativa integral: descubrimiento, contenido, continuidad, evaluación, certificación, acompañamiento, comunidad, identidad, creación, comercio y administración. Su fortaleza es conservar reglas, permisos y evidencia histórica. La publicación versionada, los derechos permanentes, la corrección en servidor y la moderación auditada resuelven problemas importantes.

La experiencia sigue organizada principalmente alrededor del curso. Los tutoriales reutilizan su estructura; la comunidad depende de sus versiones; las evaluaciones, preguntas y certificados se originan en sus lecciones; la biblioteca reúne inscripciones y recursos comprados. Falta un recorrido que conecte el objetivo de una persona con los distintos formatos, la práctica, la ayuda y el siguiente paso.

La colección local refuerza esa concentración: tiene seis cursos, 24 lecciones, seis comprobaciones finales y seis políticas de certificado. Son textos introductorios sobre Bitcoin, wallets, Lightning, facturas, LNbits y acceso mediante micropagos. Incluyen explicación, ejemplo, práctica y solución. Hay 15 lecciones gratuitas y nueve pagadas, con doce ofertas activas. Los precios y duraciones son hipótesis; la publicación técnica no representa una revisión educativa independiente ni resultados de aprendizaje.

El siguiente avance debería cerrar conexiones entre apartados y producir contenido pertinente para cada formato. Añadir más entradas al menú no resolvería por sí solo esta brecha.

## Apartados existentes

### Inicio y exploración

El inicio presenta cursos, tutoriales y recursos, pero su botón «Explorar contenido» dirige a Cursos. Su catálogo también se construye con `catalog_context({}, "cursos")`. «Explorar todo» existe en otra ruta y permite combinar tipos de contenido. La diferencia entre lo anunciado y el destino está confirmada en código y navegador.

Conviene que la acción principal abra la exploración completa, con accesos visibles a aprender un tema, resolver una tarea, encontrar un material y participar. Para una cuenta activa, el inicio puede priorizar continuar y mostrar ayuda pendiente. Una selección «Empieza aquí» debe tener criterio editorial explícito; no requiere un algoritmo de recomendación.

Evidencia: `core.views.home`, `core.views.explore`, `templates/core/home.html`, `templates/base.html`. Aceptación propuesta: una persona que busca un tutorial o recurso llega a su categoría desde la acción principal y puede volver sin perder filtros.

### Catálogo y búsqueda

Se pueden combinar búsqueda, tema, nivel, acceso y formato, con resultados paginados y filtros en la URL. Volver desde una ficha conserva contexto. Las etiquetas de contenido mixto evitan presentarlo como completamente gratuito. Son bases útiles que conviene conservar.

La búsqueda consulta títulos y descripciones, sin objetivos, requisitos o contenido de las lecciones. El orden es alfabético y no expresa pertinencia educativa ni actualización. Un nivel seleccionado en la exploración general excluye videos, materiales y referencias, porque esos modelos no tienen nivel. Ese comportamiento debe explicarse o adaptar los filtros al formato. La paginación ocurre después de reunir todos los resultados en Python; es una limitación de crecimiento, sin medición de carga que permita cuantificarla.

Mejoras: buscar por objetivos y tareas; mostrar qué filtros aplican; añadir orden editorial o por publicación; contextualizar los precios «Desde» según la unidad ofertada; mostrar acceso adquirido cuando corresponda. Antes de introducir búsqueda especializada, medir consultas y tiempo con un catálogo mayor.

Evidencia: `content.catalog.catalog_context`, `templates/core/_filters.html`, `templates/core/_card.html`. Aceptación: resultados pertinentes y explicables, filtros que no hagan desaparecer formatos sin una explicación, y precio cuya unidad se comprenda.

### Selector

El selector agrupa cursos por nivel y tema, permite comparar una ficha y conserva la selección en la URL. No contiene un plan de aprendizaje, relaciones de prerrequisito ni conexiones con tutoriales o materiales. La frase «Una ruta para lo que viene» puede sugerir más orientación de la que ofrece.

Recomiendo describirlo como comparación mientras conserve esa función, y añadir después rutas editoriales separadas. Una ruta debe indicar objetivo, conocimientos previos, contenidos de distintos formatos, práctica y criterios de avance. El primer recorrido puede ser sencillo y manual, por ejemplo comprender unidades de Bitcoin, interpretar una factura y revisar un flujo de micropagos.

Evidencia: `core.views.course_selector`, `templates/core/selector.html`. Aceptación: el alumno distingue comparar cursos de seguir una ruta, sabe por qué un contenido viene antes que otro y puede salir del plan sin perder lo aprendido.

### Cursos y fichas

La ficha muestra objetivo, requisitos, nivel, duración, temario, acceso y ofertas. Las publicaciones congelan contenido y requisitos; las compras anteriores conservan su revisión. Esta protección es una de las fortalezas del proyecto.

El control de publicación permite objetivos y requisitos vacíos, aunque la ficha anuncie «Qué aprenderás» y «Antes de empezar». Se reprodujo una publicación sin esos campos. La ficha calcula su botón de estudio a partir de la primera lección accesible; la lógica que retoma el avance está en la biblioteca y no se reutiliza aquí. El temario sigue mostrando «De pago» aunque el alumno tenga acceso, y no presenta todos los estados educativos pendientes en la misma vista.

Mejoras: criterios editoriales mínimos; objetivos observables; una acción de continuar consistente entre ficha y biblioteca; temario con completada, pendiente, evaluación y acceso adquirido; diferencias entre versiones cuando sean útiles. Conservar la versión histórica y permitir cambiar explícitamente, sin trasladar notas o progreso por simple semejanza del título.

Evidencia: `content.publication.prepare_course`, `content.version_views.course_version_detail`, `templates/content/course.html`, `learning.views.library`. Aceptación: no se publica una ficha que carezca de información educativa mínima y continuar tiene el mismo destino desde cualquier entrada.

### Tutoriales

Tienen catálogo propio en filas, tema, nivel y duración. Su modelo es `Course` con `kind="tutorial"`; usan la ficha, capítulos, inscripción y progreso del curso. Reutilizar permisos y aprendizaje evita mantener dos sistemas distintos.

La presentación aún habla de curso, temario y capítulos, incluso cuando la intención es resolver una tarea corta. En la base local consultada no hay tutoriales. Su debilidad actual combina falta de contenido con una experiencia poco diferenciada.

Cada tutorial debería comenzar con «qué vas a conseguir», herramientas y requisitos, pasos, un resultado comprobable y errores frecuentes. Puede tener una o varias lecciones, guardarse y enlazarse con un curso que explique los fundamentos. Compartir infraestructura no impide adaptar lenguaje y presentación al formato.

Evidencia: `content.models.CourseKind`, `templates/core/_tutorial_row.html`, `templates/content/course.html`. Aceptación: terminar un tutorial permite comprobar una tarea concreta y ofrece un siguiente recurso útil, sin obligar a recorrer un curso completo.

### Recursos y referencias

El apartado distingue videos, materiales y enlaces externos. Los archivos propios usan revisiones protegidas, y los externos muestran su fuente y condiciones. Hay reproducción, subtítulos VTT, transcripción y descarga cuando se han preparado esos materiales. No se observaron videos, materiales o referencias publicados en la base principal consultada.

Un recurso gratuito puede abrirse sin cuenta, pero no puede guardarse en la biblioteca personal con la misma facilidad que uno comprado. Falta relacionar un recurso con las lecciones o problemas que ayuda a resolver, y falta información estructurada de autoría, licencia, idioma y revisión editorial. Los enlaces de profundización del catálogo están incorporados al texto; eso no equivale a referencias catalogadas y mantenidas. Las referencias externas no tienen un formulario equivalente en el estudio del creador.

También se reprodujo una brecha de publicación: `ResourceVersion` conserva título, descripción, acceso y archivo, pero no tema. El catálogo filtra `Video.topic` o `Material.topic`, que pertenecen al borrador. Cambiar ese tema cambia inmediatamente la clasificación pública sin aprobar una nueva revisión. Conviene congelar los metadatos públicos o separar explícitamente una reclasificación editorial auditada.

Evidencia: `content.models.StandaloneResource`, `ResourceVersion`, `ExternalReference`, `content.catalog.catalog_context`, `content.views.resource_detail`. Aceptación: guardar no concede permisos comerciales; el recurso mantiene su referencia histórica; editar un borrador no altera silenciosamente lo publicado.

### Mi aprendizaje

La biblioteca conserva inscripciones, versiones, porcentaje de lecciones completadas, continuación, acceso a certificados y recursos adquiridos, incluidos los de paquetes. La lógica de continuación busca una lección pendiente y accesible. Se comprobó la coexistencia de dos versiones y de un material comprado con datos temporales.

Sigue siendo una biblioteca de cursos y compras. No reúne recursos gratuitos guardados, objetivos personales, notas, tareas pendientes, dudas sin resolver o conversaciones seguidas. Una persona que estudia únicamente con recursos gratuitos no obtiene una biblioteca comparable. La clasificación por cursos y tutoriales tampoco ofrece filtros de en curso, terminado o archivado.

Recomiendo convertir este apartado en el centro del aprendizaje: continuar, pendientes relevantes, biblioteca de todos los formatos y repaso. El guardado de un enlace o material debe conservar su procedencia, sin aparentar compra. Las notas privadas deben asociarse al recurso o versión para no perder contexto en una actualización.

Evidencia: `learning.views.library`, `learning.models.Enrollment`, `templates/core/workspace.html`; comprobación de recurso gratuito en el archivo de evidencias. Aceptación: el alumno recupera un curso, un tutorial, un recurso gratuito y uno adquirido desde el mismo espacio, con derechos y progreso correctos.

### Lecciones y práctica

El lector protege el cuerpo y los adjuntos en servidor, ofrece temario, navegación, evaluación, progreso y pregunta al creador. Abrir guarda la lección de continuación; completar exige una acción del alumno y aprobación del cuestionario obligatorio. El reproductor no conserva segundos de video. Texto y transcripción se presentan como párrafos mediante `linebreaks`.

La práctica del catálogo actual se resuelve fuera de un registro de evidencias: el estudiante lee el ejercicio y su solución y después puede marcar completada la lección. No hay entregas, rúbricas, revisión de un proyecto o repaso programado. Tampoco hay entrada contextual directa a la comunidad de esa versión desde la lección. No conviene confundir estas ausencias con un fallo de autorización: son brechas del recorrido educativo.

Primero separaría explicación, ejercicio y solución visualmente y conectaría pregunta privada, conversación compartida y repaso. Después añadiría una entrega pequeña por recorrido, con criterios claros y retroalimentación. Si se incorporan ejemplos de código, el lector necesita bloques que conserven indentación; el formato de párrafo actual no la garantiza.

Evidencia: `templates/content/lesson.html`, `templates/content/_media.html`, `static/js/learning.js`, `learning.services.save_progress`, `content.editorial_catalog`. Aceptación: el alumno sabe qué practicar, puede comprobarlo y entiende qué registra una marca de finalización.

### Evaluaciones

La plataforma corrige selección única y múltiple en servidor, mantiene reglas por versión, permite guardar y retomar, controla intentos y espera y conserva resultados. Las soluciones no se exponen en el formulario del alumno. Los intentos adicionales tienen motivo y registro. Son fortalezas técnicas.

El sistema solo evalúa respuestas cerradas, con igual peso y coincidencia exacta en selección múltiple. La política de mostrar soluciones solo tras aprobar puede dejar sin orientación a quien más ayuda necesita; es una decisión pedagógica por revisar, no una vulnerabilidad. Se guardan respuestas al pulsar un botón, sin autoguardado del intento.

La colección actual tiene una sola pregunta final por curso, nota mínima de 100 y tres intentos. El importador coloca la respuesta correcta en la primera opción de las seis preguntas. Completar cuatro lecciones y acertar una pregunta acredita esas condiciones, pero proporciona evidencia muy limitada de comprensión y aplicación. No demuestra dominio completo de Bitcoin o Lightning.

Mejoras: comprobaciones formativas con explicación y vínculo al contenido que conviene repasar; separar práctica de evaluación para certificado; cubrir objetivos con varias preguntas o una tarea; diversificar posiciones de respuesta y definir cualquier aleatoriedad de forma reproducible por intento. Una evaluación más larga tampoco sustituye una revisión de su validez.

Evidencia: `learning.assessment_services`, `learning.quizzes`, `templates/learning/quiz.html`, `content/management/commands/load_editorial_catalog.py`. Aceptación: cada objetivo tiene evidencia correspondiente y un error orienta al siguiente paso educativo.

### Certificados

Se exige cumplimiento de requisitos por versión; comprar no basta. Las credenciales conservan nombre, curso, emisor, fecha y evidencia, con PDF privado, compartición voluntaria, revocación y huella SHA-256. La verificación no publica respuestas o notas. El diseño histórico evita cambios retroactivos.

Faltan corrección o sustitución de una credencial emitida, un recorrido operativo para solicitarla y representación de competencias o trabajos. La huella permite comparar integridad con el registro de BTC.EDU; no es una firma del emisor ni un registro en Bitcoin. La identidad del titular se confirma por el nombre que introduce, sin verificación independiente. Estas condiciones deben formar parte de la interpretación del certificado.

Priorizaría la corrección con trazabilidad y la correspondencia entre criterios educativos y evidencia. Portabilidad mediante estándares puede evaluarse después. El perfil público y el certificado deben seguir teniendo decisiones de compartición independientes.

Evidencia: `learning.certificates`, `learning.certificate_integrity`, `templates/learning/certificate_request.html`, `templates/learning/certificate_verify.html`. Aceptación: nombre corregido mediante una sustitución relacionada con el original; ninguna edición altera la credencial histórica o presenta la huella como autenticidad criptográfica independiente.

### Preguntas privadas

El alumno inscrito con acceso pregunta desde la lección; solo el participante y el creador aprobado consultan la conversación. Hay controles de frecuencia, CSRF e idempotencia. La bandeja distingue si espera al creador. Esta función resuelve dudas que no conviene compartir en comunidad.

No ofrece cierre o marca de resuelta, filtros por estado, búsqueda, plazo de atención ni un mecanismo para reasignar soporte. Abrir la conversación tampoco ofrece un retorno directo destacado a la lección. Un promedio de primera respuesta no informa cuántas dudas siguen sin resolver.

La cuenta editorial institucional de los seis cursos no tiene contraseña utilizable. El módulo puede recibir preguntas dirigidas a esa cuenta, pero la carga de contenido no asigna una persona capaz de atenderlas por el estudio. Antes de invitar a alumnos, hay que resolver ese responsable o dejar claras las condiciones de atención. La publicación técnica no acredita acompañamiento disponible.

Evidencia: `learning.support`, `learning.essential_views.questions_context`, `templates/learning/_question.html`, `content/management/commands/load_editorial_catalog.py` y documentación de catálogo del 12 de octubre. Aceptación: cada contenido que ofrece preguntas tiene un responsable habilitado, y el alumno puede identificar resolución, demora y siguiente vía de atención.

### Comunidad y moderación

Existen espacios por versión para inscritos y el creador aprobado, con conversaciones, respuestas, búsqueda en mensajes y respuestas visibles, filtros, orden por actividad, seguimiento y avisos internos. No hace falta comprar todas las lecciones para participar. Los permisos de comunidad no conceden contenido pagado. Ocultación, cierre y suspensión conservan motivo e historial; suspender escritura conserva lectura y aprendizaje.

La búsqueda y el seguimiento recién incorporados están presentes y no deben listarse como pendientes. La limitación es de organización: publicar otra versión abre otro espacio, fragmentando conversaciones útiles. La comunidad de un curso tampoco proporciona un lugar para aprender entre personas que consultan tutoriales o materiales independientes.

Faltan títulos de conversación, temas, vínculos opcionales a la lección, mensajes fijados, respuesta marcada como solución y apelación practicable. La interfaz indica contactar al creador para revisar una suspensión, pero no ofrece un canal específico de revisión. El autor inicial recibe avisos de respuestas sin preferencia de desactivación.

Recomiendo conservar los espacios históricos y añadir, cuando se definan permisos y moderadores, comunidades por tema. Una referencia entre versiones debe mostrar su procedencia y respetar el acceso original; no hay que mover ni fusionar conversaciones privadas automáticamente. Usar conversaciones útiles para mejorar contenido requiere consentimiento cuando proceda y revisión del creador, sin publicar preguntas privadas por defecto.

Evidencia: `learning.community`, `learning.community_views`, `learning.models.CommunitySubscription`, `templates/learning/_community_space.html`. Aceptación: encontrar una respuesta por tema sin filtrar mensajes restringidos; resolución visible; reporte y revisión de una decisión con responsable e historial.

### Personas y perfiles

Los estudiantes eligen alias, presentación, intereses y sitio; el perfil se mantiene privado salvo elección explícita. El directorio requiere sesión, permite filtrar y buscar, y distingue estudiantes de creadores aprobados. La ficha del creador utiliza su perfil aprobado y catálogo. Los mensajes enlazan perfiles compartidos sin mostrar correo o nombre privado del estudiante.

El directorio ayuda a descubrir personas, pero aún no conduce a colaborar en una actividad. No hay propuestas de proyecto, grupos de estudio, seguimiento de personas o historial público voluntario de aportes. El interés es texto libre, sin conexión estructurada con los temas del catálogo. El alias no es una identidad verificada y puede repetirse; la interfaz debe evitar insinuar lo contrario.

Se reprodujo una inconsistencia: cambiar el nombre público del creador no cambia el nombre que muestra la tarjeta de catálogo. El catálogo y las fichas de recursos usan `get_full_name()`, mientras el perfil y las publicaciones de cursos pueden usar `CreatorProfile.display_name`. Debe adoptarse una identidad pública coherente, respetando cuándo el nombre se conserva históricamente.

Priorizar identidad y conexiones a comunidades pertinentes. Fotografías, mensajes directos o reputación añaden almacenamiento y moderación; no son condiciones previas para que este apartado tenga utilidad educativa. Los datos de compras, notas, preguntas privadas y certificados no deben volverse públicos por activar el perfil.

Evidencia: `accounts.models.User.public_name`, `accounts.views.members`, `content.catalog.catalog_context`, `content.views.resource_detail`, `content.publication.prepare_course`. Aceptación: presentación pública consistente y participación pertinente, con una elección independiente para cada tipo de información compartida.

### Cuentas y recuperación

Estudiante, creador y administración son identidades independientes. Correo y contraseña, recuperación por espacio y autorización en servidor están implementados. El mismo correo puede identificar cuentas diferentes según el tipo. La advertencia `auth.W004` de las pruebas corresponde al correo no único por sí solo; el backend aplica el tipo de cuenta y la restricción es correo/tipo. No se registra esa advertencia como un fallo confirmado de aislamiento.

El registro pierde el destino desde una oferta o lección: el enlace «Crear cuenta» no conserva `next` y `register` devuelve al espacio personal. El login conserva algunos destinos, pero su lista no incluye Personas. No hay verificación de correo o controles específicos de frecuencia en login y recuperación en los archivos revisados. La recuperación tiene lógica de token, pero su entrega pública depende de completar correo operativo.

Corregir el retorno después del registro con destinos permitidos; explicar el espacio activo; verificar correo antes de confiar en esa identidad; completar correo y límites de solicitudes para operación pública. Se conservan las cuentas separadas, decisión explícita del proyecto; cualquier vinculación futura requiere diseño y elección del usuario.

Evidencia: `accounts.views.register`, `StudentLoginView.get_redirect_url`, `accounts.recovery`, `accounts.backends.AccountBackend`, `platform_config.settings`. Aceptación: el registro regresa a la oferta elegida sin abrir redirecciones arbitrarias, y la recuperación llega al destinatario del espacio correcto.

### Notificaciones

Los avisos persisten por destinatario y clave de acontecimiento; abrir es POST protegido y conserva la primera lectura. El contador aparece en la navegación. Hay avisos de preguntas, respuestas, revisión, intentos, credenciales y comunidad.

La bandeja ofrece títulos genéricos y fecha, sin mostrar claramente curso o conversación antes de abrir. No tiene filtros, lectura conjunta, preferencias o resumen. Una persona puede recibir avisos útiles, pero le cuesta decidir qué necesita atención. Son avisos internos, sin correo ni push.

Añadir contexto, filtros por estado y tipo, y preferencias por conversación. Mantener al alcance los avisos que requieren una acción sobre acceso o certificado. Considerar resúmenes de correo solo cuando estén resueltos consentimiento, entrega y responsable. Medir lectura no demuestra resolución de una duda.

Evidencia: `learning.support.notify`, `learning.essential_views.notifications`, `templates/learning/_notifications.html`. Aceptación: distinguir una respuesta, una revisión y una incidencia sin abrir avisos uno por uno; un cambio de preferencia no afecta permisos educativos.

### Compras, ofertas y pagos

La aplicación congela precio e inclusiones de la factura, concede derechos en servidor y evita duplicados. Explica el acceso permanente a lo incluido y ofrece componentes faltantes cuando ya existe una compra parcial. Hay pagos controlados con FakeWallet o regtest, QR, enlace a wallet y consulta silenciosa en el recorrido externo. La conciliación supervisada puede continuar sin la pantalla abierta.

El conjunto de opciones puede resultar complejo para una persona que solo quiere aprender. Las etiquetas del contenido no siempre se adaptan a lo ya adquirido. Un pago tardío o una confirmación conflictiva conserva evidencia y no concede derechos, pero la pantalla no ofrece un proceso de atención con responsable, estado y resolución. «Consulta esta factura» no resuelve por sí solo una incidencia.

Recomiendo explicar el acceso desde la necesidad educativa y destacar solo alternativas pertinentes, respetando la regla vigente de componentes faltantes y sus precios. Antes de una operación real deben existir procedimientos de pago tardío, reclamación y eventual devolución, además de servicio supervisado y alertas. No es necesario introducir fondos reales para cumplir el reto oficial de CUBO+.

Evidencia: `commerce.views`, `commerce.offers`, `commerce.services`, `templates/commerce/offer.html`, `templates/commerce/invoice.html`. Aceptación: el alumno explica qué recibe y lo encuentra al volver; cada incidencia tiene una siguiente acción concreta. Mantener precios como cantidad y sats, y la comprobación normal silenciosa.

### Estudio de creadores

Permite solicitud y aprobación, perfil, curso o tutorial, capítulos, lecciones, archivos, recursos, evaluación, requisitos de certificado, vista previa y envío editorial. El autor puede trabajar otro borrador mientras se revisa una composición congelada. Ofertas, preguntas, estadísticas y comunidad tienen entradas en el estudio.

La creación tiene pasos distribuidos: subir archivo, preparar recurso, publicarlo, adjuntarlo, publicar curso y preparar ofertas. Reordenar capítulos o lecciones exige números libres. Faltan un diagnóstico de preparación, criterios pedagógicos por formato y un resumen de qué falta atender. El panel de contenido no integra preguntas pendientes, reportes o incidencias para organizar el trabajo diario.

Mejoras: recorrido guiado y reutilizable por formato, mover arriba/abajo con controles accesibles, comprobaciones de publicación y una bandeja de atención. La guía debería recomendar objetivo, ejercicio, respuesta esperada, derechos y accesibilidad. No todo defecto editorial tiene que convertirse en un bloqueo automático; los requisitos mínimos sí deben ser explícitos.

Evidencia: `creators.forms`, `creators.views`, `templates/creators/course.html`, `templates/creators/dashboard.html`, `templates/creators/base.html`. Aceptación: un creador prepara y mantiene un tutorial o recurso además de un curso, y sabe qué publicar o atender sin recorrer varias secciones.

### Revisión editorial y administración

La administración revisa composiciones, ofertas y creadores, consulta indicadores y puede moderar con permisos específicos. La aprobación publica exactamente lo enviado. Las observaciones y decisiones conservan responsable y fecha. La administración convencional de Django permite inspeccionar entidades.

No hay una bandeja operativa que reúna revisión, reportes, pagos anómalos, dudas institucionales y correcciones de certificados. La revisión pide comprobar derechos, accesibilidad y claridad, pero el modelo no registra una lista de criterios o la evidencia de derechos por archivo. Una aprobación técnica o una carga institucional no equivale a revisión pedagógica experta.

Recomiendo definir criterios mínimos y una cola de atención por prioridad y antigüedad, con responsables. Antes de ampliar permisos para ayudar al alumno, diseñar el acceso a soporte privado: los administradores no deben obtener lectura general de preguntas privadas solo por conveniencia del panel.

Evidencia: `creators.services.decide`, `creators.admin`, `templates/creators/review.html`, `core.analytics_views.admin_analytics`. Aceptación: toda incidencia tiene dueño y cierre verificable; la revisión registra qué se comprobó sin ampliar privacidad implícitamente.

### Estadísticas

Los paneles muestran periodo, cohortes y denominadores; distinguen transacciones de permisos y «Sin datos» de cero. Cubren compra, acceso, regreso, inscripciones, aprobación, certificados y primeras respuestas. Los permisos separan creador y administración.

Se observa actividad educativa, pero no resultados de una tarea o transferencia de conocimiento. Faltan recorridos de tutoriales y recursos gratuitos, guardados, repetición de práctica, resolución de preguntas, salud de comunidad y demoras pendientes. El promedio de primera respuesta incluye preguntas respondidas y necesita acompañarse de la cantidad y antigüedad de las pendientes. Las cohortes muestran estado actual, no necesariamente el resultado observado al terminar el intervalo.

También conviene revisar el significado de «oferta vista»: `offer_views` registra ofertas al renderizar fichas, aunque la persona no se desplace hasta ellas. La conversión usa ese evento, por lo que debe interpretarse como oferta presentada en una página, o medirse visibilidad real con un contrato distinto. No renombrar retrospectivamente eventos como si se hubieran observado de otra forma.

Propuesta: añadir métricas por objetivo y formato, criterios de resolución y cohortes comparables. Una comprobación diferida o un trabajo evaluado puede aportar evidencia educativa, con consentimiento y contexto. La cantidad de eventos no demuestra aprendizaje ni demanda.

Evidencia: `core.analytics.dashboard_data`, `core.telemetry.offer_views`, `templates/core/_analytics.html`. Aceptación: cada indicador conduce a una decisión y explica fuente, cobertura y denominador; la plataforma no atribuye dominio al simple consumo.

## Aspectos transversales

### Navegación y continuidad

La navegación conserva los apartados existentes, pero reúne once enlaces de «Tu espacio» con similar jerarquía. En móvil exige desplazarse dentro del menú. Inicio cambia a otro marco de navegación y varias pantallas de comunidad, perfiles, preguntas y avisos no señalan una sección activa propia. La ficha del curso, el lector y la biblioteca distribuyen de forma distinta continuar, ayuda, progreso y acceso.

Propongo una organización con Explorar, Mi aprendizaje, Comunidad y Personas como entradas principales, con compras, certificados, preguntas y avisos accesibles desde un espacio personal claro. El estudio conserva su navegación propia. Debe validarse que una agrupación reduce esfuerzo sin esconder acciones que los alumnos utilizan; esta revisión no aporta tiempos observados con participantes.

### Accesibilidad y conexión

Hay etiquetas, salto al contenido, foco visible, estados anunciados, controles de video, opción de subtítulos, navegación móvil y formularios protegidos. La observación a 390 × 844 mostró contenido legible y menú desplazable; no acredita conformidad completa.

La auditoría pendiente debe recorrer teclado, lector de pantalla, zoom y reflujo, contraste, tamaño de controles, errores y regreso tras vencimiento de sesión. Los archivos necesitan su propia revisión. Subtítulos y transcripción son opcionales hoy; la publicación debería definir qué alternativas requiere cada contenido. No basta con que el reproductor admita un archivo VTT.

Los videos usan MP4 con carga de metadatos y sin autoguardado de posición. Ante conexiones limitadas conviene conocer tamaño antes de reproducir, ofrecer texto equivalente y evaluar calidad adaptable si el consumo lo justifica. No se han medido velocidad ni condiciones de conectividad del público salvadoreño en este análisis.

### Operación

La base sigue siendo SQLite para la etapa local, decisión que se conserva. Los controles de concurrencia registrados y las pruebas resuelven escenarios específicos, sin acreditar capacidad para cualquier volumen. El crecimiento exige medir carga, almacenamiento, entrega de archivos y consultas antes de decidir cambios de infraestructura.

Antes de abrir al público faltan responsables de atención, correo efectivo, respaldo y restauración comprobada, instalación y reinicio de conciliación, alertas, revisión de accesos y procedimientos de incidencias. El endpoint de salud comprueba la base, no todos esos componentes. El costo de acceso permanente debe incluir versiones y archivos históricos, consumo gratuito, moderación y acompañamiento. Este informe no fija tarifas, presupuesto o garantías de servicio.

### Documentación y alcance

El documento principal todavía comienza con la compra como problema central. Debe explicar la plataforma educativa integral y conservar los micropagos como una capacidad de acceso. Parte del diseño y de los instrumentos conserva estados anteriores: por ejemplo, el documento de arquitectura del 4 de octubre enumera como pendientes módulos ya entregados después. Se debe diferenciar diseño histórico, implementación actual y evidencia.

Eventos, membresías, mensajería directa, reputación y portabilidad de credenciales son ampliaciones posibles o ya propuestas, según cada documento. No se presentan como apartados implementados ni como requisitos obligatorios del reto. No priorizaría estas ampliaciones por delante de orientación, biblioteca inclusiva, práctica y atención.

## Investigación que sustenta las mejoras

La guía del Institute of Education Sciences distingue actividades con respaldo diferente y recomienda distribuir el estudio, alternar ejemplos con resolución y usar comprobaciones para recuperar contenido. Esto fundamenta probar repaso y práctica dentro del recorrido; no permite asegurar que una interfaz concreta mejore el aprendizaje de BTC.EDU. [IES: organización del estudio](https://ies.ed.gov/ncee/wwc/PracticeGuide/1).

CAST propone retroalimentación relevante, específica y orientada a acciones para avanzar hacia un objetivo. Aplicamos ese criterio a los cuestionarios y al acompañamiento: un resultado debería sugerir qué revisar o intentar después. Es una decisión propuesta, sin resultados locales que acrediten eficacia. [CAST: retroalimentación orientada a la acción](https://udlguidelines.cast.org/engagement/effort-persistence/feedback/).

La documentación oficial de Moodle separa finalización de actividad y planes vinculados a competencias. Sirve de referencia para distinguir haber recorrido contenido de haber cumplido un objetivo, y para plantear rutas que combinen formatos. No se propone replicar todas sus funciones. [Moodle: finalización de actividades](https://docs.moodle.org/503/en/Activity_completion), [Moodle: planes de aprendizaje](https://docs.moodle.org/503/en/Learning_plans).

WCAG 2.2 proporciona criterios verificables para acceso por teclado, foco, reflujo, autenticación, errores y controles. El criterio de tamaño mínimo considera 24 × 24 píxeles CSS o condiciones de separación y sus excepciones; no se exige indiscriminadamente una medida a todo enlace. Esta referencia permite diseñar una auditoría, sin declarar conformidad de las pantallas revisadas. [W3C: WCAG 2.2](https://www.w3.org/TR/WCAG22/), [W3C: tamaño de controles](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum).

Open Badges 3.0 permite representar logros y verificar credenciales mediante un estándar. Es una opción posterior para portabilidad; una huella SHA-256 del registro actual no convierte el certificado en una credencial compatible. Antes de integrar el estándar hay que definir emisor, criterios, evidencia, identidad y revocación. [1EdTech: Open Badges 3.0](https://standards.1edtech.org/open-badges/specifications/standards/v3p0).

Los originales de CUBO+ requieren descubrir contenido, explicar muestras y precios, verificar pagos simulados, mantener acceso y medir actividad. La plataforma integral complementa ese recorrido. Una mejora educativa no sustituye su prueba de micropago a desbloqueo; tampoco se necesita una transferencia real para cumplirlo.

## Prioridades propuestas

### Primero: coherencia y atención

Corregir registro con retorno seguro, identidad pública del creador y metadatos de recursos que cambian desde el borrador. Unificar continuar entre ficha y biblioteca. Establecer un responsable real de preguntas y moderación institucional, y una vía de atención de incidencias. Actualizar el relato del documento principal y precisar qué acredita cada certificado. Son cambios concretos y verificables antes de ampliar el producto.

Aceptación conjunta: una persona llega desde una oferta, crea su cuenta y vuelve a ella; reconoce al mismo autor; una edición pendiente conserva clasificación pública; retoma su lección desde cualquier entrada; puede obtener una respuesta o una siguiente vía de ayuda real.

### Después: completar el recorrido integral

Preparar un tutorial útil, un recurso propio y una referencia externa revisada que se relacionen con la colección actual. Añadir guardados gratuitos, biblioteca con filtros y un primer objetivo o ruta editorial. Conectar lección, práctica, pregunta privada y comunidad sin confundir sus permisos. Añadir resolución de dudas y retroalimentación que indique acciones.

Aceptación conjunta: el alumno completa una tarea combinando formatos, conserva lo gratuito y lo adquirido, pide ayuda en el lugar apropiado y puede explicar qué consiguió. Se verifica primero con datos controlados y después mediante tareas observadas con participantes.

### Luego: evidencia educativa y operación

Ampliar la comprobación de objetivos con preguntas bien diseñadas o entregas; incorporar un repaso diferido apropiado al contenido. Revisar criterios y sustitución de certificados. Completar correo, preferencias, apelaciones, atención de pagos, respaldo/restauración y supervisión. Auditar accesibilidad y medir carga. Los datos de actividad deberían registrar estas decisiones con cobertura explícita.

Aceptación conjunta: la evaluación corresponde al objetivo, quien falla encuentra ayuda, las incidencias se resuelven y la operación puede recuperarse de fallos comprobados. Pasar pruebas unitarias sigue siendo necesario, pero no cierra esos resultados por sí solo.

### Ampliaciones posteriores

Evaluar comunidades por tema, grupos de proyecto, eventos, membresías y credenciales portables según necesidad demostrada y capacidad de mantenimiento. La continuidad del acceso, la privacidad y la historia no se sacrifican al añadirlas. No se asignan fechas o esfuerzo sin definir alcance, responsables y dependencias.

## Validación propuesta

El plan existente de entrevistas y usabilidad puede ampliarse con tareas de plataforma: aprender una necesidad con distintos formatos; guardar un recurso gratuito y recuperarlo; distinguir pregunta privada de conversación; encontrar ayuda sin saber el nombre del curso; interpretar progreso y certificado; publicar un tutorial y atender una duda desde el estudio.

Registrar si cada tarea se completó sin ayuda, con ayuda o no se completó; dificultades, contexto, versión, interpretación del acceso y evidencia disponible. Observar especialmente personas que usan solo recursos gratuitos, principiantes en Bitcoin/Lightning, alumnos con metas puntuales y creadores con tiempo limitado para atención. Priorizar El Salvador conforme al contexto del proyecto, sin asumir necesidades solo por país.

Para resultados educativos, definir antes una tarea ligada al objetivo y una comprobación posterior apropiada. Conservar casos que contradigan las hipótesis. Una mejora de navegación, una declaración de satisfacción o una compra simulada no acredita por sí sola aprendizaje, intención de pago real ni sostenibilidad.

## Decisión recomendada

Conservar la base de publicación, derechos, identidad separada y auditoría. Usar las siguientes entregas para que una persona pueda orientarse, estudiar con distintos formatos, practicar, pedir ayuda, participar y volver con continuidad. El valor integral debe reconocerse en esos recorridos y en su contenido, además de estar descrito en la documentación.
