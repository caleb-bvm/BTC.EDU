# Métricas y validación

## Eventos

Al 10 de octubre los paneles esenciales de creador y administración están implementados y verificados. [Fuentes, consultas, reglas, pruebas y límites](../src/docs/esenciales-2026-10-10.md). Resultados externos pendientes. La tabla describe el contrato completo: `preview_viewed` y reproducción todavía no se instrumentan; los estados terminales usan el historial comercial existente y Purchase como fuente de confirmación.

| Evento | Disparador | Fuente |
|---|---|---|
| offer_viewed | Se abre un detalle de curso, capítulo, video o material | Servidor, GET autorizado |
| preview_viewed | La muestra se presenta al usuario | Diseño pendiente |
| invoice_created | Se crea una factura nueva, no se reutiliza otra | Servidor |
| payment_paid | Una factura cambia a Paid | Servidor |
| payment_failed | Una factura cambia a Failed | Servidor |
| payment_expired | Una factura cambia a Expired | Servidor |
| purchased_content_opened | El servidor entrega correctamente un contenido comprado a su propietario | Servidor |
| library_viewed | Comprador abre su biblioteca | Servidor, GET autorizado |

Campos según corresponda: ID de evento, fecha UTC, ID de sesión, ID interno de cuenta, oferta, recurso, factura, categoría y tipo de oferta: curso, capítulo, video o material; incluir curso asociado y formato cuando corresponda. No incluir contraseña, cuerpo protegido ni correo en los eventos. Una sesión usa un identificador aleatorio; no se identifica a visitantes entre dispositivos.

La clasificación freemium es una estrategia de catálogo, no un tercer tipo de factura. Cada confirmación terminal se registra una sola vez por factura. Las aperturas repetidas son eventos separados. Se informa de aperturas, no de lectura completa ni aprendizaje.

## Indicadores

Todas las métricas muestran el intervalo de fechas aplicado y su denominador. Cuando es cero, mostrar «Sin datos». Las métricas comerciales usan cuentas compradoras; se excluyen cuentas de administrador.

| Indicador | Definición |
|---|---|
| Conversión a solicitud | Pares sesión-oferta con ambos eventos invoice_created y offer_viewed / pares sesión-oferta con offer_viewed, entre ofertas de pago y eventos dentro del intervalo |
| Finalización de pago | Facturas Paid / facturas creadas durante el intervalo, considerando su estado actual y mostrando cuántas siguen Pending |
| Apertura después de compra | Permisos adquiridos en el intervalo con al menos una apertura posterior / permisos adquiridos en el intervalo |
| Regreso a biblioteca | Compradores con library_viewed después de confirmar compra y en otra sesión / compradores del intervalo con sesión de compra registrada; informar los no observables |
| Compra repetida | Compradores del intervalo con al menos dos facturas Paid al cierre de la consulta / compradores del intervalo |
| Volumen simulado | Suma del importe de facturas Paid; un curso o capítulo se cuenta una vez |

En apertura, cada compra de curso o capítulo aporta tantos permisos como recursos incluidos. En transacciones y volumen aporta una compra. Las métricas de regreso y repetición son exploratorias para muestras pequeñas; no tienen todavía objetivos numéricos validados.

## Plan de investigación

La ronda propuesta es de seis a diez alumnos —compradores y usuarios de alternativas gratuitas— y tres a cinco creadores con material preparado/publicado. Sustituye la propuesta anterior; no hay reclutamiento realizado ni estimación estadística. Priorizar público pertinente de El Salvador y diversidad de dispositivo/pagos. Guiones y consentimiento en [16](16-validacion-con-usuarios.md).

Preguntar por la última necesidad concreta, recursos utilizados, compras anteriores, motivos para pagar o desistir y alternativas gratuitas. Explorar precios después de conocer la necesidad. Evitar presentar aceptación del concepto como compra real.

Para creadores: contenido disponible, derechos de uso, audiencia, esfuerzo de mantenimiento y preferencia entre venta de cursos, capítulos, videos y materiales.

## Pruebas de experiencia

Solicitar encontrar un recurso, explicar lo incluido, comprar con simulación, resolver una factura expirada y regresar a biblioteca. Comparar compra de curso completo, capítulo, video y material adicional, incluido un curso gratuito con compras opcionales y el caso parcialmente adquirido.

