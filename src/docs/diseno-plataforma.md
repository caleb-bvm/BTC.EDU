# Diseño técnico de la plataforma completa

Diseño del alcance futuro basado en strategy/07 y strategy/08. Al 1 de octubre de 2026 existen cuentas por correo, sesiones, administración y portada/navegación con estados vacíos. LNbits FakeWallet tiene una prueba independiente; Django todavía no lo integra. Los módulos de comercio, contenido y aprendizaje siguientes siguen pendientes. Ver [base técnica](base-tecnica.md) y [estado real](../README.md). Todo archivo técnico permanece bajo src.

## Módulos y responsabilidades

| Módulo | Datos principales | Responsabilidad del servidor |
|---|---|---|
| Cuentas | Usuario, roles, sesión, token de recuperación | Autenticación, propiedad y permisos |
| Creación | Perfil, curso, versión, capítulo, lección, archivo | Borradores, revisión, publicación y almacenamiento protegido |
| Comercio | Oferta, recursos incluidos, factura, confirmación, permiso permanente | Precio guardado, estados, confirmación y concurrencia |
| Membresías | Plan y versión, suscripción, periodos, factura de renovación | Inicio y vencimiento, cancelación de renovación y acceso temporal |
| Aprendizaje | Inscripción, progreso, posición e intervalos de video | Persistencia por usuario, requisitos de finalización |
| Evaluación | Versión de examen, pregunta, intento, respuesta y nota | Calificación y límites en servidor |
| Certificados | Credencial, alumno, versión de curso, fecha e identificador | Emisión única y verificación pública limitada |
| Comunidad | Espacio, tema, respuesta, reporte y moderación | Permisos de lectura/escritura y trazabilidad |
| Actividad | Evento y notificación interna | Métricas propias del creador y alertas relevantes |

Se eligió Django 5.2 LTS, Python 3.12, plantillas, HTMX y Bootstrap con estilos propios. SQLite es la base elegida por el usuario para esta etapa local, con límites de escritura concurrente documentados. Una aplicación modular conserva las reglas comerciales; LNbits es un servicio separado. Las pruebas comerciales de concurrencia y el despliegue siguen pendientes.

## Regla de acceso

Para cada recurso: permitir si es gratuito, si existe permiso permanente por compra o si está incluido en un periodo de membresía vigente. Comprobar también publicación y ámbito de propiedad para borradores. Mostrar la razón del acceso en la interfaz: gratis, comprado o incluido en membresía hasta fecha.

Inscripción y progreso no conceden acceso de pago. Un rol de creador no permite leer contenidos ajenos. Una compra o plan de curso apunta a una versión explícita y a los recursos incluidos. La comunidad tiene sus propios permisos. El acceso no se deduce de que aparezca una tarjeta en la biblioteca.

## Integridad de pagos

Separar proveedor de pagos y reglas comerciales. El adaptador LNbits crea factura, consulta pago y concilia confirmaciones. El simulador de pruebas permite fallar y expirar. Un trabajo periódico y la consulta de factura aplican vencimiento y recuperación tras reinicio; no confiar solo en un contador del navegador.

La confirmación abre una transacción de base de datos que bloquea factura y recursos o suscripción afectados, comprueba propietario/estado/plazo, registra pago y concede permisos o agrega un periodo. Usar restricciones únicas por confirmación, por permiso usuario/recurso y por periodo/factura. No duplicar cuando compiten consulta y notificación.

Si un plan se renueva, calcular inicio desde el mayor entre confirmación y fin de periodo vigente. Cancelar desactiva intención de renovación; el permiso se evalúa por fechas pagadas. El MVP no tiene cobro autónomo. No usar las claves de una wallet de prueba como autorización de cargo real futuro.

## Contratos orientativos

Estos son contratos propuestos, no endpoints existentes de la plataforma.

- GET /courses y GET /courses/{id}: catálogo y temario público con situación de acceso.
- POST /enrollments: inscripción gratuita sin conceder permisos de pago.
- POST /invoices y GET /invoices/{id}: crear o reutilizar factura y consultar estado propio.
- GET /resources/{id}/content: contenido autorizado; video con peticiones Range y descarga controlada.
- PUT /lessons/{id}/progress: guardar posición y finalización válida del usuario autenticado.
- POST /assessments/{id}/attempts y POST /attempts/{id}/submit: iniciar y finalizar intento propio.
- POST /courses/{id}/certificate: emisión idempotente después de verificar requisitos.
- GET /certificates/{public_id}: datos mínimos para verificar una credencial compartida.
- POST /creator/courses y POST /creator/courses/{id}/submit: crear borrador y enviar revisión.
- POST /admin/course-versions/{id}/publish: aprobar versión revisada.
- POST /subscriptions y POST /subscriptions/{id}/renew: primera factura o renovación manual.
- POST /subscriptions/{id}/cancel: cancelar renovación sin borrar periodo pagado.
- POST /spaces/{id}/topics, POST /topics/{id}/replies y POST /reports: comunidad autorizada.

Cada operación deriva cuenta y rol de la sesión; no confía en un user_id del navegador. Añadir paginación, validación, protección CSRF si se usan cookies y límites de frecuencia para cuentas, carga y publicaciones.

## Archivos y video

Almacenar archivos de pago fuera de la carpeta pública. Validar extensión, contenido MIME y tamaño; generar nombres internos. Subir subtítulos VTT asociados al video. Entregar el archivo solo con permiso vigente y soportar Range en reproducción. No usar enlaces públicos ocultos como protección. La primera versión puede servir MP4 protegido; transcodificación y CDN se evaluarán por volumen y entorno, sin prometer protección contra copias.

## Aprendizaje y versiones

El progreso se guarda por alumno, lección y versión del curso, y se conserva al vencer membresías. Los intervalos observados ayudan a calcular avance del video, pero no prueban aprendizaje. La calificación guarda la versión de preguntas y respuestas correctas; no enviar claves de corrección antes del cierre del intento. La credencial guarda requisitos y versión completada. Añadir lecciones no invalida credenciales previas.

## Pruebas necesarias

- Acceso a texto, video, subtítulos protegidos y descarga sin compra, con compra y con membresía vencida.
- Aislamiento entre creadores y acceso a borradores y métricas.
- Facturas simultáneas, confirmación repetida, expiración, cambio de precio y reinicio con pendientes.
- Compra permanente que sobrevive al vencimiento de membresía y renovación sin periodo duplicado.
- Progreso entre sesiones, intentos agotados, corrección en servidor y certificado no emitido por simple compra.
- Moderación y lectura de comunidades con permiso; recuperación con token vencido o reutilizado.
- Recorrido móvil, teclado, subtítulos y demostración completa con datos ficticios.

La entrega debe enumerar pruebas ejecutadas y resultados reales. No presentar este diseño como código implementado.
