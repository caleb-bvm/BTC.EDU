# Comunidad y moderación

Entrega del 10 de octubre de 2026 sobre `main`. Añade conversaciones compartidas, separadas de las preguntas privadas por lección. Los ejemplos y recorridos de verificación utilizan datos temporales.

Implementación guardada en el commit local `3a465c3`. La documentación y evidencia se guardan en otro commit de cierre; no se realizó push.

## Acceso y participación

Cada versión publicada y sellada de curso o tutorial tiene un espacio. Leer y escribir requiere cuenta activa de alumno e inscripción en esa misma versión. Inscribirse no compra contenido: la comunidad no sirve archivos ni textos de las lecciones protegidas. Una nueva publicación tiene otro espacio; los alumnos conservan su comunidad histórica, incluso si el curso se archiva.

El creador aprobado participa y modera únicamente sus cursos. La administración requiere cuenta activa, acceso staff y el permiso `learning.moderate_community` para intervenir en cualquier espacio. Ese permiso permite moderar y leer; no autoriza publicar como alumno ni como creador ajeno. El enlace desde la administración de mensajes lleva a la comunidad y sus controles.

Los nombres se muestran a los participantes; los correos no se incluyen en los mensajes. El texto se escapa en HTML. No se admiten archivos, HTML activo, chat privado ni respuestas anidadas. Cada conversación admite respuestas de un solo nivel. Conversaciones y respuestas se paginan de 20 en 20. Cada cuenta puede publicar hasta 30 mensajes por hora en el conjunto de comunidades. Cada envío usa UUID; un reintento idéntico recupera el mensaje y otra carga con esa clave se rechaza.

## Reportes y decisiones

Los participantes pueden reportar mensajes visibles con un motivo de hasta 500 caracteres. Cada cuenta puede reportar un mensaje una sola vez; repetirlo recupera el reporte. Se limita a 30 reportes nuevos por cuenta y hora. Un reporte no oculta automáticamente el mensaje. Solo los moderadores autorizados consultan la cola y sus motivos.

El creador y la administración pueden ocultar o mostrar mensajes, cerrar o reabrir conversaciones y descartar reportes. Toda decisión que cambia el estado conserva actor, fecha, destino, acción y motivo. Ocultar un mensaje raíz impide a los alumnos abrirlo y consultar sus respuestas; ocultar una respuesta la retira de su conversación. Los moderadores mantienen acceso para revisar. Cerrar conserva lectura y bloquea respuestas nuevas. Ocultar resuelve los reportes pendientes de ese mensaje; descartar conserva el mensaje visible y registra el motivo. Resolver afecta todos los reportes pendientes de ese mensaje en ese momento.

Suspender escritura se aplica a un alumno inscrito en una versión concreta. Mantiene lectura, inscripción, compras y progreso. La suspensión no vence automáticamente; el moderador puede restablecer escritura con un nuevo motivo. El historial enviado no se edita ni elimina: una corrección se publica como aclaración. La administración ofrece consulta del historial, sin edición directa de decisiones o estados mediante formularios de modelo.

Los avisos internos informan al autor de una respuesta, al creador de un reporte y al participante afectado por ocultación o suspensión y su recuperación. Cada aviso conserva una clave única. No hay envío de correo, avisos a todos los inscritos ni notificaciones push.

## Recorrido

Alumno: entrar con su cuenta → Comunidad → elegir versión inscrita → iniciar conversación o responder → reportar si corresponde. El enlace Comunidad está en la navegación del alumno y del estudio.

Creador: entrar al estudio → Comunidad → elegir versión propia → abrir mensaje y desplegar Moderar mensaje → elegir acción y explicar motivo. Desde Reportes y moderación puede resolver reportes, revisar suspensiones, restablecer escritura y consultar las decisiones.

Administración: entrar con cuenta administrativa y permiso de moderación → listado de mensajes en `/admin/learning/communitypost/` → Abrir comunidad. La cola y el historial comprueban el mismo permiso en servidor. Cada modificación requiere POST y protección CSRF.

## Verificación

La ejecución final del verificador integrado terminó con código 0: **210 pruebas Django en 126,634 segundos**, Ruff aprobado, sin migraciones pendientes de generar y cuatro comprobaciones de concurrencia aprobadas. Se mantiene el aviso conocido auth.W004 por cuentas independientes con correo reutilizable; sus pruebas de separación pasan.

En Chrome se recorrieron login de alumno, listado, espacio y conversación. Tras los ajustes finales se envió una respuesta por formulario y se comprobó su persistencia. La vista móvil se revisó con viewport de 390 × 844; el documento medido tuvo 375 píxeles de ancho útil y scrollWidth de 375, sin desbordamiento horizontal. La revisión visual no constituye una auditoría completa de accesibilidad. El recorrido de moderación por formularios se verifica en las pruebas Django; esta entrega no acredita su ensayo manual completo en navegador.

La migración `learning.0006` se aplicó a la base configurada después de crear respaldo SQLite privado. Se compararon cantidades y huellas del contenido de 47 tablas previas de negocio; en esta ejecución esas tablas no tenían filas. No se deduce de ello que sigan presentes los 211 registros citados en entregas anteriores. Integridad y claves foráneas correctas; las cuatro tablas comunitarias permanecen vacías. [Salida de migración](evidence/comunidad-migracion-2026-10-10.txt).

Pruebas específicas en `learning/test_community.py`: aislamiento por cuenta/versión, acceso histórico, reintentos, límites y paginación, cierre/reapertura, ocultación de raíces/respuestas, reportes y decisiones, suspensión reversible, permisos de creador/administración, cuentas inactivas, escape, privacidad del correo, CSRF, formularios y avisos internos idempotentes.

`scripts/verify-community-concurrency.py` comprueba publicaciones y reportes únicos, decisiones repetidas sin duplicar y suspensión frente a escritura con conexiones SQLite independientes a una base temporal en archivo. Se incorpora al verificador integrado. La evidencia de la ejecución final se conserva en [comunidad-check-2026-10-10.txt](evidence/comunidad-check-2026-10-10.txt).

La vista aislada se inicia con `./.venv/Scripts/python.exe scripts/preview-community.py` desde `src`. Usa el puerto 8019 y crea una base temporal con cuentas ficticias. Los identificadores y la ruta temporal quedan en `.local/community-preview.json`; la base principal no recibe esos ejemplos. Las credenciales de prueba están exclusivamente en el script de vista temporal.

## Límites y próximos pasos

La política adoptada es inscripción por versión, sin acceso público ni espacios por creador independientes del curso. No hay membresías, permisos temporales ni traslado de conversaciones entre versiones. Las preguntas privadas por lección conservan sus reglas propias. La suspensión comunitaria no suspende la cuenta ni los mensajes privados.

El creador atiende los reportes; la administración puede intervenir globalmente. No se garantiza un plazo de respuesta, no hay escalamiento automático ni apelación mediante formulario: una solicitud de revisión requiere contactar al responsable. Moderar sigue siendo una tarea humana; los controles y pruebas no acreditan capacidad operativa pública, entrevistas ni validación educativa. Antes de abrir al público deben acordarse responsables, normas editoriales, atención de incidencias, conservación de datos y capacidad de moderación.
