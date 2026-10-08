# BTC.EDU

## Introducción

BTC.EDU nace de una pregunta: ¿cómo podemos permitir que una persona compre el contenido educativo que necesita sin obligarla a adquirir un curso completo o mantener una suscripción?

Nuestra propuesta combina contenido gratuito con cursos, capítulos, videos y materiales de pago. El alumno puede explorar, revisar una muestra y conocer qué incluye una oferta antes de comprar. Después del pago, conserva el acceso a la versión adquirida.

El proyecto aborda la experiencia del alumno y el trabajo del creador. Necesitamos resolver cómo se prepara y publica el contenido, cómo se presenta su precio y cómo se mantienen los derechos de acceso cuando cambia.

Este documento explica el origen de la idea, las decisiones que la consolidaron, la investigación y el desarrollo alcanzado. Se actualizará con nuevas entregas y evidencias. Las hipótesis comerciales se distinguen de los resultados técnicos.

## La idea

La idea inicial fue permitir la compra de recursos digitales individuales mediante micropagos. Elegimos aplicarla a educación porque una explicación, un ejercicio, un video práctico o una guía pueden tener utilidad propia.

Una persona que estudia programación puede necesitar resolver una duda puntual. Un capítulo o un material específico podría responder a esa necesidad sin adquirir un conjunto mayor. Los cursos completos conservan su lugar para quien busca un recorrido amplio.

Para los creadores, la propuesta permite organizar y ofrecer distintas unidades de contenido. Su viabilidad depende de comprobar qué materiales sirven por separado y qué esfuerzo requieren para mantenerlos.

La investigación documenta que otras plataformas permiten compras individuales y membresías. Nuestra propuesta deberá demostrar utilidad a través de contenido pertinente, ofertas comprensibles y continuidad del acceso. No afirmamos que la compra individual sea una modalidad inexistente en el mercado.

## El problema

Investigamos situaciones en las que la necesidad del alumno y la unidad de venta no coinciden. Puede buscar una explicación concreta mientras la oferta disponible exige una suscripción o un curso completo.

También puede tener dudas sobre lo que recibirá. Una muestra insuficiente, una descripción ambigua o un material adicional no identificado dificultan la decisión.

Desde el lado del creador, vender recursos individuales implica decidir qué tiene valor por separado, cómo presentarlo y cuánto cuesta publicarlo y actualizarlo. Debe conservarse la relación con quien ya compró.

Estas dificultades son hipótesis de trabajo. Falta comprobar con usuarios su frecuencia, importancia y relación con las alternativas que utilizan actualmente.

## Cómo consolidamos la idea

Pasamos de un mecanismo de desbloqueo a una plataforma educativa con recorridos para alumnos, creadores y administración.

Definimos cursos gratuitos, cursos mixtos, cursos de pago y ofertas individuales. Separamos la organización educativa de las condiciones comerciales: que un material aparezca en un curso no significa que esté incluido en su compra.

Decidimos conservar las compras por versión. Esta regla requiere publicaciones que mantengan su composición: actualizar un curso no debe sustituir silenciosamente lo adquirido ni borrar el progreso anterior.

Incorporamos revisión editorial. El creador prepara y envía contenido; la administración publica la composición revisada o devuelve observaciones. Las cuentas de estudiantes y creadores son independientes, con permisos y actividad propios.

Estas decisiones dieron forma al producto. Las reglas implementadas se verifican técnicamente; su conveniencia para usuarios debe evaluarse con personas.

## Investigación

### Qué revisamos

Revisamos documentación oficial de Udemy, Teachable, Thinkific y Patreon para organización, publicación, progreso y funciones educativas. Ampliamos la investigación a Coursera, Codecademy, Google AdSense, Cloudflare Stream y Lightning Labs para comparar acceso, muestras y costos.

También consultamos guías de entrevistas y usabilidad de GOV.UK y Nielsen Norman Group, métodos de precios de Qualtrics y un estudio académico sobre disposición a pagar.

Estas fuentes documentan prácticas y condiciones externas. No sustituyen entrevistas, pruebas de BTC.EDU o resultados de mercado.

### Modelos de monetización

La suscripción concede acceso durante un periodo pagado. Su conveniencia depende de que el alumno utilice suficientes recursos y encuentre valor continuo. Debemos explicar qué incluye y cuándo termina el acceso.

La publicidad permite financiar parte del contenido mediante anuncios. Requiere evaluar el rendimiento publicitario y su efecto sobre la experiencia de aprendizaje.

