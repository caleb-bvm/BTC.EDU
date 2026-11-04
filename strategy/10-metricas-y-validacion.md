# Métricas y validación

Eventos e indicadores implementados, plan de investigación e instrumentos de validación con usuarios. Las sesiones con participantes siguen pendientes.

<a id="05-metricas-y-validacion"></a>

## Métricas y validación

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Eventos

Al 10 de octubre los paneles esenciales de creador y administración están implementados y verificados. [Fuentes, consultas, reglas, pruebas y límites](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). Resultados externos pendientes. La tabla describe el contrato completo: `preview_viewed` y reproducción todavía no se instrumentan; los estados terminales usan el historial comercial existente y Purchase como fuente de confirmación.

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

### Indicadores

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

### Plan de investigación

La ronda propuesta es de seis a diez alumnos —compradores y usuarios de alternativas gratuitas— y tres a cinco creadores con material preparado/publicado. Sustituye la propuesta anterior; no hay reclutamiento realizado ni estimación estadística. Priorizar público pertinente de El Salvador y diversidad de dispositivo/pagos. Guiones y consentimiento en [16](10-metricas-y-validacion.md#16-validacion-con-usuarios).

Preguntar por la última necesidad concreta, recursos utilizados, compras anteriores, motivos para pagar o desistir y alternativas gratuitas. Explorar precios después de conocer la necesidad. Evitar presentar aceptación del concepto como compra real.

Para creadores: contenido disponible, derechos de uso, audiencia, esfuerzo de mantenimiento y preferencia entre venta de cursos, capítulos, videos y materiales.

### Pruebas de experiencia

Solicitar encontrar un recurso, explicar lo incluido, comprar con simulación, resolver una factura expirada y regresar a biblioteca. Comparar compra de curso completo, capítulo, video y material adicional, incluido un curso gratuito con compras opcionales y el caso parcialmente adquirido.

Registrar tarea, resultado, dificultad, cita autorizada y cambio propuesto. Obtener consentimiento para notas o grabaciones. Separar pruebas manuales del equipo de sesiones con participantes externos.

Clasificar sin ayuda / con ayuda / no completada / no intentada. Informar cantidades, versión y denominador por tarea, sin sumar versiones distintas. Separar observación, declaración, interpretación y decisión; reprobar cambios relevantes. La compra simulada no demuestra disposición a pagar. Explorar precios según [13](04-producto-y-monetizacion.md#13-monetizacion-precios-y-muestras) sin declarar precio óptimo con una muestra pequeña.

### Entregables pendientes

La comparación de modelos/tarifas/costos y métodos de precios está incorporada en 13; guiones y tareas en 16. Pendientes: ejecutar sesiones, analizar resultados, completar prototipos, validar precios, auditar analítica y presupuesto, y cerrar recomendación final. Los datos del simulador no prueban ingresos reales ni voluntad de pago.

### Actividad de cursos y formatos

Registrar también free_content_opened cuando el servidor entrega contenido gratuito, video_started al comenzar la reproducción y material_downloaded cuando el servidor autoriza una descarga. Registrar formato y curso asociado. Empezar un video o descargar un archivo no demuestra terminarlo ni aprender. Los permisos adquiridos son la unidad para medir apertura, incluso si el mismo recurso aparece en varias ofertas.

### Métricas de aprendizaje, creación y membresías

Registrar enrollment_created, lesson_completed, assessment_submitted, assessment_passed, certificate_issued, course_submitted, course_published, question_posted, question_answered, subscription_started, subscription_renewed y subscription_expired. Guardar versión del curso o plan y origen del acceso cuando corresponda. La fuente del resultado de examen, certificado, publicación y periodo es el servidor.

Medir finalización por inscritos en una versión de curso; aprobación por intentos y por alumnos, mostrando ambos denominadores; tiempo hasta primera respuesta; cursos enviados y publicados; renovación por periodos que llegaron a vencimiento; retención por regreso en una sesión posterior. Separar compras individuales, pagos de membresía y volumen simulado. No sumar renovaciones como compradores nuevos. Separar venta individual de resultados educativos; completar una lección no demuestra aprendizaje.

El creador solo ve datos de sus contenidos, preferentemente agregados y con los alumnos pertinentes a su curso. El administrador consulta el conjunto. No publicar datos personales en métricas o páginas de certificados sin la configuración de compartición del alumno.

### Cobertura implementada de los paneles

`ActivityEvent` conserva UUID, fecha UTC, sesión aleatoria y referencias internas a cuenta, creador, versión, recurso, oferta o factura cuando corresponde. No registra IP, correo ni cuerpo de mensajes. Visitas de creadores/administradores no se cuentan; los compradores son cuentas de alumno sin privilegios administrativos. No se reconstruyen eventos históricos ni hay borrado automático de actividad.

El intervalo usa días inclusivos en America/El_Salvador. Facturas e inscripciones son cohortes por creación; sus resultados, apertura de permisos, regreso y repetición reflejan el estado al consultar, incluidos hechos posteriores al intervalo. Aperturas de oferta/contenido se filtran por fecha del evento. Solicitud usa la intersección de pares observados en el periodo. Reutilizar factura no añade evento; redirecciones sin contenido y accesos denegados no cuentan como aperturas.

Una compra confirmada se prueba por Purchase y se suma una vez aunque conceda varios derechos. Apertura se deduplica por alumno/recurso y exige fecha posterior a adquirirlo. Regreso exige sesión distinta y fecha posterior a confirmar; comprador sin sesión observada se excluye del denominador y se informa aparte. Los creadores solo ven sus contenidos y la administración requiere permisos específicos.

Aprendizaje usa Enrollment, LessonProgress y QuizAttempt; certificados usa emisiones, incluidas las después revocadas. Finalización de temario exige todas las lecciones; aprobación por inscripción significa al menos un intento aprobado, no todos los cuestionarios. Preguntas usa la primera respuesta real del creador para calcular promedio entre conversaciones respondidas. Se muestran también pendientes editoriales, compras recientes y filas por versión. Cero denominador devuelve Sin datos. Pruebas en core/test_analytics.py; no equivalen a validación de utilidad con usuarios.

<a id="16-validacion-con-usuarios"></a>

## Validación con usuarios

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Instrumentos preparados el 5 de octubre de 2026. **No hay participantes reclutados, entrevistas realizadas ni resultados externos registrados.** Las cantidades, tiempos y criterios siguientes son propuestas del equipo; no estimaciones representativas ni estándares impuestos por CUBO+.

### Preguntas

| Hipótesis | Evidencia que buscaremos | Qué podría cuestionarla |
|---|---|---|
| Comprar una unidad responde a una necesidad concreta | Experiencias recientes y elección ante alternativas | Lo gratuito o el curso completo resuelve mejor la necesidad |
| La oferta explica lo que se adquiere | Explicación correcta de precio, inclusiones y extras antes de pagar | Compra bajo una interpretación equivocada |
| El pago simulado y la biblioteca son comprensibles | Tareas sin ayuda y recuperación en otra sesión | Confusión de estados o acceso perdido |
| El creador puede preparar una oferta sostenible | Material existente, costos, mantenimiento y uso del editor | No puede ofrecerlo por separado o su costo supera el beneficio previsto |

La documentación de plataformas sustenta posibilidades de diseño, no estas hipótesis. Entrevistas exploran experiencias; tareas observan interacción; precios recogen percepción; ninguno por sí solo acredita demanda. [Monetización y muestras](04-producto-y-monetizacion.md#13-monetizacion-precios-y-muestras).

### Participantes

Primera ronda propuesta: seis a diez alumnos, incluyendo compradores y usuarios de alternativas gratuitas, y tres a cinco creadores con materiales ya preparados o publicados. Priorizar el público relacionado con El Salvador y aprendizaje de tecnología/programación. Incluir diversidad de dispositivo, experiencia y familiaridad con pagos digitales. No reclutar solo compañeros del equipo o personas que ya conocen la interfaz.

Registrar criterios de inclusión y cómo se contactó/reclutó, sin publicar contactos. Las sesiones externas se distinguen de pilotos con colegas. Se puede dividir la ronda en grupos pequeños, corregir problemas y registrar la versión usada por cada participante. No sumar resultados de versiones distintas como si fueran una misma condición.

Propuesta: entrevista de 30–45 minutos o prueba de 30–60 minutos. Cuando se combinen, reducir tareas; no intentar todo en una sesión. No contactar participantes ni enviar invitaciones por esta preparación documental.

### Consentimiento

Antes de empezar, explicar propósito, responsable/contacto, actividades, voluntariedad, observadores, datos recogidos, uso/compartición, grabación opcional y duración de conservación acordada. Registrar consentimiento y cómo solicitar retiro. Evitar contraseñas, saldos reales y documentos financieros; usar cuentas temporales. No publicar grabaciones, citas identificables ni datos personales sin el permiso correspondiente. [Guía metodológica de GOV.UK](https://www.gov.uk/service-manual/user-research/getting-users-consent-for-research).

La duración de conservación y la persona responsable deben fijarse antes del reclutamiento. El consentimiento para participar no equivale a consentimiento para publicar una grabación. Esta guía metodológica no constituye una evaluación de obligaciones legales locales.

### Entrevistas

Preparar y pilotar el guion antes de usarlo. Investigar experiencias recientes antes de explicar BTC.EDU; evitar preguntas que sugieran que el participante necesita nuestra solución. La memoria y las intenciones tienen límites: contrastar cuando sea posible con comportamientos observados. [GOV.UK](https://www.gov.uk/service-manual/user-research/using-in-depth-interviews), [NN/G](https://www.nngroup.com/articles/why-user-interviews-fail/).

#### Alumnos

1. Cuéntame la última vez que buscaste aprender algo para resolver una tarea.
2. ¿Qué necesitabas conseguir y qué recursos consultaste?
3. ¿Cómo decidiste cuál utilizar?
4. Si pagaste, ¿qué compraste y qué información revisaste antes?
5. Si elegiste algo gratuito, ¿qué influyó en esa decisión?
6. ¿Hubo contenido que compraste y no utilizaste?
7. ¿Cómo recuperaste el material cuando lo necesitaste de nuevo?
8. ¿Qué dificultades encontraste, si hubo alguna?
9. ¿Qué medios de pago utilizas y cómo ha sido tu experiencia?

Repreguntas según el relato: qué alternativa consideró, qué ocurrió después, si la situación se repite y cómo retoma. No exigir recibos ni capturas con información privada. Presentar el concepto al final; registrar reacción como opinión, no compra.

#### Creadores

1. Cuéntame cómo preparaste y publicaste tu último material.
2. ¿A quién iba dirigido?
3. ¿Cómo decidiste qué sería gratuito y qué tendría precio?
4. ¿Cómo calculaste ese precio?
5. ¿Qué parte podría utilizarse de manera independiente, si alguna?
6. ¿Qué costos y tareas de mantenimiento tienes?
7. ¿Cómo atiendes dudas y problemas de acceso?
8. ¿Qué ocurre cuando actualizas contenido que alguien ya compró?
9. ¿Qué información utilizas para decidir qué mejorar?

Explorar autoría/derechos y frecuencia de actualización sin asumir que todos venden contenido. Registrar plataforma y condiciones mencionadas como experiencia del participante, no como tarifa externa verificada.

### Usabilidad

Presentar metas creíbles sin decir botones o caminos. Observar y pedir que explique lo que está pensando; no corregir inmediatamente. Anotar cada ayuda. Las pruebas moderadas permiten detectar comprensión y problemas de interacción. [GOV.UK](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing).

Solo ejecutar tareas correspondientes a módulos disponibles. Preguntas y evaluaciones están implementadas; las membresías u otras funciones pendientes podrán probarse en un prototipo identificado, sin describirlas como implementación. Usar facturas simuladas y datos temporales, sin modificar la base principal.

| ID | Tarea de alumno | Evidencia buscada |
|---|---|---|
| U01 | Encontrar un recurso para una necesidad dada | Búsqueda, filtros y elección pertinente |
| U02 | Explicar una oferta antes de comprar | Precio, muestra, inclusiones y extras correctos |
| U03 | Adquirir un recurso individual | No presupone comprar todo el curso |
| U04 | Completar un pago simulado | Comprende importe, estado y acceso obtenido |
| U05 | Resolver una factura vencida | Entiende que no concedió derechos y cómo reintentar |
| U06 | Recuperar contenido desde otra sesión | Cuenta, biblioteca y acceso persistente |
| U07 | Obtener contenido faltante de un curso parcialmente adquirido | Comprende bloqueo conjunto y alternativas |

| ID | Tarea de creador | Evidencia buscada |
|---|---|---|
| C01 | Preparar una lección y vincular un material | Claridad del editor y archivos |
| C02 | Organizar capítulos y lecciones | Estructura educativa comprensible |
| C03 | Definir una oferta | Muestra, precio e inclusión sin ambigüedad |
| C04 | Enviar a revisión y resolver observaciones | Entiende publicación y reenvío |
| C05 | Preparar una actualización | Entiende efectos sobre versiones y compras |

Registrar resultado: sin ayuda / con ayuda / no completada / no intentada. Medir tiempo, errores, dudas y explicación final. Una tarea no intentada no cuenta como éxito o fracaso. Ejemplo de métrica: éxito sin ayuda / intentos válidos de esa tarea, con cantidades y versión. No combinar perfiles ni transformar la pequeña muestra en una tasa de mercado.

Para contrastar la barra estandarizada, pedir que recupere una compra, encuentre una respuesta privada y solicite ayuda; en móvil, que salga de una lección enfocada hacia otra sección y regrese al curso. Con el educador, pedir que consulte una pregunta, revise su contenido y abra la academia. Registrar primer destino elegido, desvíos, ayuda y retorno al punto de origen, sin nombrar controles. Son tareas preparadas el 14 de octubre de 2026, todavía sin sesiones ejecutadas.

### Precios

Primero definir un recurso concreto con muestra, resultado e inclusiones. Investigar gasto anterior antes de mostrar precios del catálogo. Conservar la misma oferta durante la comparación; incluir elección de no comprar.

Preguntas exploratorias adaptadas de Van Westendorp: ¿qué precio te haría dudar de la calidad por ser muy bajo?, ¿cuál considerarías económico?, ¿cuál caro pero aún considerarías?, ¿cuál descartaría la compra? Gabor-Granger permite explorar aceptación de importes definidos cuando existe un rango previo. No aplicar análisis estadístico representativo a unas pocas entrevistas. [Qualtrics](https://www.qualtrics.com/en-au/articles/strategy-research/pricing-survey-questions/).

Probar comprensión de sats y, si hace falta, equivalencia informativa en USD con referencia explícita. Registrar si las condiciones de presentación cambian. Definir rango después de entrevistas y costos, no copiar 50/100/300 sats como precio validado.

Comparar recurso individual, conjunto y ninguna compra. Evitar ordenar siempre desde el precio más bajo, que puede anclar respuestas. Registrar razones. Las respuestas siguen siendo declaraciones y una compra simulada sigue siendo una tarea de usabilidad. El sesgo entre disposición declarada y real está documentado por [Schmidt y Bijmolt](https://link.springer.com/article/10.1007/s11747-019-00666-6).

### Registro y análisis

| Campo | Contenido |
|---|---|
| Sesión | ID, fecha, responsable, versión/commit y perfil pertinente |
| Actividad | Pregunta/tarea e instrucciones dadas |
| Evidencia | Acción observada o declaración autorizada; distinguir ambas |
| Resultado | Finalización, ayuda, error, tiempo o abandono |
| Interpretación | Explicación propuesta y posibles alternativas |
| Acción | Cambio, prioridad, responsable o nueva pregunta |
| Comprobación | Nueva evidencia después del cambio, si existe |

Separar observación → interpretación → decisión. Revisar patrones y casos contrarios; no eliminar evidencia porque contradiga nuestra idea. Compartir un resumen anonimizado y conservar notas según consentimiento. [Análisis de sesiones](https://www.gov.uk/service-manual/user-research/analyse-a-research-session).

Clasificar problemas como bloqueo de tarea, error de compra/acceso, dificultad recuperable o detalle menor. Priorizar consecuencias, repetición y alcance, sin inventar una puntuación científica. Reprobar cambios relevantes con la versión actualizada.

### Resultados

Pendientes. No existe evidencia externa que permita afirmar comprensión, disposición a pagar, preferencias de compra o usabilidad del creador. La primera ejecución deberá registrar participantes, versión, tareas, cantidades, hallazgos, cambios y limitaciones. Actualizar 01/04/05/07/13 y el documento principal con los resultados que realmente se obtengan.

### Tareas de perfiles y comunidad

Instrumentos añadidos el 12 de octubre de 2026; sesiones con participantes todavía pendientes. Pedir al estudiante que elija un alias, prepare una presentación y explique qué información aparecerá al compartirla. Después, pedirle que oculte el perfil y compruebe la diferencia entre el alias de los mensajes y el acceso a la ficha. Registrar confusiones sobre privacidad sin sugerir la respuesta.

Pedir a un participante inscrito que encuentre una conversación sin respuesta, busque un término presente en una respuesta visible, siga una conversación ajena y localice el aviso interno. Pedir al creador que abra una ficha desde la comunidad y vuelva a su estudio. Registrar éxito, dificultades y comprensión de los límites de acceso. Estas tareas deben ejecutarse sobre una versión identificada y con consentimiento; la revisión técnica con cuentas sintéticas no cuenta como una sesión educativa o comercial.

### Tareas de continuidad y lectura

Instrumentos preparados el 12 de octubre de 2026; ejecución con participantes pendiente. Pedir que retome un curso tras estudiar una lección, explique su progreso y encuentre una pendiente. Comprobar que distingue abrir, completar y aprobar evaluación. Pedir que complete una muestra gratuita y explique qué puede estudiar después sin comprar. Registrar errores, ayudas, comprensión y versión, sin sugerir botones.

Pedir que encuentre el temario en móvil, intente una práctica antes de consultar la solución y use la lectura enfocada. Pedir que busque un curso en su biblioteca y encuentre los completados. Comparar la comprensión del certificado con la finalización de todas las lecciones. La revisión en navegador con cuentas sintéticas es evidencia técnica y no cuenta como ejecución de estas sesiones. [Diseño y límites de la entrega](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12).

### Tareas de conversación en lecciones

Instrumentos preparados el 12 de octubre de 2026; ejecución con participantes pendiente. Pedir al estudiante que comente al terminar una lección, explique quién puede leer su mensaje, responda a un compañero y siga una conversación. Pedirle que distinga ese recorrido de la pregunta privada al creador y que encuentre el mismo comentario desde Comunidad. Observar si entiende la inscripción y el acceso cuando una lección está bloqueada.

Pedir al creador que encuentre un comentario nuevo mediante su aviso, responda y vuelva a la lección. Registrar claridad del contexto, dificultades, ayuda necesaria y expectativas de atención. Una respuesta recibida no prueba que la duda esté resuelta. Las pruebas técnicas y las cuentas ficticias de esta entrega no son sesiones con usuarios.

### Tareas de evaluaciones

Instrumentos actualizados el 12 de octubre de 2026; ejecución externa pendiente. Pedir al alumno que explique las condiciones antes de empezar, responda parcialmente, salga y retome. Observar si distingue preguntas respondidas de respuestas correctas, si confía en el guardado automático y si usa la marca para revisar. Pedir que revise una respuesta, encuentre una pendiente, entregue y explique la nota y el siguiente paso. Con creadores, observar configuración de reglas, edición de una pregunta plegada, incorporación de otra y autorización adicional con motivo. Registrar ayudas, errores, dudas y versión, incluyendo móvil y teclado. Las comprobaciones técnicas registradas en la entrega de UI no cuentan como sesiones con participantes.