Registrar tarea, resultado, dificultad, cita autorizada y cambio propuesto. Obtener consentimiento para notas o grabaciones. Separar pruebas manuales del equipo de sesiones con participantes externos.

Clasificar sin ayuda / con ayuda / no completada / no intentada. Informar cantidades, versión y denominador por tarea, sin sumar versiones distintas. Separar observación, declaración, interpretación y decisión; reprobar cambios relevantes. La compra simulada no demuestra disposición a pagar. Explorar precios según [13](13-monetizacion-precios-y-muestras.md) sin declarar precio óptimo con una muestra pequeña.

## Entregables pendientes

La comparación de modelos/tarifas/costos y métodos de precios está incorporada en 13; guiones y tareas en 16. Pendientes: ejecutar sesiones, analizar resultados, completar prototipos, validar precios, auditar analítica y presupuesto, y cerrar recomendación final. Los datos del simulador no prueban ingresos reales ni voluntad de pago.

## Actividad de cursos y formatos

Registrar también free_content_opened cuando el servidor entrega contenido gratuito, video_started al comenzar la reproducción y material_downloaded cuando el servidor autoriza una descarga. Registrar formato y curso asociado. Empezar un video o descargar un archivo no demuestra terminarlo ni aprender. Los permisos adquiridos son la unidad para medir apertura, incluso si el mismo recurso aparece en varias ofertas.


## Métricas de aprendizaje, creación y membresías

Registrar enrollment_created, lesson_completed, assessment_submitted, assessment_passed, certificate_issued, course_submitted, course_published, question_posted, question_answered, subscription_started, subscription_renewed y subscription_expired. Guardar versión del curso o plan y origen del acceso cuando corresponda. La fuente del resultado de examen, certificado, publicación y periodo es el servidor.

Medir finalización por inscritos en una versión de curso; aprobación por intentos y por alumnos, mostrando ambos denominadores; tiempo hasta primera respuesta; cursos enviados y publicados; renovación por periodos que llegaron a vencimiento; retención por regreso en una sesión posterior. Separar compras individuales, pagos de membresía y volumen simulado. No sumar renovaciones como compradores nuevos. Separar venta individual de resultados educativos; completar una lección no demuestra aprendizaje.

El creador solo ve datos de sus contenidos, preferentemente agregados y con los alumnos pertinentes a su curso. El administrador consulta el conjunto. No publicar datos personales en métricas o páginas de certificados sin la configuración de compartición del alumno.


## Cobertura implementada de los paneles

`ActivityEvent` conserva UUID, fecha UTC, sesión aleatoria y referencias internas a cuenta, creador, versión, recurso, oferta o factura cuando corresponde. No registra IP, correo ni cuerpo de mensajes. Visitas de creadores/administradores no se cuentan; los compradores son cuentas de alumno sin privilegios administrativos. No se reconstruyen eventos históricos ni hay borrado automático de actividad.

El intervalo usa días inclusivos en America/El_Salvador. Facturas e inscripciones son cohortes por creación; sus resultados, apertura de permisos, regreso y repetición reflejan el estado al consultar, incluidos hechos posteriores al intervalo. Aperturas de oferta/contenido se filtran por fecha del evento. Solicitud usa la intersección de pares observados en el periodo. Reutilizar factura no añade evento; redirecciones sin contenido y accesos denegados no cuentan como aperturas.

Una compra confirmada se prueba por Purchase y se suma una vez aunque conceda varios derechos. Apertura se deduplica por alumno/recurso y exige fecha posterior a adquirirlo. Regreso exige sesión distinta y fecha posterior a confirmar; comprador sin sesión observada se excluye del denominador y se informa aparte. Los creadores solo ven sus contenidos y la administración requiere permisos específicos.

Aprendizaje usa Enrollment, LessonProgress y QuizAttempt; certificados usa emisiones, incluidas las después revocadas. Finalización de temario exige todas las lecciones; aprobación por inscripción significa al menos un intento aprobado, no todos los cuestionarios. Preguntas usa la primera respuesta real del creador para calcular promedio entre conversaciones respondidas. Se muestran también pendientes editoriales, compras recientes y filas por versión. Cero denominador devuelve Sin datos. Pruebas en core/test_analytics.py; no equivalen a validación de utilidad con usuarios.