Freemium combina contenido gratuito y ampliaciones pagadas. Permite explorar antes de comprar, pero exige explicar la frontera de acceso y cubrir también el consumo gratuito.

Los micropagos permiten comprar una unidad concreta por un importe pequeño. Su conveniencia depende de la necesidad del usuario y de que procesamiento, decisión de compra y soporte no consuman el valor de la operación.

Esta comparación es nuestra interpretación. Los modelos pueden combinarse: freemium describe acceso gratuito/pagado y micropagos describe la unidad e importe de compra.

Patreon admite compras únicas y membresías; Codecademy ofrece acceso gratuito y planes pagados. Son referencias de coexistencia, sin demostrar preferencia por nuestra oferta. [Patreon](https://www.patreon.com/policy/legal), [Codecademy](https://www.codecademy.com/pricing).

La hipótesis principal sigue siendo contenido gratuito y muestras junto con compras individuales. La membresía se evaluará para un uso frecuente. No proponemos incorporar publicidad por esta comparación.

### Costos

Separamos el precio al alumno del costo de la plataforma para el creador. Teachable publica Starter a USD 39 mensuales y Builder a USD 89 con facturación mensual; Thinkific publica Basic a USD 54 y Start a USD 109. Son referencias externas que deben revisarse antes de una contratación, no precios sugeridos para BTC.EDU. [Teachable](https://www.teachable.com/pricing), [Thinkific](https://www.thinkific.com/pricing/).

El componente fijo de procesamiento puede pesar sobre compras pequeñas. Con las tarifas publicadas del plan estándar de Patreon para tarjeta y liquidación en USD, calculamos cargos de USD 0.429 sobre USD 1 y USD 0.945 sobre USD 5, antes de impuestos y otros cargos. Es una ilustración externa, no nuestro costo. [Tarifas de Patreon](https://support.patreon.com/hc/en-us/articles/11111747095181-Creator-fees-overview).

Lightning contempla comisiones y liquidez. La integración elegida necesitará su propia evaluación; la simulación actual no acredita costos de fondos reales. [Lightning Labs](https://docs.lightning.engineering/the-lightning-network/pathfinding/channel-fees).

También debemos estimar consumo después de comprar. Cloudflare Stream ofrece una referencia de almacenamiento por minutos y entrega por reproducciones. Con sus tarifas, mil minutos almacenados y seis mil entregados al mes sumarían USD 11 por esos conceptos. No incluye toda la operación ni implica elegir ese servicio. [Cloudflare Stream](https://developers.cloudflare.com/stream/pricing/).

El acceso permanente exige presupuestar entrega futura y conservación de versiones. La estimación completa de sostenibilidad sigue pendiente.

### Muestras

Coursera documenta muestra gratuita del primer módulo de la mayoría de sus cursos. Esta referencia muestra una forma de explorar antes de pagar; no fija la muestra adecuada para nuestro contenido. [Coursera](https://blog.coursera.org/introducing-courseras-new-course-preview-experience/).

Proponemos una lección útil con temario para cursos, una actividad representativa para capítulos, un fragmento para videos y un extracto con formato e inclusiones para materiales.

Las muestras se mantendrán separadas del contenido protegido. Probaremos si permiten explicar qué se recibe, qué queda fuera y para qué sirve. No fijaremos una duración o porcentaje universal sin evidencia.

### Entrevistas

Las entrevistas partirán de experiencias recientes antes de presentar BTC.EDU. Se preguntará qué necesitaba la persona, qué recursos utilizó, cómo eligió, si pagó, cómo recuperó el material y qué dificultades encontró. Con creadores, exploraremos preparación, precio, derechos, mantenimiento, actualización y atención.

Proponemos una ronda inicial de seis a diez alumnos y tres a cinco creadores. Incluiremos compradores y usuarios de alternativas gratuitas, con distinta experiencia en dispositivos y pagos, priorizando el público relacionado con El Salvador. Es una muestra exploratoria, no una representación del mercado.

Los guiones se pilotarán y la participación contará con consentimiento. Evitaremos preguntas que sugieran respuestas y contrastaremos declaraciones con tareas observadas, porque recuerdos e intenciones pueden diferir del comportamiento. [GOV.UK: entrevistas](https://www.gov.uk/service-manual/user-research/using-in-depth-interviews), [NN/G](https://www.nngroup.com/articles/why-user-interviews-fail/).

No se han realizado estas sesiones ni existen resultados externos registrados.

### Usabilidad

Las pruebas observarán encontrar un recurso, explicar la oferta, comprar individualmente, resolver un vencimiento y recuperar acceso en otra sesión. Se incluirá la regla de compra parcial para comprobar su comprensión.

Con creadores observaremos preparar una lección, organizar un curso, configurar una oferta, resolver revisión y actualizar contenido. Cada sesión utilizará tareas pertinentes a módulos disponibles o a un prototipo claramente identificado.

Registraremos finalización sin ayuda, con ayuda o no completada, además de tiempo, dudas y errores. No revelaremos el camino al plantear tareas. Usaremos cuentas temporales y pagos simulados. [GOV.UK: usabilidad](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing).

Las sesiones con usuarios y los pilotos internos tendrán registros separados. Una compra simulada permite observar comprensión, sin demostrar voluntad de gastar dinero real.

### Precios

Los precios actuales son ficticios. La evaluación comenzará con experiencias de gasto y una oferta definida, manteniendo el mismo contenido al comparar.

Van Westendorp ayuda a explorar rangos percibidos y Gabor-Granger aceptación de precios definidos. Sus respuestas siguen siendo declaraciones. Con pocas entrevistas no calcularemos un precio óptimo ni una demanda representativa. [Qualtrics](https://www.qualtrics.com/en-au/articles/strategy-research/pricing-survey-questions/).

Un metaanálisis documenta diferencias entre disposición declarada y real. Contrastaremos percepción con costos y alternativas, permitiendo elegir ninguna compra. También observaremos comprensión de sats y, si hace falta, probaremos una equivalencia informativa. [Schmidt y Bijmolt](https://link.springer.com/article/10.1007/s11747-019-00666-6).

### Cómo registraremos los resultados

Separaremos observaciones, interpretaciones y decisiones. Cada sesión conservará identificador, fecha, versión, tarea, resultado, evidencia y cambio propuesto, respetando consentimiento y privacidad. [GOV.UK: análisis](https://www.gov.uk/service-manual/user-research/analyse-a-research-session).

Los informes mostrarán cantidades reales y casos contrarios a nuestras hipótesis. Los cambios relevantes se comprobarán de nuevo. No extrapolaremos una pequeña muestra al mercado.

## Objetivos

### Objetivo general

Desarrollar y evaluar una plataforma educativa que permita adquirir contenidos específicos mediante pagos simulados, con condiciones claras y acceso persistente.

### Objetivos específicos

Investigar las necesidades de alumnos y creadores relacionadas con recursos individuales y comparar modelos de monetización para justificar una propuesta de precios y muestras.

Diseñar un recorrido comprensible desde el descubrimiento hasta el acceso, protegiendo los recursos de pago en el servidor y conservando las compras y el aprendizaje de la versión correspondiente.

Facilitar la preparación y revisión del contenido, medir la compra y el uso mediante indicadores definidos y evaluar los recursos y costos necesarios para mantener la plataforma.

## Enfoque

### Producto

Nos enfocamos inicialmente en aprendizaje de tecnología/programación. El contenido gratuito, las muestras y las unidades de compra deben responder a necesidades educativas reconocibles. La investigación orientará qué combinación conservar y qué cambiar.

### Experiencia

Trabajamos el recorrido completo: explorar, revisar, elegir, entrar en la cuenta, pagar y recuperar contenido. Los estados fallidos y vencidos, las inclusiones y el acceso histórico forman parte de la comprensión que evaluaremos.

### Desarrollo

Construimos por entregas que cierren recorridos. Definimos reglas, permisos, errores y cambios de versión antes de programar cada módulo. Una referencia externa o una propuesta de investigación no introduce automáticamente nuevas funciones.

### Validación

Distinguimos propuesta, implementación y verificación técnica de la validación con personas. Los métodos ya están preparados; la ejecución externa sigue pendiente. Una declaración favorable o un pago ficticio no se registra como demanda o ingreso.

### Medición

El marco de analítica contempla conversión a solicitud, finalización de pago, apertura después de comprar, regreso a biblioteca y compras repetidas.

La conversión a solicitud se calcula dividiendo los pares de sesión y oferta con una factura creada entre los pares con una oferta vista, considerando ofertas de pago dentro del periodo.

La finalización del pago compara las facturas pagadas con las creadas en el periodo, indicando cuántas permanecen pendientes.

La apertura posterior compara los permisos adquiridos que registraron una apertura después de la compra con el total de permisos adquiridos en el periodo.

El regreso a biblioteca compara los compradores que vuelven en una sesión posterior con los compradores del periodo. La compra repetida compara los compradores del periodo que tienen dos o más facturas pagadas al cierre con el total de compradores de ese periodo.

Cada indicador necesita fuente, intervalo y denominador; si este es cero se mostrará que no hay datos. Una compra de conjunto puede conceder varios permisos, pero es una sola transacción. La cobertura de eventos y paneles deberá auditarse antes de informar resultados. Apertura, reproducción y finalización declarada no demuestran aprendizaje.

### Operación

El creador mantiene materiales propios; la administración revisa publicaciones y atiende incidencias. Business investiga necesidades y condiciones comerciales; Dev construye y verifica el sistema. La estimación deberá asignar responsables y recursos para revisión editorial, almacenamiento, respaldo/restauración, correo, conciliación y soporte. Las tarifas externas orientan escenarios, sin constituir un presupuesto completo ni ingresos previstos.

## Desarrollo

### Estado actual

Los registros al 4 de octubre describen cuentas independientes, aprobación de creadores, estudio y revisión, contenido versionado, archivos protegidos, ofertas, facturas, compras, biblioteca, inscripción y progreso.

Las cuentas tienen registro, acceso, perfiles y recuperación independientes. La entrega de correo para operación pública sigue pendiente de preparación y verificación.

El contenido se organiza en cursos, tutoriales y recursos con archivos protegidos. El catálogo editorial definitivo requiere producción y comprobación de derechos de uso.

Los creadores cuentan con aprobación, editor, vista previa y revisión. El acompañamiento y las métricas completas siguen pendientes.

El comercio dispone de compras simuladas y derechos históricos. Faltan conciliación periódica supervisada y analítica completa.

El aprendizaje dispone de biblioteca, inscripción y progreso por versión. Desde la entrega de evaluaciones, una lección puede exigir aprobación antes de marcarse como completada. Los certificados siguen pendientes.

Preguntas, avisos, comunidad y membresías tienen diseño definido, pero necesitan implementación y validación. Las membresías propuestas tendrán acceso temporal y renovación manual.

### Evaluaciones

El creador puede preparar preguntas de selección única y múltiple, configurar la nota mínima, el límite de intentos, la espera y cuándo se muestran las soluciones. Las preguntas y reglas se conservan en la composición enviada a revisión. Editar el borrador después no cambia esa copia ni los intentos de las versiones anteriores.

El alumno necesita inscripción y acceso a la lección. Antes de empezar ve las reglas; puede guardar respuestas, retomar el intento y entregarlo cuando ha respondido todas las preguntas. Iniciar consume un intento. El servidor corrige con preguntas de igual peso y exige coincidencia exacta en selección múltiple, sin crédito parcial. La aprobación usa la puntuación exacta; el redondeo solo afecta la nota mostrada.

Una evaluación obligatoria requiere aprobación para completar la lección. El creador puede autorizar otro intento con motivo cuando se agotan los disponibles. Esta autorización conserva resultados y espera, sin borrar notas anteriores. Una aprobación previa tampoco se pierde por una nota posterior menor.

La entrega aprobó 148 pruebas técnicas y comprobaciones de concurrencia. Se verificaron guardado, recuperación, fallo, aprobación, edición y conservación de versiones en navegador, con el cliente de Django. Las pantallas comprobadas funcionaron en tamaños de escritorio y móvil; la conexión HTTP directa al servidor local no pudo verificarse en este entorno. La migración conservó las filas originales y mantuvo los ejemplos fuera de la base principal. Esta evidencia comprueba funcionamiento, sin demostrar aprendizaje ni sustituir sesiones con usuarios.
### Publicación y acceso

El envío editorial conserva una composición revisable. Aprobar publica esa composición; las ediciones posteriores preparan otra versión.

Las facturas conservan precio e inclusiones. El servidor confirma condiciones y concede acceso sin duplicar compras. Los derechos permanecen asociados a la cuenta y la versión adquirida.

LNbits FakeWallet proporciona el entorno simulado. No se utilizan fondos reales ni se acreditan ingresos.

### Base técnica y pruebas

La aplicación utiliza Django, plantillas HTML y HTMX; SQLite sostiene la etapa local. El servidor controla contenido, cuentas, compras y aprendizaje, y conserva las claves del proveedor.

Los registros informan 129 pruebas aprobadas, concurrencia SQLite e integración FakeWallet, además de recorridos de escritorio/móvil. Son evidencias fechadas de la entrega registrada, no pruebas reejecutadas por la actualización documental.

### Organización del trabajo

BTC.EDU continúa como proyecto individual. Caleb asume la investigación, las decisiones de producto, el desarrollo y la documentación. La planificación debe ajustarse a su disponibilidad, que todavía no está cuantificada. Priorizaremos cerrar el recorrido central y sus evidencias antes de comprometer fechas para los módulos adicionales.

La matriz inicial de trazabilidad relaciona los requisitos del reto y los criterios de producto con registros técnicos y tareas pendientes. Esta revisión documental no acredita nuevas funciones ni una ejecución nueva de las pruebas. Sigue pendiente comprobar la cobertura de cada criterio, completar la analítica administrativa y verificar los recorridos de la versión que demostraremos.

El original de evaluación exige cuatro integrantes. La continuidad individual requiere aclarar con CUBO+ cómo se aplicará esa condición; no contamos con una excepción confirmada.
### Actualizaciones

Cada entrega revisará comportamiento, decisiones, pruebas, límites y próximos pasos. El estado actual se mantendrá separado de la bitácora para conservar evolución sin contradicciones.

La investigación documental incorporó métodos y referencias comerciales. La entrega de evaluaciones amplía el aprendizaje y conserva las condiciones comerciales y los pagos simulados existentes.

## A dónde queremos llegar

Queremos una experiencia en la que el alumno encuentre contenido pertinente, comprenda la compra y pueda continuar aprendiendo. El creador debe preparar, publicar y mantener sus materiales sin perjudicar el acceso existente.

Las evaluaciones ya permiten comprobar respuestas y conservar resultados por versión. El siguiente bloque será definir y construir certificados de finalización sobre requisitos históricos. Preguntas, comunidad, notificaciones y membresías renovadas manualmente se desarrollarán y verificarán por entregas.

Necesitamos analítica que explique consulta, pago, uso y regreso sin confundir actividad con aprendizaje. También un presupuesto que considere consumo gratuito, acceso permanente, archivos históricos, correo, respaldos, supervisión y soporte.

La operación pública y una integración con fondos reales requerirán decisiones y evidencias propias. La investigación externa ayuda a identificar condiciones; no acredita que ya estén resueltas.

## Qué demostramos

La evidencia técnica registrada muestra una oferta que genera una factura simulada y una confirmación válida que concede acceso específico. Documenta persistencia, protección y conservación de referencias históricas.

La revisión permite publicar una composición aprobada mientras se preparan cambios posteriores. Las evaluaciones verifican respuestas en el servidor y conservan reglas e intentos de cada versión; estos resultados técnicos no prueban dominio educativo.

La investigación documenta alternativas de monetización y condiciones externas de costos. Todavía no demuestra preferencia por BTC.EDU, disposición real a pagar, frecuencia de compra o mejora educativa.

## Logros

Definimos unidades de compra, muestras, permisos y responsabilidades de publicación. Conectamos creación, revisión, oferta, compra simulada y aprendizaje, conservando versiones históricas. Incorporamos evaluaciones con resultados persistentes y control de intentos, sin alterar las compras existentes.

Ampliamos la comparación de modelos y costos, y preparamos instrumentos para entrevistas, usabilidad y precios. Es un avance de investigación documental y preparación, no una validación externa terminada.

Los resultados de mercado y aprendizaje se incorporarán cuando exista evidencia suficiente.

## Próximos pasos

Preparar reclutamiento y consentimiento; ejecutar entrevistas y tareas con la versión identificada; analizar dificultades y objeciones; comprobar los cambios relevantes.

Contrastar rangos de precio con costos y preparar escenarios de sostenibilidad. Completar la cobertura de analítica y las especificaciones de módulos pendientes.

Actualizar el documento con cada entrega, vinculando decisiones y resultados a sus evidencias reales.

## Conclusiones

BTC.EDU propone adaptar la compra de contenido a necesidades educativas concretas. El desarrollo registrado permite verificar publicación, pago simulado y acceso persistente.

La investigación muestra alternativas comparables y costos que debemos considerar. La siguiente etapa deberá contrastar la utilidad y comprensión con alumnos y creadores, y evaluar la sostenibilidad de los precios.

Mantendremos las conclusiones comerciales como provisionales hasta reunir esa evidencia.

## Referencias

Las fuentes externas se enlazan junto a las afirmaciones que sustentan. Los precios y condiciones comerciales se consultaron el 5 de octubre de 2026; deben revisarse antes de contratar o publicar una recomendación final.

Los documentos originales de CUBO+ definen el reto y la evaluación. La investigación funcional, las decisiones y los registros técnicos del proyecto conservan el detalle y los límites de cada entrega.

La bitácora y los anexos reunirán las evidencias de desarrollo, instrumentos y resultados reales. El enlace al Google Doc y la validación con participantes siguen pendientes de incorporar.
