# Investigación y requisitos

El [informe principal](19-recomendacion-y-entrega-final.md) describe el producto vigente. Este archivo reúne fuentes, costos, instrumentos, requisitos y decisiones que lo respaldan. Las referencias comerciales conservan sus fechas de consulta; deben verificarse antes de contratar. Las entrevistas y sesiones externas siguen pendientes.

## Cómo mantener esta documentación

La documentación principal queda en cuatro archivos: el informe de BTC.EDU, su exportación de texto para Google Docs, este archivo y la [operación y bitácora técnica](../src/docs/operacion-y-bitacora.md). Las capturas y registros originales permanecen en `src/docs/evidence`; los dos documentos de CUBO+ permanecen en `docs`. Son evidencias y fuentes, no nuevos informes.

Actualizar las secciones correspondientes dentro de estos archivos en cada entrega. El informe mantiene el estado actual; los registros fechados conservan el historial y sus límites. No crear documentos nuevos por cada función. Regenerar la exportación de texto cuando cambie el informe. No registrar preparación de instrumentos como sesiones ejecutadas.

## Consulta por tema

- [13-monetizacion-precios-y-muestras](#13-monetizacion-precios-y-muestras)
- [16-validacion-con-usuarios](#16-validacion-con-usuarios)
- [14-trazabilidad-y-backlog](#14-trazabilidad-y-backlog)
- [03-especificacion-funcional](#03-especificacion-funcional)
- [05-metricas-y-validacion](#05-metricas-y-validacion)
- [15-especificaciones-modulos-pendientes](#15-especificaciones-modulos-pendientes)
- [20-comunidad-en-lecciones](#20-comunidad-en-lecciones)
- [07-investigacion-y-necesidades](#07-investigacion-y-necesidades)
- [10-arquitectura-y-experiencia-btc-edu](#10-arquitectura-y-experiencia-btc-edu)
- [11-enfoque-creadores](#11-enfoque-creadores)
- [08-aprendizaje-creadores-y-membresias](#08-aprendizaje-creadores-y-membresias)
- [09-identidad-visual](#09-identidad-visual)
- [04-pantallas-y-recorrido](#04-pantallas-y-recorrido)
- [01-producto-y-negocio](#01-producto-y-negocio)
- [02-catalogo-de-prueba](#02-catalogo-de-prueba)
- [06-plan-y-decisiones](#06-plan-y-decisiones)
- [12-plan-documentacion-business-a-desarrollo](#12-plan-documentacion-business-a-desarrollo)
- [README](#readme)

## Antecedentes y detalle

Las secciones siguientes conservan los documentos de origen para mantener criterios AC/UX, fuentes, cálculos y decisiones. Sus descripciones de estado son históricas; ante una diferencia, consultar el informe principal y la entrega técnica fechada correspondiente. El catálogo anterior de programación es un antecedente; el catálogo local vigente es el de Bitcoin y Lightning.

<a id="13-monetizacion-precios-y-muestras"></a>

## Monetización, precios y muestras

Origen: `strategy/13-monetizacion-precios-y-muestras.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Investigación documental del 5 de octubre de 2026, incorporada con autorización del usuario. Los precios externos son referencias de las páginas consultadas, no cotizaciones para El Salvador ni precios elegidos para BTC.EDU. Las interpretaciones y propuestas se identifican como tales. No se realizaron compras de prueba en esas plataformas ni entrevistas externas.

### Modelos

Los modelos no son excluyentes. Freemium describe la combinación de acceso gratuito y pagado; micropagos describe compras de importes pequeños. Pueden convivir con suscripciones. Patreon permite compras únicas y membresías; Teachable contempla planes gratuitos, compra única y pagos recurrentes. Esta coexistencia documenta alternativas, no demanda por nuestra solución. [Patreon](https://www.patreon.com/policy/legal), [Teachable](https://support.teachable.com/en/articles/15627279-price-your-products).

La siguiente comparación es una interpretación para BTC.EDU:

| Modelo | Forma de acceso | Conveniencia por comprobar | Costos y límites |
|---|---|---|---|
| Suscripción | Acceso durante un periodo pagado | Uso frecuente de varios recursos | Oferta suficiente, renovación, vencimiento, soporte y consumo continuo |
| Publicidad | El anunciante financia parte del acceso | Contenido gratuito | Rendimiento dependiente de actividad publicitaria; evaluar efectos sobre aprendizaje y experiencia |
| Freemium | Contenido gratuito y ampliaciones pagadas | Explorar antes de comprar | El acceso gratuito también consume recursos; explicar qué es gratis y qué requiere pago |
| Micropagos | Compra de una unidad concreta por importe pequeño | Necesidad puntual sin adquirir un conjunto mayor | Decisión y operación por compra; procesamiento, entrega y soporte pueden pesar sobre el precio |

Coursera Plus muestra USD 59 mensuales para el conjunto incluido, con exclusiones. Es una referencia del precio al alumno, no un costo de alojamiento del creador ni una tarifa garantizada localmente. [Coursera Plus](https://www.coursera.org/courseraplus).

Codecademy ofrece Basic gratuito y planes pagados. Documenta freemium en programación, sin validar nuestra combinación o precios. [Codecademy](https://www.codecademy.com/pricing).

AdSense define RPM como ingresos estimados por mil vistas o impresiones. No garantiza una tarifa para BTC.EDU. Nuestra interpretación es no asumir publicidad como fuente principal sin audiencia y rendimiento propios. [Google AdSense](https://support.google.com/adsense/answer/190515?hl=en).

### Referencias de costos

Separar precio al alumno, suscripción del creador, comisión de plataforma, procesamiento e infraestructura. Los importes pueden cambiar y no incluyen necesariamente impuestos ni todos los cargos. No acreditan disponibilidad de liquidación para nuestro equipo.

| Plataforma / plan | Facturación mensual observada | Comisión de plataforma observada |
|---|---:|---|
| Teachable Starter | USD 39/mes | 7.5 % |
| Teachable Builder | USD 89/mes | 0 % bajo las condiciones de sus pasarelas aplicables; procesamiento aparte |
| Thinkific Basic | USD 54/mes | Consultar procesamiento y condiciones; no se presume ausencia de cargos |
| Thinkific Start | USD 109/mes | Consultar procesamiento; incluye membresías y suscripciones |

Fuentes: [Teachable](https://www.teachable.com/pricing), [Thinkific](https://www.thinkific.com/pricing/). No trasladar estos importes como precio de nuestros cursos.

#### Compras pequeñas

Patreon documenta 10 % de comisión de plataforma para su plan estándar y, con tarjeta y liquidación en USD, procesamiento de 2.9 % + USD 0.30. [Tarifas](https://support.patreon.com/hc/en-us/articles/11111747095181-Creator-fees-overview).

Cálculo propio con esas condiciones: `cargos = 0.10 × precio + 0.029 × precio + 0.30`.

| Precio | Cargos ilustrativos | Proporción |
|---|---:|---:|
| USD 1 | USD 0.429 | 42.9 % |
| USD 5 | USD 0.945 | 18.9 % |

Excluye impuestos, retiros y otros cargos. Muestra el peso del componente fijo; no representa BTC.EDU ni Lightning. En Lightning existen comisiones base/proporcionales y necesidades de liquidez. Evaluar proveedor, recepción, liquidez y operación antes de afirmar costos de micropagos reales. [Comisiones](https://docs.lightning.engineering/the-lightning-network/pathfinding/channel-fees), [Liquidez](https://docs.lightning.engineering/the-lightning-network/liquidity/manage-liquidity).

#### Video y acceso permanente

Cloudflare Stream publica USD 5 mensuales por cada bloque de mil minutos de capacidad almacenada y USD 1 por mil minutos entregados. Es referencia, no elección de proveedor. [Precios](https://developers.cloudflare.com/stream/pricing/).

Escenario propio: mil minutos almacenados y seis mil entregados al mes → USD 11. Con doce mil entregados → USD 17. Excluye aplicación, otros archivos, correo, producción, soporte y respaldos. Reproducciones repetidas y gratuitas también tienen costo.

Mantener acceso permanente por versión exige estimar consumo posterior, conservación de archivos históricos y mantenimiento. No cambia la regla vigente de compras; añade una obligación para la estimación operativa. Faltan escenarios de uso, costos humanos y sostenibilidad completa.

### Muestras

Coursera documenta muestra gratuita del primer módulo de la mayoría de los cursos. Es una referencia, no la regla ni una medida óptima para BTC.EDU. [Descripción del modelo](https://blog.coursera.org/introducing-courseras-new-course-preview-experience/).

| Formato | Propuesta de muestra | Pregunta de validación |
|---|---|---|
| Curso | Lección útil, objetivos y temario | ¿Comprende nivel, alcance y extras? |
| Capítulo | Explicación o actividad representativa | ¿Reconoce su utilidad por separado? |
| Video | Fragmento representativo y resultado esperado | ¿Puede evaluar contenido y claridad? |
| Material | Extracto, formato y lista de lo incluido | ¿Entiende qué descargará? |

No fijar un porcentaje o duración universal sin comparar variantes. Mantener muestra pública separada del contenido protegido. Pedir al participante que explique qué obtiene, qué queda fuera y por qué le sirve. Instrumentos en [validación](investigacion-y-requisitos.md#16-validacion-con-usuarios).

### Precios por validar

Los valores de 02 siguen siendo ficticios. No se modifican las ofertas ni se proponen precios de mercado a partir de estas referencias.

Van Westendorp explora percepciones de precio demasiado bajo, económico, caro y demasiado caro. Gabor-Granger consulta aceptación de distintos precios para una oferta definida. Son instrumentos para investigación, no pruebas de compra. [Qualtrics](https://www.qualtrics.com/en-au/articles/strategy-research/pricing-survey-questions/).

El metaanálisis de Schmidt y Bijmolt documenta diferencias entre disposición declarada y real. No convertir respuestas favorables en ventas previstas ni aplicar un ajuste universal a nuestra muestra. [Estudio](https://link.springer.com/article/10.1007/s11747-019-00666-6).

Primera etapa propuesta: necesidad y gasto anterior → misma descripción/muestra → rangos y razones → elección entre recurso/conjunto/ninguno → comprensión de sats → contraste con costos. Si se necesita, probar equivalencia informativa en USD con referencia y fecha explícitas; no es una función implementada ni un cambio de moneda autorizado por esta investigación. Una encuesta más amplia requiere diseño de muestra propio. Con entrevistas pequeñas no declarar precio óptimo ni demanda representativa.

### Recomendación provisional

Conservar contenido gratuito y muestras junto con compras individuales como hipótesis principal. Evaluar membresía para consumo frecuente. Diferenciar BTC.EDU por utilidad de las unidades educativas, claridad y continuidad del acceso; no afirmar que las compras individuales son una innovación inexistente en otras plataformas.

Compras repetidas: probar biblioteca/continuación y descubrimiento pertinente, sin recompras. La regla provisional de compra conjunta parcialmente adquirida sigue vigente y debe observarse en sesiones. No introduce descuentos, fondos reales, publicidad, comisiones o cobros automáticos.

Pendientes: participantes, aceptación de precios, producción autorizada de catálogo, disponibilidad de servicios y presupuesto operativo. Estas condiciones impiden una recomendación comercial definitiva.

<a id="16-validacion-con-usuarios"></a>

## Validación con usuarios

Origen: `strategy/16-validacion-con-usuarios.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Instrumentos preparados el 5 de octubre de 2026. **No hay participantes reclutados, entrevistas realizadas ni resultados externos registrados.** Las cantidades, tiempos y criterios siguientes son propuestas del equipo; no estimaciones representativas ni estándares impuestos por CUBO+.

### Preguntas

| Hipótesis | Evidencia que buscaremos | Qué podría cuestionarla |
|---|---|---|
| Comprar una unidad responde a una necesidad concreta | Experiencias recientes y elección ante alternativas | Lo gratuito o el curso completo resuelve mejor la necesidad |
| La oferta explica lo que se adquiere | Explicación correcta de precio, inclusiones y extras antes de pagar | Compra bajo una interpretación equivocada |
| El pago simulado y la biblioteca son comprensibles | Tareas sin ayuda y recuperación en otra sesión | Confusión de estados o acceso perdido |
| El creador puede preparar una oferta sostenible | Material existente, costos, mantenimiento y uso del editor | No puede ofrecerlo por separado o su costo supera el beneficio previsto |

La documentación de plataformas sustenta posibilidades de diseño, no estas hipótesis. Entrevistas exploran experiencias; tareas observan interacción; precios recogen percepción; ninguno por sí solo acredita demanda. [Monetización y muestras](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras).

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

Instrumentos actualizados el 12 de octubre de 2026; ejecución externa pendiente. Pedir al alumno que explique las condiciones antes de empezar, responda parcialmente, guarde, salga y retome. Observar si distingue preguntas respondidas de respuestas correctas y si entiende que navegar no guarda. Pedir que revise una respuesta, encuentre una pendiente, entregue y explique la nota y el siguiente paso. Con creadores, observar configuración de reglas, edición de una pregunta plegada, incorporación de otra y autorización adicional con motivo. Registrar ayudas, errores, dudas y versión, incluyendo móvil y teclado. Las comprobaciones técnicas registradas en la entrega de UI no cuentan como sesiones con participantes.

<a id="14-trazabilidad-y-backlog"></a>

## Trazabilidad y trabajo pendiente

Origen: `strategy/14-trazabilidad-y-backlog.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Base de esta revisión

Matriz inicial preparada el 7 de octubre de 2026. Se consultaron los dos originales de CUBO+ en `docs`, los criterios de 03/08/10 y los registros técnicos. La base documental está integrada en `main` mediante `d0bb7e4`; esta revisión continúa en `business/teorica`. No se reejecutaron pruebas ni se realizaron sesiones con personas.

«Registrado» significa que existe evidencia técnica anterior relacionada; no certifica que cada criterio se haya auditado individualmente. «Parcial» identifica una diferencia o cobertura incompleta. «Pendiente» indica diseño sin entrega acreditada. D04 permanece abierto hasta vincular pruebas específicas, comprobar recorridos y revisar toda la cobertura contra la versión final.

### Requisitos de los originales

| ID | Exigencia | Regla o documento | Evidencia disponible | Brecha y tarea |
|---|---|---|---|---|
| O-01 | Usuario, oportunidad e impacto local | 01, 07, 19 | Hipótesis y análisis documental | D02/D08: contrastar con alumnos y creadores de El Salvador |
| O-02 | Comparar suscripción, publicidad, freemium y micropagos | 13 | Comparación y fuentes del 5 de octubre | D03: contrastar recomendación con usuarios y costos |
| O-03 | Muestras, precios y contenido | 02, 13 | Catálogo ficticio y muestras propuestas | D03/D10: probar comprensión y documentar derechos de activos |
| O-04 | Descubrimiento, pago y desbloqueo con estados completos | 03, 04, AC-01…20 | Registros de comercio y experiencia de compra del 4 de octubre | D05/D08: tareas observadas y estados alternativos |
| O-05 | Persistencia, recompra y datos mínimos de usuario | 03, 08, 13 | Cuentas separadas, biblioteca y derechos por versión | D08: comprobar recuperación y comprensión de compra parcial |
| O-06 | KPIs de conversión, consumo, pago y retención | 05, 19 | Paneles y consultas probados en core/test_analytics.py; entrega del 10 de octubre | D07: extender reproducción/muestras y retención cuando se definan; no reconstruir visitas históricas |
| O-07 | Wireframes/prototipo y prueba de concepto funcional | 04, 10, 11 | Aplicación y capturas en src/docs/evidence | D05: enlazar tareas y aceptación; identificar contribuciones de Business |
| O-08 | Recursos gratuitos/protegidos y control en servidor | 03, AC-01…06 | Registros de versiones/archivos y comercio | D04: enlazar pruebas específicas de entrega directa y permisos |
| O-09 | Facturas simuladas, confirmación y base de acceso | 03, AC-08…17 | Comercio, FakeWallet y concurrencia registrados | D04/D12: verificar recuperación tras reinicio; documentar supervisión |
| O-10 | Administración de transacciones y actividad; eventos del embudo | 03, 05 | Panel administrativo, ActivityEvent y compras; permisos, cohortes y HTTP verificados el 10 de octubre | Implementado el panel esencial; mantener límites de eventos y probar capacidad antes de operación pública |
| O-11 | Diseño adaptable | AC-19, UX-08 | Capturas y recorridos escritorio/móvil | D05: auditoría de teclado y dispositivos; no inferirla de capturas |
| O-12 | API, arquitectura, pruebas, límites y futuro Bitcoin/Lightning | src/README.md, src/docs | Documentación y resultados fechados | D04/D12: revisar correspondencia con versión demostrada |
| O-13 | Operación, mantenimiento y recursos | 12, 13 | Referencias de costos y límites operativos | D09: presupuesto completo, responsables y procedimientos |
| O-14 | Evolución diaria y colaboración; Google Doc con historial | 06 | Commits existentes y bitácora local | D01/D11: confirmar equipo; usuario incorpora texto y comparte enlace; no reconstruir historial |
| O-15 | Manuales y reportes claros | 06, src/docs | Reportes técnicos | D12: manuales probados por otra persona |
| O-16 | PDF estratégico, TXT de repositorio público y demo de 10 minutos | 19, original de evaluación | Informe progresivo y exportación copiable | D13: PDF/anexos, acceso público y ensayo; confirmar plazo contradictorio 3/8 de noviembre |

### Responsabilidad actual

Caleb asume todas las tareas de Business y Dev por confirmación del 7 de octubre. Las funciones de la tabla describen el tipo de trabajo, no integrantes adicionales. La capacidad semanal está por definir y el requisito oficial de cuatro personas requiere aclaración con CUBO+.

### Orden de trabajo

| Tarea | Prioridad | Resultado de cierre | Función propuesta |
|---|---|---|---|
| T-01 | P0 | Horas disponibles y alcance de mentoría confirmados; condición de equipo aclarada | Caleb (Business + Dev) |
| T-02 | P0 | AC/UX enlazados a pruebas o a una brecha explícita, con versión | Business + Dev |
| T-03 | P0 | Contrato de eventos y cobertura del panel administrativo, con consultas verificables | Dev + Business |
| T-04 | P0 | Políticas de evaluaciones/certificados y preguntas listas para estimación | Business + Dev |
| T-05 | P1 | Consentimiento, reclutamiento y sesiones reales; hallazgos separados de hipótesis | Business |
| T-06 | P1 | Escenarios de costos, catálogo con derechos y procedimientos operativos | Business + Dev |
| T-07 | P1 | Manuales y recorrido de mentoría comprobados contra la versión disponible | Business + Dev |
| T-08 | P2 | Informe consolidado, PDF revisado, enlaces accesibles y demo ensayada | Equipo |

La analítica administrativa pertenece al núcleo oficial. Evaluaciones, certificados, comunidad y membresías son ampliaciones del equipo; su prioridad debe considerar las brechas oficiales antes de comprometer nuevas fechas.

### Criterios de producto y experiencia

Cada fila conserva el escenario y aceptación originales. La columna final indica el registro relacionado y la comprobación que falta; no constituye una nueva ejecución.

| ID | Escenario | Aceptación | Estado documental y siguiente comprobación |
|---|---|---|---|
| AC-01 | Explorar un curso gratis | Todas sus lecciones gratuitas abren sin cuenta | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-02 | Curso gratis con capítulo de pago | Lo gratuito sigue disponible; el capítulo se compra y abre por separado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-03 | Material de pago de un curso gratis | Se compra el archivo sin exigir comprar el curso | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-04 | Comprar video individual | Se abre el video completo sin comprar otros contenidos | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-05 | Comprar curso completo | Se conceden todos los recursos enumerados y ningún extra excluido | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-06 | Pedir texto, video o archivo de pago sin compra | El servidor deniega entrega, incluso por URL directa | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-07 | Comprar sin iniciar sesión | Se solicita cuenta y se conserva el destino | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-08 | Confirmar factura válida | Paid y acceso automático a los recursos correctos | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-09 | Fallo, pendiente o vencimiento | No hay permisos nuevos; reintento según elegibilidad | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-10 | Repetir confirmación | Una sola compra, permisos sin duplicados y un evento de pago | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-11 | Reiniciar y volver a iniciar sesión | Compras y permisos permanecen; pendientes se concilian sin conceder acceso indebidamente | Parcial: persistencia y comando de conciliación registrados; no se probó reinicio de LNbits durante transacción. T-02/T-07: verificar reinicio y supervisión. |
| AC-12 | Entrar desde otro navegador | Se recuperan cursos y compras | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-13 | Consultar facturas de otra cuenta | Acceso denegado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-14 | Tener parte de un curso de pago | Se bloquea compra conjunta y se ofrecen capítulos faltantes | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-15 | Confirmaciones concurrentes con solapamiento | Solo la primera elegible concede permisos; la otra falla | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-16 | Confirmar después del plazo | Expired, sin permisos nuevos | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-17 | Cambiar precio después de facturar | Se conserva el importe facturado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-18 | Entrar a administración como comprador | Acceso denegado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-19 | Usar móvil y escritorio | Catálogo, lecciones, video, compras y biblioteca funcionan | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-20 | Ocultar contenido comprado | Sigue disponible para su comprador | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-21 | Retomar en otro dispositivo | Misma posición guardada y lecciones completadas | Parcial: completadas y continuación por lección; segundos de video no implementados. T-02/T-04: separar aceptación y tarea restante. |
| AC-22 | Abrir curso gratuito | Inscripción sin compra; extras de pago siguen identificados | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-23 | Enviar evaluación | Nota calculada en servidor; intento registrado y límite aplicado | Implementado: evaluaciones por versión, corrección, límites e historia. learning/tests.py y learning/test_essential.py; entrega del 7 de octubre y regresión del 10. |
| AC-24 | Comprar curso sin terminarlo | No se emite certificado | Implementado: comprar/inscribirse no basta. test_certificate_requires_completion_and_approval_not_only_enrollment; entrega del 10 de octubre. |
| AC-25 | Completar requisitos y repetir solicitud | Un certificado verificable por alumno y versión | Implementado: credencial única, PDF y verificación voluntaria. Pruebas de reintento/privacidad y verify-essential-concurrency.py; recorrido HTTP del 10 de octubre. |
| AC-26 | Creador modifica curso ajeno | Acceso denegado | Registrado: estudio de creadores del 3 de octubre. T-02: enlazar permisos y revisión congelada. |
| AC-27 | Enviar borrador a revisión | No es público hasta aprobación; observaciones visibles al autor | Registrado: estudio de creadores del 3 de octubre. T-02: enlazar permisos y revisión congelada. |
| AC-28 | Reportar comentario | Moderación autorizada con registro; terceros no leen espacio restringido | Implementado: comunidad por versión, reportes, ocultación/cierre y suspensión reversible con motivo e historial. learning/test_community.py y verify-community-concurrency.py; entrega del 10 de octubre. |
| AC-29 | Activar membresía mediante pago | Acceso temporal solo al contenido incluido | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-30 | Cancelar renovación | Acceso hasta fin del periodo; no se crea renovación posterior | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-31 | Vencer membresía con compra individual | Compra, progreso y certificado permanecen | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-32 | Repetir confirmación de renovación | Un solo periodo añadido | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-33 | Cambiar temario después de certificado | Certificado conserva su versión y requisitos cumplidos | Implementado: requisitos y evidencia congelados por versión. test_certificate_name_and_course_version_remain_after_edits y prueba de edición de políticas; entrega del 10 de octubre. |
| AC-34 | Recuperar contraseña | Token vence y no se reutiliza; no se revelan claves | Registrado: cuentas independientes del 3 de octubre; correo público pendiente. T-02/T-06: enlazar tokens y verificar entrega antes de operación pública. |
| AC-35 | Pregunta y respuesta por lección | Alumno ve respuesta y aviso; creador ve su bandeja | Implementado: preguntas privadas, bandeja del creador y avisos. Pruebas de acceso/reintentos/lectura/CSRF y formularios HTTP; entrega del 10 de octubre. |
| UX-01 | Filtrar por tema/nivel, abrir y regresar | Contexto conservado y resultados coherentes | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-02 | Elegir desde el selector | Misma ficha, precio y acceso que el catálogo | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-03 | Buscar tutorial y finalizarlo | Resultado práctico claro, progreso guardado con cuenta | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-04 | Abrir referencia externa y recurso propio | Origen/acción diferenciados; protección solo donde corresponde | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-05 | Encontrar curso mixto en filtro gratis | Se entiende qué está gratis y qué se compra | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-06 | Comprar video reutilizado en una lección | Un permiso abre el mismo recurso; no exige nueva compra | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-07 | Retirar un curso adquirido del catálogo | Sigue accesible en la versión comprada; borradores ajenos siguen ocultos | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-08 | Usar selector, pago y temario con teclado y móvil | Sin controles inaccesibles ni pérdida de selección | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-09 | Perder conexión o sesión al guardar avance | Aviso recuperable; no se anuncia éxito inexistente | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-10 | Actualizar temario/nota mínima | Inscripción y certificado anteriores conservan versión | Implementado para inscripción, evaluaciones y certificado: versiones y reglas históricas inmutables. Pruebas de edición y evidencia en esenciales-2026-10-10.md. |
| UX-11 | Navegar sin resultados o con archivo ausente | Mensaje y siguiente acción útil, sin botones engañosos | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-12 | Recibir evidencia tardía o solapada de pago de prueba | Incidencia conservada, sin permiso indebido ni compra duplicada | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |

### Auditoría de la entrega esencial

Al 10 de octubre, O-06/O-10 y T-03 disponen de paneles de creador/administración, fuentes ORM, ActivityEvent y pruebas específicas en core/test_analytics.py. No se cierra cobertura completa de eventos: reproducción/muestras y retención automática siguen pendientes. T-04 queda cubierto para evaluaciones/certificados/preguntas mediante 15; comunidad y membresías conservan diseño pendiente. 179 pruebas pasan, con concurrencia y evidencia HTTP de formularios y permisos. [Registro y capturas](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). El resto de criterios parciales conserva sus brechas: esta entrega no acredita auditoría completa de teclado, reinicio transaccional de LNbits ni usuarios externos.

### Huellas de certificados

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital ni un registro en Bitcoin.

Implementado y verificado el 10 de octubre. [Contrato, privacidad, migración y pruebas](../src/docs/operacion-y-bitacora.md#certificados-sha256-2026-10-10). La exportación permite recalcular exactamente los bytes JSON; no representa el hash de todo el PDF.

### Perfiles y comunidad

Entrega del 12 de octubre de 2026 sobre `main`, base `4000ed5`, con cambios locales. Estudiantes con alias, presentación e intereses, perfil privado por defecto y compartición reversible. Creadores con ficha y catálogo existentes integrados en Personas y conversaciones. Comunidad por versión con búsqueda que respeta ocultación, filtros y seguimiento con avisos internos. Cubre ampliación de AC-28 sin abrir espacios a terceros ni publicar información académica privada. 227 pruebas, Ruff, migraciones y cuatro controles de concurrencia; 35 pruebas específicas repetidas tras ajustes. [Contrato y evidencia](../src/docs/operacion-y-bitacora.md#perfiles-y-comunidad-2026-10-12). Verificación de correo, preferencias de avisos, soluciones, apelaciones y operación pública siguen pendientes. Este registro no convierte preparación de instrumentos en sesiones con usuarios.

### Conversaciones en lecciones

Entrega del 12 de octubre de 2026 en `main`, base `4000ed5`, cambios locales. Amplía AC-28 y el acompañamiento de AC-35 con comentarios compartidos ligados a una lección y versión; conserva las preguntas privadas. Incluye respuestas, seguimiento, avisos al creador y permisos de lección en lectura, búsqueda, reportes, respuestas y notificaciones. [Diseño y criterios](investigacion-y-requisitos.md#20-comunidad-en-lecciones) y [verificación técnica](../src/docs/operacion-y-bitacora.md#comunidad-en-lecciones-2026-10-12). Marcar soluciones, destacar respuestas y evaluar utilidad con participantes siguen pendientes.

### Evidencia del recorrido de aprendizaje

Entrega del 12 de octubre de 2026: continuidad compartida entre ficha y biblioteca, inscripción para empezar, estados del temario, práctica/solución, lectura enfocada, filtros y precios por unidad. Se verificaron 39 pruebas enfocadas, la recuperación del cliente y cuatro controles de concurrencia. Las capturas usan cuentas temporales; las sesiones externas siguen pendientes. El chequeo general de esta tarea registró seis incidencias en cambios concurrentes de cuentas/creadores, por lo que no acredita verificación global. [Comportamiento, respaldo, resultados y límites](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12).

<a id="03-especificacion-funcional"></a>

## Especificación funcional

Origen: `strategy/03-especificacion-funcional.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

**Referencia vigente de estructura, 2 de octubre de 2026:** [arquitectura y experiencia](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu). Incorpora tutoriales y biblioteca de referencias/recursos, selector por tema/nivel, versiones y reglas de disponibilidad. Se conservan AC-01…35. Archivar para descubrimiento no equivale a convertir en borrador ni retirar acceso adquirido; evidencia de pago tardío o solapado se conserva para conciliación aunque no conceda permisos. El diseño no demuestra implementación.

### Plataforma y cuentas

La investigación del 5 de octubre se incorpora en [13](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) y [16](investigacion-y-requisitos.md#16-validacion-con-usuarios). Mantiene AC-01…35 y reglas vigentes. Publicidad, tarifas externas o equivalencia USD son investigación/propuestas de prueba, sin introducir funciones ni cambiar ofertas, acceso permanente o proveedor. Auditar cobertura analítica antes de informar resultados del embudo.

El sitio incluye catálogo de cursos y contenidos, páginas de cursos con capítulos y lecciones ordenados, reproductor de video, materiales descargables, cuenta, pago, Mis cursos y compras, y administración. Permite filtrar por formato, tema y contenido gratuito o de pago.

El visitante explora cursos, abre contenidos gratuitos y ve muestras sin cuenta. Para comprar se registra con correo y contraseña. Al iniciar sesión desde otro dispositivo recupera sus compras. La recuperación de contraseña se implementa con un token de un solo uso y correo configurable según el documento 08. La verificación de correo para publicación pública se definirá al configurar el despliegue; las pruebas usan cuentas ficticias.

Los creadores aprobados tienen perfil y panel para crear y gestionar su propio contenido. El administrador revisa las publicaciones. El comprador no puede consultar compras o facturas ajenas ni acceder al panel. Ser administrador no equivale a tener una compra.

### Cursos y compras

Un curso organiza capítulos, lecciones, videos y materiales. Cada recurso tiene formato y condición gratuita o de pago. Los capítulos pueden agrupar varias lecciones y videos. Un video puede venderse individualmente. El usuario no debe comprar un curso para comprar un video individual o un material que se ofrece por separado.

Las ofertas de curso completo o capítulo enumeran los recursos incluidos. Los materiales adicionales pueden quedar fuera y venderse aparte. Las relaciones del catálogo se distinguen de los permisos: estar asociado a un curso no concede acceso por sí mismo.

Cada compra concede permisos permanentes a los recursos incluidos. Una oferta completamente adquirida muestra enlaces para abrir su contenido. Si una oferta de curso o capítulo está parcialmente adquirida, su compra conjunta queda bloqueada y se ofrecen los contenidos faltantes que tengan oferta individual. El catálogo de prueba garantiza esas ofertas. No hay descuentos personalizados.

Los permisos, compras y fechas se conservan en la base de datos. Las versiones publicadas conservan su composición para compras existentes; nuevas versiones y sus condiciones se gestionan según el documento 08.

### Facturas y LNbits

LNbits con FakeWallet genera y verifica pagos internos de prueba. No se transfieren fondos reales. Las claves se usan únicamente en el servidor de la plataforma.

La factura pertenece a una cuenta y una oferta: curso, capítulo, video o material. Guarda una copia del importe y los recursos incluidos. Cambiar el precio no modifica facturas existentes.

Estados: Pending, Paid, Expired y Failed. Nace Pending, vence en 15 minutos y solo puede pasar a un estado terminal. Una cuenta solo mantiene una factura Pending vigente por oferta; solicitar otra devuelve la existente.

El servidor verifica propietario, plazo y pago. La confirmación válida concede acceso automáticamente, en una operación que no puede duplicar compras, permisos ni eventos. El navegador no concede permisos.

Antes de crear y confirmar una factura se comprueba lo ya adquirido. Ante solapamiento por compras concurrentes, la segunda factura falla sin conceder permisos. Esta regla está diseñada para la simulación; una integración real debe resolver los cobros confirmados antes de aplicar bloqueos comerciales.

La demostración permite confirmar, fallar y expirar mediante controles claramente identificados. El vencimiento también se aplica por tiempo. FakeWallet no resuelve por sí sola todos los estados ni la recuperación de pendientes tras reiniciar: se debe implementar y probar en el servicio de pagos de la plataforma.

Un fallo o vencimiento permite reintentar con una nueva factura si la oferta sigue siendo elegible. Un error de conexión permite consultar la misma factura; no se presume fallo ni se crea otra automáticamente.

### Protección de contenido

El servidor verifica permiso antes de entregar textos, videos completos y descargas de pago. No se incluyen en HTML público, datos iniciales ni archivos estáticos accesibles sin autorización. El reproductor obtiene el video a través de una ruta protegida que permite reproducción y solicitudes parciales. Las muestras públicas usan contenido separado. No se promete impedir que un comprador copie lo que ya puede ver.

### Administración

Crear y editar cursos, orden de capítulos y lecciones, textos, videos, archivos, descripciones, muestras, precios y visibilidad. Validar formato y tamaño de archivos. Los archivos de pago se guardan fuera del almacenamiento público.

Ocultar contenido lo retira del catálogo pero conserva el acceso de quienes lo compraron. No se eliminan recursos adquiridos. El panel muestra facturas, cuenta compradora, oferta, importe, estado y fecha; permite filtrar por estado y consultar actividad y métricas. No muestra contraseñas ni claves de LNbits.

### Criterios de aceptación

| ID | Escenario | Resultado |
|---|---|---|
| AC-01 | Explorar un curso gratis | Todas sus lecciones gratuitas abren sin cuenta |
| AC-02 | Curso gratis con capítulo de pago | Lo gratuito sigue disponible; el capítulo se compra y abre por separado |
| AC-03 | Material de pago de un curso gratis | Se compra el archivo sin exigir comprar el curso |
| AC-04 | Comprar video individual | Se abre el video completo sin comprar otros contenidos |
| AC-05 | Comprar curso completo | Se conceden todos los recursos enumerados y ningún extra excluido |
| AC-06 | Pedir texto, video o archivo de pago sin compra | El servidor deniega entrega, incluso por URL directa |
| AC-07 | Comprar sin iniciar sesión | Se solicita cuenta y se conserva el destino |
| AC-08 | Confirmar factura válida | Paid y acceso automático a los recursos correctos |
| AC-09 | Fallo, pendiente o vencimiento | No hay permisos nuevos; reintento según elegibilidad |
| AC-10 | Repetir confirmación | Una sola compra, permisos sin duplicados y un evento de pago |
| AC-11 | Reiniciar y volver a iniciar sesión | Compras y permisos permanecen; pendientes se concilian sin conceder acceso indebidamente |
| AC-12 | Entrar desde otro navegador | Se recuperan cursos y compras |
| AC-13 | Consultar facturas de otra cuenta | Acceso denegado |
| AC-14 | Tener parte de un curso de pago | Se bloquea compra conjunta y se ofrecen capítulos faltantes |
| AC-15 | Confirmaciones concurrentes con solapamiento | Solo la primera elegible concede permisos; la otra falla |
| AC-16 | Confirmar después del plazo | Expired, sin permisos nuevos |
| AC-17 | Cambiar precio después de facturar | Se conserva el importe facturado |
| AC-18 | Entrar a administración como comprador | Acceso denegado |
| AC-19 | Usar móvil y escritorio | Catálogo, lecciones, video, compras y biblioteca funcionan |
| AC-20 | Ocultar contenido comprado | Sigue disponible para su comprador |

### Fuera de esta primera versión

Bitcoin/Lightning con fondos reales, comisiones y liquidaciones, recomendaciones automáticas, vigilancia de exámenes y descuentos personalizados. Se incluyen creación por usuarios aprobados, progreso, evaluaciones, certificados, comunidad y membresías; ver documento 08. Las renovaciones iniciales se pagan manualmente con facturas simuladas.

### Ampliación de requisitos

El documento [08](investigacion-y-requisitos.md#08-aprendizaje-creadores-y-membresias) forma parte de esta especificación: define progreso, evaluaciones, certificados, roles de creador, publicación, comunidad, membresías y criterios AC-21 a AC-35. El acceso se concede por recurso gratuito, compra permanente o membresía vigente. La inscripción gratuita no concede recursos de pago. Para compras individuales se mantienen los criterios anteriores.

<a id="05-metricas-y-validacion"></a>

## Métricas y validación

Origen: `strategy/05-metricas-y-validacion.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

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

La ronda propuesta es de seis a diez alumnos —compradores y usuarios de alternativas gratuitas— y tres a cinco creadores con material preparado/publicado. Sustituye la propuesta anterior; no hay reclutamiento realizado ni estimación estadística. Priorizar público pertinente de El Salvador y diversidad de dispositivo/pagos. Guiones y consentimiento en [16](investigacion-y-requisitos.md#16-validacion-con-usuarios).

Preguntar por la última necesidad concreta, recursos utilizados, compras anteriores, motivos para pagar o desistir y alternativas gratuitas. Explorar precios después de conocer la necesidad. Evitar presentar aceptación del concepto como compra real.

Para creadores: contenido disponible, derechos de uso, audiencia, esfuerzo de mantenimiento y preferencia entre venta de cursos, capítulos, videos y materiales.

### Pruebas de experiencia

Solicitar encontrar un recurso, explicar lo incluido, comprar con simulación, resolver una factura expirada y regresar a biblioteca. Comparar compra de curso completo, capítulo, video y material adicional, incluido un curso gratuito con compras opcionales y el caso parcialmente adquirido.

Registrar tarea, resultado, dificultad, cita autorizada y cambio propuesto. Obtener consentimiento para notas o grabaciones. Separar pruebas manuales del equipo de sesiones con participantes externos.

Clasificar sin ayuda / con ayuda / no completada / no intentada. Informar cantidades, versión y denominador por tarea, sin sumar versiones distintas. Separar observación, declaración, interpretación y decisión; reprobar cambios relevantes. La compra simulada no demuestra disposición a pagar. Explorar precios según [13](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) sin declarar precio óptimo con una muestra pequeña.

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

<a id="15-especificaciones-modulos-pendientes"></a>

## Reglas de los módulos educativos

Origen: `strategy/15-especificaciones-modulos-pendientes.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Cobertura actual

Evaluaciones entregadas el 7 de octubre. Certificados, preguntas, notificaciones internas y paneles esenciales entregados el 10 de octubre de 2026. [Implementación, rutas, pruebas y límites](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). Esta especificación registra las reglas efectivamente adoptadas; comunidad y moderación se incorporan el 10 de octubre; las membresías y el acceso temporal siguen pendientes.

### Certificados

El creador aprobado configura únicamente sus cursos. Habilitar requiere una o más lecciones incluidas; todos los cuestionarios obligatorios también deben aprobarse. La política se conserva con el envío editorial y la versión publicada. La compra individual, inscripción o pago del conjunto no emiten la credencial.

El alumno confirma su nombre y solicita emisión cuando cumple los requisitos históricos. Una inscripción concede como máximo una credencial, independiente de reintentos y concurrencia. Se conserva nombre, título, creador, fecha, versión y evidencia de lecciones e intentos. No se modifica por ediciones futuras o por cambios posteriores en progreso.

El PDF es privado. La verificación usa UUID y requiere que el titular habilite compartir; puede desactivarlo. La página compartida no divulga correo, notas ni respuestas. La administración revoca con permiso específico y motivo, preservando historial y notificando al alumno. Revocar bloquea nuevas descargas; no borra archivos ya descargados. Corregir o reemplazar nombres después de emitir queda pendiente: se exige confirmación previa y atención administrativa de incidencias.

Aceptación comprobada: requisitos pendientes no permiten emitir; todos los obligatorios se cumplen; una solicitud repetida/concurrente no duplica; borradores ajenos y revisiones antiguas no sobrescriben políticas; versiones anteriores mantienen sus datos; compartir es voluntario; terceros no descargan; revocar conserva evidencia. Pruebas en `learning/test_essential.py` y `scripts/verify-essential-concurrency.py`.

### Preguntas

Crear requiere cuenta activa de alumno, inscripción en la misma versión y acceso a la lección. Leer corresponde al alumno participante y al creador aprobado propietario. Responder requiere esos permisos; el alumno además conserva acceso al contenido. Las conversaciones son privadas, sin foro público ni permiso administrativo general por estas rutas.

Entradas de texto de hasta 2.000 caracteres, paginación, escape HTML y 30 mensajes por cuenta/hora. El historial enviado es inmutable; se corrige mediante una aclaración. La clave del formulario permite recuperar reintentos sin duplicar; otra carga con la misma clave se rechaza. No hay archivos, edición, eliminación, cierre manual ni garantía de atención. La bandeja identifica las conversaciones cuyo último mensaje espera respuesta del creador.

Aceptación comprobada: denegación por cuenta ajena, curso ajeno, falta de acceso/inscripción y suspensión; persistencia y aislamiento; reintentos/concurrencia; escape; límite y CSRF; respuesta asociada a la lección y su versión. Los permisos de lectura conservada no acreditan que existan membresías implementadas.

### Notificaciones

Cada acontecimiento genera como máximo un aviso por clave interna. Destinatario y enlace se determinan en servidor. Los eventos implementados son preguntas/respuestas, decisiones editoriales, intentos adicionales y emisión/revocación. La cuenta consulta su propia bandeja/contador; abrir y marcar leído es POST protegido y repetirlo conserva la primera fecha. Son avisos internos, sin entrega de correo ni notificaciones push.

### Paneles

El creador consulta métricas agregadas de sus contenidos. La administración exige permisos de lectura de facturas, inscripciones y actividad. Fuentes, cohortes, denominadores, periodos y cobertura están en [05](investigacion-y-requisitos.md#05-metricas-y-validacion) y el registro técnico. Se muestran ceros y ausencia de datos sin inventar resultados anteriores. Visitas, marcas manuales, aprobaciones y certificados son hechos técnicos distintos de aprendizaje comprobado.

### Límites de alcance

La entrega esencial solicitada queda implementada y verificada. Mantener separadas las ampliaciones pendientes: membresías de renovación manual de 30 días, correcciones de credenciales, reproducción medida y operación pública. Las pruebas con cuentas temporales no equivalen a sesiones con personas ni a validación de precios o demanda.

### Huellas de certificados

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital ni un registro en Bitcoin.

Implementado y verificado el 10 de octubre. [Contrato, privacidad, migración y pruebas](../src/docs/operacion-y-bitacora.md#certificados-sha256-2026-10-10). La exportación permite recalcular exactamente los bytes JSON; no representa el hash de todo el PDF.

### Comunidad y moderación

Se adopta un espacio por versión publicada y sellada, accesible a alumnos activos inscritos en esa versión y al creador aprobado propietario. La inscripción habilita comunidad, sin conceder contenidos de pago. Las versiones históricas conservan su comunidad; no hay espacios públicos ni acceso por membresía en esta entrega. La administración requiere staff y el permiso learning.moderate_community.

Conversaciones con respuestas de un nivel, texto escapado hasta 2000 caracteres, 30 publicaciones por cuenta/hora y paginación de 20. Los mensajes enviados no se editan ni borran; las correcciones son aclaraciones. Reintentos con UUID conservan un solo mensaje. Reportar requiere motivo, con un reporte por cuenta/mensaje y límite de 30 nuevos por hora. No hay archivos ni chat privado.

Ocultar/mostrar, cerrar/reabrir y descartar reportes requieren motivo e historial. Suspender escritura afecta a un alumno inscrito y una versión, preservando lectura, compras y progreso; restablecer requiere otra decisión. Ocultar una raíz impide leer sus respuestas a los alumnos, conservando acceso para moderadores. La suspensión permanece hasta revisión manual. El creador atiende reportes y la administración puede intervenir; no hay plazo garantizado, apelación por formulario ni escalamiento automático. Los avisos internos cubren respuestas al autor, reportes al creador y decisiones al participante afectado.

Aceptación y límites verificables en [registro técnico](../src/docs/operacion-y-bitacora.md#comunidad-2026-10-10), learning/test_community.py y scripts/verify-community-concurrency.py. No equivale a operación pública ni validación con personas.

<a id="20-comunidad-en-lecciones"></a>

## Comunidad en las lecciones

Origen: `strategy/20-comunidad-en-lecciones.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Decisión

El estudiante puede plantear dudas y compartir aportes al terminar una lección, dentro de su contexto de estudio. Comunidad conserva la vista central del curso. Ambas entradas muestran la misma conversación, vinculada a una lección de una versión publicada; no crean copias ni trasladan comentarios cuando se publica una versión nueva.

El patrón se contrastó con documentación oficial de [Teachable](https://support.teachable.com/en/articles/11682464-course-comments) y [Thinkific](https://support.thinkific.com/hc/en-us/articles/360030351434-On-Lesson-Discussions), consultada el 12 de octubre de 2026. Teachable documenta comentarios y respuestas dentro de lecciones; Thinkific describe discusiones habilitadas por lección. Estas referencias respaldan una decisión de diseño, no resultados educativos ni disponibilidad de un plan comercial para BTC.EDU.

### Comportamiento implementado

«Conversación de esta lección» aparece después del contenido y los controles de avance. Permite iniciar comentarios, responder en un solo nivel, seguir conversaciones y reportar mensajes. Las respuestas del creador se identifican con su rol. La pregunta privada conserva un acceso y una explicación separados.

El lector presenta cinco conversaciones por página y hasta tres respuestas recientes por conversación. «Abrir conversación» ofrece el historial paginado completo. Los envíos regresan a la conversación y a su página correspondiente. Las validaciones conservan el texto enviado; no anuncian publicación cuando existe un error. No exige participar para completar la lección.

Comunidad integra los comentarios de lecciones junto a los temas generales. Identifica la lección y permite volver a su contenido. La búsqueda y los recuentos excluyen conversaciones de lecciones sin acceso y actividad oculta para los estudiantes. El creador puede utilizar los filtros existentes para revisar conversaciones sin respuesta; ese filtro significa ausencia de respuestas de cualquier participante, no ausencia de una respuesta del creador ni solución confirmada.

### Permisos y atención

Leer o escribir requiere inscripción en la misma versión y acceso a la lección. Comprar un material adicional no desbloquea automáticamente el texto de la lección. Los visitantes y estudiantes no inscritos reciben una invitación, sin ver mensajes. El creador aprobado participa en sus cursos y la administración conserva su permiso específico de moderación.

El creador recibe un aviso interno por un nuevo comentario de lección. El autor de la conversación y sus seguidores reciben avisos por respuestas de otras personas, comprobando nuevamente los permisos de acceso. Los reintentos idénticos no duplican mensajes ni avisos. Se conservan límites de publicación, protección CSRF, escape de texto y decisiones de moderación con motivo e historial.

Ocultar, cerrar o suspender escritura mantiene las reglas de la comunidad existente. Suspender escritura permite continuar leyendo, siguiendo conversaciones y estudiando. Los temas generales anteriores conservan su contenido y no se asignan retrospectivamente a una lección.

### Evaluación pendiente

La hipótesis es que conversar junto al contenido facilitará expresar dudas y aprovechar aclaraciones previas. Falta observar con usuarios si encuentran el espacio, entienden quién lee sus mensajes y distinguen comentarios compartidos de preguntas privadas. También debe evaluarse si el creador puede atender el volumen de consultas.

Marcar soluciones, destacar aclaraciones, avisos por correo y plazos de respuesta quedan fuera de esta entrega. Una prueba técnica o una revisión con cuentas ficticias no demuestra demanda, satisfacción ni aprendizaje. La verificación y sus límites se registran en [la entrega técnica](../src/docs/operacion-y-bitacora.md#comunidad-en-lecciones-2026-10-12).

<a id="07-investigacion-y-necesidades"></a>

## Investigación de plataformas y necesidades

Origen: `strategy/07-investigacion-y-necesidades.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

La comparación funcional conserva la consulta del 1 de octubre de 2026. El 5 de octubre se amplió con [modelos, tarifas, muestras y costos](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras), y [guiones/pruebas](investigacion-y-requisitos.md#16-validacion-con-usuarios). La ausencia de comparación de precios correspondía a la consulta inicial. No se usaron cuentas externas ni se realizaron entrevistas. Las necesidades siguen siendo propuestas por validar.

### Ampliación

Las fuentes documentan coexistencia de compras y membresías, freemium y muestras por módulo. No permiten presentar la compra individual como una modalidad inexistente en el mercado. La recomendación provisional mantiene gratuito + compras individuales, validando utilidad y claridad.

Los costos distinguen suscripción del creador, precio al alumno, comisión, procesamiento y video. Un cargo fijo pesa sobre compras pequeñas; el acceso permanente requiere estimar consumo posterior y archivos históricos. No se eligió proveedor ni se fijaron precios de mercado.

Los instrumentos no producen resultados hasta ejecutarse. Fuentes comerciales y metodológicas con fecha en 13 y 16; síntesis integrada en el [documento principal](19-recomendacion-y-entrega-final.md).

### Plataformas de referencia

| Referencia | Comportamiento documentado | Aplicación propuesta |
|---|---|---|
| Udemy | Panel del instructor con organización del contenido, preparación para publicar y gestión del curso [S1] | Editor de cursos, orden de capítulos y revisión antes de publicar |
| Teachable | Finalización de lecciones, seguimiento de video y cuestionarios con nota mínima e intentos [S2] | Progreso guardado y evaluaciones configurables |
| Thinkific | Membresías que agrupan productos educativos y beneficios como comunidad [S3] | Planes con alcance y duración definidos, además de compras individuales |
| Patreon | Membresías y compras únicas de videos y otros productos [S4] | Ofrecer compra individual aunque exista una membresía |
| Udemy | Subtítulos de video mediante archivos VTT [S5] | Soportar subtítulos cargados por el creador |
| Udemy | Panel de preguntas y respuestas para instructores [S6] | Bandeja de preguntas asociadas a cursos y lecciones |
| Thinkific | Comunidades con publicaciones, comentarios y moderadores [S7, S8] | Espacios por curso o creador, con reportes y moderación |
| Teachable | Informes de lecciones completadas, videos y resultados de cuestionarios [S9] | Métricas educativas por curso y creador |
| Thinkific | Certificado disponible después de completar el curso [S10] | Certificado condicionado a requisitos de finalización |
| Patreon | Cancelar la membresía puede conservar acceso hasta terminar el periodo pagado [S11] | Separar cancelación de renovación de vencimiento del acceso |

No copiamos todas las reglas comerciales de esas plataformas. Por ejemplo, el precio de una compra de curso después de adquirir capítulos necesita una decisión propia. Las fuentes no establecen nuestra política de descuentos ni nuestros precios.

### Lado del alumno o comprador

| Momento | Necesidad propuesta | Cómo la atenderemos | Evidencia y validación pendiente |
|---|---|---|---|
| Elegir | Entender qué aprenderá, requisitos y qué incluye el precio | Objetivos, temario, muestra, formato y lista de extras | Organización del curso [S1]; probar si puede explicar lo incluido |
| Comprar | Elegir curso, capítulo, video o material sin obligación de suscribirse | Ofertas independientes, precio y acceso visible | Compras únicas y membresías coexisten [S4]; validar preferencias |
| Estudiar | Retomar una lección y un video | Continuar aprendiendo, última posición y lecciones completadas | Seguimiento educativo [S2, S9]; probar cambio de dispositivo |
| Acceder | Usar video con subtítulos y controles accesibles | VTT, teclado, velocidad y diseño móvil | Subtítulos [S5]; realizar pruebas de accesibilidad |
| Practicar | Saber qué comprende y qué necesita repasar | Cuestionarios, resultado, explicación y reglas de reintento | Evaluaciones [S2]; validar utilidad de preguntas |
| Preguntar | Resolver dudas en el contexto correcto | Preguntas por lección y respuestas del creador | Panel de preguntas [S6]; validar carga de soporte |
| Finalizar | Obtener evidencia de haber terminado | Certificado verificable según requisitos | Finalización [S10]; validar interés, sin prometer acreditación |
| Participar | Conversar con otros alumnos sin perder el contexto | Comunidad por curso o creador, búsqueda y reportes | Comunidad y moderadores [S7, S8]; validar participación |
| Administrar acceso | Entender lo comprado y cuándo vence una membresía | Biblioteca, historial, fecha de vigencia y cancelar renovación | Periodo pagado [S11]; probar comprensión de cancelación |
| Volver | Recuperar cuenta y ver novedades relevantes | Recuperación de contraseña y notificaciones internas | Propuesta propia; probar recuperación y evitar avisos excesivos |

### Lado del creador

| Necesidad propuesta | Cómo la atenderemos | Evidencia y validación pendiente |
|---|---|---|
| Presentarse | Perfil con descripción, temas y cursos publicados | Perfil de instructor y publicación [S1]; validar información necesaria |
| Preparar contenido | Borradores, capítulos ordenados, carga de video, texto, archivos y subtítulos | Organización [S1] y VTT [S5]; observar a un creador usando el editor |
| Revisar antes de publicar | Vista como alumno, lista de faltantes, envío a revisión y motivos de rechazo | Preparación de publicación [S1]; definir controles propios |
| Vender con claridad | Definir qué es gratis, qué se compra y qué incluye una membresía | Combinación de formas de venta [S3, S4]; revisar ofertas ambiguas |
| Evaluar | Crear preguntas, nota mínima, intentos y requisitos de certificado | Evaluaciones [S2, S10]; medir tiempo de preparación |
| Acompañar | Bandeja de preguntas, comentarios y notificaciones internas | Preguntas [S6]; validar disponibilidad para responder |
| Mejorar cursos | Ver avance, abandono, resultados y preguntas frecuentes | Informes [S9]; evitar confundir aperturas con aprendizaje |
| Administrar comunidad | Moderar sus espacios, reportar problemas y delegar según permiso | Moderadores [S8]; validar responsabilidades |
| Entender resultados comerciales | Facturas, compras y volumen simulado de sus ofertas | Propuesta propia apoyada en venta [S4]; sin presentar saldo ficticio como ingreso |
| Actualizar sin perjudicar compras | Versiones publicadas y conservación de lo comprado | Propuesta propia; probar cambios de temario y contenidos |

Un creador puede también ser alumno. El acceso al panel de creador no concede permisos sobre cursos de otros creadores. Solo verá datos educativos y comerciales de sus contenidos; no contraseñas ni claves de pago.

### Lo que falta comprobar con personas

Entrevistar alumnos sobre su última compra o curso real, cómo retoman, cuándo compran solo un video, dificultades al pagar, utilidad de evaluaciones y certificados y preferencia entre membresía y compra individual. Entrevistar creadores sobre publicación actual, estructura de materiales, respuesta a preguntas, derechos de contenido, actualización y métricas utilizadas.

Probar tareas en un prototipo: distinguir gratuito y comprado; comprar un video; entender extras del curso; retomar en otro dispositivo; consultar una duda; completar evaluación; cancelar membresía sin perder compras. Con creadores: preparar un curso, añadir material, configurar oferta, enviar a revisión y responder una pregunta. Registrar hallazgos reales y cambios derivados; no inventar resultados.

### Fuentes oficiales

- S1: [Udemy — panel de gestión de cursos](https://support.udemy.com/hc/en-us/articles/230048607-How-to-Navigate-the-Course-Management-Dashboard)
- S2: [Teachable — requisitos de finalización](https://support.teachable.com/en/articles/11682463-course-compliance)
- S3: [Thinkific — crear una membresía](https://support.thinkific.com/hc/en-us/articles/360052568634-Create-a-Membership)
- S4: [Patreon — membresías y compras únicas](https://support.patreon.com/hc/en-us/articles/16263061573645-Get-started-on-Patreon)
- S5: [Udemy — subtítulos para videos](https://support.udemy.com/hc/en-us/articles/229605428-Adding-Captions-to-Your-Videos)
- S6: [Udemy — panel de preguntas y respuestas](https://support.udemy.com/hc/en-us/articles/229606328-Instructor-Q-A-Dashboard)
- S7: [Thinkific — comunidades](https://support.thinkific.com/hc/en-us/articles/7265849758999-Get-Started-with-Thinkific-Communities)
- S8: [Thinkific — moderador de comunidad](https://support.thinkific.com/hc/en-us/articles/7897629454871-Community-Moderator-Role)
- S9: [Teachable — informes educativos](https://support.teachable.com/en/articles/11682570-course-reporting-tools)
- S10: [Thinkific — probar certificados](https://support.thinkific.com/hc/en-us/articles/360060666253-How-can-I-create-a-test-certificate)
- S11: [Patreon — cancelar membresía](https://support.patreon.com/hc/en-gb/articles/360005502572-Cancelling-a-paid-membership)

<a id="10-arquitectura-y-experiencia-btc-edu"></a>

## BTC.EDU — arquitectura de producto y experiencia

Origen: `strategy/10-arquitectura-y-experiencia-btc-edu.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Definición de trabajo del **2 de octubre de 2026**, El Salvador. Orienta las siguientes implementaciones; no acredita que las funciones descritas ya existan. El usuario confirmó cursos, tutoriales y recursos en la primera versión, y eventos después. Las reglas anteriores de compras simuladas, acceso permanente, revisión por administrador y membresías manuales se conservan. Las decisiones nuevas de organización y comportamiento son la base propuesta para desarrollar y validar, no resultados de entrevistas.

**Estado de implementación al 4 de octubre:** cuentas independientes, aprobación/perfil, estudio/editor/archivos, revisión, versiones, ofertas y compras simuladas, biblioteca, inscripción y progreso básico ya funcionan. 129 pruebas pasan. [Entrega y límites verificados](../src/docs/operacion-y-bitacora.md#comercio-y-aprendizaje-2026-10-04). Evaluaciones, certificados, preguntas, comunidad, membresías y métricas completas permanecen pendientes; las secciones siguientes definen el horizonte del producto.

### 1. Producto y referencia

La investigación incorporada el 5 de octubre en [13](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) conserva gratuito + compras individuales como hipótesis principal. Los [instrumentos](investigacion-y-requisitos.md#16-validacion-con-usuarios) probarán inclusiones, unidades, pago, recuperación y compra parcial. No alteran reglas de arquitectura ni acreditan demanda. Presupuestar consumo gratuito, acceso permanente y archivos históricos antes de operación pública.

BTC.EDU será una academia donde una persona puede encontrar contenido adecuado, entender qué aprenderá y qué incluye el acceso, estudiar a su ritmo y retomar su avance. Los micropagos permiten adquirir capítulos, videos o materiales sin obligar a comprar un curso entero. Coexisten cursos gratuitos, muestras gratuitas, compras permanentes y, en una fase posterior, membresías temporales.

Las cuatro capturas suministradas muestran: catálogo por temas con tarjetas y filtros; selector tema → nivel → curso con resumen; tutoriales por categoría con búsqueda; biblioteca de recursos por tipo. También muestran navegación lateral persistente y pestañas propias de cada sección. Son evidencia de esas pantallas de escritorio. No permiten afirmar cómo funcionan progreso, pagos, administración, certificados ni móvil en Plan B Academy.

Tomamos de la referencia la organización, jerarquía y continuidad de navegación. Conservamos la dirección visual aprobada de BTC.EDU: blanco cálido, negro, naranja discreto, tipografía legible e identidad industrial. No se copian marcas ni ilustraciones de la referencia.

El nombre BTC.EDU no cambia automáticamente el público o los temas ya propuestos en el documento 01. La temática editorial definitiva debe validarse; Bitcoin, tecnología o programación son datos de catálogo, no categorías codificadas en la aplicación. Se inicia en español. La traducción completa es posterior y requiere traducir también los contenidos, no solo añadir un selector de idioma.

### 2. Alcance y orden

| Entrega | Funciones | Condición de cierre |
|---|---|---|
| Primera academia funcional | Cursos, selector, tutoriales, recursos, registro/recuperación, texto/video/archivos, ofertas y compra simulada, biblioteca, inscripción y progreso básico, administración | Encontrar → abrir o comprar → estudiar → retomar en otra sesión; sin pérdida de permisos |
| Operación por creadores | Perfil, solicitud/aprobación, editor, cargas, revisión, versiones y métricas propias | Un creador prepara contenido y un administrador lo publica sin alterar compras previas |
| Aprendizaje ampliado | Evaluaciones, certificados, preguntas y notificaciones | Intentos y requisitos verificables; respuestas contextualizadas |
| Relación continua | Comunidad, moderación y membresías de 30 días con renovación manual | Acceso temporal, compras y progreso conviven correctamente |
| Ampliaciones posteriores | Eventos, reseñas, rutas editoriales más avanzadas e idiomas | Datos, responsable operativo y validación para cada función |

Progreso, evaluaciones, certificados, comunidad y membresías siguen dentro del alcance completo del documento 08; escalonarlos no los elimina. Eventos y reseñas amplían el horizonte, sin convertirse en requisito de la primera entrega. No se promete una fecha para toda la lista antes de revisar capacidad. Los eventos de actividad del assignment son registros del sistema y siguen en la primera entrega; son distintos del futuro calendario de eventos educativos.

No se incluyen fondos reales, liquidaciones a creadores, descuentos personalizados, chat privado, vigilancia de exámenes ni recomendaciones mediante IA en esta etapa.

### 3. Navegación y superficies

La portada pública explica la propuesta y conduce a aprender. El interior de la academia usa una estructura común: encabezado compacto, navegación lateral en escritorio, área principal y navegación local de la sección. La lectura prioriza el contenido y permite plegar la navegación global para dejar espacio al temario.

```mermaid
flowchart TD
    I[Inicio] --> C[Cursos]
    I --> T[Tutoriales]
    I --> R[Recursos]
    C --> CA[Todos los cursos]
    C --> S[Selector: tema y nivel]
    CA --> F[Ficha y temario]
    S --> F
    F --> E[Estudiar]
    F --> P[Oferta y pago simulado]
    P --> E
    T --> E
    R --> D[Ficha, lectura, descarga o enlace externo]
    M[Mi aprendizaje] --> E
    E --> M
    CR[Panel de creador] --> REV[Revisión y publicación]
    REV --> C
    REV --> T
    REV --> R
```

| Área | Navegación local | Visibilidad |
|---|---|---|
| Cursos | Todos / Selector | Pública |
| Tutoriales | Todos / categorías disponibles | Pública |
| Recursos | Todos / tipos disponibles | Pública |
| Mi aprendizaje | Continuar / cursos / tutoriales / recursos guardados | Cuenta |
| Compras y acceso | Compras / facturas / membresías cuando existan | Cuenta |
| Cuenta | Perfil / contraseña / preferencias de privacidad | Cuenta |
| Crear | Contenidos / revisión / preguntas / métricas según fase | Creador aprobado |
| Administración | Publicación / cuentas / facturas / moderación | Personal autorizado |

Certificados se agregan a Mi aprendizaje cuando la función esté lista. Comunidad y eventos aparecen al disponer de la función y contenido operable. La navegación no ofrece enlaces que solo conducen a promesas.

En móvil: menú global plegable con foco controlado, encabezado breve, tarjetas en una o dos columnas según espacio, filtros desplegables y temario accesible desde la lección. Las pestañas pueden desplazarse horizontalmente; la página no debe exigir desplazamiento horizontal. El selector pasa de tres columnas a pasos tema → nivel/curso → resumen, conservando selección y regreso.

### 4. Qué es cada contenido

| Concepto | Uso y relación |
|---|---|
| Tema | Clasificación principal configurable; puede tener subtemas. Un curso tiene un tema principal y etiquetas complementarias |
| Nivel | Principiante, intermedio o avanzado; es un requisito editorial, no una medida de progreso del alumno |
| Curso | Recorrido amplio con objetivos, requisitos, capítulos y lecciones; puede combinar gratis y pago |
| Tutorial | Guía breve orientada a una tarea concreta; reutiliza capítulos/lecciones, lectura y progreso; tiene catálogo propio |
| Capítulo | Agrupación ordenada de lecciones; puede tener una oferta que enumera lo incluido |
| Lección | Unidad de aprendizaje con texto, video, materiales relacionados y posteriormente evaluación |
| Recurso propio | Video independiente, guía, ejercicio o archivo alojado; puede estar vinculado a varios contenidos sin duplicar el archivo |
| Referencia externa | Libro, proyecto, podcast, canal, artículo u otro enlace curado; no es un archivo vendido ni protegido por BTC.EDU |
| Archivo | Video, documento, imagen, subtítulo o muestra; su ubicación técnica no determina el precio ni el permiso |
| Oferta | Condiciones de compra e inventario exacto de recursos incluidos; no es el temario |
| Inscripción | Relación del alumno con una versión de curso o tutorial para conservar aprendizaje |
| Permiso | Derecho de abrir un recurso por compra permanente o acceso temporal |

El tutorial se implementará como variante del recorrido educativo existente, no como un segundo motor de aprendizaje. Un video vendido individualmente y mostrado en una lección apunta al mismo recurso protegido: comprarlo una vez concede acceso a ese mismo video donde aparezca.

Los enlaces externos indican origen y que se sale de BTC.EDU; no se bloquean ni se venden como si fueran archivos propios. Una descarga propia asociada a un curso indica si es gratis, incluida en la compra o extra. Un recurso guardado no equivale a un recurso comprado.

### 5. Descubrir y elegir

#### Catálogo de cursos

Tarjeta: portada original o autorizada, título, resumen breve, creador, nivel, duración estimada y acceso/precio. El distintivo “Empieza aquí” es una selección editorial explícita. No se inventan duraciones, estrellas, alumnos o resultados. La duración puede sumar minutos de video y lectura estimada; se etiqueta como estimación, diferenciando tiempo de video.

Vista inicial: grupos por tema con una selección editorial y enlace “Ver todos”. Cada grupo usa una retícula o fila navegable con controles accesibles, sin reproducción automática. La vista de un tema o búsqueda usa resultados paginados; en la primera implementación preferimos retícula para que el descubrimiento no dependa de un carrusel.

Filtros combinables: tema, nivel, formato de lecciones, acceso y búsqueda. Orden inicial editorial en la portada del catálogo; resultados por relevancia sencilla o título y opción de recientes. Los filtros y la página quedan en la URL, se pueden compartir, y volver desde una ficha conserva el contexto. “Limpiar filtros” y número de coincidencias visibles.

Acceso describe tres situaciones: “Todo gratis”, “Gratis con extras” y “De pago · muestra gratis” si existe muestra. Una etiqueta “Desde X sats de prueba” solo aparece cuando existe una oferta activa que la justifica; junto a ella se aclara si es precio del curso, capítulo o extra. El filtro gratis no debe hacer pasar un curso mixto por totalmente gratuito.

#### Selector de cursos

Otra presentación del mismo catálogo: tema, cursos agrupados por nivel y resumen del curso seleccionado. Resumen: portada, título, objetivo breve, creador, nivel, duración, acceso/precio y enlace a la ficha. No duplica ofertas ni contenido ni requiere un recomendador automático.

Estado seleccionado representado en URL. Al cambiar tema se limpia una selección incompatible. Si no hay cursos en un nivel no se muestra una opción vacía como recomendación. Carga y errores conservan contexto. Teclado y móvil permiten realizar la selección completa.

#### Tutoriales

Categorías por tarea o tema, búsqueda y filas con icono/portada, título, resumen, nivel, duración y acceso. La ficha explica el resultado práctico, requisitos, herramientas, fecha de revisión y pasos. Puede ser una sola lección o varias. Un tutorial sin cuenta se abre cuando es gratuito; con cuenta puede guardarse y retomarse.

#### Biblioteca de recursos

Índice por tipo, búsqueda y filtros por tema, formato/idioma cuando haya datos. Tipos configurables; no se añaden once categorías vacías solo por reproducir la captura. Ficha con autor/origen, descripción, idioma, tipo, fecha de revisión, relación con cursos y acción adecuada: leer, reproducir, descargar, adquirir o visitar fuente.

Los recursos externos requieren revisión editorial de enlaces y procedencia. Los propios requieren archivo disponible y permiso correcto. Una ficha informativa sin archivo no presenta un botón de descarga funcional.

### 6. Curso, aprendizaje y continuidad

La ficha debe responder: qué aprenderé, para quién es, qué necesito, quién enseña, cuánto tiempo requiere, qué contiene, cuánto cuesta y qué obtengo. Incluye portada/muestra, objetivos, requisitos, temario plegable, formatos y duración por lección, extras e información de certificado si aplica.

La acción principal depende de la situación: “Empezar gratis”, “Inscribirme gratis”, “Comprar curso”, “Continuar” o “Abrir contenido comprado”. Nunca depende solo de la etiqueta visual. En cursos mixtos las acciones gratuitas y las ofertas opcionales están separadas.

La pantalla de estudio contiene título y contexto, lector/reproductor, temario con lección actual, navegación anterior/siguiente, materiales y progreso. Posteriormente incorpora evaluación y preguntas. Una lección bloqueada muestra el motivo y la oferta aplicable sin recibir el cuerpo, URL de archivo ni subtítulos protegidos. No se avanza automáticamente hacia una compra.

Video: controles de reproducción, teclado, velocidad, pantalla completa, subtítulos y transcripción cuando exista. Guarda posición con frecuencia limitada y al pausar/salir; muestra confirmación de guardado o aviso de error. Un salto al final no demuestra video observado. En la primera versión el usuario puede marcar lecciones como completadas manualmente; requisitos de visionado o evaluación se añaden cuando se implementen sus comprobaciones.

Progreso por alumno y versión: última lección, posición y completadas. “Continuar” lleva a la última lección accesible; si está temporalmente bloqueada, explica cómo recuperar acceso y permite elegir una lección disponible. No borra el progreso. El porcentaje usa las lecciones requeridas de esa versión; extras opcionales no penalizan la finalización. Completar texto no equivale a demostrar dominio.

Mi aprendizaje muestra primero Continuar, después inscritos y completados. Permite filtrar cursos/tutoriales, ver porcentaje y estado de acceso, recursos guardados y certificados cuando existan. Compras y facturas están separadas del progreso. Compras individuales aparecen como recursos y dentro de su curso relacionado, sin afirmar que se posee el curso completo.

El visitante puede consumir contenido gratuito sin cuenta. Se ofrece registro para guardar avance. Para comprar, evaluar o participar se exige sesión conservando el destino. No se guarda progreso personal de invitados como si perteneciera a una cuenta.

### 7. Reglas de compra y acceso

La oferta identifica versión, importe entero en sats de prueba, recursos incluidos y extras excluidos. Compra de curso o capítulo concede los recursos enumerados, no todos los objetos relacionados. La inscripción, un rol de creador, un marcador y una tarjeta de biblioteca no conceden pago.

Se mantiene la regla vigente de compra parcial: si ya se posee parte permanente del paquete, no se vende otra vez el paquete completo; se muestran las ofertas individuales faltantes y sus precios. Cada componente pagado incluido debe tener una alternativa comprable por separado antes de publicar el paquete. No se calcula un descuento nuevo a partir del precio del paquete. Esta regla añade fricción y deberá probarse; un futuro precio por diferencia requiere una decisión comercial propia.

Una membresía vigente no equivale a propiedad permanente: permite estudiar y muestra “Incluido hasta…”, pero deja comprar acceso permanente si el usuario elige hacerlo con explicación visible. Renovación de 30 días manual; cancelar significa dejar de ofrecer/recordar renovación, no retirar el periodo pagado. No hay mandato de cobro automático.

Factura: propia de una cuenta, precio y composición congelados, vigencia de 15 minutos. Se reutiliza la pendiente de la misma oferta; un error de conexión no se interpreta como impago. Pago confirmado válido → compra y permisos persistentes. Pendiente, vencida o fallida → sin permisos nuevos. Confirmaciones repetidas no duplican acceso ni periodos.

La interfaz de prueba identifica claramente la simulación y permite comprobar estados. No muestra QR ni instrucciones para enviar fondos reales. Las claves LNbits permanecen en el servidor. Evidencia de pago recibida después de vencimiento o con solapamiento comercial se conserva como incidencia de conciliación; no se hace pasar por una compra completada ni se descarta la evidencia. El detalle técnico está en src/docs/diseno-plataforma.md.

Se separan publicación y disponibilidad: borradores invisibles a terceros; retirado del catálogo conserva acceso de compradores a su versión; bloqueo excepcional por problema de contenido se registra y explica. Archivar una oferta no elimina compras. Los requisitos de certificados, recursos comprados y planes tienen versión; actualizar el catálogo no los reemplaza silenciosamente.

### 8. Cuentas, creación y administración

Registro, login, cierre de sesión y recuperación con destino conservado dentro de cada espacio. Perfil con nombre visible; correo no publicado en tarjetas. Mensajes de recuperación no revelan si un correo existe. Token de recuperación con vencimiento; la entrega por correo debe probarse antes de abrir el sitio al público. Decisión del 3 de octubre: creador y estudiante tienen cuentas independientes, accesos y perfiles separados. Una persona puede tener ambos usando incluso el mismo correo; contraseña, permisos y datos pertenecen a la identidad de cada espacio. La administración tiene acceso propio. El estudio usa navegación de creación, separada de la navegación de aprendizaje.

Creador aprobado: perfil, cursos/tutoriales/recursos propios, editor ordenado, archivos/subtítulos/muestras, metadatos, ofertas, vista como alumno, lista de faltantes y envío a revisión. Los formularios conservan cambios ante error y avisan antes de salir con cambios sin guardar. Cargas muestran progreso, validación y reintento.

Publicación: borrador → revisión → publicado o cambios solicitados. El administrador verifica metadatos, derechos, archivos, acceso, ofertas y coherencia del temario. Editar una composición publicada prepara una versión nueva. La publicación nueva no modifica permisos ni certificados históricos.

Administrador: cuentas y aprobación de creadores, revisión editorial, ofertas, facturas e incidencias, moderación y actividad. Un permiso de administración no equivale a una compra; las vistas de inspección se autorizan expresamente y registran. El creador no ve facturas o aprendizaje de otros creadores. Las métricas comerciales se identifican como simuladas.

Evaluaciones: selección única/múltiple, nota e intentos configurables, corrección en servidor. Certificado por requisitos cumplidos y versión, una emisión verificable, sin acreditación oficial. Preguntas ligadas a lección y comunidad con permisos propios, reportes y moderación. Reseñas futuras: una valoración por alumno y versión/curso según política a definir, moderación y agregados reales; no se agregan estrellas decorativas ahora.

Eventos futuros requieren fecha/zona horaria, modalidad, ubicación/enlace, organizador, estado y responsabilidad de actualización. Inscripciones/cupos o venta de entradas necesitarían reglas nuevas; no reutilizar facturas de cursos sin definirlas.

### 9. Nivel de interfaz que buscamos

La referencia depende de consistencia y contenido editorial además del diseño. BTC.EDU necesita un sistema de componentes y estados común:

| Grupo | Componentes y comportamiento |
|---|---|
| Estructura | Encabezado, menú lateral/plegable, pestañas, breadcrumbs, ancho de lectura y retícula |
| Descubrimiento | Tarjeta con portada, fila de tutorial, ficha de recurso, filtros, selector, paginación y limpiar filtros |
| Estudio | Temario plegable, reproductor/lector, progreso, materiales, bloqueo, evaluación y preguntas por fase |
| Acceso | Etiquetas gratis/mixto/comprado/temporal, oferta e incluidos, factura, biblioteca y confirmación |
| Operación | Formularios, editor, carga de archivos, vista previa, observaciones y tablas de gestión |
| Estados | Cargando, vacío inicial, sin resultados, error recuperable, sesión vencida, sin permiso, archivo ausente y acción completada |

Tipografía: marca de puntos solo para BTC.EDU, títulos y lectura legibles, monoespaciada en datos breves. Tokens de color, espaciado, tamaños, bordes y foco compartidos. Ilustraciones propias con encuadre consistente; no colocar una imagen enorme decorativa dentro de la pantalla de lectura.

Definimos como objetivo WCAG 2.2 AA para las funciones entregadas: teclado, foco visible y no oculto, contraste, etiquetas y mensajes asociados, controles táctiles, subtítulos para video pregrabado y reflujo. La conformidad requiere pruebas, no se infiere de usar Bootstrap. Referencia: [W3C, guía WCAG 2.2](https://www.w3.org/WAI/WCAG22/quickref/).

En toda pantalla: una acción principal clara, retorno a contexto, estados honestos y recuperación. Una actualización HTMX anuncia resultados sin robar foco y funciona con navegación normal. Sesión vencida durante guardado no borra el texto ni aparenta éxito. Las validaciones indican campo y solución.

Presupuesto inicial de experiencia: primera fila de imágenes ligera y con dimensiones reservadas; carga diferida fuera de vista; ninguna consulta por tarjeta que crezca con el catálogo; videos cargados al pedir reproducción. La fuente de marca actual de unos 14.9 MB necesita reducción autorizada o sustitución y revisión de licencia antes de publicación. Medir carga, desplazamientos de diseño y respuesta de filtros en móvil real; fijar objetivos cuantitativos con el primer prototipo medido.

### 10. Brecha desde el código actual

| Área | Existe | Falta |
|---|---|---|
| Datos de catálogo | Título, descripción, creador, objetivos, requisitos | Tema, nivel, portada, duración, etiquetas, tipo curso/tutorial y datos editoriales |
| Navegación | Portada y enlaces superiores | Estructura de academia, vistas propias, pestañas y menú móvil |
| Descubrimiento | Búsqueda y filtros formato/acceso | Agrupación por tema, selector, paginación, búsqueda contextual y precios reales de prueba |
| Curso y lectura | Temario, texto, anterior/siguiente | Video, subtítulos, adjuntos, versiones y acciones por estado de alumno |
| Recursos | Fichas Video/Material | Archivos propios, referencias externas, categorías y relación reutilizable con lecciones |
| Cuenta | Login, sesión y administración | Registro, recuperación expuesta, roles aprobados y límites de abuso |
| Biblioteca | Pantalla vacía | Inscripción, recursos guardados, compras, progreso y continuar |
| Comercio | LNbits independiente | Ofertas, facturas integradas, compras, permisos y conciliación |
| Creación | Administración básica | Panel propio, revisión, archivos y versionado |
| Aprendizaje ampliado | Documentación | Evaluación, certificados, preguntas, comunidad y membresías |
| Calidad | 24 pruebas de la base actual | Pruebas de nuevas funciones, usabilidad, accesibilidad, rendimiento y operación |

Riesgos concretos del código: el catálogo carga temarios y filtra parte en memoria; falta paginar y consultar metadatos/conteos eficientemente. Curso elimina en cascada capítulos/lecciones: antes de compras se deben proteger las versiones adquiridas. La regla de acceso actual rechaza todo ancestro no publicado: debe distinguir borrador de archivado comprado. Video/Material aún no modelan entrega. No existe autorización por propiedad para un panel de creador público. Estos son trabajos pendientes, no fallos demostrados de funciones ya implementadas.

### 11. Orden de construcción y comprobación

1. **Modelo y contratos:** temas/nivel/portadas, curso/tutorial, recurso/archivo, versión publicada, ofertas y reglas de acceso. Migraciones incrementales que preserven cuentas y datos; datos de demostración solo en entornos temporales o con autorización.
2. **Estructura visual y descubrimiento:** plantilla de academia, catálogo, selector, tutoriales y recursos sobre los mismos datos. Revisar escritorio/móvil con registros temporales representativos, sin falsear métricas.
3. **Recorrido completo:** registro y recuperación, archivos protegidos, compra simulada, inscripción y progreso, Mi aprendizaje. Estas piezas cierran la primera academia; se pueden demostrar por entregas pequeñas.
4. **Operación:** creador, editor, revisión y publicación apoyados en el versionado anterior. El administrador ya puede publicar durante el desarrollo del panel.
5. **Ampliaciones:** evaluaciones/certificados, preguntas, comunidad y membresías. Cada fase debe integrar permisos y navegación antes de abrir la siguiente.
6. **Entrega pública:** correo, servidor, HTTPS, respaldos y restauración, almacenamiento, conciliación periódica, logs, accesibilidad, rendimiento y evidencia. Configuración y pruebas antes de anunciar disponibilidad.

Escenarios obligatorios adicionales a AC-01…35:

| ID | Tarea | Resultado verificable |
|---|---|---|
| UX-01 | Filtrar por tema/nivel, abrir y regresar | Contexto conservado y resultados coherentes |
| UX-02 | Elegir desde el selector | Misma ficha, precio y acceso que el catálogo |
| UX-03 | Buscar tutorial y finalizarlo | Resultado práctico claro, progreso guardado con cuenta |
| UX-04 | Abrir referencia externa y recurso propio | Origen/acción diferenciados; protección solo donde corresponde |
| UX-05 | Encontrar curso mixto en filtro gratis | Se entiende qué está gratis y qué se compra |
| UX-06 | Comprar video reutilizado en una lección | Un permiso abre el mismo recurso; no exige nueva compra |
| UX-07 | Retirar un curso adquirido del catálogo | Sigue accesible en la versión comprada; borradores ajenos siguen ocultos |
| UX-08 | Usar selector, pago y temario con teclado y móvil | Sin controles inaccesibles ni pérdida de selección |
| UX-09 | Perder conexión o sesión al guardar avance | Aviso recuperable; no se anuncia éxito inexistente |
| UX-10 | Actualizar temario/nota mínima | Inscripción y certificado anteriores conservan versión |
| UX-11 | Navegar sin resultados o con archivo ausente | Mensaje y siguiente acción útil, sin botones engañosos |
| UX-12 | Recibir evidencia tardía o solapada de pago de prueba | Incidencia conservada, sin permiso indebido ni compra duplicada |

Probar tareas con alumnos y creadores: localizar un curso apropiado, explicar lo incluido, comprar un componente, retomar y publicar. Registrar éxito, errores y dudas reales. Las métricas son tiempo hasta empezar, errores de filtro, comprensión de acceso y reanudación correcta; no prometer aprendizaje a partir de aperturas.

### 12. Límites y decisiones pendientes

La arquitectura y los recorridos anteriores permiten empezar a implementar. Siguen pendientes como trabajo editorial/operativo: público y temática definitiva, contenido y derechos, precios de prueba, moderación y soporte, producción de subtítulos, capacidad y calendario, dominio/alojamiento y proveedor de correo. Ninguno se resuelve copiando la pantalla de una academia.

Revisar específicamente la regla de compra parcial con usuarios antes de cambiarla. Los certificados son de finalización; no se promete acreditación. No hay compromiso de paridad con todas las funciones de Plan B Academy: el objetivo es alcanzar una experiencia clara y consistente en los recorridos definidos.

Este documento es la referencia vigente de estructura y experiencia; el [diseño técnico](../src/docs/operacion-y-bitacora.md#diseno-plataforma) define su implementación prevista. Los documentos 03 y 08 conservan las reglas comerciales y AC-01…35 salvo aclaraciones explícitas aquí. Las capturas no sustituyen validación ni los originales del assignment.

<a id="11-enfoque-creadores"></a>

## Enfoque integral para creadores

Origen: `strategy/11-enfoque-creadores.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Definición del 3 de octubre de 2026. El proyecto se aborda como una plataforma completa. Este documento amplía el recorrido de creación de los documentos 08 y 10; define producto y orden de construcción, no funciones ya implementadas ni una fecha de entrega comprometida.

**Registro de implementación al 4 de octubre:** cuentas independientes, aprobación/perfil, estudio/editor/archivos, revisión, versiones, ofertas y compras simuladas, biblioteca, inscripción y progreso básico ya funcionan. 129 pruebas pasan. [Entrega y límites verificados](../src/docs/operacion-y-bitacora.md#comercio-y-aprendizaje-2026-10-04). Evaluaciones, certificados, preguntas, comunidad, membresías y métricas completas permanecen pendientes; las secciones siguientes definen el horizonte del producto.

**Actualización del 7 de octubre:** el creador configura evaluaciones por lección, las envía como parte del curso y consulta resultados privados por versión. Puede autorizar un intento adicional con motivo, conservando notas y espera. Selección exacta, corrección, completado obligatorio y permisos comprobados; 148 pruebas aprobadas. [Entrega y límites](../src/docs/operacion-y-bitacora.md#evaluaciones-2026-10-07). Certificados, preguntas, comunidad, membresías y métricas completas siguen pendientes.

### Cobertura vigente

Entrega del 10 de octubre: configuración de certificados por versión, bandeja de preguntas, notificaciones internas y panel de actividad agregado por creador, además del panel administrativo con permisos. 179 pruebas y recorridos HTTP de escritorio/móvil verificados. [Reglas y evidencia](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). Comunidad y moderación por versión se incorporan el 10 de octubre. Membresías, reproducción medida y operación pública siguen pendientes. Los registros fechados anteriores conservan el estado de sus entregas; el horizonte siguiente no acredita funciones adicionales.

### Propósito

El creador es un docente y responsable de su oferta educativa. BTC.EDU debe permitirle preparar, publicar, mantener y comercializar contenido, acompañar a sus alumnos y mejorar a partir de resultados. El panel será su espacio de trabajo cotidiano, con identidad visual compartida con la academia y navegación propia.

Decisión confirmada el 3 de octubre: estudiante y creador tienen cuentas independientes, perfiles propios y entradas separadas. Una persona puede usar ambos espacios registrando una cuenta para cada uno; puede reutilizar correo, pero cada identidad conserva contraseña, permisos y datos propios. El registro de creador no transforma una cuenta de estudiante. La aprobación del perfil habilita herramientas; cada operación comprueba además propiedad y permiso en el servidor. La administración tiene su propio acceso.

### Recorrido completo

Solicitud y aprobación → configurar perfil → preparar contenidos y archivos → definir oferta y requisitos educativos → previsualizar y enviar a revisión → resolver observaciones → publicar → atender alumnos y comunidad → consultar resultados → preparar una nueva versión.

La incorporación explica responsabilidades, derechos de los materiales y proceso editorial. El perfil público presenta biografía, especialidad, enlaces y contenido publicado; el correo de la cuenta permanece privado. La solicitud muestra estado y observaciones.

### Espacio de trabajo

| Área | Responsabilidad |
|---|---|
| Inicio | Priorizar observaciones de revisión, preguntas pendientes, incidencias y contenido por terminar; resumen de actividad real |
| Contenido | Gestionar cursos, tutoriales y recursos; filtrar borradores, revisiones, publicaciones y archivados |
| Biblioteca de archivos | Cargar y reutilizar videos, materiales, subtítulos y transcripciones; mostrar validación, uso y límites de almacenamiento |
| Alumnos | Consultar inscripciones y avance de sus contenidos; revisar intentos y ofrecer acompañamiento con datos personales mínimos |
| Preguntas y comunidad | Responder por lección, gestionar espacios y moderar reportes con motivo e historial |
| Ventas y membresías | Configurar ofertas y planes; consultar compras confirmadas, periodos y volumen en sats de prueba |
| Estadísticas | Consultar alcance, inscripciones, avance, finalización, resultados y conversión con periodos y definiciones explícitas |
| Perfil y notificaciones | Mantener identidad pública y preferencias; recibir avisos de revisión, preguntas e incidencias |

Las áreas se habilitan cuando sus recorridos funcionan. El diseño contempla todas desde el principio; las pantallas entregadas muestran datos reales y acciones operativas.

### Editor educativo

El curso se organiza en Información, Temario, Materiales, Acceso y precios, Evaluaciones y certificado, Comunidad, y Revisión y versiones. El creador configura objetivos, público, requisitos, tema, nivel, portada, muestra y duración; ordena capítulos y lecciones; redacta texto y vincula recursos reutilizables.

El tutorial usa una variante centrada en resultado práctico y pasos. El recurso independiente tiene su propia ficha, procedencia, archivo o enlace y oferta. Se comparten componentes y revisiones para evitar duplicaciones y mantener consistencia entre publicaciones.

Los formularios conservan trabajo ante errores, muestran estado de guardado y advierten de cambios pendientes. Las cargas muestran progreso, resultado y reintento. La vista previa permite inspeccionar el recorrido de alumno y sus bloqueos mediante permisos expresos, sin generar compras ficticias ni alterar progreso.

El editor de evaluaciones define preguntas, respuestas, explicaciones, nota mínima, intentos y espera. El certificado se configura mediante requisitos explícitos de la versión del curso y es de finalización, sin afirmar acreditación oficial.

### Revisión y mantenimiento

Borrador → En revisión → Publicado o Cambios solicitados. Archivar retira el contenido del descubrimiento sin eliminar el acceso adquirido. El administrador revisa calidad, derechos, archivos, accesibilidad, coherencia educativa y condiciones de acceso; devuelve observaciones vinculadas al contenido y registra sus decisiones.

Enviar a revisión fija la composición a revisar. Las ediciones posteriores preparan un borrador distinto; aprobar publica exactamente la composición revisada. El creador puede retirar un envío pendiente para corregir y reenviar. Una publicación vigente permanece disponible mientras se revisa su sustituta.

Actualizar prepara otra versión. Se muestran diferencias, motivo del cambio y efecto para alumnos existentes antes de publicar. Compras, inscripciones, progreso, evaluaciones y certificados conservan sus referencias históricas. La concesión de una nueva versión a alumnos existentes debe ser explícita y no reemplaza silenciosamente sus registros anteriores.

Una retirada excepcional de acceso por contenido problemático requiere intervención administrativa, motivo, registro y explicación al afectado. Suspender a un creador no elimina automáticamente archivos, compras ni aprendizaje; la administración resuelve la continuidad del contenido.

### Comercio y relación con alumnos

La [comparación de costos](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) no define comisiones, liquidaciones ni precios aceptados. Los [guiones](investigacion-y-requisitos.md#16-validacion-con-usuarios) explorarán unidades vendibles, derechos, mantenimiento, atención y actualización; las tareas observarán oferta/revisión/versiones. No se realizaron sesiones ni se compromete un tiempo de atención. Los hallazgos deberán alimentar operación y prioridades del estudio.

El creador define contenido gratuito, muestras, ofertas individuales, paquetes y membresías conforme a las reglas comerciales vigentes. Antes de enviar a revisión ve lo incluido, lo excluido, precio en sats de prueba y duración del acceso. Cambiar precio afecta nuevas facturas; las pendientes conservan sus condiciones.

Las compras individuales son permanentes para la composición adquirida. Las membresías conceden acceso temporal y se renuevan manualmente con facturas simuladas de 30 días. Vencimiento conserva compras, progreso y certificados. El panel distingue ventas confirmadas, pendientes e incidencias; no presenta volumen simulado como ingreso real ni saldo disponible para retirar. Fondos reales y liquidaciones requerirán una definición comercial y operativa propia.

El acompañamiento reúne preguntas por lección, avisos, evaluaciones y comunidad. El creador solo consulta alumnos relacionados con sus contenidos y la información necesaria para acompañarlos. Las estadísticas agregadas separan inscripción, actividad, finalización y aprobación; una apertura o reproducción no demuestra aprendizaje. No se incluyen conversaciones privadas en esta definición.

### Orden de construcción

1. Diseñar navegación, pantallas y contratos para todo el estudio de creador, incluidos estados vacíos, errores, permisos y relación con academia y administración.
2. Implementar solicitud/aprobación, perfil, gestión de contenido, biblioteca de archivos, editor, vista previa y revisión sobre el versionado existente.
3. Integrar ofertas, facturas, permisos adquiridos, inscripciones y progreso para cerrar el recorrido creador → publicación → compra o inscripción → aprendizaje.
4. Integrar evaluaciones, certificados, preguntas, notificaciones, comunidad y moderación.
5. Integrar membresías y métricas completas; preparar operación pública con cuotas, respaldos/restauración, tratamiento de archivos huérfanos, incidencias y soporte.

Cada entrega debe cerrar un recorrido utilizable y verificar sus permisos. Este orden conserva el alcance completo; no reduce el producto a un panel de cargas ni compromete plazos sin revisar capacidad.

### Condiciones de aceptación

- Un creador aprobado prepara y envía contenido desde su espacio, sin depender de la administración de Django para editarlo.
- Ninguna ruta o carga permite consultar o modificar borradores, archivos, alumnos o ventas de otro creador.
- La publicación corresponde a la composición aprobada y las observaciones permiten corregir y reenviar.
- Una actualización no rompe contenido adquirido, progreso o certificados anteriores.
- Un creador puede comprobar qué puede ver un visitante, un inscrito, un comprador y un miembro, sin concederse derechos ajenos.
- Las métricas corresponden a registros verificables y las operaciones simuladas se identifican claramente.
- Los recorridos principales funcionan con teclado y en móvil; fallos de sesión, red y carga permiten recuperar el trabajo.
- La validación con creadores comprueba preparar una lección, organizar un curso, entender su oferta, resolver una revisión y responder a un alumno. Se registran dificultades reales.

### Huellas de certificados

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital ni un registro en Bitcoin.

Implementado y verificado el 10 de octubre. [Contrato, privacidad, migración y pruebas](../src/docs/operacion-y-bitacora.md#certificados-sha256-2026-10-10). La exportación permite recalcular exactamente los bytes JSON; no representa el hash de todo el PDF.

### Comunidad implementada

El 10 de octubre se incorpora conversación por versión para alumnos inscritos y creador aprobado; reportes, moderación con motivo e historial, cierre/reapertura, ocultación y suspensión/restablecimiento de escritura. La administración interviene con permiso específico. Conserva lectura, compras y progreso; no habilita membresías ni acceso público. Avisos internos, límites y condiciones en [reglas adoptadas](investigacion-y-requisitos.md#15-especificaciones-modulos-pendientes) y [registro técnico](../src/docs/operacion-y-bitacora.md#comunidad-2026-10-10). Las propuestas anteriores de otros tipos de espacio permanecen como diseño.

<a id="08-aprendizaje-creadores-y-membresias"></a>

## Funciones de aprendizaje y creación

Origen: `strategy/08-aprendizaje-creadores-y-membresias.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Este documento amplía el alcance e invalida exclusiones anteriores. Es diseño sustentado en 07, no requisitos adicionales del assignment. Cuentas, publicación, creadores y progreso básico están registrados como implementados al 4 de octubre; las evaluaciones se entregaron el 7 de octubre; certificados, preguntas, notificaciones y paneles esenciales se entregaron el 10 de octubre. Comunidad y moderación por versión se incorporan el 10 de octubre. Membresías, reproducción medida y operación pública siguen pendientes. Ver [estado](../src/docs/operacion-y-bitacora.md#guia-local-anterior).

La [comparación comercial](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) documenta posibilidades, no demanda. Las [sesiones propuestas](investigacion-y-requisitos.md#16-validacion-con-usuarios) deberán evaluar necesidades y comprensión. No cambia renovación manual de 30 días ni derechos históricos. Probar módulos pendientes en prototipos identificados.

La [arquitectura y experiencia del 2 de octubre](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu) conserva este alcance completo y escalona las entregas: primero academia con cursos/tutoriales/recursos, compra y progreso básico; luego operación por creadores y módulos ampliados. Las estimaciones de este documento preceden esa definición; deben revisarse, no reutilizarse como compromiso para el alcance nuevo.

### Evaluaciones entregadas

Al 7 de octubre funcionan selección única/múltiple, preguntas con igual peso y coincidencia exacta, límites, espera, guardado/retoma y soluciones al entregar o al aprobar. Iniciar consume un intento; el abierto se retoma sin consumir otro. La evaluación obligatoria exige aprobación antes de completar la lección. Autorizar un intento adicional conserva motivo e historia y no borra notas ni elimina espera. Preguntas y reglas se congelan con la composición enviada a revisión. [Recorrido, pruebas y límites](../src/docs/operacion-y-bitacora.md#evaluaciones-2026-10-07).

### Entrega esencial

Las reglas efectivamente implementadas se conservan en [15](investigacion-y-requisitos.md#15-especificaciones-modulos-pendientes) y [evidencia técnica](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). El alumno confirma su nombre antes de emitir; compartir es voluntario y la revocación conserva motivo. Corregir o reemplazar credenciales queda pendiente. Preguntas privadas y avisos internos funcionan; el foro comunitario y correo no forman parte de esta entrega. Las condiciones futuras descritas abajo, como porcentaje observado de video y membresías, siguen siendo diseño.

### Alumno

Puede explorar sin cuenta. Necesita cuenta para conservar progreso, participar, realizar evaluaciones y comprar. Inscribirse en un curso gratuito es gratis y no compra sus extras. La pantalla principal muestra Continuar aprendiendo, cursos inscritos, compras, membresías, preguntas, notificaciones y certificados.

Progreso: guardar la posición del video y el estado de cada lección por cuenta. Marcar una lección como completada no demuestra dominio. Las lecciones sin evaluación pueden completarse manualmente; el creador puede exigir un porcentaje de video observado, indicando la regla. No contar saltar al final como observarlo completo. Las evaluaciones obligatorias requieren aprobar para completar la lección. El aprendizaje se conserva aunque termine el acceso temporal.

Evaluaciones: preguntas de selección única y múltiple, explicaciones y nota mínima entre 0 y 100; número de intentos y espera configurables. Antes de empezar se muestran reglas. Corregir en el servidor, guardar intentos y devolver explicaciones al cerrar el intento según configuración. Los reinicios de intentos por creador se registran con motivo. La primera versión no incluye vigilancia remota ni corrección automática de ensayos.

Certificados: un curso indica si ofrece certificado y cuáles son sus lecciones y evaluaciones obligatorias. Completar el conjunto requerido y aprobar las evaluaciones emite una sola credencial por alumno y versión del curso. Comprar o terminar un video individual no emite el certificado del curso. Descargar PDF y consultar una página de verificación con identificador no predecible. Mostrar nombre del alumno, curso, creador, fecha y condición de finalización; el usuario elige compartir el enlace. No afirmar acreditación oficial.

### Creador y publicación

Una persona registra una cuenta de creador independiente de su cuenta de estudiante y solicita aprobación al administrador. El creador gestiona únicamente sus cursos y materiales: perfil, objetivos, requisitos, temario, videos, textos, archivos, subtítulos, muestras, precios, evaluaciones, certificados y comunidad. Esta separación fue confirmada el 3 de octubre; reutilizar correo no comparte contraseña, perfil ni actividad entre cuentas.

Estados de publicación: Draft, InReview, Published, ChangesRequested y Archived. El creador puede guardar borradores y verlos como alumno sin hacerlos públicos. Envía a revisión cuando contiene los campos, muestras y archivos necesarios. El administrador aprueba o devuelve observaciones. Modificar un curso publicado prepara otra versión; no cambia silenciosamente lo incluido en compras o los requisitos de certificados ya emitidos.

El creador puede archivar una oferta sin eliminar compras previas. Los cambios de precio solo afectan nuevas facturas. Los cambios de composición no alteran compras confirmadas. Para el primer lanzamiento, congelar la composición publicada y permitir correcciones que no retiren recursos; la ampliación de un curso requiere versionar y declarar si se concede a alumnos existentes.

Panel: cursos y borradores, revisión, preguntas por responder, comunidad, alumnos inscritos, progreso agregado, resultados de evaluaciones, compras y volumen simulado. No hay pagos reales a creadores ni liquidaciones todavía.

### Comunidad

Espacios por curso o creador con publicaciones y respuestas; además preguntas vinculadas a una lección. Definir si el espacio es público para leer, requiere inscripción gratuita, compra de curso o membresía activa. Escribir requiere cuenta y el permiso del espacio.

El creador modera sus espacios; el administrador puede intervenir globalmente. Reportar, ocultar, cerrar conversación y suspender escritura, con motivo y registro. Sanear texto, limitar frecuencia y paginar. No incluir chat privado ni archivos en comentarios en la primera versión. Conservar historial de decisiones. La cancelación de membresía conserva progreso y compras, pero puede terminar el permiso de participar en un espacio exclusivo al vencer el periodo.

### Membresías y suscripciones

Un creador ofrece planes con precio, duración y contenidos enumerados. Una membresía concede acceso temporal al conjunto incluido y a los espacios indicados. Puede coexistir con compras individuales permanentes. Un curso gratuito sigue gratis aunque el creador tenga planes.

Implementación inicial: periodos de 30 días con facturas LNbits simuladas; renovación mediante una nueva factura confirmada por el usuario. Cancelar la renovación no quita el periodo ya pagado. Al vencer, deja de abrir contenidos disponibles solo por membresía; conserva compras permanentes, progreso y certificados. No borrar datos educativos por impago.

La primera versión demuestra suscripciones renovables, pero no cobra automáticamente una wallet. Una renovación automática real requiere un mecanismo autorizado y una integración específica que LNbits no proporciona por el mero hecho de crear facturas. No presentar un cobro manual como automático.

Confirmar dos veces la misma factura no extiende dos veces la membresía. Renovar antes de vencer extiende desde la fecha final vigente; renovar después de vencer inicia desde la confirmación. Una compra permanente permite abrir aunque la membresía haya vencido. Cambiar precio o contenidos crea una nueva versión del plan y muestra condiciones antes del siguiente pago.

### Cuentas y soporte

Separar roles y permisos por propiedad. Añadir recuperación de contraseña con token de un solo uso, con vencimiento y correo transaccional configurable. En desarrollo usar una bandeja local de correo; en despliegue se necesita configurar el proveedor y probar entrega. Notificaciones internas por respuesta, revisión, certificado y próxima renovación. No enviar mensajes reales desde esta investigación.

### Compra parcial de curso

Mantener provisionalmente el bloqueo de oferta conjunta si hay propiedad parcial y ofrecer lo faltante. Las referencias consultadas no justifican esa regla como estándar. Probar comprensión y conveniencia frente a cobrar únicamente recursos faltantes; si elegimos el segundo comportamiento, definir cálculo de precio y conflictos antes de implementarlo. No cambiar la regla silenciosamente.

### Criterios adicionales

| ID | Prueba | Resultado esperado |
|---|---|---|
| AC-21 | Retomar en otro dispositivo | Misma posición guardada y lecciones completadas |
| AC-22 | Abrir curso gratuito | Inscripción sin compra; extras de pago siguen identificados |
| AC-23 | Enviar evaluación | Nota calculada en servidor; intento registrado y límite aplicado |
| AC-24 | Comprar curso sin terminarlo | No se emite certificado |
| AC-25 | Completar requisitos y repetir solicitud | Un certificado verificable por alumno y versión |
| AC-26 | Creador modifica curso ajeno | Acceso denegado |
| AC-27 | Enviar borrador a revisión | No es público hasta aprobación; observaciones visibles al autor |
| AC-28 | Reportar comentario | Moderación autorizada con registro; terceros no leen espacio restringido |
| AC-29 | Activar membresía mediante pago | Acceso temporal solo al contenido incluido |
| AC-30 | Cancelar renovación | Acceso hasta fin del periodo; no se crea renovación posterior |
| AC-31 | Vencer membresía con compra individual | Compra, progreso y certificado permanecen |
| AC-32 | Repetir confirmación de renovación | Un solo periodo añadido |
| AC-33 | Cambiar temario después de certificado | Certificado conserva su versión y requisitos cumplidos |
| AC-34 | Recuperar contraseña | Token vence y no se reutiliza; no se revelan claves |
| AC-35 | Pregunta y respuesta por lección | Alumno ve respuesta y aviso; creador ve su bandeja |

### Fases y esfuerzo orientativo

Una jornada significa un día de trabajo técnico concentrado de una persona. Son estimaciones preliminares del equipo, no datos de las plataformas ni una promesa de plazo. No incluyen producir cursos, investigación con participantes ni operación del sitio.

| Fase | Entrega verificable | Jornadas estimadas |
|---|---|---|
| 1 | Cuentas, catálogo, cursos, compra y protección de contenido | 5–7 |
| 2 | Creador, editor, cargas, revisión y versiones básicas | 4–6 |
| 3 | Progreso, evaluaciones y certificados | 4–6 |
| 4 | Preguntas, comunidad y moderación | 3–5 |
| 5 | Membresías, renovación y convivencia con compras | 3–5 |
| 6 | Métricas, accesibilidad, integración, pruebas y documentación | 4–6 |

Total orientativo: 23–35 jornadas técnicas, con trabajo de diseño y pruebas de Business en paralelo. Hasta el 3 de noviembre hay 33 días transcurridos desde el 1 de octubre; eso no equivale a 33 jornadas disponibles. Con un Dev, la capacidad y las dependencias deben comprobarse con las primeras entregas. El cierre del 15 de octubre no es una base realista para comprometer toda esta lista sin estimación adicional. Proponemos usar el sprint completo como planificación de trabajo, sujeto al acuerdo del equipo.

Hito del 13 de octubre: demostrar plataforma navegable, curso gratuito, compra de capítulo o video, acceso protegido y editor de creador en el estado alcanzado. Registrar lo que de verdad esté construido. Después integrar las otras funciones por dependencia y cerrar cambios antes de la entrega confirmada. Revisar las estimaciones al terminar la fase 1; mantener todo en el diseño y declarar honestamente lo implementado en la entrega.

### Huellas de certificados

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital ni un registro en Bitcoin.

Implementado y verificado el 10 de octubre. [Contrato, privacidad, migración y pruebas](../src/docs/operacion-y-bitacora.md#certificados-sha256-2026-10-10). La exportación permite recalcular exactamente los bytes JSON; no representa el hash de todo el PDF.

### Comunidad implementada

El 10 de octubre se incorpora conversación por versión para alumnos inscritos y creador aprobado; reportes, moderación con motivo e historial, cierre/reapertura, ocultación y suspensión/restablecimiento de escritura. La administración interviene con permiso específico. Conserva lectura, compras y progreso; no habilita membresías ni acceso público. Avisos internos, límites y condiciones en [reglas adoptadas](investigacion-y-requisitos.md#15-especificaciones-modulos-pendientes) y [registro técnico](../src/docs/operacion-y-bitacora.md#comunidad-2026-10-10). Las propuestas anteriores de otros tipos de espacio permanecen como diseño.

<a id="09-identidad-visual"></a>

## Identidad visual de BTC.EDU

Origen: `strategy/09-identidad-visual.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Definido por el usuario

Nombre: BTC.EDU. Referencias: Nothing Tech, Plan B Academy y diseño industrial. Colores: blancos, negros y tonos leves de naranja. El nombre no implica que el dominio esté registrado ni que la plataforma tenga acreditación educativa.

Esta dirección sustituye el uso de Micropayments como nombre visible del producto. Los documentos originales del assignment conservan su título. Durante la propuesta inicial la implementación visual estuvo pausada; la aprobación del 1 de octubre permitió construir la base actual.

**Actualización del 2 de octubre:** la pausa anterior corresponde a la propuesta inicial y ya fue superada por la aprobación registrada al final de este documento. La base visual está implementada. La [arquitectura y experiencia vigente](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu) define la organización de las nuevas pantallas; los valores efectivamente usados y fuentes están en [componentes visuales](../src/docs/operacion-y-bitacora.md#componentes-visuales). Las propuestas de los apartados siguientes se conservan como antecedente, no como un segundo sistema de estilos.

### Propuesta para revisar

Una interfaz clara, de apariencia industrial, con fondo blanco cálido, texto negro, líneas finas, bloques ordenados y naranja reservado a detalles. Los siguientes valores son propuestas, no decisiones aprobadas:

| Uso | Color |
|---|---|
| Fondo principal | #FAFAF7 |
| Superficies | #FFFFFF |
| Texto y botones principales | #171717 |
| Texto secundario | #626262 |
| Bordes | #D8D8D2 |
| Detalle naranja | #E99555 |
| Fondo naranja suave | #FBEBDD |

Texto de botones naranja claro siempre oscuro; no usar naranja suave para texto pequeño sobre blanco. Verificar contraste en los diseños concretos antes de implementar.

Tipografía propuesta: sans serif legible para lectura y títulos; monoespaciada para precios, duraciones y etiquetas pequeñas. Una tipografía de puntos puede explorarse solo para el nombre o detalles de marca, nunca para párrafos ni instrucciones. Fuentes concretas y logotipo pendientes.

Componentes: botones sólidos negros, acciones secundarias con borde, tarjetas con poco redondeo, estados de selección discretos, formularios claros y foco visible. Iconos sencillos y consistentes. Evitar decoración que dificulte leer cursos o usar el reproductor.

### Qué tomamos de las referencias

- Nothing: explorar lettering de puntos, composición contenida y detalles visuales de producto. La inspección inicial mostró la identidad del encabezado y el aviso de cookies; falta revisar el resto de la página sin ese aviso antes de definir composiciones inspiradas en ella.
- Plan B Academy: se observó navegación lateral, filtros de tema/nivel/tipo/precio, tarjetas de curso y acentos naranja. Tomar esa claridad para organizar aprendizaje; definir un estilo propio para BTC.EDU.
- Diseño industrial: propuesta de retícula, líneas, numeración y etiquetas de apariencia técnica. El usuario todavía debe precisar cuánto protagonismo quiere darles.

Referencias consultadas el 1 de octubre de 2026: https://intl.nothing.tech/ y https://planb.academy/en/learn-anytime. No reutilizar sus logos, ilustraciones o fotografías sin permiso.

### Orden de trabajo

La aprobación visual no acredita usabilidad. El [plan de pruebas](investigacion-y-requisitos.md#16-validacion-con-usuarios) observará precios/inclusiones, estados, navegación y recuperación. Los hallazgos pueden ajustar texto, jerarquía y controles dentro de la identidad acordada. No hay sesiones externas ni cambio de identidad derivados de esta investigación.

1. Revisar esta dirección visual, tipografía y tratamiento del nombre.
2. Preparar una lámina de estilo con colores, nombre, botones y tarjetas de ejemplo sin cursos reales.
3. Revisar la portada y la estructura vacía del catálogo en escritorio y móvil.
4. Implementar la base visual aprobada y documentar sus componentes en src.

No se cargan cursos, capítulos ni recursos durante esta etapa. No se ha creado todavía un logo ni una pantalla aprobada.

### Concepto aprobado el 1 de octubre de 2026

El usuario aprobó la imagen conceptual y autorizó comenzar la base técnica y visual en un nuevo chat. Referencia guardada en src/design/btc-edu-concepto-aprobado.png. Usar su composición, nombre de puntos, fondos claros, tipografía legible, tarjetas y objetos industriales con acentos naranja como guía. Los títulos y precios en la imagen son ejemplos; no cargar cursos todavía. La aprobación corresponde a la dirección visual, no a todas las funciones o textos de ejemplo.

<a id="04-pantallas-y-recorrido"></a>

## Pantallas y recorrido

Origen: `strategy/04-pantallas-y-recorrido.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Este documento conserva los recorridos comerciales originales. La estructura de navegación y pantallas vigente está en [arquitectura y experiencia](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu): Cursos (Todos/Selector), Tutoriales, Recursos, Mi aprendizaje y Compras y acceso. Hay dirección visual aprobada y pantallas base implementadas; los prototipos de las nuevas vistas y su validación con usuarios siguen pendientes.

### Inicio y catálogo

Mostrar cursos, videos y materiales con filtros por tema, formato y gratis o de pago. Cada tarjeta indica título, creador, descripción y precio cuando corresponde. Un curso con lecciones gratuitas y otras de pago muestra esa combinación sin sugerir que todo está incluido gratis. Navegación: Cursos, Videos, Materiales, Mis cursos y compras, y Cuenta.

### Curso

Descripción, objetivo, requisitos, creador y capítulos ordenados. Cada lección indica formato y si es gratuita, comprada o de pago. Los cursos de pago enumeran lo incluido y el precio completo. Los materiales adicionales muestran si están incluidos, son gratis o se compran aparte.

En cursos gratuitos con compras opcionales, abrir las lecciones gratis no exige comprar nada. Un capítulo de pago muestra su precio y contenidos. Un curso parcialmente adquirido ofrece los capítulos faltantes; el totalmente adquirido permite abrirlos.

### Lección, video y material

Lección: texto o reproductor, navegación entre lecciones y materiales asociados. Video individual: descripción, muestra independiente y compra de ese video. Material: descripción, formato, muestra y botón de descarga cuando sea gratis o esté comprado. La compra no exige completar lecciones previas.

Quien ya compró ve Abrir o Descargar. Antes de comprar se muestra exactamente qué recibe y el precio en sats de prueba.

### Cuenta y compras

Registro y acceso con correo y contraseña, conservando el destino elegido. Enlace para recuperar contraseña mediante correo y token de un solo uso. Mis cursos y compras organiza cursos, capítulos, videos y materiales adquiridos, con fecha y enlaces para abrir. Muestra progreso guardado, última lección y posición de video, distinguiendo lo disponible por compra o membresía.

### Pago simulado

Oferta, contenidos incluidos, importe, identificador, estado y tiempo restante. Aviso visible: Pago de prueba. No envíes bitcoin. No mostrar QR ni instrucciones para transferir fondos reales.

Pending: espera y controles de simulación separados. Paid: confirmación y enlaces al contenido. Expired o Failed: motivo y reintento si corresponde. Conflicto por compra previa: llevar a las compras o a la oferta actualizada. Error de conexión: consultar el estado de la misma factura.

### Administración

Gestión de cursos, capítulos, lecciones, videos, materiales, muestras, precios y visibilidad. Tabla de facturas y resumen de actividad. Los importes se identifican como sats simulados.

### Recorridos para demostrar

El [plan de validación](investigacion-y-requisitos.md#16-validacion-con-usuarios) observará elección, inclusiones/extras, compra individual, vencimiento, recuperación y compra parcial, además del editor/revisión/versiones para creadores. Registrar ayudas, errores y versión; no revelar caminos en los enunciados. Probar solo módulos disponibles o prototipos identificados. Las sesiones externas siguen pendientes.

1. Abrir un curso completamente gratuito.
2. Abrir una lección gratis y comprar un capítulo del mismo curso.
3. Comprar material adicional de un curso gratuito.
4. Comprar un video individual sin comprar el curso.
5. Comprar un curso completo y comprobar lo incluido y los extras excluidos.
6. Resolver pago fallido o vencido y recuperar compras en otro navegador.
7. Comprobar que el servidor bloquea videos y archivos de pago sin compra.

### Pantallas de aprendizaje, creadores y membresías

Probar las [variantes de muestra](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) antes de fijar proporciones. La estética aprobada no demuestra comprensión. Una equivalencia USD es solo propuesta de investigación para comprensión de sats, no una función entregada ni un cambio de moneda.

Continuar aprendiendo con posición guardada. Evaluación con instrucciones, nota requerida, intentos, envío y resultado. Certificados con requisitos pendientes, descarga y verificación. Preguntas por lección y comunidad con publicaciones, respuestas y reportes. Notificaciones internas y recuperación de contraseña.

Panel de creador con borradores, editor de temario, cargas, muestras, precios, evaluaciones, criterios de certificado, vista como alumno, revisión, respuestas y métricas propias. Panel administrador con revisión de versiones y moderación.

Membresías: comparar planes, contenidos incluidos, duración, pago de prueba, renovación manual, fecha de vencimiento y cancelación. Separar biblioteca comprada de acceso temporal sin borrar progreso.

Añadir pruebas: retomar video en otro dispositivo; aprobar evaluación y emitir certificado; publicar curso mediante revisión; preguntar y moderar; renovar o cancelar membresía conservando compras individuales.



### Recorrido de cursos y lectura vigente

La ficha ofrece empezar, continuar, repasar o revisar acceso según la versión y el avance de la cuenta. El temario muestra finalización, evaluación y acceso. El lector organiza prácticas y soluciones desplegables, permite enfocar la lectura y mantiene la continuación tras el guardado confirmado. Mi aprendizaje presenta resumen, recorrido destacado, búsqueda y estados. En móvil el temario precede al texto. La descripción y sus límites técnicos están en [la entrega de aprendizaje](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12); las tareas con participantes permanecen pendientes en el documento 16.


### Navegación por contexto

La barra lateral cambia según la página visitada. El catálogo reúne cursos, tutoriales y recursos; el espacio de aprendizaje reúne el avance, los certificados y las preguntas; las compras agrupan las facturas; y la comunidad reúne conversaciones, personas y notificaciones. La cuenta concentra los datos del perfil. Los accesos para cambiar de espacio permiten continuar el recorrido sin mostrar todas las opciones en cada página.

Dentro de un curso o tutorial, la barra prioriza el regreso al curso y, durante una lección, el acceso a su temario. Cuando existe una inscripción a una versión publicada, también ofrece la comunidad del curso. El estudio de creador distingue la gestión del contenido, el acompañamiento de alumnos y el perfil. Las opciones respetan el tipo de cuenta y el estado de aprobación del creador; estos cambios de navegación no sustituyen las comprobaciones de acceso de cada página.

### Recorrido vigente de evaluaciones

La preparación distingue reglas y disponibilidad de intentos. El alumno responde una pregunta por pantalla con JavaScript, puede navegar libremente, guardar y retomar, y revisa las respuestas antes de entregar. El avance cuenta preguntas con alguna selección, sin anticipar aciertos. Sin JavaScript conserva un formulario completo. El resultado separa nota y repaso; el editor ofrece preguntas plegables y los resultados del creador conservan autorización adicional con motivo. [Decisiones, evidencia y límites](../src/docs/operacion-y-bitacora.md#experiencia-evaluaciones-2026-10-12).

<a id="01-producto-y-negocio"></a>

## Producto y modelo de negocio

Origen: `strategy/01-producto-y-negocio.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Propuesta

Una plataforma web para explorar cursos, ver lecciones y videos, y obtener materiales adicionales. Combina contenido gratuito con compras de cursos completos, capítulos, videos individuales y materiales. Las compras se pagan con LNbits en un entorno simulado, sin fondos reales.

### Formas de ofrecer contenido

- Curso completamente gratuito: todas sus lecciones son gratuitas.
- Curso gratuito con capítulos de pago: las lecciones gratuitas siguen disponibles y cada capítulo de pago se puede comprar por separado.
- Curso gratuito con materiales de pago: el curso no exige comprar los ejercicios, guías o archivos adicionales.
- Curso completo de pago: la compra incluye las lecciones enumeradas antes de pagar. Puede tener lecciones de muestra gratuitas.
- Video de pago individual: se compra sin exigir la compra del curso al que pertenece.
- Material adicional gratuito o de pago: guías, ejercicios, textos y archivos descargables, con una descripción clara de lo incluido.

Cada oferta debe indicar exactamente qué entrega. Pertenecer a un curso no significa que un material adicional esté incluido en la compra del curso. El acceso comprado es permanente dentro del MVP y se recupera al iniciar sesión desde otro dispositivo.

### Público y validación

El catálogo inicial se centra en Bitcoin y Lightning para personas que quieren aprender fundamentos y recorridos técnicos sin una suscripción. La primera colección se publica bajo el perfil editorial BTC.EDU, sin atribuirla a instructores ficticios. Los creadores preparan contenido y la administración revisa su publicación. La demanda, los precios y la preferencia entre comprar un curso o contenidos separados todavía deben validarse.

La [comparación de modelos](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) está documentada con precios externos, procesamiento y video. La hipótesis principal conserva contenido gratuito/muestras + compras individuales; evaluar membresías para uso frecuente. Los modelos pueden combinarse. No hay demanda ni precios validados.

Los [guiones y tareas](investigacion-y-requisitos.md#16-validacion-con-usuarios) están preparados para una primera ronda propuesta de seis a diez alumnos y tres a cinco creadores. No hay reclutamiento ni sesiones realizadas. Investigar experiencias anteriores y observar comprensión de ofertas, pagos y recuperación de acceso.

### Operación

Business selecciona contenidos y verifica derechos de uso. Dev construye y mantiene la plataforma, almacenamiento, base de datos y conexión con LNbits. Los creadores gestionan sus cursos, capítulos, videos, materiales y comunidad; el administrador revisa publicaciones y atiende reportes. Se incluyen progreso, evaluaciones, certificados y membresías según el documento 08.

El MVP no calcula comisiones ni liquidaciones. Las referencias de 13 no son tarifas propias ni una elección de proveedor. Presupuestar consumo gratuito, reproducciones posteriores a compra permanente, versiones históricas, correo, respaldos, soporte y mantenimiento. La estimación operativa completa y las condiciones de liquidación siguen pendientes.

### Aprendizaje y relación con creadores

La plataforma también incluirá progreso guardado, evaluaciones, certificados de finalización, preguntas, comunidad y un panel de creación. Las membresías ofrecen periodos temporales de acceso, con renovación simulada y manual mediante LNbits, junto a compras individuales permanentes. El detalle está en [funciones completas](investigacion-y-requisitos.md#08-aprendizaje-creadores-y-membresias); las referencias y necesidades propuestas están en [investigación](investigacion-y-requisitos.md#07-investigacion-y-necesidades).

### Comunidad junto al contenido

El lector incorpora conversaciones al final de las lecciones, conectadas con Comunidad y separadas de las preguntas privadas al creador. Los estudiantes inscritos con acceso a la lección pueden comentar y responder; el creador aprobado atiende y modera sus cursos. Esta decisión busca conservar el contexto de las dudas y reunir aclaraciones compartidas. Su utilidad educativa y el esfuerzo operativo siguen como hipótesis por evaluar. [Alcance y evaluación](investigacion-y-requisitos.md#20-comunidad-en-lecciones).

<a id="02-catalogo-de-prueba"></a>

## Catálogo de prueba

Origen: `strategy/02-catalogo-de-prueba.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Colección vigente de Bitcoin y Lightning

La colección publicada localmente el 12 de octubre de 2026 sustituye los ejemplos de programación siguientes como catálogo inicial. Son seis cursos con cuatro lecciones de texto cada uno, organizadas en dos capítulos. Los textos incluyen explicación, ejemplo, ejercicio y solución, con referencias técnicas. No incluyen videos ni archivos descargables. El perfil público es BTC.EDU y no representa a un instructor ficticio.

Bitcoin desde cero: unidades, red y transacciones; Wallets y autocustodia: claves, respaldo y recepción; y Lightning desde cero: canales, rutas y liquidez son completamente gratuitos. Facturas Lightning: del QR a la confirmación; LNbits: organiza un laboratorio de micropagos; y Contenido con micropagos: compra, acceso y versiones incluyen una primera lección gratuita y tres pagadas.

Cada curso pagado cuesta 120 sats y cada lección pagada se ofrece por 50 sats. Los precios son valores de prueba; no acreditan validación ni ingresos. Cada curso requiere completar sus cuatro lecciones y aprobar una pregunta final para obtener certificado; esa comprobación no demuestra dominio exhaustivo. Las duraciones son estimaciones para leer y realizar ejercicios, no tiempos medidos. Las prácticas no requieren fondos reales.

La carga se realiza con `python manage.py load_editorial_catalog` desde `src`, crea respaldo y conserva cursos existentes. [Reglas, comprobación y límites](../src/docs/operacion-y-bitacora.md#catalogo-editorial-2026-10-12). La revisión educativa externa sigue pendiente.

### Ejemplos históricos de programación

Los títulos, creadores y precios son ficticios. No representan contenido terminado, ventas ni precios validados. Los videos y archivos deben producirse o seleccionarse con permiso de uso antes de la demo.

| ID | Contenido | Organización | Acceso y precio |
|---|---|---|---|
| CUR-001 | Primeros pasos con JavaScript | Curso completamente gratuito | Gratis |
| LES-001 | Variables y operaciones | Lección de CUR-001 | Gratis |
| VID-001 | Ejemplo con variables | Video de CUR-001 | Gratis |
| CUR-002 | Funciones en JavaScript | Curso con lecciones gratis y capítulos de pago | Explorar gratis; compras indicadas abajo |
| LES-002 | Qué es una función | Lección de CUR-002 | Gratis |
| CHP-001 | Parámetros y resultados | Capítulo de CUR-002 con una lección y un video | 100 sats |
| VID-002 | Resolver un ejercicio con funciones | Video de CUR-002 vendido por separado, fuera de CHP-001 | 80 sats |
| MAT-001 | Ejercicios y soluciones | Archivo adicional de CUR-002 | 50 sats; no obligatorio |
| CUR-003 | Construye una API sencilla | Curso completo de pago | 300 sats por CHP-002 y CHP-003 |
| LES-003 | Presentación del proyecto | Lección de muestra de CUR-003 | Gratis |
| CHP-002 | Crear una ruta | Capítulo de CUR-003, con texto y video | 150 sats individualmente |
| CHP-003 | Validar los datos | Capítulo de CUR-003, con texto y video | 200 sats individualmente |
| MAT-002 | Lista de comprobación | Material de CUR-003, fuera de la compra del curso | Gratis |
| MAT-003 | Ejercicios adicionales de API | Material de CUR-003, fuera de la compra del curso | 60 sats |

### Muestras y contenido

La investigación de [13](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) no cambia los precios del catálogo. Mantener oferta y muestra constantes al comparar y permitir elegir ninguna compra. Probar lección útil para cursos, actividad para capítulos, fragmento para videos y extracto para materiales. Son variantes propuestas, no proporciones aprobadas. Cada activo necesita autoría/permiso y muestra separada del contenido protegido.

Cada página explica objetivo, requisitos, creador, formato y contenidos incluidos. Las lecciones gratuitas se muestran completas. Los capítulos de pago tienen una descripción y una muestra de texto separada del contenido comprado. Cada video de pago tiene una muestra pública independiente; el archivo completo no se entrega antes de verificar la compra. Los materiales describen formato y contenido y pueden mostrar un extracto público separado.

Ejemplo gratuito LES-001: `const precio = 10; const cantidad = 2;` y explicación de `precio * cantidad`.
Ejemplo de muestra de CHP-001: explicar qué son los parámetros e indicar que la compra incluye explicación completa y un video práctico.
Ejemplo de MAT-001: dos ejercicios con soluciones; la muestra muestra un enunciado y la compra entrega el archivo completo.

CUR-003 incluye únicamente CHP-002 y CHP-003 y sus lecciones y videos. MAT-003 se compra aparte. Su composición queda fija durante el MVP. La compra del curso cuesta 300 sats frente a 350 sats por los capítulos separados. Los recursos que se compran aparte también se enumeran antes de pagar.

Si ya se compró parte de CUR-003, se ofrecen los capítulos faltantes individualmente. Si ya se compró todo, se muestran los enlaces para abrirlo. No se calcula un descuento personalizado en esta versión.

### Datos adicionales para probar el alcance ampliado

Preparar un creador autorizado Aula Demo y otro creador para comprobar aislamiento; una evaluación de prueba con preguntas, nota mínima e intentos; una versión de CUR-003 con requisitos de certificado; un espacio de preguntas por lección y comunidad del curso; y un plan de 30 días con contenidos explícitos y precio ficticio. Los valores concretos de nota, intentos y precio se fijan en los datos de prueba y no representan validación comercial. Probar un alumno con compra individual y membresía que vence; no borrar su compra ni progreso.

<a id="06-plan-y-decisiones"></a>

## Plan y registro de decisiones

Origen: `strategy/06-plan-y-decisiones.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Alcance

Plataforma con cursos, capítulos, videos y materiales gratis o de pago, cuentas de alumnos y creadores, progreso, evaluaciones, certificados, preguntas, comunidad y membresías. Las compras individuales son permanentes; las membresías tienen acceso por periodo y renovación manual con pagos simulados de LNbits. Los documentos 07 y 08 sustentan y detallan esta ampliación.

### Calendario propuesto

El objetivo anterior de cerrar desarrollo el 15 de octubre se debe revisar con el equipo ante el alcance solicitado. Proponemos trabajar durante el sprint completo hasta la entrega planificada el 3 de noviembre. No se garantiza que todo esté terminado. Las 23–35 jornadas de 08 son una estimación histórica anterior y no representan el trabajo restante. Desde el 7 de octubre, el usuario confirma que trabaja solo en Business y Dev; las horas disponibles aún no están definidas.

Construir según la [arquitectura vigente](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu): primero modelo/versiones, estructura visual y descubrimiento (cursos, selector, tutoriales y recursos); cerrar cuenta, archivos protegidos, compras, inscripción y progreso básico; después panel de creador/revisión, evaluaciones/certificados, preguntas, comunidad y membresías. Accesibilidad y pruebas acompañan cada entrega. Eventos educativos después. Investigación, contenido y validación de Business avanzan en paralelo. El registro diario siguiente determina el avance vigente; el calendario y la disponibilidad todavía requieren revisión.

Mentoría del 13 de octubre: demostrar el curso gratuito, una compra de contenido y protección en el servidor, junto al editor y las demás funciones que estén realmente terminadas. Revisar el plazo al completar la primera fase. Reservar los últimos días antes de la entrega para correcciones y evidencia.

### Estado verificado

**12 de octubre de 2026 — catálogo Bitcoin y Lightning:** seis cursos publicados localmente, 24 lecciones con explicación, ejemplo, práctica y solución. Tres cursos gratuitos y tres con primera lección gratuita, ofertas de 120 sats por curso y 50 sats por lección. Seis preguntas finales y políticas de certificado. Carga con respaldo y sin duplicados; comprobación HTTP en copia temporal de catálogo, selector, fichas y lecciones, incluidos nueve bloqueos del texto pagado. Ruff aprobado para archivos nuevos. Sin nueva prueba de pago, certificado emitido ni validación con usuarios; precios y duraciones son hipótesis. [Entrega y evidencia reproducible](../src/docs/operacion-y-bitacora.md#catalogo-editorial-2026-10-12). Cambios paralelos de perfiles y comunidad fuera de esta entrega.

**10 de octubre de 2026 — conciliación periódica:** `reconcile_payments --watch` consulta lotes sin navegador, reintenta indisponibilidad, rota reservas sin emitir y conserva incidencias tardías sin permisos. 192 pruebas, migraciones, Ruff y los tres controles de concurrencia aprobados. Desarrollado en `main`, sin migración nueva ni cambios en la base principal. [Registro y evidencia](../src/docs/operacion-y-bitacora.md#conciliacion-2026-10-10). Requiere un terminal supervisado; servicio, alertas y prueba adicional de ZEUS siguen pendientes.

**10 de octubre de 2026 — ampliación SHA-256:** huella persistente por certificado, comparación web y exportación reproducible privada o compartida por decisión del titular. 184 pruebas, migraciones, Ruff y concurrencia aprobados; comprobación independiente con Node y formularios HTTP. La migración conservó 258 filas originales en 50 tablas, con respaldo. [Entrega vigente](../src/docs/operacion-y-bitacora.md#certificados-sha256-2026-10-10). El registro anterior conserva el estado del bloque esencial antes de añadir las huellas.

**10 de octubre de 2026:** bloque esencial de certificados, preguntas, notificaciones y paneles implementado. 179 pruebas, migraciones, revisión estática y tres comprobaciones de concurrencia pasan. Navegación y formularios por HTTP, escritorio/móvil y PDF comprobados; migración con respaldo conservó 211 filas originales, sin ejemplos en la base principal. [Entrega vigente y límites](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). Comunidad, membresías, operación pública y validación externa siguen pendientes. El usuario comprobará después el pago completo desde ZEUS.

**4 de octubre de 2026:** cuentas independientes, estudio y revisión editorial, ofertas, compra simulada integrada, derechos históricos, biblioteca, inscripción y progreso por versión. 129 pruebas pasan; integración real contra FakeWallet y concurrencia SQLite en archivo verificadas. Próxima fase: evaluaciones/certificados y preguntas; operación supervisada y validación siguen pendientes. Los párrafos fechados anteriores conservan su contexto histórico.

LNbits 1.6.2 funciona localmente con uv y FakeWallet. Se verificó creación de factura, pago interno y consulta por API, también después de mover todo el entorno técnico a src. Al 2 de octubre, el sitio cuenta con cuentas por correo, modelos de contenido, catálogo publicado con búsqueda y filtros, detalle de curso y lectura protegida de lecciones. Los pagos integrados y los módulos educativos adicionales siguen pendientes.

La investigación funcional se conserva en 07. Al 5 de octubre, [13](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) incorpora modelos, tarifas y costos con fuentes; [16](investigacion-y-requisitos.md#16-validacion-con-usuarios), métodos y guiones. No hay entrevistas, resultados externos ni precios validados. La publicación por creadores, certificados, comunidad, progreso y membresías conservan su lugar en el alcance.

### Organización actual

El 7 de octubre el usuario confirmó que BTC.EDU continúa como proyecto individual. Caleb asume Business y Dev: investigación, decisiones, desarrollo, verificación y documentación. La disponibilidad semanal no está definida; no se asignan jornadas ni fechas de cierre de módulos sin estimación. Se prioriza cerrar brechas del núcleo oficial y preparar el recorrido de mentoría antes de comprometer ampliaciones. El requisito original de cuatro integrantes sigue pendiente de aclaración con CUBO+; no se presupone una excepción autorizada.

### Trabajo del 7 de octubre

Se revisaron rama, historial, plan, requisitos originales y registros técnicos. La documentación anterior está integrada en main mediante d0bb7e4; se continuó en business/teorica actualizada a esa base. Se creó la matriz inicial 14 con requisitos oficiales, AC-01…35 y UX-01…12, evidencias relacionadas y tareas. La matriz identifica cobertura parcial de progreso de video, recuperación tras reinicio, accesibilidad y analítica administrativa. No se reejecutaron las 129 pruebas ni se realizaron entrevistas. D01 sigue abierto por disponibilidad y aclaración del equipo; D04 por auditoría de pruebas y recorridos específicos. Próximo paso: T-02/T-03, comprobar cobertura por criterio y especificar eventos/panel; preparar demo del núcleo para el 13 de octubre. El informe y la exportación copiable incorporan esta organización. Google Docs permanece a cargo del usuario; no se editó directamente.
### Trabajo diario y requisitos oficiales

**5 de octubre de 2026 — documentación de Business:** por autorización del usuario se incorporó la investigación presentada sobre monetización, tarifas, muestras, video y métodos de validación. Se actualizaron las referencias y pendientes, y se preparó el [documento principal](19-recomendacion-y-entrega-final.md) con títulos sencillos y sin campos de portada añadidos. El usuario copiará el contenido a Google Docs; no se editó allí ni se creó historial retroactivo. Trabajo realizado en `business/teorica`; cambios locales, sin publicación. Evidencias: documentos 13 y 16 con fuentes y cálculos; informe 19 y documentos relacionados. Las 129 pruebas siguen siendo el registro del 4 de octubre. No hay participantes ni validación externa. Próximo paso: responsables, reclutamiento/consentimiento, ejecución y análisis; completar presupuesto y trazabilidad. Esta entrada se actualiza si los cambios se versionan o publican posteriormente.

**4 de octubre de 2026 — experiencia de compra:** el usuario pidió lenguaje realista y preparación como producto. Se entregó resumen → continuar → pagar con importe → confirmación → biblioteca; precios en sats, estados de procesamiento y errores comprensibles. Una indicación común identifica el entorno de desarrollo con saldo de prueba; FakeWallet y sus comprobaciones permanecen activos. 60 pruebas relacionadas, Ruff, consistencia de migraciones, smoke del proveedor y compra en navegador pasan. No hay migraciones ni datos de ejemplo en la base principal. Commit funcional `d36b152`; [registro y evidencia](../src/docs/operacion-y-bitacora.md#experiencia-compra-2026-10-04). Wallet externa, pagos reales y operación pública siguen pendientes.

**4 de octubre de 2026 — comercio y continuidad de aprendizaje:** por autorización del usuario se cerró el recorrido creador → revisión/publicación → oferta → compra simulada → biblioteca → aprendizaje. Precio e inventario se congelan por factura; derechos y progreso permanecen en su versión aunque cambie la publicación. Incluye alternativas individuales, prevención de recompras, evidencia de incidencias, recuperación de emisión incierta y avance sin sobrescritura entre sesiones. 129 pruebas, migraciones, revisión estática y concurrencia con conexiones SQLite separadas pasan. Compra integrada contra LNbits FakeWallet, petición autenticada con CSRF y respuesta perdida verificadas; escritorio/móvil inspeccionados en navegador. Respaldos y migraciones aplicados sin poblar la base principal. Commits funcionales `1e470de` y `aa70fca`; documentación/evidencia en un commit adicional. [Registro y límites](../src/docs/operacion-y-bitacora.md#comercio-y-aprendizaje-2026-10-04). Conciliación disponible como comando, aún sin supervisor periódico. Evaluaciones, certificados, preguntas, comunidad, membresías y métricas conservan el alcance del proyecto completo.

**4 de octubre de 2026 — cierre con commits:** por petición del usuario, cada bloque terminado debe quedar guardado en commits al cerrar el trabajo. El estudio de creadores y las cuentas independientes se versionan juntos por sus dependencias de acceso; documentación y evidencia se guardan en otro commit. Publicar los commits al remoto es un paso separado.

**3 de octubre de 2026 — cuentas independientes:** el usuario confirmó separar las cuentas de estudiante y creador. Se implementaron registro/login, recuperación y perfiles por espacio, autenticación por correo/tipo, menú propio del estudio y administración independiente. La aprobación sigue siendo necesaria para operar como creador. 96 pruebas pasan, incluida migración con datos históricos y recuperación sin afectar la otra identidad. Base local respaldada/migrada sin cuentas ni ejemplos. [Evidencia y límites](../src/docs/operacion-y-bitacora.md#cuentas-independientes-2026-10-03). Esta decisión sustituye las referencias anteriores a una cuenta compartida con roles.

**3 de octubre de 2026 — estudio de creadores:** se definió el enfoque integral y se implementaron solicitud/aprobación, perfil público, panel, edición de cursos/tutoriales/capítulos/lecciones, recursos, cargas privadas, vista previa y revisión editorial con observaciones. Los envíos congelan contenido; aprobar publica la copia revisada y conserva las publicaciones anteriores. 77 pruebas, migraciones y revisión estática pasan; recorrido verificado en navegador con datos temporales. Respaldo y migración aplicados sin añadir cuentas ni contenido a la base real. [Registro y límites](../src/docs/operacion-y-bitacora.md#estudio-creadores-2026-10-03). Próximo bloque: ofertas/compras y derechos históricos, inscripción/progreso; después acompañamiento y módulos ampliados del [enfoque de creadores](investigacion-y-requisitos.md#11-enfoque-creadores).

**2 de octubre de 2026 — versiones y archivos:** se implementaron composiciones publicadas selladas, revisiones reutilizables, carga privada validada en administración, reproducción MP4 con VTT/transcripción y descarga PDF/TXT con autorización por contexto. Se preservan IDs, texto y archivos anteriores; editar no cambia el contenido publicado hasta la siguiente publicación. 54 pruebas, migraciones y revisión estática pasan; reproducción/descarga y vistas móvil/escritorio verificadas con temporales separados. Respaldo antes de migrar y cantidades originales conservadas. [Registro y límites](../src/docs/operacion-y-bitacora.md#contenido-versiones-y-archivos-2026-10-02). Siguiente: comercio simulado y derechos sobre revisiones, incluido acceso adquirido a versiones históricas; después inscripción/progreso. Panel de creador y despliegue siguen pendientes.

**2 de octubre de 2026 — interfaz de academia:** el usuario eligió estética industrial más marcada. Se construyeron cursos, selector, tutoriales y recursos con metadatos configurables y navegación común, fichas/lectura/cuenta integradas, filtros y regreso conservados, temario plegable y estados vacíos. 32 pruebas y revisión estática pasan; revisión en navegador de escritorio/móvil con datos temporales separados. Respaldo/migración preservaron los registros y no se cargó catálogo real. Evidencia: [registro de interfaz](../src/docs/operacion-y-bitacora.md#interfaz-academia-2026-10-02). Archivos, versiones, compras y progreso permanecen pendientes.

**2 de octubre de 2026 — definición de arquitectura:** se revisaron código, documentación y cuatro capturas de referencia. El usuario confirmó cursos, tutoriales y recursos en la primera versión, eventos después. Se documentaron navegación, selector, recursos reutilizables, biblioteca/progreso, versiones, compras y protección, con módulos y criterios UX-01…12. Se aclararon acceso a compras archivadas, integridad SQLite y evidencia de pagos en conflicto. Evidencia: [producto y experiencia](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu) y [arquitectura técnica](../src/docs/operacion-y-bitacora.md#arquitectura-btc-edu). Son decisiones de diseño; no se implementaron módulos ni se cargó contenido. Próximo paso: modelo/versionado y prototipo de estructura de academia con datos temporales.

**2 de octubre de 2026 — desarrollo con Codex:** se implementó el recorrido catálogo → curso → lección siguiendo las necesidades propuestas de claridad del acceso, objetivos, requisitos y navegación del documento 07. Evidencia: 24 pruebas, revisión estática y [registro técnico](../src/docs/operacion-y-bitacora.md#recorrido-aprendizaje-2026-10-02). No se cargó contenido en la base del usuario. Próximo paso: ofertas, precios y compras simuladas con permisos persistentes. La validación con personas sigue pendiente.

Registrar fecha, responsable, trabajo real, evidencia, decisiones, bloqueo y próximo paso. No crear actividad retroactiva. El assignment pide avances diarios en GitHub y un Google Doc con historial para Business; el enlace sigue pendiente.

Aclarar equipo de dos integrantes frente a cuatro exigidos, fecha de cierre interna y fecha oficial de entrega: el documento indica tanto 3 como 8 de noviembre. Planificar con el 3 hasta confirmar. Demo prevista el 8 de noviembre.

### Trabajo del 10 de octubre

Commit funcional local: `bb3745c`. La documentación y evidencia se conservan en el commit de cierre de esta entrega. No se publicaron al remoto.

Por petición del usuario se implementaron certificados, preguntas, notificaciones, métricas y paneles para cerrar el desarrollo esencial. Se congelan requisitos con el envío editorial; emisión histórica única, PDF privado, compartir voluntario y revocación auditada. Se añadieron conversaciones privadas, avisos idempotentes y consultas con cohortes/denominadores explícitos. Pruebas y evidencias reales en el registro técnico; base temporal para ejemplos y respaldo de la base principal. Se actualizaron 05/08/11/12/14/15/19 y la exportación de texto. No se ejecutaron entrevistas, pruebas con fondos reales ni despliegue público. El cierre se guarda en commits locales, sin publicar al remoto.

### Ampliación de certificados del 10 de octubre

El usuario solicitó SHA-256 para verificar certificados. Se adoptó una huella de datos históricos guardada al emitir, visible en PDF/web y reproducible con JSON; comparación con el registro de BTC.EDU, conservando privacidad y revocación. Se documenta la diferencia entre hash y firma y no se presenta como registro Bitcoin. Evidencia técnica y pruebas específicas en el registro de certificados SHA-256. Se guardará el bloque en commit local, sin push.

### Comunidad y moderación del 10 de octubre

Por elección del usuario se continúa desarrollo técnico con comunidad por versión, acceso por inscripción, respuestas y reportes, moderación con motivo e historial y suspensión reversible de escritura. Se mantienen compras, progreso y lectura. Se añaden avisos internos y pruebas de permisos, privacidad, reintentos y concurrencia. [Reglas y evidencia](../src/docs/operacion-y-bitacora.md#comunidad-2026-10-10). Implementación en commit local 3a465c3, sobre main; se preservan los archivos de revisión integrada que ya estaban sin seguimiento. Membresías y operación pública siguen pendientes. No se ejecutan sesiones externas ni se publica al remoto.

**12 de octubre de 2026 — cursos, lectura y continuidad:** inspección del recorrido actual y consulta de NN/g, W3C y ayuda oficial de Udemy. Se implementaron continuación compartida entre ficha y biblioteca, estados del temario, prácticas con solución desplegable, lectura enfocada, búsqueda/estados y actualización confirmada del avance. Base Git `4000ed5`, rama `main`, cambios locales anteriores conservados; sin commit propio en esta entrega. [Decisiones, comprobaciones y límites](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12). Las sesiones externas y los resultados educativos continúan pendientes.

### Conversación al final de cada lección

El 12 de octubre de 2026 el usuario autorizó implementar la propuesta de comunidad vinculada a lecciones. Se reutiliza la comunidad por versión: una misma conversación puede abrirse en el lector y en Comunidad, sin copias. Los comentarios de lecciones de pago exigen acceso al contenido incluso desde búsqueda o un enlace directo; la inscripción por sí sola no desbloquea ese intercambio. La pregunta privada conserva su función. [Propuesta y alcance](investigacion-y-requisitos.md#20-comunidad-en-lecciones). El registro técnico conserva las pruebas y las limitaciones reales de esta ejecución.

**12 de octubre de 2026 — corrección visual del temario:** una captura del usuario reveló que una regla heredada estiraba el marcador circular. Se corrigió la herencia de flex y se verificaron proporciones 1:1 en curso y lector, incluido móvil. [Causa y evidencia](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12). El texto principal mantiene sus secciones, pues no cambia el comportamiento educativo.

**12 de octubre de 2026 — UI/UX de evaluaciones:** se inspeccionó la interfaz actual y se consultaron referencias primarias de LatitudeLearning, GOV.UK y Duolingo. Se implementaron preparación separada, pregunta por pantalla, opciones amplias, avance, revisión previa, resultados de repaso y editor plegable. Rama `main`, cambios locales previos conservados, sin commit propio en esta entrega. Pasaron 29 pruebas enfocadas y se verificó el recorrido por HTTP en una base temporal. [Decisiones, evidencias y límites](../src/docs/operacion-y-bitacora.md#experiencia-evaluaciones-2026-10-12). Validación externa pendiente.

<a id="12-plan-documentacion-business-a-desarrollo"></a>

## Plan de documentación: Business → Desarrollo

Origen: `strategy/12-plan-documentacion-business-a-desarrollo.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Fecha: 5 de octubre de 2026 (El Salvador). Rama de trabajo: `business/teorica`, creada desde `main` en `c0ac528`. El plan se actualiza con la investigación documental incorporada en 13, los instrumentos de 16 y el informe de 19. No acredita sesiones externas ni nuevas funciones.

### Objetivo y punto de partida

Preparar un paquete de decisiones, especificaciones y evidencias que permita continuar el desarrollo sin ambigüedades y cumplir los entregables estratégicos del assignment. El desarrollo ya comenzó: la documentación registra cuentas separadas, publicación versionada, compras simuladas, biblioteca y progreso. Las 129 pruebas son un resultado registrado al 4 de octubre, no una ejecución nueva de esta revisión.

Las fuentes de alcance son los originales de `docs/Micropayments for Content.docx` y `docs/assignment final evaluation.docx`, los documentos 01–11 de esta carpeta y los registros de `src/docs`. La documentación existente debe completarse y armonizarse antes de duplicarla.

El assignment exige investigación de modelos de monetización, usuarios, precios, muestras, recorrido de pago, prototipo, métricas y recomendación; además, oportunidad/impacto, operación/recursos y Google Doc con historial. Evaluaciones, certificados, comunidad y membresías son ampliaciones del equipo: se conservan en el alcance, con entregas separadas del núcleo exigido.

### Documento principal del proyecto exigido para la entrega

La evaluación exige entregar un **PDF que detalle la solución estratégica del caso de estudio**, junto con un archivo `.txt` que contenga el enlace al repositorio público. El documento principal del proyecto será ese informe integrado: explicará BTC.EDU a un evaluador que no conoce el repositorio y remitirá a evidencias concretas. Su preparación empieza ahora y se actualiza durante el trabajo; la exportación final depende de los resultados disponibles. D13 incluye este informe además de la recomendación y preparación de entrega.

El PDF, los documentos de trabajo de `/strategy` y el Google Doc con historial cumplen funciones distintas. El informe presenta la solución y sus resultados; los documentos de trabajo permiten construirla y verificarla; el Google Doc acredita evolución diaria real. La evaluación también exige especificaciones claras y una prueba de concepto funcional: describirlas en el informe debe ir acompañado de evidencia accesible.

#### Índice propuesto del informe

Este índice es una propuesta del equipo alineada con los originales; CUBO+ no fija un índice, extensión ni plantilla en los archivos recibidos.

La estructura acordada posteriormente con el usuario sustituye la propuesta inicial: Introducción; La idea; El problema; Cómo consolidamos la idea; Investigación; Objetivos; Enfoque; Desarrollo; A dónde queremos llegar; Qué demostramos; Logros; Próximos pasos; Conclusiones; Referencias. El [informe](19-recomendacion-y-entrega-final.md) desarrolla esta estructura investigativa.

Usar títulos naturales y omitir campos de país, caso, fecha de actualización, estado, equipo y repositorio en la portada; el usuario los añadirá si corresponde. Mantener fechas/versiones en bitácora y evidencias. Los criterios de evaluación siguen cubiertos por el contenido y anexos: oportunidad, monetización, prototipo/especificaciones, métricas, operación, colaboración y recomendación. No se eliminan requisitos del assignment por esta preferencia editorial.

#### Relación con los pilares de evaluación

| Pilar del original de evaluación | Cómo lo cubrirá el informe | Evidencia acompañante |
|---|---|---|
| Transparencia y evolución | Avances y decisiones fechados, con límites explícitos | Commits publicados y Google Doc con historial accesible |
| Ejecución técnica | Explicación de funcionamiento y verificación | Código organizado, README técnico, pruebas y demo funcional |
| Colaboración real | Contribuciones de Business y Dev al mismo problema y decisiones compartidas | Trabajo por integrante, especificaciones, validación y prueba de concepto |
| Documentación | Informe comprensible y recorridos reproducibles | Reportes de avance y manuales de usuario |
| Propuesta de valor | Utilidad e innovación justificadas para el ecosistema Bitcoin en El Salvador | Investigación, hallazgos, comparación de alternativas y resultados |

No se asignan pesos ni puntuaciones: los originales proporcionados no los especifican. Antes de exportar, comprobar que cada afirmación de resultado tiene evidencia, que los enlaces son accesibles al jurado y que el contenido coincide con la versión demostrada.

### Inventario y brechas

| Área | Base existente | Brecha para desarrollo o entrega |
|---|---|---|
| Producto y oportunidad | 01, 07 | Problema respaldado por usuarios; segmento prioritario; impacto práctico para el ecosistema de Bitcoin en El Salvador |
| Mercado y monetización | 07 funcional; 13 modelos/tarifas/costos | Contrastar con usuarios y presupuesto; recomendación comercial final |
| Catálogo y precios | 02, precios ficticios | Justificación, límites de muestra, inventario editorial y derechos de cada archivo |
| Requisitos y reglas | 03, 08, 10, 11 | Matriz única de trazabilidad, decisiones abiertas y detalle de los módulos pendientes |
| Experiencia | 04, 09, 10 y pantallas implementadas | Prototipo navegable de nuevas vistas, estados alternativos y resultados de pruebas con personas |
| Métricas | 05 | Contrato de eventos, cobertura implementada, consultas verificables y especificación del panel administrativo |
| Operación | Referencias en 13, 01/11 y documentos técnicos | Presupuesto completo, escenarios de consumo, sostenibilidad y responsabilidades |
| Plan y evidencia | 06 y registros técnicos | Capacidad real, responsables, riesgos, enlace a Google Doc e historial diario auditable |
| Entrega | README técnico y evidencias fechadas | Recomendación final, manuales, PDF estratégico y guion de demostración |

### Paquetes de trabajo

P0 prepara la próxima entrega de desarrollo; P1 completa la validación y preparación de entrega; P2 consolida resultados finales. Los responsables son funciones propuestas, pendientes de asignar a personas. Business redacta las decisiones de producto; Dev revisa viabilidad y documenta contratos técnicos; ambos verifican aceptación.

| ID / prioridad | Documento y ubicación propuesta | Contenido que debe producirse | Criterio para darlo por terminado | Dependencia / responsable |
|---|---|---|---|---|
| D01 / P0 | Actualizar 06: alcance, decisiones y capacidad | Núcleo del assignment, ampliaciones por entrega, disponibilidad, responsables, riesgos y decisiones abiertas con fecha | Cada entrega tiene alcance, responsable, dependencia y condición de cierre; fechas inciertas visibles | Ninguna / Business + Dev |
| D02 / P0 | Actualizar 01 y 07: oportunidad y usuarios | Segmento inicial, problema concreto, alternativas actuales, hipótesis e impacto local; guion y reclutamiento | Cada afirmación se identifica como fuente, hipótesis o hallazgo; no se inventan entrevistas | D01 / Business |
| D03 / P0 | `13-monetizacion-precios-y-muestras.md` | Comparación de cuatro modelos, precios de referencias, propuesta, compras repetidas, muestras por formato y preguntas de validación | Matriz con fuentes/fechas; precio e inclusión de cada oferta justificados como hipótesis o evidencia; acceso permanente/temporal claro | D02 / Business; revisión Dev |
| D04 / P0 | `14-trazabilidad-y-backlog.md`; armonizar 03/08/10/11 | Requisito oficial o ampliación → regla → historia → aceptación → pantalla → evidencia → estado | Todos los requisitos oficiales y AC-01…35/UX vigentes están vinculados; cada brecha tiene una tarea y prioridad | D01 y D03 / Business + Dev |
| D05 / P0 | Actualizar 04; prototipos en `strategy/prototipos/` | Recorridos de alumno, creador y administrador; estados vacíos, errores, permisos, móvil y teclado | Prototipo ejecutable/navegable y enlace o instrucciones; cada tarea se puede recorrer y cada pantalla tiene aceptación | D04 / Business; revisión Dev |
| D06 / P0 por módulo | `15-especificaciones-modulos-pendientes.md`; detalle técnico en `src/docs/` | Evaluaciones/certificados, preguntas/avisos, comunidad/moderación y membresías; matriz de roles y estados | Para cada módulo: entradas, reglas, transiciones, datos históricos, errores y escenarios aceptados; Dev puede estimarlo sin decidir políticas de producto | D04/D05 / Business + Dev |
| D07 / P0 | Actualizar 05; contrato técnico en `src/docs/` | Eventos del embudo, propiedades, deduplicación, permisos, retención propuesta, denominadores y panel básico | Cada KPI tiene evento/fuente/consulta, ejemplo calculable y manejo de cero; cobertura real distinguida de diseño | D04 / Business + Dev |
| D08 / P1 | `16-validacion-con-usuarios.md` | Consentimiento, guiones, tareas, notas, resultados y cambios priorizados | Sesiones reales fechadas; muestra y limitaciones explícitas; hallazgo → decisión → cambio → nueva comprobación cuando corresponda | D02/D03/D05 / Business |
| D09 / P1 | `17-modelo-operativo-y-recursos.md` | Recursos humanos, alojamiento, video/archivos, correo, soporte, moderación, mantenimiento, costos y sostenibilidad | Escenarios de uso y costos con supuestos/fuentes; responsable y frecuencia de cada operación; separación entre volumen simulado e ingresos | D01/D03/D06 / Business + Dev |
| D10 / P1 | Completar 02; `18-politica-editorial-y-contenido.md` | Catálogo de demostración, procedencia/licencias, muestras, subtítulos, revisión y continuidad de acceso | Cada activo tiene permiso, autor, versión, formato y estado; ofertas coherentes; datos de demo aislados de la base principal | D03/D05 / Business; revisión Dev |
| D11 / P0–P1 | Actualizar 06 y crear registro de trabajo en Google Docs | Bitácora real por fecha: persona, cambio, evidencia, decisión y siguiente paso | Enlace accesible y permisos comprobados; historial de edición continuo desde su creación; vínculo a commits/evidencias reales | Iniciar desde ahora / Business + equipo |
| D12 / P1 | Manuales en `strategy/manuales/`; operación técnica en `src/docs/` | Alumno: compra/recuperación/biblioteca; creador: revisión/publicación; administrador: incidencias; instalación, respaldo/restauración y límites | Otra persona puede completar las tareas documentadas; capturas coinciden con la entrega; pasos técnicos verificados por Dev | Entrega funcional correspondiente / Business + Dev |
| D13 / P0 → P2 | Informe principal en `19-recomendacion-y-entrega-final.md` y PDF estratégico | Redacción progresiva del documento del proyecto según el índice de este plan; caso estratégico, evidencia, recomendación, resultados y anexos; guion de demo de 10 minutos | Cobertura de los cinco pilares; recomendación sustentada en D03/D08/D09; PDF revisado; archivo .txt del repositorio público y enlaces comprobados | Iniciar con fuentes existentes; cierre con D08–D12 / equipo |

Estado del 5 de octubre: D03 tiene comparación y recomendación provisional en 13, pendiente de validar precios y sostenibilidad; D08 tiene instrumentos en 16, pendiente de ejecución/resultados; D13 tiene informe integrado en 19, pendiente de resultados finales, PDF y anexos. D02 sigue pendiente de evidencia con usuarios y D09 del presupuesto completo. Los otros archivos propuestos no se crean como encabezados vacíos. Este avance no cierra los criterios de aceptación de paquetes todavía incompletos.

### Decisiones que deben cerrarse antes de programar cada módulo

| Tema | Decisión/documentación necesaria |
|---|---|
| Evaluaciones | Puntuación de selección múltiple, redondeo, intentos interrumpidos, momento de mostrar respuestas, espera y reinicio autorizado; mantener corrección en servidor |
| Certificados | Requisitos congelados por versión, nombre mostrado, privacidad de verificación, correcciones/revocación y su evidencia; una credencial por alumno/versión |
| Preguntas y avisos | Quién lee/escribe/responde, acceso tras vencer membresía, estados, edición/eliminación y avisos internos; responsabilidades y tiempo objetivo de atención |
| Comunidad | Alcance del espacio, participación, reportes, escalamiento, suspensión y conservación de historial; permisos propios del creador |
| Membresías | Versión del plan, inicio/fin, zona horaria de presentación, factura pendiente al vencer, cambios de plan, cancelación y acceso histórico; renovación manual de 30 días |
| Analítica | Qué eventos existen realmente, fuente de verdad, visibilidad por creador/administrador y tratamiento de datos; no inferir aprendizaje de aperturas |
| Operación | Conciliación periódica supervisada, correo, cuotas, respaldo/restauración, archivos huérfanos, incidencias y condiciones para operación pública |

No reabrir decisiones confirmadas sin motivo y registro: cuentas independientes, compras permanentes por versión, pagos simulados, conservación de derechos históricos y bloqueo provisional de compras conjuntas parcialmente adquiridas.

### Orden de ejecución y calendario propuesto

1. **5–7 de octubre:** D01/D02 y matriz inicial D04; iniciar D11 y la redacción del informe principal D13 con hechos y fuentes existentes. Armonizar documentos que mezclan diseño y estado actual. Identificar responsables, participantes y capacidad disponible.
2. **8–12 de octubre:** D03, D05, contrato D07 y primeras sesiones D08. Preparar el paquete de la siguiente entrega con D06. Para mentoría, reunir evidencias del núcleo ya construido y declarar pendientes.
3. **13 de octubre:** mentoría: demostrar un recorrido real y explicar oportunidad, reglas de acceso, hipótesis comerciales y evidencia disponible. Registrar observaciones sin simular validación externa.
4. **14–23 de octubre:** completar D06 por orden de desarrollo; iterar D05/D08; cerrar D09/D10. Entregar cada módulo a Dev cuando cumpla sus condiciones, sin esperar a terminar todo Business.
5. **24–30 de octubre:** verificar D04 contra la entrega, probar manuales D12 y consolidar D13. Corregir contradicciones y enlaces.
6. **31 de octubre–3 de noviembre:** revisar/exportar PDF estratégico, archivo .txt del repositorio, permisos e historial; ensayar demostración. Planificar entrega para el 3 de noviembre mientras se confirma la contradicción del original, que también menciona envío el 8. Demo prevista el 8 de noviembre.

Estas ventanas ordenan trabajo, no prometen capacidad. Si falta disponibilidad, mantener el alcance completo documentado y declarar qué entrega se construye y qué queda pendiente. No reutilizar las 23–35 jornadas antiguas como estimación del trabajo restante.

### Condiciones de paso a desarrollo

Una entrega está preparada cuando: tiene objetivo y prioridad; reglas y dudas bloqueantes resueltas; historias con aceptación; pantallas y estados revisados; datos/permisos/versiones definidos; eventos necesarios especificados; dependencias y estimación técnica revisadas; y evidencia de revisión registrada. Una hipótesis aún no validada puede pasar a un experimento identificado, con riesgo y prueba previstos; no se presenta como demanda comprobada.

La rama de desarrollo debe recibir una entrega trazable: versión/commit de los documentos, resumen de decisiones, tareas concretas, prototipo y escenarios de aceptación. El nombre de la rama destino y el mecanismo de integración se acuerdan antes de integrar; no se presume que exista una rama `development`. Este plan no incorpora cambios de código.

### Cierre documental de la entrega final

- Cada exigencia del assignment tiene documento y evidencia localizable en D04, incluidos analítica administrativa, arquitectura/API, pruebas y posibilidades futuras de Bitcoin/Lightning.
- La validación externa, pruebas internas y resultados simulados se distinguen; la recomendación reconoce límites y decisiones pendientes.
- `/strategy` contiene oportunidad/impacto, especificaciones y prototipo funcional, operación/recursos y enlace al Google Doc con historial real.
- `/src` conserva instalación, arquitectura, lógica, pruebas, limitaciones y manuales técnicos actualizados; el historial diario remoto se verifica, no se infiere del historial local.
- La entrega incluye PDF estratégico, enlace público del repositorio en .txt y demo de 10 minutos ensayada.
- Equipo y fecha se confirman: el original exige cuatro personas (2 Dev y 2 Business) y contiene fechas de envío contradictorias. Registrar la respuesta oficial en 06.

### Próxima acción

Ejecutar D01/D04: responsables, capacidad y matriz requisito → evidencia → tarea. Usar 13/16 para reclutar con consentimiento, ejecutar sesiones y analizar hallazgos; estimar presupuesto antes de cerrar precios. Entregar a Dev módulos listos mientras avanza la validación. Cada entrega debe actualizar estado, evidencia y secciones afectadas del informe 19; proporcionar al usuario texto completo para copiar a Google Docs. Conservar historial en 06 y registros técnicos, sin actividad retroactiva.

### Revisión del 7 de octubre

El usuario confirma continuidad individual: Caleb asume Business y Dev, con horas disponibles por definir. D01 registra esta organización en 06; la condición de cuatro integrantes requiere aclaración con CUBO+. D04 tiene una matriz inicial en 14 con los requisitos oficiales y 47 criterios AC/UX; sigue abierto hasta auditar pruebas y recorridos específicos. La siguiente tarea documental es T-02/T-03: precisar cobertura y contrato de analítica administrativa. No se ejecutaron sesiones ni nuevas pruebas. El calendario continúa siendo orientativo y se ajustará a capacidad real.

### Entrega esencial del 10 de octubre

Por prioridad del usuario, certificados, preguntas, notificaciones y paneles quedaron implementados y verificados sobre main, sin cambiar de rama. D06 dispone de reglas adoptadas en 15 y evidencia técnica; mantiene comunidad, membresías y correcciones de credenciales pendientes. D07 dispone de contrato actualizado en 05, consultas, permisos y paneles probados; no declara reproducción, muestras ni actividad histórica inexistente. D04 enlaza los nuevos criterios en 14. D13 refleja la versión disponible en 19 y el texto plano para copia manual. D08 sigue sin sesiones externas y D09 sin presupuesto completo.

La siguiente prioridad esencial es catálogo/derechos, manuales y ensayo de la demostración; posteriormente correo, conciliación supervisada y procedimientos operativos. El usuario conserva la comprobación móvil del pago. La entrega no cierra automáticamente el assignment completo ni las ampliaciones pendientes; resultados y límites en [registro](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10).

### Avance técnico posterior del 10 de octubre

Por petición del usuario de continuar el desarrollo técnico, se implementó conciliación periódica con `reconcile_payments --watch`. Se verificaron reintentos, rotación de lotes y conservación de reglas de acceso: 192 pruebas, revisión estática, migraciones y tres controles de concurrencia aprobados. [Evidencia y límites](../src/docs/operacion-y-bitacora.md#conciliacion-2026-10-10). La herramienta se ejecuta en un terminal supervisado; instalación como servicio, alertas y comprobación de pago desde ZEUS siguen pendientes. Este avance no acredita validación externa ni cierra D09/D12.

### Comunidad y moderación del 10 de octubre

Por elección del usuario se continúa desarrollo técnico con comunidad por versión, acceso por inscripción, respuestas y reportes, moderación con motivo e historial y suspensión reversible de escritura. Se mantienen compras, progreso y lectura. Se añaden avisos internos y pruebas de permisos, privacidad, reintentos y concurrencia. [Reglas y evidencia](../src/docs/operacion-y-bitacora.md#comunidad-2026-10-10). Trabajo en main; se preservan los archivos de revisión integrada que ya estaban sin seguimiento. Membresías y operación pública siguen pendientes. No se ejecutan sesiones externas ni se publica al remoto.

<a id="readme"></a>

## Producto y especificaciones

Origen: `strategy/README.md`. Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

El proyecto es una plataforma web de cursos, videos y materiales, con contenido gratis y de pago. La colección inicial publicada localmente reúne seis cursos de Bitcoin y Lightning con 24 lecciones de texto, prácticas y soluciones. Tres cursos son gratuitos y tres combinan muestra gratuita y lecciones de pago. Los precios son de prueba y la revisión educativa externa sigue pendiente. Los ejemplos históricos de programación permanecen documentados por separado.

La [arquitectura de producto y experiencia](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu) es la referencia vigente de estructura: cursos, tutoriales y biblioteca de recursos en la primera academia funcional, eventos educativos después. Distingue lo implementado del diseño y organiza las ampliaciones por entregas.

### Documentos

- [Documento de BTC.EDU](19-recomendacion-y-entrega-final.md): texto completo para copiar a Google Docs y actualizar con cada entrega.
- [Monetización, precios y muestras](investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras): comparación, fuentes, cálculos y límites.
- [Trazabilidad y trabajo pendiente](investigacion-y-requisitos.md#14-trazabilidad-y-backlog): requisitos oficiales, criterios AC/UX y matriz inicial de evidencias y brechas.
- [Validación con usuarios](investigacion-y-requisitos.md#16-validacion-con-usuarios): guiones, tareas, precios y registro; ejecución pendiente.
- [Plan de documentación Business → Desarrollo (5 de octubre)](investigacion-y-requisitos.md#12-plan-documentacion-business-a-desarrollo): brechas, entregables, dependencias y condiciones de paso.
- [Producto y negocio](investigacion-y-requisitos.md#01-producto-y-negocio)
- [Catálogo de prueba](investigacion-y-requisitos.md#02-catalogo-de-prueba)
- [Reglas y criterios de aceptación](investigacion-y-requisitos.md#03-especificacion-funcional)
- [Pantallas y recorrido](investigacion-y-requisitos.md#04-pantallas-y-recorrido)
- [Métricas y validación](investigacion-y-requisitos.md#05-metricas-y-validacion)
- [Plan y decisiones](investigacion-y-requisitos.md#06-plan-y-decisiones)
- [Investigación y necesidades de alumnos y creadores](investigacion-y-requisitos.md#07-investigacion-y-necesidades)
- [Aprendizaje, creadores, comunidad y membresías](investigacion-y-requisitos.md#08-aprendizaje-creadores-y-membresias)
- [Identidad visual](investigacion-y-requisitos.md#09-identidad-visual)
- [Arquitectura y experiencia de BTC.EDU](investigacion-y-requisitos.md#10-arquitectura-y-experiencia-btc-edu)
- [Enfoque integral para creadores](investigacion-y-requisitos.md#11-enfoque-creadores)

### Qué exige el assignment y qué decidimos

El assignment exige plataforma con contenidos gratis y de pago, facturas simuladas, protección en el servidor, acceso persistente, administración, eventos, diseño adaptable y documentación técnica. Permite lecciones, videos y descargas; no obliga a desarrollar todas las funciones de una plataforma educativa.

El equipo eligió organizar el producto en cursos, capítulos, lecciones, videos y materiales con compras individuales y de cursos completos. El acceso comprado será permanente dentro del MVP, asociado a una cuenta con correo y contraseña. El creador aprobado prepara su contenido y el administrador revisa su publicación. Los contenidos parcialmente adquiridos se ofrecen por separado sin descuentos personalizados.

Al 4 de octubre de 2026, LNbits FakeWallet está integrado: ofertas y revisión, facturas, compra simulada, derechos permanentes sobre revisiones, biblioteca, inscripción y progreso funcionan en desarrollo. No hay fondos reales. Se verificaron vencimientos, pagos en conflicto, recuperación de respuesta perdida y actualizaciones simultáneas. Hay un comando de conciliación; su ejecución periódica supervisada queda pendiente. [Estado, 129 pruebas y evidencia](../src/docs/operacion-y-bitacora.md#comercio-y-aprendizaje-2026-10-04).

Todo el código y la documentación técnica están en [src](../src/docs/operacion-y-bitacora.md#guia-local-anterior). Esta carpeta conserva investigación, requisitos, prototipo y decisiones de Business. Los documentos originales del assignment permanecen en docs sin modificaciones.

### Pendientes

La comparación documental de modelos/tarifas/costos y los instrumentos de entrevistas/usabilidad/precios están preparados al 5 de octubre. Hay una recomendación provisional y un documento principal integrado. Siguen pendientes sesiones externas, precios validados, prototipos nuevos, presupuesto completo, recomendación final y enlace al Google Doc con historial. El usuario incorporará el texto manualmente. Revisar capacidad, equipo y fechas oficiales. No se añadieron funciones ni se modificaron precios por esta actualización.

### Alcance ampliado

Se incluyen progreso, evaluaciones, certificados, preguntas, comunidad, panel de creador y membresías con renovación simulada manual. Los detalles están en el documento 08 y el diseño técnico en src/docs/diseno-plataforma.md. Las funciones observadas en otras plataformas respaldan el diseño, pero todavía deben validarse con usuarios. El estudio de creadores, progreso, evaluaciones, certificados, preguntas y comunidad por versión están implementados. La entrega de perfiles integra Personas, presentación voluntaria, búsqueda y seguimiento de conversaciones; las membresías siguen pendientes. La documentación de diseño no acredita funciones entregadas.

La comunidad también se integra al final de cada lección con comentarios, respuestas del creador, seguimiento y avisos internos, respetando inscripción y acceso al contenido. [Decisión y alcance](investigacion-y-requisitos.md#20-comunidad-en-lecciones) y [entrega técnica](../src/docs/operacion-y-bitacora.md#comunidad-en-lecciones-2026-10-12). La validación con usuarios permanece pendiente.

La experiencia de cursos, lectura y continuidad fue ampliada el 12 de octubre: temario con estados, continuación compartida, prácticas con solución desplegable, lectura enfocada y biblioteca con filtros. [Entrega, fuentes, evidencias y alcance de las pruebas](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12). La revisión técnica no equivale a validación educativa o comercial.
