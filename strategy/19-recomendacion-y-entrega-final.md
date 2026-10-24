# BTC.EDU

## Introducción

BTC.EDU nace de una pregunta: ¿cómo podemos permitir que una persona compre el contenido educativo que necesita sin obligarla a adquirir un curso completo o mantener una suscripción?

BTC.EDU es una plataforma de aprendizaje práctico en distintas áreas, donde una persona puede adquirir una unidad útil para su necesidad y continuar hacia un recorrido más amplio. Combina contenido gratuito con cursos, capítulos, videos y materiales de pago. El alumno puede explorar, revisar una muestra y conocer qué incluye una oferta antes de comprar. Después del pago, conserva el acceso a la versión adquirida.

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

## Propuesta y diferencias

### A quién queremos servir

El enfoque confirmado es educación de distintas áreas desde el inicio. El catálogo local reúne Bitcoin, Tecnología y Creación: a la primera colección de Bitcoin y Lightning añadimos recorridos de fotografía, video, desarrollo web y Python. El público inicial por investigar son estudiantes, personas que trabajan y autodidactas que necesitan aplicar un conocimiento concreto: resolver un ejercicio, preparar un archivo, utilizar una herramienta o completar una tarea. El Salvador es el contexto inicial de investigación, sin atribuir a su población una preferencia por Bitcoin o una disposición a pagar que no hemos medido.

Para el creador, buscamos facilitar la publicación de conocimientos que tengan utilidad por separado, conservando su relación con cursos, prácticas y alumnos. Su beneficio dependerá del esfuerzo editorial, la remuneración y la atención requerida. Todavía no hemos documentado actividad de creadores externos ni condiciones de liquidación comprobadas.

### Qué ofrecemos

La propuesta es aprender algo aplicable, elegir qué adquirir y recuperar lo comprado cuando se necesite. Cada unidad de pago debería declarar resultado esperado, requisitos, muestra, inclusiones y una práctica que permita comprobar su utilidad. La extensión la determina la tarea educativa: dividir un curso en fragmentos breves no garantiza que cada fragmento tenga valor independiente.

El alumno puede empezar por una necesidad puntual y encontrar después un curso relacionado. Al completar un capítulo o curso del que ya compró partes, paga solo la diferencia: lo pagado por esas partes se reconoce como crédito y el paquete incluye únicamente lo que falta. La política de crédito está implementada como propuesta provisional; su comprensión y conveniencia deben probarse con participantes.

### Qué debemos demostrar frente a otras opciones

La comparación documental del 13 de octubre de 2026 permite delimitar nuestra oportunidad; no demuestra superioridad ni constituye una revisión exhaustiva del mercado.

| Alternativa | Oferta documentada | Diferencia que BTC.EDU debe demostrar |
|---|---|---|
| Udemy | Compra de cursos y acceso duradero sujeto a sus condiciones | Utilidad de unidades menores que un curso y una transición comprensible hacia el conjunto |
| Domestika | Cursos con proyectos, recursos y comunidad; compra individual y Plus | Resultados útiles por unidad en distintas áreas, con calidad suficiente para justificar la elección |
| Coursera Plus | Suscripción a un conjunto de cursos y programas | Conveniencia para una necesidad puntual, sin exigir consumo frecuente ni prometer acreditación equivalente |
| Gumroad y Patreon | Venta de productos y contenidos individuales, además de membresías | Integración entre compra, práctica, progreso y acompañamiento educativo |
| Teachable y Thinkific | Herramientas para vender cursos, recursos y otros productos educativos | Valor de un catálogo compartido entre creadores y de una política consistente de unidades, revisión y acceso |

