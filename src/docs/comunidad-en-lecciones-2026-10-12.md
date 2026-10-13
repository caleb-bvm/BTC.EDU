# Comunidad en cada lección

## Estado de la feature

El lector de lecciones publicadas incorpora «Conversación de esta lección» al final, después de contenido, progreso, consulta privada y navegación. Los estudiantes inscritos con acceso pueden comentar y responder. El creador aprobado responde en sus cursos y conserva la moderación. Las preguntas privadas no se convierten en comentarios públicos y participar no es requisito de progreso.

Comunidad y el lector muestran los mismos `CommunityPost`. La nueva referencia opcional `lesson` identifica una `VersionLesson`; las respuestas heredan la lección de su raíz y el modelo comprueba que lección, versión y raíz coincidan. Los temas generales anteriores tienen `lesson = NULL`; no se reclasifican ni trasladan al publicar otra versión.

## Acceso y avisos

La inscripción de la misma versión es necesaria para leer, escribir y seguir. Las conversaciones de una lección de pago también requieren acceso a su texto. Comprar un video o material asociado no concede automáticamente ese acceso. Los visitantes y estudiantes no inscritos ven una invitación, sin mensajes.

Los permisos se aplican en lectura directa, publicaciones, respuestas, seguimiento, reportes, búsqueda y recuentos. El filtrado precede a la búsqueda y paginación; se excluyen las respuestas ocultas de resultados y actividad para estudiantes. El creador de ese curso y la administración con permiso específico conservan su acceso de moderación.

Un comentario inicial de lección genera un aviso interno al creador, salvo cuando él es el emisor. Las respuestas avisan al autor inicial y a seguidores autorizados, excluyendo al emisor y comprobando nuevamente acceso a la lección. Las claves únicas de mensajes y avisos conservan idempotencia. No se envían mensajes por correo ni se avisa a todos los inscritos.

Los avisos utilizan el servicio común `notify`; las preferencias de comunidad incorporadas en la entrega paralela de cuentas se aplican también a las claves `community-lesson:` y `community-reply:`. El envío de comentarios no depende de aceptar avisos.

## Interfaz y recorrido

Se muestran cinco conversaciones por página, de más reciente a más antigua, y hasta tres respuestas recientes por conversación, ordenadas cronológicamente dentro de ese extracto. El historial completo permanece paginado de veinte en veinte en la vista de conversación. El envío y el seguimiento regresan al comentario y su página. Los reportes iniciados desde el lector también regresan allí; las decisiones de moderación conservan su página de historial.

Las validaciones conservan el texto y el UUID del envío. Un formulario de respuesta tiene identificadores propios; los controles de avance no reciben los envíos comunitarios. Los mensajes se escapan y solo se aceptan cambios mediante POST con CSRF. Se conservan límites por hora, cierre, ocultación y suspensiones. Las redirecciones construyen rutas internas a partir del registro, sin aceptar una URL arbitraria enviada por el usuario.

Alumno: abrir una lección accesible de su inscripción → leer → comentar o desplegar Responder → enviar → consultar el mismo hilo desde Comunidad o seguirlo para recibir avisos. La acción «Preguntar al creador» explica que la consulta es privada.

Creador: consultar el aviso de comentario nuevo o entrar a Comunidad → abrir conversación con el contexto de lección → responder → volver a la lección. Los filtros existentes permiten localizar conversaciones sin respuestas de ningún participante; no indican solución confirmada ni atención pendiente exclusiva del creador.

## Verificación

El 12 de octubre de 2026 pasaron inicialmente 38 pruebas de comunidad y conversaciones en el espacio compartido. Tras añadir preservación de migración y comprobar paginación de errores y redirecciones, pasaron 57 pruebas en una copia aislada: `learning.test_lesson_discussion`, `learning.test_community`, `learning.test_experience`, `content.test_public_coherence.ResourceTopicMigrationTests` y `content.test_journey.LearningJourneyTests`. La copia evita que ediciones concurrentes cambien el código a mitad de una ejecución; sus datos son ficticios.

La copia incluía modelos de cuentas en desarrollo cuya migración todavía no existía. Se generó esa migración únicamente dentro de la copia para hacer comprobables sus dependencias; no se trasladó al espacio compartido. Esta prueba acredita la integración de conversaciones con ese código aislado, no la conclusión del trabajo paralelo de cuentas. La salida se conserva en `.local/lesson-community-verification-path.txt` y `verification-tests.txt` dentro de la copia.

