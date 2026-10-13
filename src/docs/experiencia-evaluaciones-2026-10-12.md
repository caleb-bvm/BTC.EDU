# Experiencia de evaluaciones

## Diagnóstico

Revisión del 12 de octubre de 2026 en la rama `main`, base Git `4000ed5`, sobre cambios locales previos conservados y sin commit propio en esta entrega. La pantalla inicial acumulaba reglas en párrafos largos; el intento mostraba todas las preguntas seguidas, opciones pequeñas y acciones al final sin avance ni revisión previa. El editor desplegaba todos los campos; el resultado mezclaba nota, respuestas y explicaciones. Se inspeccionó la implementación y la pantalla real mediante HTTP en una base temporal. Las capturas del 7 de octubre conservan el aspecto histórico y no representan esta entrega.

## Referencias y decisiones

[LatitudeLearning, Assessment Student UI](https://www.latitudelearning.com/ai-lms/portfolio/assessment-student-user-interface/) documenta resumen inicial, una pregunta por pantalla, opciones seleccionables desde toda su superficie, navegación numerada y revisión del resultado. Se adopta ese recorrido, sin incorporar marcado de preguntas ni nuevas reglas de evaluación.

[GOV.UK, Question pages](https://design-system.service.gov.uk/patterns/question-pages/) aporta una estructura de pregunta, regreso y continuación. [Radios](https://design-system.service.gov.uk/components/radios/) orienta la selección única y sus etiquetas. Se conservan controles nativos, `fieldset`/`legend`, etiquetas completas, instrucciones de selección y errores del servidor. La navegación es libre y cambiar de pregunta no selecciona una opción ni guarda automáticamente.

[Duolingo, Core tabs redesign](https://blog.duolingo.com/core-tabs-redesign/) muestra una revisión de jerarquía, espaciado y consistencia entre superficies. Se mantiene la marca, títulos NType82, etiquetas Space Mono y paleta de papel, tinta y naranja de BTC.EDU; el texto funcional de estas pantallas usa Arial del sistema, sin añadir fuentes remotas. Verde identifica respuestas contestadas y aprobaciones junto con texto o símbolos. Una respuesta contestada no significa que sea correcta.

Estas referencias sustentan decisiones de diseño; no prueban que la nueva experiencia mejore comprensión, tiempo o aprendizaje en BTC.EDU. Esa comprobación requiere participantes.

## Recorrido vigente

La preparación separa cantidad de preguntas, nota mínima, ausencia de límite de tiempo, reglas y disponibilidad de intentos. El inicio y la continuación tienen un área propia. Se conservan los estados de espera, agotamiento, intento activo y aprobación anterior. El historial presenta fecha, número, estado y nota en filas enlazadas.

Con JavaScript el intento presenta una pregunta a la vez. El mapa permite saltar entre preguntas; los botones Anterior y Siguiente no realizan peticiones ni guardan respuestas. El avance cuenta preguntas con alguna selección, incluidas las de selección múltiple aún incompletas. Las opciones son etiquetas amplias con radio o casilla nativos, selección visible y foco. Al retomar se abre la primera pregunta sin responder, o la primera si todas tienen respuesta. No se exponen claves ni explicaciones en el intento abierto.

Guardar conserva el envío normal con CSRF y revisión del intento. Se identifica cuando existen cambios locales sin guardar y el navegador puede advertir al salir. El guardado no cierra el intento. La revisión previa muestra las respuestas elegidas y permite volver a cada pregunta. La entrega se habilita cuando todas tienen alguna selección; el servidor sigue comprobando validez, autorización, revisión y puntuación. No se informa corrección antes de entregar. Sin JavaScript, todas las preguntas y los botones Guardar/Entregar permanecen disponibles en un formulario completo.

El resultado distingue nota, estado, fecha y siguiente paso. Las respuestas se consultan en bloques desplegables; las incorrectas se abren para facilitar el repaso. Si las soluciones requieren aprobar ese intento, solo se presentan las respuestas propias hasta cumplir la regla. Aprobar sigue sin marcar la lección automáticamente.

El editor agrupa reglas y permite plegar cada pregunta. La primera se abre inicialmente; las preguntas con errores se abren al volver del servidor. Añadir pregunta abre y enfoca los nuevos campos. Los errores nativos de campos requeridos abren su bloque antes de recibir foco. La pregunta vacía adicional permanece disponible para el recorrido sin JavaScript. Opciones por línea, claves numéricas, eliminación y publicación conservan el modelo existente. Los resultados del creador separan estudiante, versión, fecha y nota, con autorización adicional desplegable y motivo obligatorio.

## Verificación de esta entrega

Pasaron 29 pruebas existentes: `learning.test_assessments` y `learning.test_experience`. Incluyen guardado y retoma, selección exacta, privacidad de soluciones, revisión obsoleta, intentos, espera, permisos y efecto sobre el completado. Tras los últimos ajustes de plantillas se repitieron y aprobaron las 19 pruebas de evaluaciones. También pasaron la comprobación de sintaxis de `quizzes.js` y Ruff de `assessment_forms.py`; no se declara verificación global del repositorio.

En el navegador se comprobó HTTP real contra `scripts/preview-assessments.py`, con cuentas ficticias, cookies propias y SQLite temporal. Se recorrió la revisión con preguntas pendientes y botón Entregar deshabilitado; selección única, guardado parcial, retoma en la pregunta pendiente, navegación, resumen, entrega de selección múltiple parcial con 50/100, nuevo intento completo con 100/100, alta y guardado de una pregunta desde el editor, y autorización adicional con motivo conservando ambas notas.

Se inspeccionaron pantallas de escritorio y móvil a 390×844 en modo claro y oscuro. En las pantallas medidas, el contenido no excedió el ancho del viewport. Las capturas corresponden a cuentas temporales. Las pruebas no equivalen a una auditoría con lector de pantalla, a dispositivos físicos ni a sesiones con alumnos o creadores externos.

## Evidencia

- [Preparación en escritorio](evidence/evaluaciones-preparacion-2026-10-12.jpg).
- [Intento en escritorio](evidence/evaluaciones-intento-escritorio-2026-10-12.jpg).
- [Intento en móvil](evidence/evaluaciones-intento-movil-2026-10-12.jpg).
- [Revisión previa](evidence/evaluaciones-revision-escritorio-2026-10-12.jpg).
- [Resultado en móvil](evidence/evaluaciones-resultado-movil-2026-10-12.jpg).
- [Editor en escritorio](evidence/evaluaciones-editor-2026-10-12.jpg).
- [Editor en móvil](evidence/evaluaciones-editor-movil-2026-10-12.jpg).
- [Resultados del creador](evidence/evaluaciones-creador-resultados-2026-10-12.jpg).

## Límites y próximos pasos

No hay guardado automático de respuestas ni conservación de cambios locales tras un fallo de navegación o recarga. La advertencia al salir depende del navegador; guardar sigue siendo necesario. El avance indica respuestas presentes, no aciertos. No se añadieron temporizadores, orden aleatorio, ponderaciones ni crédito parcial. No se modificaron esquemas, pagos, reglas de acceso ni datos de la base principal.

Observar con participantes cómo interpretan el avance, guardan y retoman, revisan pendientes, entregan y explican el resultado. Evaluar también la carga cognitiva del editor y su uso con teclado y lector de pantalla. Registrar versión, ayudas y errores antes de afirmar mejoras de usabilidad o educativas. Los requisitos originales de CUBO+ siguen centrados en el recorrido de micropago y acceso; este pulido acompaña la experiencia de aprendizaje sin sustituir su verificación.