Fuentes: [Udemy](https://support.udemy.com/hc/en-us/articles/229603708-Lifetime-access), [Domestika](https://support.domestika.org/hc/en-us/articles/360003052778-About-Domestika-s-courses), [Coursera Plus](https://www.coursera.org/courseraplus/), [Gumroad](https://gumroad.com/features), [Patreon](https://support.patreon.com/hc/en-us/articles/204606215-Can-I-make-a-one-time-payment), [Teachable](https://www.teachable.com/digital-downloads), [Thinkific](https://support.thinkific.com/hc/en-us/articles/9942695724695-An-Introduction-to-Selling-Thinkific-Learning-Products).

También debemos comparar cada recurso con alternativas gratuitas que el participante ya utiliza. En nuestra primera colección, PlebDevs ofrece contenido gratuito sobre desarrollo y Mi Primer Bitcoin publica recursos educativos abiertos. Son alternativas y posibles referencias de contenido, sin alianzas establecidas. [PlebDevs](https://www.plebdevs.com/), [Mi Primer Bitcoin](https://github.com/MyFirstBitcoin).

Las compras individuales, las muestras, el acceso duradero, la comunidad y los certificados ya existen en otras plataformas. Nuestra combinación propuesta es unidades con resultado propio, práctica, adquisición flexible en sats y continuidad del acceso por versión. Las reglas de acceso están implementadas; la calidad educativa, la comodidad del pago y la preferencia por esa combinación todavía deben comprobarse.

La ventaja a construir dependerá de materiales útiles, revisión por especialistas, creadores que puedan mantenerlos y evidencia de resultados. El diseño visual y la integración técnica ayudan a entregar esa experiencia, pero no acreditan por sí solos una ventaja competitiva sostenible.

### Cómo desarrollar el potencial

Comenzamos con colecciones pequeñas en varias áreas y un mismo criterio de calidad. Creación y Tecnología ya tienen cursos originales publicados localmente; su demanda y sus resultados educativos siguen por evaluar. Cada área necesita revisión independiente, mantenimiento y prácticas comprobadas con participantes antes de ampliar su oferta.

El descubrimiento debería ayudar a encontrar una tarea y su nivel, además de un tema. Por ejemplo, «organizar datos en una hoja de cálculo» expresa una necesidad concreta. Las rutas de varios cursos ya ordenan recorridos hacia un objetivo, como «De cero a Lightning», con progreso conjunto y una credencial propia. La búsqueda orientada a resultados sigue requiriendo diseño propio.

La primera captación puede probarse con creadores que ya tengan materiales y una audiencia, junto con comunidades educativas. Esto permitiría evaluar una colección concreta sin depender de un catálogo masivo. No hemos contactado aliados ni estimado el costo de adquisición.

La sostenibilidad debe relacionar ingreso, remuneración del creador, pagos, revisión, entrega futura y soporte. Evaluar una comisión sobre ventas es una hipótesis de modelo; el MVP no calcula comisiones ni liquidaciones. Los precios de prueba no justifican anunciar que la plataforma será más barata o rentable.

El nombre BTC.EDU puede sugerir una academia dedicada únicamente a Bitcoin. Recomendamos acompañarlo con una descripción clara del aprendizaje en distintas áreas y probar su comprensión. Bitcoin mantiene su lugar en el mecanismo de compra y en el valor del proyecto para el ecosistema de El Salvador; usarlo para adquirir otro conocimiento podría ampliar su aplicación, algo todavía por validar.

### Por dónde empezar

Proponemos un primer ciclo con tres unidades piloto en áreas distintas: una del catálogo actual y dos nuevas candidatas por seleccionar con participantes y especialistas. Cada ficha debe explicar necesidad, público, resultado, requisitos, muestra, inclusiones, práctica, precio y alcance de atención. Revisaremos primero la promesa y el contenido; después ensayaremos compra y recuperación y observaremos el resultado de la práctica. [Entregas y condiciones para avanzar](investigacion-y-requisitos.md#primer-ciclo-de-enfoque).

La revisión del catálogo identifica diagramas, matrices de acceso y guiones de prueba como resultados posibles. Debemos distinguir comprensión, diseño y ejecución: preparar un plan de laboratorio no demuestra haberlo ejecutado. La ampliación del producto se priorizará por dificultades observadas, mientras la ampliación temática exigirá contenido revisado y responsables de mantenimiento.

Las fichas educativas conservan resultado, requisitos, muestra y acompañamiento por revisión. Las prácticas ya permiten registrar soluciones privadas y recibir retroalimentación por criterios; su uso con participantes sigue pendiente. El reconocimiento de compras previas al completar un conjunto ya funciona; el descubrimiento por tarea sigue pendiente. [Alcance y comprobaciones](investigacion-y-requisitos.md#desarrollo-del-enfoque).

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

La plataforma se orienta a educación de distintas áreas desde el inicio, unidas por aprendizaje práctico y compras por unidades útiles. El catálogo local reúne diez cursos y 72 lecciones en Bitcoin, Tecnología y Creación. Bitcoin y Lightning cubre fundamentos, wallets y autocustodia, facturas, laboratorio con LNbits y acceso a contenido mediante micropagos; Creación y Tecnología añaden cuatro cursos de pago (fotografía, edición de video, desarrollo web y Python). Ampliar a otras áreas requiere contenidos y revisión propios; el contenido gratuito, las muestras y las unidades de compra deben responder a necesidades educativas reconocibles.

### Experiencia

Trabajamos el recorrido completo: explorar, revisar, elegir, entrar en la cuenta, pagar y recuperar contenido. Los estados fallidos y vencidos, las inclusiones y el acceso histórico forman parte de la comprensión que evaluaremos.

La revisión de interfaz identificó menús cambiantes, acciones dispersas y dependencias poco visibles. La actualización implementa menús estables para estudiantes y educadores, acciones principales claras y continuidad entre elección, acceso, aprendizaje y publicación. Conserva la identidad industrial, la marca, los colores y los modos claro y oscuro, con una tipografía funcional más legible. El [diagnóstico y cobertura](investigacion-y-requisitos.md#revision-ui-ux) separa los 16 hallazgos iniciales, las correcciones implementadas y la comprensión que todavía debemos comprobar con personas.

La etapa comercial permite reunir cursos, tutoriales y recursos en un carrito, revisar el total y completar un pedido con un pago, conservando Comprar ahora para una unidad. Detecta contenido duplicado, conserva la selección al entrar y recupera la misma factura cuando el resultado del pago es desconocido. El [recorrido comercial](investigacion-y-requisitos.md#experiencia-comercial) integra Guardados, autor enlazado, escaparates, ayuda desde el pedido/recurso y continuidad hacia Mi aprendizaje. Las facturas anteriores mantienen su oferta y las nuevas corresponden a un pedido con líneas conservadas.

Las imágenes de contenido comparten proporciones: 16:9 para portadas de catálogo, ficha, comparación y biblioteca; 1:1 para miniaturas de continuación, estudio y carrito. Se conserva la imagen completa sin deformarla ni recortarla, dejando espacio alrededor cuando su formato es distinto. Las ilustraciones actuales están integradas en la aplicación; la carga de portadas personalizadas sigue pendiente. El [criterio de imágenes](investigacion-y-requisitos.md#imagenes-de-contenido) establece las dimensiones de referencia.

### Desarrollo

Construimos por entregas que cierren recorridos. Definimos reglas, permisos, errores y cambios de versión antes de programar cada módulo. Una referencia externa o una propuesta de investigación no introduce automáticamente nuevas funciones.

### Validación

Distinguimos propuesta, implementación y verificación técnica de la validación con personas. Los métodos ya están preparados; la ejecución externa sigue pendiente. Una declaración favorable o un pago ficticio no se registra como demanda o ingreso.

### Medición

El marco de analítica contempla conversión a solicitud, finalización de pago, apertura después de comprar, regreso a biblioteca y compras repetidas.

La conversión a solicitud se calcula dividiendo los pares de sesión y oferta con una factura creada entre los pares con una oferta vista, considerando ofertas de pago dentro del periodo.

La finalización del pago compara las facturas pagadas con las creadas en el periodo, indicando cuántas permanecen pendientes.

La apertura posterior compara los permisos adquiridos que registraron una apertura después de la compra con el total de permisos adquiridos en el periodo.

El regreso a biblioteca compara los compradores que vuelven después de confirmar la compra, en una sesión distinta, con los compradores del periodo cuya sesión de compra está registrada; los no observables se informan aparte. La compra repetida compara los compradores del periodo que tienen dos o más facturas pagadas al cierre con el total de compradores de ese periodo.

Cada indicador necesita fuente, intervalo y denominador; si este es cero se mostrará que no hay datos. Una compra de conjunto puede conceder varios permisos, pero es una sola transacción. Los paneles esenciales y sus consultas están implementados y probados. La cobertura comienza con los eventos registrados, sin reconstruir visitas anteriores ni medir reproducción o muestras por separado. Apertura, reproducción y finalización declarada no demuestran aprendizaje.

### Operación

El creador mantiene materiales propios; la administración revisa publicaciones y atiende incidencias. Business investiga necesidades y condiciones comerciales; Dev construye y verifica el sistema. La estimación deberá asignar responsables y recursos para revisión editorial, almacenamiento, respaldo/restauración, correo, conciliación y soporte. Las tarifas externas orientan escenarios, sin constituir un presupuesto completo ni ingresos previstos.

## Desarrollo

### Fichas educativas

El creador prepara resultado, requisitos, tipo de actividad, muestra pública y acompañamiento para cada lección, video o material. Puede guardar un borrador incompleto; para enviarlo a revisión debe completar la ficha. La publicación conserva esos datos junto con el contenido adquirido. El alumno puede consultarlos en el lector, la ficha del recurso y lo incluido en la oferta, sin recibir el texto protegido. Las versiones anteriores siguen disponibles; sus fichas se completarán en nuevas revisiones.

Se comprobó el recorrido de edición y envío y la muestra en escritorio y móvil con datos temporales. La revisión educativa independiente sigue pendiente; la ampliación de áreas se concreta en los cursos descritos a continuación.

### Catálogo inicial

Publicamos seis cursos introductorios de Bitcoin y Lightning con 24 lecciones de texto. Cada lección incluye explicación, ejemplo, práctica y solución. Los cursos presentan objetivos, requisitos, temario y duración estimada para realizar las actividades; todavía no hemos medido esos tiempos con alumnos.

Bitcoin desde cero, Wallets y autocustodia y Lightning desde cero son gratuitos. Facturas Lightning, Laboratorio con LNbits y Contenido con micropagos ofrecen la primera lección gratis y tres lecciones de pago. El precio inicial es 120 sats por curso o 50 sats por lección individual, como valores de prueba sin validación comercial.

Cada curso incluye una pregunta final y un certificado condicionado a completar las cuatro lecciones y aprobar esa comprobación. Es una comprobación introductoria limitada, no una evaluación exhaustiva ni evidencia de dominio. Las prácticas usan cálculos, escenarios y diseños que no exigen fondos reales. Los textos son material introductorio propio de BTC.EDU con referencias técnicas; no incorporan videos ni sesiones realizadas con usuarios.

La carga conserva versiones publicadas, registra decisiones de publicación y ofertas, crea un respaldo local y evita duplicar cursos al repetirse. Comprobamos el catálogo, sus fichas y las 24 lecciones por HTTP en una copia de la base, incluida la protección del texto de pago. La revisión educativa externa y la comprobación del nuevo catálogo con personas siguen pendientes.

### Creación y Tecnología

El 15 de octubre de 2026 incorporamos cuatro cursos originales completos de autoestudio. Cada uno tiene cuatro capítulos, doce lecciones desarrolladas, ejercicios con solución, cuatro evaluaciones de cuatro preguntas y un proyecto final con criterios. Las duraciones incluyen práctica y son estimadas.

| Categoría | Curso | Duración estimada | Curso completo |
|---|---|---|---|
| Creación | Fotografía con celular: de la captura a una serie visual | 6 horas | 1800 sats |
| Creación | Edición de video con Shotcut: del guion a la publicación | 8 horas | 2400 sats |
| Tecnología | Desarrollo web: crea y publica un sitio accesible | 10 horas | 3000 sats |
| Tecnología | Python práctico: automatiza reportes con CSV | 10 horas | 3000 sats |

Todas sus lecciones requieren compra. Antes de pagar se muestran objetivos, requisitos, temario y una muestra breve; el desarrollo, las soluciones y los complementos de la lección permanecen protegidos. Ofrecemos lecciones, capítulos y curso completo con su inventario preciso. Los importes son decisiones editoriales iniciales, sin validación comercial.

Los textos y proyectos son originales de BTC.EDU, apoyados en documentación primaria de Apple, Google, Shotcut, MDN, W3C, GitHub, Python y Microsoft Learn. Incorporamos portadas fotográficas con licencia Unsplash y créditos, y videos externos atribuidos como complemento. La compra corresponde al recorrido original; los videos conservan su acceso y condiciones en la plataforma de origen. No revendemos cursos de terceros ni dependemos de sus videos para completar las explicaciones. [Fuentes y derechos](investigacion-y-requisitos.md#cursos-completos-creacion-tecnologia).

El certificado de finalización exige completar doce lecciones y aprobar las cuatro evaluaciones con al menos 75 %. El proyecto incluye instrucciones y rúbrica para autoevaluación; no incluye tutoría ni corrección personal y su recepción está cerrada hasta asignar atención. Su revisión no condiciona el certificado. El catálogo local suma diez cursos y 72 lecciones. El entorno de pagos conserva su configuración local; publicar contenido completo no acredita cobros reales, acreditación institucional ni validación con alumnos. [Operación y comprobaciones de esta entrega](../src/docs/operacion-y-bitacora.md#cursos-completos-2026-10-15).

### Estado actual

BTC.EDU dispone de cuentas independientes, aprobación de creadores, edición y revisión editorial, contenido y archivos protegidos por versión, ofertas, carrito, pedidos, facturas, compras, biblioteca, guardados, inscripción, progreso y evaluaciones. La entrega esencial añade certificados, preguntas por lección, notificaciones internas y paneles de creador y administración. La compra agrupada conecta selección, pago y acceso; la remuneración del educador permanece por definir.

La revisión comparativa con otras plataformas del 23 de octubre de 2026 añadió crédito por compras anteriores, cupones, regalos, propinas al educador, reembolsos por Lightning, sello de certificados con OpenTimestamps, reseñas verificadas, galería de proyectos, rutas de varios cursos y lectura sin conexión como aplicación instalable. Son funciones implementadas y probadas técnicamente; ninguna está validada con participantes.

### Apariencia

La interfaz ofrece modo claro y oscuro desde la cabecera. En la primera visita utiliza la preferencia del sistema; al elegir un modo, conserva esa elección en el navegador para las siguientes visitas. La apariencia se aplica a la academia, la lectura, las compras, los perfiles y el espacio de creadores. Esta preferencia es local al navegador y no se sincroniza con la cuenta.

El lenguaje visual es industrial y monocromo: negro, blanco y grises neutros, con un único acento naranja reservado a la acción principal, el paso actual o un estado vivo. La marca, las cifras y los precios usan Doto, una tipografía de matriz de puntos; la lectura y los controles usan Inter Tight, y las etiquetas, Space Mono. Botones en forma de píldora, tarjetas redondeadas con líneas finas y una pantalla de pago con el total destacado completan el sistema ([decisiones y contraste](investigacion-y-requisitos.md#lenguaje-monocromo-2026-10-24)). La organización de pantallas sigue la [propuesta de estudiante, educador y móvil](../src/design/btc-edu-ui-ux-propuesta-2026-10-14-v2.png). Las [capturas de la aplicación](../src/docs/operacion-y-bitacora.md#overhaul-ui-ux-2026-10-14) del 14 de octubre muestran el resultado funcional con datos temporales y la paleta cálida anterior; todavía no se han renovado con el lenguaje monocromo.

### Cursos, lectura y progreso

La experiencia de aprendizaje conecta la ficha del curso, el temario, la lección y Mi aprendizaje. La acción principal permite empezar, retomar una lección pendiente o repasar un recorrido completado. El temario identifica las lecciones completadas, las evaluaciones y el contenido que requiere acceso. El catálogo distingue el precio del curso completo de las ofertas por capítulo o lección; si el estudiante ya está inscrito, la tarjeta muestra también su avance. La ficha y la biblioteca utilizan la misma decisión de continuación y conservan la versión estudiada. En Mi aprendizaje, cada curso muestra su estado, el avance por lección y el siguiente paso; cuando las lecciones restantes requieren acceso, la tarjeta lo indica y lleva a las opciones de acceso.

El lector organiza la explicación, los ejemplos, la práctica y la solución. Esta última se despliega cuando el alumno decide consultarla. El modo de lectura enfocada reduce las distracciones y mantiene la navegación del curso. En móvil, el temario está disponible antes del texto. Completar una lección sigue siendo una acción explícita: abrirla guarda el punto de continuación, y las evaluaciones obligatorias deben aprobarse antes de marcarla.

Mi aprendizaje coloca primero la continuación accesible, independiente de los filtros del inventario, y separa cursos, recursos, guardados y certificados. El progreso se actualiza después de la confirmación del servidor y puede corregirse desmarcando una lección. Los errores de guardado ofrecen recuperación sin sobrescribir un avance más reciente. Los certificados enumeran las lecciones y evaluaciones pendientes con enlaces a la versión exacta. Las comprobaciones técnicas y la revisión de pantallas se registran por separado; todavía debemos evaluar comprensión, facilidad de uso y resultados educativos con participantes.

### Colecciones y prácticas

Guardados permite crear, renombrar y eliminar colecciones personales como «Para estudiar», «Mi proyecto» o «Repasar». Un contenido puede pertenecer a varias colecciones. La búsqueda y los filtros por tipo se combinan con la colección elegida y con «Sin colección». Eliminar una colección conserva sus guardados; organizar una referencia no compra contenido ni cambia la inscripción.

El educador puede añadir una práctica por lección, con instrucciones, criterios de aprobación y un plazo previsto de revisión de entre 1 y 30 días naturales. La revisión editorial conserva estos datos en la versión publicada. El estudiante inscrito y con acceso envía texto, un enlace o un archivo privado de hasta 10 MB (PDF, ZIP, TXT, PNG o JPG). Cada entrega se conserva y solo el estudiante y el educador pueden descargar su adjunto.

La bandeja de Alumnos → Entregas ordena las entregas antiguas primero, permite filtrar por curso y estado y señala plazos superados. El educador registra los criterios cumplidos y una explicación; puede aprobar o solicitar cambios. Aprobar exige cumplir todos los criterios. Una solicitud de cambios habilita otra entrega completa, conservando el historial. Los avisos son internos y el educador puede pausar la recepción para atender su cola. El plazo es una previsión visible, no una garantía automatizada de respuesta.

Estas prácticas complementan las evaluaciones automáticas: su aprobación no añade requisitos al progreso ni a los certificados existentes. Las versiones publicadas y sus entregas permanecen intactas al editar el borrador. La implementación no incorpora análisis antivirus, revisión automática del proyecto ni envío de correo; antes de operación pública deben definirse capacidad de atención, retención y protección adicional de adjuntos. La utilidad educativa y la carga real del educador requieren validación con participantes.

### Evaluaciones

La preparación de la evaluación separa las reglas, la nota mínima, las preguntas y los intentos disponibles. El creador configura selección única o múltiple, nota mínima, intentos, espera y presentación de soluciones. El editor agrupa las reglas y permite abrir cada pregunta para editarla; los resultados distinguen estudiante, versión, intento y nota.

Con JavaScript, el alumno responde una pregunta a la vez, con opciones amplias, un indicador de preguntas respondidas y navegación para volver a cualquiera de ellas. Antes de entregar, revisa sus respuestas y completa las pendientes. El indicador cuenta preguntas con alguna selección; no indica aciertos. Sin JavaScript, el formulario completo conserva el guardado y la entrega.

El alumno puede guardar y retomar; iniciar consume un intento. Cambiar de pregunta no guarda respuestas y salir sin guardar puede perder los cambios locales. El servidor corrige con igual peso por pregunta y coincidencia exacta en selección múltiple, sin crédito parcial. La aprobación usa la puntuación exacta; el redondeo afecta solo la presentación. El resultado separa nota, estado y revisión de respuestas, respetando cuándo pueden mostrarse las soluciones.

Las evaluaciones obligatorias requieren aprobación para completar la lección. Aprobar no la marca automáticamente como completada. El creador puede autorizar un intento adicional con motivo, conservando notas y espera. Preguntas, reglas y resultados permanecen asociados a su versión; editar el borrador no cambia los intentos históricos.

La revisión técnica comprobó guardado, retoma, navegación, revisión previa y entregas, además del editor y los resultados en pantallas de escritorio y móvil. Estas comprobaciones no demuestran mejoras de aprendizaje ni sustituyen la validación de usabilidad con alumnos y creadores, que sigue pendiente.

### Certificados

El creador elige las lecciones requeridas y la publicación conserva esos requisitos. El alumno debe completarlas y aprobar todas las evaluaciones obligatorias de la versión, incluso las de lecciones opcionales. Comprar o inscribirse no cumple estas condiciones.

Al confirmar su nombre, el alumno obtiene una credencial única por inscripción, con evidencia histórica y descarga PDF privada. La verificación pública requiere que habilite compartir y puede ocultarse nuevamente. La administración puede revocar con motivo, sin borrar el historial. La corrección o sustitución después de emitir queda pendiente. El certificado acredita finalización según esas reglas, sin constituir una titulación oficial ni demostrar aprendizaje por sí mismo.

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital.

Cuando se activa en el entorno, la huella se envía a calendarios públicos de OpenTimestamps. La prueba `.ots` se descarga junto a los datos del certificado y, cuando los calendarios la anclan en un bloque de Bitcoin, permite comprobar la fecha con un cliente de OpenTimestamps sin depender de BTC.EDU. El sello prueba que esos datos existían en esa fecha; no prueba quién los emitió ni sustituye la consulta de revocación. Está desactivado por defecto y no se ha ensayado contra los calendarios reales.

### Pagos y complementos con Lightning

Quien compró lecciones o recursos de un capítulo o curso puede completarlo pagando la diferencia. El crédito suma lo pagado por compras propias cuyo contenido de pago pertenece por completo a ese paquete; excluye regalos y compras reembolsadas y nunca deja un artículo por debajo de 1 sat. La línea del pedido conserva el precio de lista, el crédito y solo los componentes que faltan.

El educador crea cupones en sats o porcentaje, con inicio, vencimiento, límite de usos y alcance por curso. El descuento se aplica después del crédito, solo a sus ofertas, y cada estudiante puede usar un cupón en una compra pagada. Un código inválido explica el motivo sin impedir la compra.

Comprar ahora permite regalar: la compra no concede acceso a quien paga y genera un enlace de canje de un solo uso, con mensaje opcional. Quien lo canjea recibe el acceso permanente y la inscripción; el comprador recibe un aviso.

Las propinas agradecen una lección o al educador con una factura Lightning de 10 a 100 000 sats y un mensaje opcional. No compran contenido ni cambian el acceso; el educador recibe un aviso y las consulta en Ventas. Se registran por educador, sin liquidación.

El estudiante puede pedir un reembolso durante siete días si no obtuvo un certificado con ese contenido ni lo usó como crédito en otra compra. Entrega una factura Lightning por el importe exacto y la administración aprueba o rechaza con nota. Al confirmarse el pago, termina el acceso que concedía esa compra; la compra, la evidencia y el avance se conservan. Si el resultado del pago es incierto, el acceso se mantiene hasta conciliarlo. Requiere la clave de pago de la wallet receptora, que la preparación local con FakeWallet ya guarda; en regtest no se asigna.

### Reseñas, proyectos y rutas

Solo opinan quienes compraron contenido de pago del curso o lo completaron. Cada reseña indica esa base, la versión y el alias público; el educador puede responder y la administración puede ocultarla. La ficha muestra el promedio y el número de reseñas reales.

Con permiso explícito del estudiante, una práctica aprobada aparece en la galería del curso con su solución escrita y su enlace; los adjuntos siguen privados y puede retirarla cuando quiera.

La administración publica rutas con cursos ordenados. Cada paso muestra si está sin empezar, en curso, completado o certificado. Al completar todos, el estudiante obtiene una credencial con huella SHA-256 que incluye los certificados de cada curso o, si un curso no ofrece certificado, su finalización. La verificación pública es opcional.

### Uso sin conexión

BTC.EDU puede instalarse como aplicación web. El estudiante guarda en su dispositivo las lecciones a las que tiene acceso y puede leerlas sin conexión; las demás páginas muestran qué guardó. Las lecciones guardadas pertenecen a una cuenta: al cerrar sesión o entrar con otra se eliminan. El avance, las compras y la comunidad necesitan conexión. Los videos y archivos no se guardan.

### Preguntas y notificaciones

El alumno inscrito con acceso puede preguntar desde una lección. Solo el participante y el creador aprobado del curso consultan la conversación. Los mensajes enviados se conservan; una corrección se añade como aclaración. Los límites de frecuencia, la protección de formularios y las claves de envío impiden duplicados y restringen la participación.

La bandeja propia avisa de preguntas, respuestas, decisiones editoriales, intentos adicionales y cambios del certificado. Abrir el aviso conserva su lectura. Esta entrega utiliza notificaciones internas; el envío de correo sigue pendiente.

### Perfiles

Cada estudiante puede elegir un alias, escribir una presentación e indicar sus intereses y sitio web. Su perfil comienza privado y puede compartirlo voluntariamente o volver a ocultarlo. El alias identifica sus mensajes en la comunidad; el nombre de cuenta, correo, compras, progreso y notas permanecen privados.

Los creadores aprobados mantienen una ficha con nombre público, biografía, especialidad, sitio web y contenido publicado. El directorio Personas permite encontrar estudiantes que comparten su perfil y creadores aprobados por nombre o tema. Las fichas se conectan con las conversaciones, sin publicar las comunidades de cada persona ni conceder acceso a otros cursos.

### Comunidad y moderación

Cada versión publicada tiene una comunidad para sus alumnos inscritos y el creador aprobado. Al final de cada lección, «Conversación de esta lección» permite comentar, responder y seguir conversaciones junto al contenido. Esos mismos mensajes aparecen en Comunidad, identificados con la lección y un enlace para volver a ella. Las preguntas privadas al creador conservan su recorrido separado.

Leer o escribir en la conversación requiere inscripción en la misma versión y acceso a la lección. Inscribirse no compra contenido de pago. La búsqueda, los recuentos y los avisos respetan estos permisos y la ocultación de mensajes. Una nueva versión conserva un espacio separado; las conversaciones anteriores mantienen su contexto histórico.

Los perfiles permiten reconocer a quienes participan y las respuestas del autor del curso se identifican como «Educador». El creador recibe avisos internos por nuevos comentarios de lección. El autor de una conversación y sus seguidores reciben avisos de respuestas de otras personas, según sus preferencias y sin duplicarlos por un reintento. Participar es opcional y no condiciona completar la lección.

Los participantes pueden reportar mensajes. El creador modera sus cursos y la administración interviene con permiso específico. Ocultar mensajes, cerrar conversaciones, suspender escritura y restablecerla requiere un motivo y conserva quién tomó la decisión y cuándo. La suspensión mantiene lectura, seguimiento, compras y progreso. La utilidad educativa y la capacidad de atención todavía requieren evaluación con personas.

### Métricas y paneles

El creador consulta resultados de sus contenidos; la administración consulta el conjunto con permisos específicos. Los paneles muestran compras confirmadas y volumen, conversión desde oferta, aperturas posteriores, regreso a biblioteca, compra repetida, inscripciones, progreso agregado, evaluaciones, certificados y atención de preguntas.

Cada indicador presenta periodo y denominador, con fechas de El Salvador y ausencia de datos explícita. Una compra conjunta se cuenta una vez como transacción y aporta varios permisos. Los eventos nuevos no reconstruyen visitas anteriores; reproducción y muestras siguen sin medición específica. La actividad técnica no demuestra aprendizaje ni validación comercial.

### Publicación y acceso

Enviar a revisión conserva una composición; aprobar publica exactamente esa copia. Las facturas mantienen precio e inclusiones y los derechos conservan la versión adquirida. El servidor verifica pagos y condiciones antes de conceder acceso, sin duplicar compras.

Los pagos pueden probarse con FakeWallet o con LNbits conectado a Polar en regtest. El usuario confirmó previamente un pago desde ZEUS hacia LNbits. BTC.EDU muestra el QR y consulta el estado silenciosamente; la compra completa desde ZEUS dentro de la aplicación queda para su comprobación posterior. No se acreditan fondos reales ni ingresos.

### Conciliación de pagos

La conciliación puede mantenerse en un proceso periódico supervisado, sin que el alumno conserve abierta la página de pago. El sistema consulta lotes de facturas, reintenta cuando el proveedor no responde y evita que las reservas antiguas sin emitir retrasen la revisión de otros pagos. Conserva las reglas de acceso: una confirmación repetida no duplica compras y un pago observado después del vencimiento se registra como incidencia sin conceder permisos. El proceso puede detenerse y reanudarse; su instalación como servicio con reinicio automático y alertas sigue pendiente. Las pruebas con un proveedor controlado verifican este comportamiento, sin acreditar una nueva prueba de pago desde ZEUS ni operación pública.

### Base técnica y pruebas

La incorporación de funciones comparadas con otras plataformas, del 23 de octubre de 2026 sobre la carpeta local sin commit propio, pasó 559 pruebas Django con `--parallel 4`, con y sin `DJANGO_DEBUG=true`, además de `manage.py check`, `makemigrations --check` y Ruff. En una base temporal con proveedor controlado se recorrieron en navegador el pago de una lección, la compra del curso con crédito y cupón, una propina, un regalo en vista móvil, los paneles del educador y la lectura de una lección guardada con el servidor detenido. No se repitieron los controles de concurrencia ni se contactaron calendarios de OpenTimestamps o wallets reales. [Detalle](../src/docs/operacion-y-bitacora.md#23-de-octubre-de-2026).

La revisión completa anterior, del mismo día, pasó las 524 pruebas Django con `--parallel 4`, con y sin `DJANGO_DEBUG=true`, además de `manage.py check` sin avisos, `makemigrations --check` y Ruff. No repitió los controles de concurrencia ni los verificadores de navegador, y no cambió el comportamiento de la plataforma. Las cifras de los párrafos siguientes corresponden a cada entrega en su fecha y no se suman a esta. [Detalle](../src/docs/operacion-y-bitacora.md#23-de-octubre-de-2026).

La estandarización de navegación del 14 de octubre de 2026, sobre la misma base con cambios locales, pasó una batería de 441 pruebas Django y completó 1.882 comprobaciones de navegador sin fallos sobre 184 cargas de páginas de cinco perfiles, cuatro tamaños y ambos temas. La barra conservó su geometría entre páginas; se comprobaron enlaces uniformes, ausencia de duplicados, avatar móvil, cierre, control del foco y adaptación del panel al cambiar de tamaño. Las revisiones adicionales comprobaron lectura enfocada, acceso, altura reducida, anclas y desplazamiento. Después del ajuste final del retorno del educador pasaron 75 pruebas de cuentas y 24 de navegación, sin sumar las ejecuciones solapadas a la batería anterior. La [bitácora de navegación](../src/docs/operacion-y-bitacora.md#barra-lateral-2026-10-14) conserva sus resultados y alcance. Estos resultados técnicos no equivalen a sesiones con participantes ni a una auditoría completa de accesibilidad.

La etapa comercial del 14 de octubre de 2026, en `main` sobre `687a773` con cambios locales, pasó 429 pruebas Django, configuración, consistencia de migraciones, revisión estática y cinco controles de concurrencia. También pasaron cinco escenarios del cliente de carrito, nueve de guardado y el verificador de progreso. En navegador se comprobó un pedido de tres artículos de dos educadores con una factura simulada de 250 sats, continuidad al entrar, guardados, recuperación al retirar, acceso posterior, historial, ayuda y atribución privada de ventas. Las migraciones conservaron las filas y columnas anteriores de 65 tablas, con respaldo; las cuatro tablas nuevas quedaron vacías, sin ejemplos en la base principal. El control posterior confirmó 69 tablas e integridad correcta. [Registro y evidencias comerciales](../src/docs/operacion-y-bitacora.md#etapa-comercial-2026-10-14). No se ejecutaron sesiones con participantes ni un nuevo pago desde ZEUS o con fondos reales.

La actualización de interfaz del 14 de octubre de 2026, en `main` sobre `687a773` con cambios locales, pasó 359 pruebas, comprobación de configuración y migraciones, revisión estática y cinco controles de concurrencia. Se verificaron por separado nueve escenarios de guardado del cliente y la recuperación del progreso. En navegador se ensayaron compra simulada con retorno a la lección, continuación, requisitos del certificado, pendientes del estudio, edición y corrección de errores, búsqueda, menú móvil y ambos temas. Las vistas temporales conservaron un ancho sin desbordamiento en las pantallas comprobadas a 320 px. No se ejecutaron sesiones externas, una auditoría completa de accesibilidad ni pagos desde ZEUS en esta entrega. [Registro y evidencias](../src/docs/operacion-y-bitacora.md#overhaul-ui-ux-2026-10-14).

Después de los últimos ajustes pasaron 29 pruebas de descubrimiento, navegación y autoría y la revisión estática. La migración que conserva la lección elegida en la factura se aplicó con respaldo y comparación de todas las columnas y filas anteriores de 65 tablas; la integridad y las relaciones se conservaron, sin cargar ejemplos en la base principal. El detalle está en el mismo registro.

La entrega de fichas del 13 de octubre de 2026, en `main` sobre `2d318f6` con cambios locales, pasó 319 pruebas, configuración sin errores, consistencia de migraciones, revisión estática y cinco controles de concurrencia. Después de los últimos ajustes pasaron 32 pruebas enfocadas. La migración tuvo respaldo y conservó 616 filas anteriores en 64 tablas. Se ensayó edición, envío y consulta de muestras en navegador con datos temporales; no se repitió la compra desde ZEUS. Permanece la advertencia conocida por correos reutilizables entre tipos de cuenta. [Evidencias](investigacion-y-requisitos.md#desarrollo-del-enfoque).

La aplicación utiliza Django, HTML y HTMX, con SQLite para la etapa local. La entrega esencial con huellas SHA-256 pasó 184 pruebas y comprobaciones de concurrencia comercial, de evaluaciones y de certificados y mensajes. Se recorrieron las nuevas pantallas por HTTP en escritorio y móvil y se verificaron formularios, privacidad y PDF. La migración tuvo respaldo y conservó los 211 registros originales, sin cargar ejemplos en la base principal.

La ampliación de conciliación pasó 192 pruebas Django, revisión estática y comprobación de migraciones, junto con los tres controles de concurrencia. No necesitó una migración nueva ni modificó la base principal. La verificación usó datos de prueba y un proveedor controlado; el ensayo adicional con ZEUS sigue pendiente.

La incorporación de comunidad y moderación pasó 210 pruebas Django, revisión estática, consistencia de migraciones y cuatro controles de concurrencia con conexiones SQLite independientes. La migración local se aplicó con respaldo y sin ejemplos. Se comprobó el recorrido de alumno y el envío de una respuesta en Chrome, incluida la vista móvil; los formularios de moderación se verificaron en las pruebas automatizadas. Esta entrega no repite el pago desde ZEUS ni acredita operación pública.

La ampliación de perfiles y comunidad pasó 227 pruebas Django, revisión estática, comprobación de migraciones y cuatro controles de concurrencia, incluido el seguimiento simultáneo. Tras los últimos ajustes se repitieron las 35 pruebas de perfiles y comunidad. Se revisaron el directorio, la ficha pública y la edición de alias en navegador con cuentas sintéticas, incluida la ficha en móvil. Las migraciones locales tuvieron respaldo y se comprobó la conservación de las filas anteriores; las adiciones de catálogo observadas durante la revisión corresponden a actividad concurrente y se conservaron. Esta evidencia no acredita uso público ni validación educativa.

La integración de conversaciones en lecciones pasó 57 pruebas de lecciones, comunidad, acceso e historial, además de la comprobación de concurrencia para envíos y avisos únicos. Se revisaron comentarios, respuestas y seguimiento del estudiante, la respuesta del creador y la presentación móvil con cuentas ficticias. La migración conservó los 227 registros previos, con respaldo y sin añadir ejemplos. En aquella entrega, la revisión general quedó pendiente del cierre de otros cambios concurrentes; estas comprobaciones no constituyen validación educativa.

### Organización y próximos pasos

Caleb continúa con Business y Dev. El requisito oficial de cuatro integrantes requiere aclaración con CUBO+. Las siguientes tareas son preparar contenido y derechos comprobados, manuales y demostración; ejecutar validación con personas y completar presupuesto, correo, instalación de la conciliación como servicio y procedimientos para operación pública. Las membresías permanecen como ampliación pendiente; la comunidad por versión ya permite conversar y moderar con historial. El estado actual se mantiene separado de la bitácora y de los resultados externos todavía inexistentes.

La verificación de correo, las preferencias de avisos y la solicitud de revisar una suspensión de cuenta ya tienen recorridos implementados. La entrega real de correo y sus procedimientos deben comprobarse antes de operar públicamente. Marcar respuestas como solución y las apelaciones sobre moderación de conversaciones permanecen como ampliaciones por diseñar y verificar.

## A dónde queremos llegar

Queremos una experiencia en la que el alumno encuentre contenido pertinente, comprenda la compra y pueda continuar aprendiendo. El creador debe preparar, publicar y mantener sus materiales sin perjudicar el acceso existente.

Las evaluaciones y certificados conservan requisitos y resultados por versión. Las preguntas y notificaciones ya permiten acompañar al alumno; los paneles ofrecen indicadores con fuentes y denominadores explícitos. La comunidad por versión incorpora conversación y moderación; las membresías renovadas manualmente quedan como ampliación por desarrollar y verificar.

Necesitamos analítica que explique consulta, pago, uso y regreso sin confundir actividad con aprendizaje. También un presupuesto que considere consumo gratuito, acceso permanente, archivos históricos, correo, respaldos, supervisión y soporte.

La operación pública y una integración con fondos reales requerirán decisiones y evidencias propias. La investigación externa ayuda a identificar condiciones; no acredita que ya estén resueltas.

## Qué demostramos

La evidencia técnica registrada muestra ofertas individuales y pedidos con varias líneas que generan una factura por el total. Una confirmación válida concede el acceso específico de forma única. Documenta persistencia, protección y conservación de referencias históricas; la compra agrupada se ensayó con un proveedor local de prueba, sin fondos reales.

La revisión permite publicar una composición aprobada mientras se preparan cambios posteriores. Las evaluaciones y certificados conservan reglas, intentos y evidencia de finalización por versión. También comprobamos preguntas privadas, avisos persistentes y paneles con datos de prueba; estos resultados técnicos no prueban dominio educativo.

La investigación documenta alternativas de monetización y condiciones externas de costos. Todavía no demuestra preferencia por BTC.EDU, disposición real a pagar, frecuencia de compra o mejora educativa.

## Logros

Definimos unidades de compra, muestras, permisos y responsabilidades de publicación. Conectamos creación, revisión, oferta, carrito, pedido, compra simulada y aprendizaje, conservando versiones históricas. Incorporamos evaluaciones con resultados persistentes, certificados históricos, acompañamiento por preguntas y avisos, y paneles con consultas verificadas. La compra agrupada conserva sus precios e inclusiones y atribuye las líneas al educador correspondiente. Añadimos funciones que solo Lightning facilita, como propinas, reembolsos y completar un curso pagando la diferencia, junto con reseñas, cupones, regalos, rutas, galería de proyectos, sello de certificados y lectura sin conexión.

Ampliamos la comparación de modelos y costos, y preparamos instrumentos para entrevistas, usabilidad y precios. Es un avance de investigación documental y preparación, no una validación externa terminada.

Los resultados de mercado y aprendizaje se incorporarán cuando exista evidencia suficiente.

## Próximos pasos

Validar con participantes el recorrido comercial implementado: selección de una o varias unidades, comprensión del total y las inclusiones, crédito al completar un conjunto, recuperación del pago y apertura de lo adquirido. Definir remuneración y liquidación a educadores, y revisar con criterio legal el plazo y las condiciones de reembolso. Resolver automáticamente pagos observados tarde necesita una hora de cobro fiable; ahora conservamos la evidencia y ofrecemos revisión sin inducir otro pago. El [alcance comercial](investigacion-y-requisitos.md#experiencia-comercial) distingue la entrega y las ampliaciones pendientes.

Observar la interfaz implementada con estudiantes y educadores nuevos mediante tareas neutrales: encontrar y abrir/comprar contenido, retomar aprendizaje y preparar una publicación. Registrar dudas, finalización, ayuda y errores, y contrastar los hallazgos con el diagnóstico anterior antes de afirmar una mejora medida de usabilidad. Completar la revisión de accesibilidad con tecnologías de asistencia. La cobertura y los criterios están en [el plan de interfaz](investigacion-y-requisitos.md#revision-ui-ux).

Consolidar una selección pequeña de unidades en varias áreas, con resultados y requisitos explícitos. Revisar sus prácticas con especialistas y comparar su utilidad con las alternativas gratuitas y pagadas que ya usa el público. Probar si el crédito por compras anteriores se entiende y si cambia la decisión de completar un conjunto.

Quedan fuera de esta etapa la entrada con Lightning (LNURL-auth), que exige un dominio público con HTTPS para que la wallet responda; el pago por minuto de video y audio; la liquidación automática a educadores; el asistente de IA; otros idiomas y un pase con créditos, que contradice la tesis de micropagos y queda como hipótesis.

Preparar reclutamiento y consentimiento; ejecutar entrevistas y tareas con la versión identificada; analizar dificultades y objeciones; comprobar los cambios relevantes.

Contrastar rangos de precio con costos y preparar escenarios de sostenibilidad. Preparar la demostración y los manuales de la entrega esencial; completar operación y especificaciones de las ampliaciones pendientes. Extender analítica solo cuando los nuevos eventos tengan reglas y utilidad definidas.

Actualizar el documento con cada entrega, vinculando decisiones y resultados a sus evidencias reales.

## Conclusiones

BTC.EDU propone adaptar la compra de contenido a necesidades educativas concretas. El desarrollo registrado permite verificar publicación, pago simulado y acceso persistente.

La investigación muestra alternativas comparables y costos que debemos considerar. La siguiente etapa deberá contrastar la utilidad y comprensión con alumnos y creadores, y evaluar la sostenibilidad de los precios.

Mantendremos las conclusiones comerciales como provisionales hasta reunir esa evidencia.

## Referencias

Las fuentes externas se enlazan junto a las afirmaciones que sustentan. Los precios y condiciones de la investigación de costos conservan la consulta del 5 de octubre de 2026; deben revisarse antes de contratar. La comparación de posicionamiento se amplió el 13 de octubre de 2026 con documentación oficial de las plataformas, sin compras ni pruebas de sus recorridos. El detalle y las hipótesis están en [posicionamiento y validación](investigacion-y-requisitos.md#posicionamiento-y-validacion).

Los documentos originales de CUBO+ definen el reto y la evaluación. La investigación funcional, las decisiones y los registros técnicos del proyecto conservan el detalle y los límites de cada entrega.

La bitácora y los anexos reunirán las evidencias de desarrollo, instrumentos y resultados reales. El enlace al Google Doc y la validación con participantes siguen pendientes de incorporar.



## Navegación y tareas

Al entrar a Cursos, Tutoriales o Recursos se elige entre Bitcoin, Tecnología y Creación; Inicio también presenta las categorías de cursos. Cada categoría reúne subcategorías: los temas anteriores, como Lightning y Desarrollo Lightning, quedan dentro de Bitcoin. Tecnología incorpora áreas como hardware, redes, desarrollo web y móvil; Creación reúne herramientas Adobe, fotografía y creación de contenido, entre otras. Las tarjetas muestran imagen, nombre y cantidad de publicaciones del catálogo elegido. Dentro de una categoría se ofrecen las subcategorías con publicaciones; al elegir una, «Cambiar subcategoría» permite volver a las opciones. Una categoría vacía mantiene accesibles sus áreas mediante «Ver subcategorías». Su incorporación no implica cursos nuevos publicados ni demanda comprobada.

La búsqueda directa, «Ver todos», los filtros y el regreso desde una ficha conservan la selección. Los conteos respetan el tema de la versión o revisión publicada, sin adelantar cambios del borrador ni mezclar Cursos, Tutoriales y Recursos. El contenido sin tema permanece en «Por descubrir». Las ilustraciones están integradas; la carga de imágenes personalizadas sigue pendiente. La ampliación pasó 73 pruebas focalizadas, una prueba adicional de compatibilidad del importador y una revisión de escritorio en modo oscuro; la migración local mantuvo los conteos de contenido y los identificadores anteriores. La [organización y sus límites](investigacion-y-requisitos.md#categorias-del-catalogo) distinguen este cambio técnico de la validación pendiente con participantes.

La barra de búsqueda indica el catálogo y la categoría o subcategoría elegidos. «Filtros» reúne únicamente opciones que pueden acotar esas publicaciones y se despliega cuando hace falta; las selecciones activas se pueden retirar sin perder la categoría. La misma barra se usa en Cursos, Tutoriales, Recursos, Explorar y Comparar cursos. El ajuste pasó 69 pruebas focalizadas, dos pruebas adicionales ejecutadas por separado y una revisión de escritorio y móvil; sus [comprobaciones y límites](../src/docs/operacion-y-bitacora.md#filtros-catalogo-2026-10-15) quedan separados de la entrega de categorías.

Sus cuatro iconos de búsqueda, filtros, cierre y flecha proceden de Font Awesome Free y se incluyen localmente; la flecha conserva su tamaño, alineación y espacio al abrir los desplegables. La [corrección de iconos](../src/docs/operacion-y-bitacora.md#iconos-filtros-2026-10-15) se registra por separado de las pruebas anteriores de la barra.

El panel de filtros distribuye los campos y la acción de aplicar según el espacio disponible, con una presentación plana y un separador fino. El foco de teclado se reconoce mediante fondo suave y subrayado. La [corrección de distribución](../src/docs/operacion-y-bitacora.md#panel-filtros-2026-10-15) conserva su registro propio.

La navegación principal conserva los mismos destinos durante cada recorrido. El estudiante encuentra Cursos, Tutoriales, Recursos, Rutas, Mi aprendizaje, Compras y Comunidad. El visitante accede directamente a los catálogos, a Rutas y a Enseñar. Compras incluye Propinas y Ventas incluye Cupones y Propinas. El educador aprobado mantiene Mi estudio, Contenido, Alumnos, Comunidad y Ventas, con los tres catálogos separados de sus herramientas. El pendiente muestra Estado de mi cuenta y conserva el catálogo público; el suspendido ve únicamente destinos permitidos de estado, cuenta, ayuda y avisos. Academia y estudio comparten el marco y la geometría de la barra; cuenta y ayuda se consultan desde el avatar también en móvil, sin duplicarlas en el lateral.

Cada catálogo tiene página, título, filtros y selección propios. Cursos reúne recorridos completos; Tutoriales, guías para una tarea; Recursos, videos, materiales y fuentes externas. Comparar cursos permanece dentro de Cursos. Los enlaces anteriores de Explorar siguen funcionando, pero ya no hay una segunda fila de pestañas que repita los catálogos. Mi aprendizaje separa continuación, cursos, recursos adquiridos, guardados, certificados y Mis preguntas. Curso, temario y comunidad conservan su lugar junto al lector. Compras reúne carrito, pendientes e historial. Las ofertas de una lección bloqueada incluyen únicamente opciones aplicables a esa lección; el pedido conserva ese destino durante el acceso a la cuenta y lo recupera después de comprobar el pago.

La separación posterior de los catálogos pasó 41 pruebas focalizadas y 445 comprobaciones de navegador, sin fallos. El [registro de este ajuste](../src/docs/operacion-y-bitacora.md#catalogos-separados-2026-10-14) conserva capturas, alcance y límites. La documentación conserva resultados resumidos; los volcados extensos de pruebas se eliminaron y los verificadores ya no los exportan automáticamente.

La selección activa identifica la tarea y el panel móvil controla el foco, se cierra con Escape y abre también en lectura enfocada. Entrada, registro y recuperación comparten una cabecera simplificada sin barra lateral. El [detalle de navegación](investigacion-y-requisitos.md#barra-lateral-estandarizada) conserva el alcance y la [bitácora](../src/docs/operacion-y-bitacora.md#barra-lateral-2026-10-14), las comprobaciones reales. Las sesiones de usabilidad con participantes siguen pendientes.

El estudio reúne contenido y acciones pendientes. El editor de curso separa información, temario, evaluaciones, certificado, publicación y precio. Permite ordenar capítulos y lecciones con botones, cargar un archivo desde su recurso y volver a la tarea. La publicación muestra requisitos enlazados y distingue versión publicada, borrador y envío en revisión. La vista del estudiante y la prueba de evaluación permiten revisar el contenido sin registrar aprendizaje. Alumnos reúne preguntas pendientes y resultados; Ventas reúne actividad y ofertas contextualizadas.

Los formularios de autoría advierten antes de abandonar cambios locales. El guardado con JavaScript conserva los valores ante errores y enlaza los campos que necesitan corrección; sin JavaScript se mantiene el envío normal. Las reglas de aprobación, propiedad, acceso y conservación por versión siguen comprobándose en el servidor. Estos recorridos están implementados; su facilidad de uso para distintos públicos sigue pendiente de validación con participantes.

El visitante puede reunir cursos, tutoriales y recursos, seguir explorando y conservar su selección al entrar. El estudiante revisa líneas, educador, versión, inclusiones y total; puede quitar, deshacer o guardar para después. Comprar ahora conserva una ruta directa. La confirmación activa el contenido del pedido y elimina únicamente los artículos comprados, preservando cambios posteriores del carrito. Un paquete parcialmente adquirido se completa con crédito. Los conflictos por contenido ya adquirido sin crédito aplicable, paquetes solapados, cambios de oferta o pagos pendientes exigen resolver la selección antes de otro cobro. El resumen muestra el crédito y el cupón aplicados.

Guardados admite cursos y tutoriales por versión sin conceder acceso. Los autores enlazan a sus perfiles públicos permitidos, con publicaciones filtrables. La ayuda de plataforma conserva una referencia comprobada de pedido o recurso; cada educador ve sus propios productos e importes en Ventas. Estos registros no representan liquidación disponible. El carrito admite 20 artículos; un excedente al incorporar la selección de visitante permanece solo en esa sesión hasta resolverlo. El [detalle y las evidencias de la entrega comercial](../src/docs/operacion-y-bitacora.md#etapa-comercial-2026-10-14) conservan sus límites.