Al estar disponibles las migraciones paralelas, se repitieron las mismas 57 pruebas en el espacio compartido: todas pasaron en 22,063 segundos. También pasó `makemigrations --check --dry-run`, sin cambios detectados. Diez archivos centrales de conversaciones coincidieron por SHA-256 con la copia verificada; el informe privado está en `.local/lesson-community-source-verification.json`. La evidencia resumida se conserva en [comunidad-lecciones-check-2026-10-12.txt](evidence/comunidad-lecciones-check-2026-10-12.txt).

La comprobación de concurrencia con conexiones SQLite independientes pasó: publicaciones y reportes únicos, decisiones y seguimiento sin duplicados, suspensión frente a escritura, dos envíos simultáneos del mismo comentario de lección y dos respuestas simultáneas del creador. Cada operación idempotente produjo un mensaje y un aviso únicos. Ruff pasó para los archivos funcionales de esta feature.

La revisión de navegador integrado, antes de las modificaciones concurrentes de acceso a cuentas, confirmó login de estudiante, publicación de comentario, respuesta por formulario y seguimiento con regreso al lector y cambio a «Dejar de seguir». Posteriormente se completó login de creador y envío de una respuesta desde el lector en la copia aislada, con la configuración de cuentas actualizada; se confirmó la persistencia y la etiqueta «Creador». Se revisó el modo oscuro en escritorio y viewport de 390 × 844: ancho útil 375 y ancho desplazable 375, sin desbordamiento horizontal. Capturas: [escritorio](evidence/comunidad-leccion-escritorio.jpg), [móvil](evidence/comunidad-leccion-movil.jpg) y [respuesta del creador](evidence/comunidad-leccion-creador.jpg).

La primera revisión general ejecutó 262 pruebas y terminó con una aserción de texto anterior al cambio paralelo del lector y un error en una prueba de migración al introducir una dependencia innecesaria a `content.0005`. La dependencia de esta feature se corrigió a `content.0004`, donde existe `VersionLesson`; las 57 pruebas aisladas incluyen ambos recorridos afectados y pasan. Los intentos posteriores de verificación compartida encontraron nuevos campos de cuentas y creadores aún sin migraciones. La revisión general del conjunto compartido necesita repetirse cuando esas entregas paralelas estén terminadas; no se presenta como aprobada.

## Migración local

Se aplicó únicamente `learning.0008_communitypost_lesson`, con respaldo mediante la API de backup de SQLite. La comparación posterior conservó los 227 registros previos y sus columnas originales en 52 tablas, excluyendo tablas internas de migraciones, permisos y tipos de contenido. Integridad `ok` y cero errores de claves foráneas. No se insertaron comentarios sintéticos en la base principal; el recuento de comentarios ligados a lecciones era cero al terminar la migración.

El informe privado `.local/lesson-community-migration-verification.json` identifica el respaldo y la comparación. La verificación automatizada adicional crea una raíz general cerrada y una respuesta oculta en el esquema anterior; después de migrar conserva todas sus columnas y mantiene nula la referencia a lección.

## Límites y próximos pasos

Esta entrega no incorpora soluciones marcadas, respuestas destacadas, traslado entre versiones, edición de mensajes, archivos, correo ni plazos de atención. Los reportes y decisiones mantienen la política existente. No demuestra utilidad educativa, demanda ni capacidad operativa de moderación. Las tareas con usuarios se añaden a `strategy/16-validacion-con-usuarios.md` y están pendientes de ejecución.

Se deben completar los cambios concurrentes de cuentas y navegación, repetir el verificador integrado y comprobar el recorrido de ambas cuentas sobre la versión efectivamente presentada. El script `scripts/preview-lesson-community.py` usa base temporal, cookies propias y cuentas sintéticas en el puerto 8021; requiere modelos y migraciones consistentes.

## Registro de la entrega

Fecha de ejecución: 12 de octubre de 2026, contexto de El Salvador. Rama observada: `main`; base Git `4000ed5`; cambios locales sin commit. Se conservaron cambios anteriores y concurrentes, sin cambiar de rama ni atribuirlos a esta entrega. Se consultaron los documentos originales de CUBO+: comunidad complementa el aprendizaje y no sustituye el recorrido de pago, la protección de contenido o la validación con usuarios.

La decisión y sus referencias están en [strategy/20-comunidad-en-lecciones.md](../../strategy/20-comunidad-en-lecciones.md). Se actualizó la sección «Comunidad y moderación» del documento principal y su exportación de texto, junto a producto, decisiones, trazabilidad, instrumentos y README.
