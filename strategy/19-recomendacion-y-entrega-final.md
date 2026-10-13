# BTC.EDU

## Introducción

BTC.EDU es una plataforma integral de educación que busca conectar descubrimiento, estudio, práctica, acompañamiento y comunidad. Cursos, tutoriales y recursos permiten abordar tanto un recorrido amplio como una necesidad concreta. El espacio personal debe ayudar a conservar lo estudiado y continuar con un propósito claro.

El proyecto nació de una pregunta sobre acceso: ¿cómo permitir que una persona compre el contenido educativo que necesita sin obligarla a adquirir un curso completo o mantener una suscripción? Los micropagos complementan el contenido gratuito y permiten adquirir unidades específicas, conservando acceso a la versión comprada.

La propuesta comprende al alumno que aprende, al creador que prepara y acompaña y a la administración que revisa y sostiene la operación. Necesitamos conectar esos recorridos, comprobar la utilidad educativa de los contenidos y mantener sus derechos, resultados y conversaciones cuando cambian las publicaciones.

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

### Revisión integral

Revisamos cómo se relacionan los apartados existentes: inicio y búsqueda, cursos, tutoriales, recursos, biblioteca, lecciones, evaluaciones, certificados, preguntas, comunidad, personas, cuentas, avisos, compras, creación, revisión y estadísticas. La base técnica permite conservar versiones, permisos e historial, pero la experiencia sigue organizada principalmente alrededor del curso.

La colección local consultada tiene seis cursos introductorios sobre Bitcoin, wallets, Lightning, facturas, LNbits y acceso mediante micropagos. Cada curso incluye cuatro lecciones con explicación, ejemplo, práctica y solución, una pregunta final y requisitos de certificado. Tutoriales y Recursos tienen estructura funcional, pero todavía no contienen publicaciones propias en esa colección. La publicación técnica y una sola pregunta final no demuestran dominio completo de los objetivos.

La revisión identifica la necesidad de orientar el inicio, guardar también recursos gratuitos, conectar formatos mediante objetivos, dar continuidad a la práctica y facilitar ayuda y participación desde el contenido estudiado. También reproduce inconsistencias en el retorno después del registro, el nombre público del creador y la clasificación de recursos editados en borrador. Los cursos institucionales requieren un responsable humano para atender las preguntas dirigidas a su cuenta técnica.

La guía del Institute of Education Sciences ofrece fundamento para probar práctica y repaso distribuidos. CAST orienta la retroalimentación hacia acciones concretas de mejora. WCAG 2.2 proporciona criterios para una auditoría de accesibilidad. Estas referencias sustentan propuestas de diseño; no acreditan resultados educativos de BTC.EDU. [IES](https://ies.ed.gov/ncee/wwc/PracticeGuide/1), [CAST](https://udlguidelines.cast.org/engagement/effort-persistence/feedback/), [W3C](https://www.w3.org/TR/WCAG22/).

Se ejecutaron 227 pruebas sobre una instantánea del código y comprobaciones adicionales con datos temporales. El recorrido visual incluyó pantallas públicas, biblioteca, lección y comunidades, con una revisión parcial de móvil. No se hicieron sesiones externas, una auditoría completa de accesibilidad ni una nueva prueba de pago contra LNbits. El análisis detallado conserva fuentes, evidencia y prioridades en [Revisión integral de BTC.EDU](20-analisis-integral-plataforma-educativa.md).

Las siguientes entregas deben conectar orientación, biblioteca de distintos formatos, práctica, ayuda y comunidad, conservando el recorrido de micropago y acceso. Las rutas editoriales, entregas prácticas, guardados gratuitos y comunidades por tema siguen siendo propuestas por desarrollar y verificar.

### Cuentas y servicio

BTC.EDU conserva cuentas independientes para estudiantes y creadores, aunque compartan correo. Cada espacio mantiene contraseña, perfil y actividad propios. Mi cuenta reúne foto, presentación, acceso, avisos y ayuda. Cambiar de espacio exige entrar con la otra cuenta y explica que la sesión cambia también en las demás pestañas; los formularios detectan el cambio y conservan los datos pendientes.

Se implementaron fotografía con recorte, cambio de contraseña, confirmación de correo, cambio confirmado desde ambos buzones, gestión de sesiones, exportación y desactivación con reactivación. Estas acciones conservan el identificador, compras y registros históricos. Los enlaces tienen propósito y vencimiento, y el acceso aplica límites temporales. El correo tiene cola y reintentos; la entrega real requiere configurar y comprobar un proveedor.

El creador consulta estado, observaciones e historial de su solicitud. Cada decisión genera un aviso. Si está suspendido, puede gestionar su cuenta y solicitar revisión desde un área restringida, mientras las herramientas de publicación siguen bloqueadas. Su estudio reúne preguntas pendientes, cambios editoriales y reportes, y orienta la primera publicación. El alumno puede guardar recursos y fuentes en Mi aprendizaje sin que guardar compre o amplíe sus permisos.

La suite completa pasó 310 pruebas; tras el último ajuste de confirmaciones simultáneas se repitieron las 39 pruebas de cuentas y guardados. También pasaron cinco controles de concurrencia y se revisaron pantallas de escritorio y móvil con datos temporales. La migración tuvo respaldo y conservó los valores de 540 filas anteriores. Es evidencia técnica; la comprensión de los recorridos y su utilidad deben comprobarse con participantes. El [informe de cuentas](22-usuarios-creadores-y-estudiantes.md) conserva comportamiento, evidencias y límites.

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

Desarrollar y evaluar una plataforma integral de educación que permita descubrir contenidos pertinentes, estudiar y practicar, recibir acompañamiento, participar en comunidad y continuar el aprendizaje, combinando contenido gratuito con adquisiciones específicas mediante pagos simulados y acceso persistente.

### Objetivos específicos

Investigar las necesidades de alumnos y creadores al aprender, resolver tareas, compartir conocimiento y mantener contenidos, y comparar modelos de monetización para justificar precios y muestras.

Diseñar recorridos que conecten cursos, tutoriales y recursos con objetivos, práctica, ayuda y continuidad, protegiendo el contenido de pago y conservando compras, progreso y resultados de la versión correspondiente.

Facilitar la preparación y revisión de contenido educativo, la atención de preguntas y la moderación, con criterios de calidad, responsabilidades y condiciones de acceso comprensibles.

Evaluar usabilidad y resultados educativos con tareas y evidencias definidas, medir compra y uso sin confundirlos con aprendizaje y estudiar los recursos y costos necesarios para sostener la plataforma.

## Enfoque

### Producto

La estructura comprende cursos, tutoriales, recursos, aprendizaje personal, acompañamiento y comunidad. La colección inicial aborda Bitcoin, Lightning y micropagos; su contenido y evaluación requieren revisión educativa y contraste con alumnos. El contenido gratuito, las muestras y las unidades de compra deben responder a necesidades reconocibles. La investigación orientará qué formatos y conexiones aportan utilidad.

### Experiencia

Trabajamos el recorrido desde orientarse y explorar hasta estudiar, practicar, pedir ayuda, participar y retomar. Cuando hay una adquisición, el alumno debe comprender precio, inclusiones y estados del pago y recuperar su acceso. La biblioteca debe evolucionar para reunir también recursos gratuitos guardados; esa ampliación aún está pendiente.

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

### Catálogo inicial

Publicamos seis cursos introductorios de Bitcoin y Lightning con 24 lecciones de texto. Cada lección incluye explicación, ejemplo, práctica y solución. Los cursos presentan objetivos, requisitos, temario y duración estimada para realizar las actividades; todavía no hemos medido esos tiempos con alumnos.

Bitcoin desde cero, Wallets y autocustodia y Lightning desde cero son gratuitos. Facturas Lightning, Laboratorio con LNbits y Contenido con micropagos ofrecen la primera lección gratis y tres lecciones de pago. El precio inicial es 120 sats por curso o 50 sats por lección individual, como valores de prueba sin validación comercial.

Cada curso incluye una pregunta final y un certificado condicionado a completar las cuatro lecciones y aprobar esa comprobación. Es una comprobación introductoria limitada, no una evaluación exhaustiva ni evidencia de dominio. Las prácticas usan cálculos, escenarios y diseños que no exigen fondos reales. Los textos son material introductorio propio de BTC.EDU con referencias técnicas; no incorporan videos ni sesiones realizadas con usuarios.

La carga conserva versiones publicadas, registra decisiones de publicación y ofertas, crea un respaldo local y evita duplicar cursos al repetirse. Comprobamos el catálogo, sus fichas y las 24 lecciones por HTTP en una copia de la base, incluida la protección del texto de pago. La revisión educativa externa y la comprobación del nuevo catálogo con personas siguen pendientes.

### Estado actual

BTC.EDU dispone de cuentas independientes, aprobación de creadores, edición y revisión editorial, contenido y archivos protegidos por versión, ofertas, facturas, compras, biblioteca, inscripción, progreso y evaluaciones. La entrega esencial añade certificados, preguntas por lección, notificaciones internas y paneles de creador y administración.

### Registro, identidad y clasificación

El estudiante conserva el destino desde el que llegó al entrar o crear su cuenta, incluidos los filtros. Los enlaces entre acceso y registro mantienen ese recorrido también cuando debe corregir un error del formulario. Solo se aceptan destinos internos del espacio de estudiante; el registro de creador conserva la solicitud y aprobación requeridas.

El catálogo, el selector y las fichas muestran el nombre público vigente del creador aprobado. Las versiones y los certificados emitidos conservan su atribución histórica. Cambiar la presentación pública no modifica los datos de las credenciales anteriores.

El tema de un video o material pertenece a la revisión enviada y aprobada. Editar su borrador no altera la clasificación pública; el nuevo tema se muestra al aprobar otra revisión. La migración conserva la clasificación disponible de los recursos actuales, sin inventar la de revisiones anteriores que carecen de esa información.

### Evaluaciones

El creador configura selección única o múltiple, nota mínima, intentos, espera y presentación de soluciones. El alumno puede guardar, retomar y entregar respuestas; iniciar consume un intento. El servidor corrige con igual peso por pregunta y coincidencia exacta en selección múltiple, sin crédito parcial. La aprobación usa la puntuación exacta; el redondeo afecta solo la presentación.

Las evaluaciones obligatorias requieren aprobación para completar la lección. El creador puede autorizar un intento adicional con motivo, conservando notas y espera. Preguntas, reglas y resultados permanecen asociados a su versión; editar el borrador no cambia los intentos históricos.

### Certificados

El creador elige las lecciones requeridas y la publicación conserva esos requisitos. El alumno debe completarlas y aprobar todas las evaluaciones obligatorias de la versión, incluso las de lecciones opcionales. Comprar o inscribirse no cumple estas condiciones.

Al confirmar su nombre, el alumno obtiene una credencial única por inscripción, con evidencia histórica y descarga PDF privada. La verificación pública requiere que habilite compartir y puede ocultarse nuevamente. La administración puede revocar con motivo, sin borrar el historial. La corrección o sustitución después de emitir queda pendiente. El certificado acredita finalización según esas reglas, sin constituir una titulación oficial ni demostrar aprendizaje por sí mismo.

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital ni un registro en Bitcoin.

### Preguntas y notificaciones

El alumno inscrito con acceso puede preguntar desde una lección. Solo el participante y el creador aprobado del curso consultan la conversación. Los mensajes enviados se conservan; una corrección se añade como aclaración. Los límites de frecuencia, la protección de formularios y las claves de envío impiden duplicados y restringen la participación.

La bandeja propia distingue avisos de servicio, preguntas y comunidad, incorpora contexto del curso y permite filtrar pendientes o marcar como leídos los propios. Cada cuenta elige si recibe nuevos avisos de preguntas y comunidad; las decisiones necesarias de cuenta, revisión y moderación se mantienen. Son avisos internos. El correo se utiliza para acceso y confirmaciones, con entrega real todavía por comprobar.

### Perfiles

Cada estudiante puede elegir alias, foto, presentación, intereses y sitio web. También puede indicar un objetivo privado de aprendizaje. La ficha empieza privada y puede compartirse voluntariamente o volver a ocultarse. Antes de compartir, se explica que sus campos públicos pueden verse sin iniciar sesión; nombre de cuenta, correo, compras, progreso y notas permanecen privados. Ocultar la ficha no elimina los mensajes enviados.

Los creadores aprobados mantienen una ficha con foto, nombre público, biografía, especialidad y contenido publicado. Personas permite encontrar perfiles compartidos y creadores aprobados. Las fotos se validan, recortan y almacenan sin metadatos originales; su entrega comprueba privacidad y participación autorizada. Sustituirlas o retirarlas revoca el acceso a la imagen anterior desde el servicio. Perfil y certificado conservan decisiones de compartición independientes.

### Comunidad y moderación

Cada versión publicada tiene una comunidad para sus alumnos inscritos y el creador aprobado. Las conversaciones y respuestas se comparten dentro de ese espacio; las preguntas por lección conservan su carácter privado. Inscribirse permite participar, pero no compra las lecciones de pago. Una nueva versión tiene otro espacio y las comunidades anteriores conservan su historial.

Los perfiles permiten reconocer a quienes participan. La búsqueda encuentra conversaciones y respuestas visibles; los filtros distinguen abiertas, sin respuesta y propias o seguidas. El recuento de respuestas y el orden por actividad respetan la ocultación de mensajes. Seguir una conversación genera avisos internos de nuevas respuestas, sin ampliar los permisos de acceso o escritura.

Los participantes pueden reportar mensajes. El creador modera sus cursos y la administración interviene con permiso específico. Ocultar mensajes, cerrar conversaciones, suspender escritura y restablecerla requiere un motivo y conserva quién tomó la decisión y cuándo. La suspensión mantiene lectura, compras y progreso. Los controles de acceso, formularios y reintentos se verifican con datos temporales. Todavía no hay operación pública ni validación con personas.

### Métricas y paneles

El creador consulta resultados de sus contenidos; la administración consulta el conjunto con permisos específicos. Los paneles muestran compras confirmadas y volumen, conversión desde oferta, aperturas posteriores, regreso a biblioteca, compra repetida, inscripciones, progreso agregado, evaluaciones, certificados y atención de preguntas.

Cada indicador presenta periodo y denominador, con fechas de El Salvador y ausencia de datos explícita. Una compra conjunta se cuenta una vez como transacción y aporta varios permisos. Los eventos nuevos no reconstruyen visitas anteriores; reproducción y muestras siguen sin medición específica. La actividad técnica no demuestra aprendizaje ni validación comercial.

### Publicación y acceso

Enviar a revisión conserva una composición; aprobar publica exactamente esa copia. Las facturas mantienen precio e inclusiones y los derechos conservan la versión adquirida. El servidor verifica pagos y condiciones antes de conceder acceso, sin duplicar compras.

Los pagos pueden probarse con FakeWallet o con LNbits conectado a Polar en regtest. El usuario confirmó previamente un pago desde ZEUS hacia LNbits. BTC.EDU muestra el QR y consulta el estado silenciosamente; la compra completa desde ZEUS dentro de la aplicación queda para su comprobación posterior. No se acreditan fondos reales ni ingresos.

### Conciliación de pagos

La conciliación puede mantenerse en un proceso periódico supervisado, sin que el alumno conserve abierta la página de pago. El sistema consulta lotes de facturas, reintenta cuando el proveedor no responde y evita que las reservas antiguas sin emitir retrasen la revisión de otros pagos. Conserva las reglas de acceso: una confirmación repetida no duplica compras y un pago observado después del vencimiento se registra como incidencia sin conceder permisos. El proceso puede detenerse y reanudarse; su instalación como servicio con reinicio automático y alertas sigue pendiente. Las pruebas con un proveedor controlado verifican este comportamiento, sin acreditar una nueva prueba de pago desde ZEUS ni operación pública.

### Base técnica y pruebas

La aplicación utiliza Django, HTML y HTMX, con SQLite para la etapa local. La entrega esencial con huellas SHA-256 pasó 184 pruebas y comprobaciones de concurrencia comercial, de evaluaciones y de certificados y mensajes. Se recorrieron las nuevas pantallas por HTTP en escritorio y móvil y se verificaron formularios, privacidad y PDF. La migración tuvo respaldo y conservó los 211 registros originales, sin cargar ejemplos en la base principal.

La ampliación de conciliación pasó 192 pruebas Django, revisión estática y comprobación de migraciones, junto con los tres controles de concurrencia. No necesitó una migración nueva ni modificó la base principal. La verificación usó datos de prueba y un proveedor controlado; el ensayo adicional con ZEUS sigue pendiente.

La incorporación de comunidad y moderación pasó 210 pruebas Django, revisión estática, consistencia de migraciones y cuatro controles de concurrencia con conexiones SQLite independientes. La migración local se aplicó con respaldo y sin ejemplos. Se comprobó el recorrido de alumno y el envío de una respuesta en Chrome, incluida la vista móvil; los formularios de moderación se verificaron en las pruebas automatizadas. Esta entrega no repite el pago desde ZEUS ni acredita operación pública.

La ampliación de perfiles y comunidad pasó 227 pruebas Django, revisión estática, comprobación de migraciones y cuatro controles de concurrencia, incluido el seguimiento simultáneo. Tras los últimos ajustes se repitieron las 35 pruebas de perfiles y comunidad. Se revisaron el directorio, la ficha pública y la edición de alias en navegador con cuentas sintéticas, incluida la ficha en móvil. Las migraciones locales tuvieron respaldo y se comprobó la conservación de las filas anteriores; las adiciones de catálogo observadas durante la revisión corresponden a actividad concurrente y se conservaron. Esta evidencia no acredita uso público ni validación educativa.

### Organización y próximos pasos

La primera entrega de mejoras integrales pasó 238 pruebas Django, revisión estática, consistencia de migraciones y cuatro controles de concurrencia. La migración local tuvo respaldo y conservó todos los valores anteriores de 496 filas. Se comprobaron pantallas de acceso y recursos con datos temporales. Los siguientes recorridos son explorar distintos formatos, continuar desde cualquier entrada y guardar también contenido gratuito; práctica, acompañamiento y operación conservan sus tareas pendientes. Esta verificación técnica no acredita validación educativa con participantes.

Caleb continúa con Business y Dev. El requisito oficial de cuatro integrantes requiere aclaración con CUBO+. Las siguientes tareas son preparar contenido y derechos comprobados, manuales y demostración; ejecutar validación con personas y completar presupuesto, entrega real de correo, instalación de la conciliación como servicio y procedimientos para operación pública. Las membresías permanecen como ampliación pendiente; la comunidad por versión ya permite conversar y moderar con historial. El estado actual se mantiene separado de la bitácora y de los resultados externos todavía inexistentes.

Verificación de correo, preferencias de avisos y solicitudes de revisión de suspensión del creador están implementadas. La entrega real del correo, la atención humana y la validación con participantes siguen pendientes. Respuestas marcadas como solución y apelaciones de moderación comunitaria requieren una ampliación propia.

## A dónde queremos llegar

Queremos que una persona pueda reconocer un objetivo, combinar cursos, tutoriales y recursos, practicar, recibir ayuda y continuar con claridad. La compra debe integrarse cuando necesita contenido de pago. El creador debe preparar, publicar, acompañar y mantener materiales sin perjudicar el acceso existente.

Las evaluaciones y certificados conservan requisitos y resultados por versión. Las preguntas y notificaciones ya permiten acompañar al alumno; los paneles ofrecen indicadores con fuentes y denominadores explícitos. La comunidad por versión incorpora conversación y moderación; las membresías renovadas manualmente quedan como ampliación por desarrollar y verificar.

Necesitamos analítica que explique consulta, pago, uso y regreso sin confundir actividad con aprendizaje. También un presupuesto que considere consumo gratuito, acceso permanente, archivos históricos, correo, respaldos, supervisión y soporte.

La operación pública y una integración con fondos reales requerirán decisiones y evidencias propias. La investigación externa ayuda a identificar condiciones; no acredita que ya estén resueltas.

## Qué demostramos

La evidencia técnica registrada muestra una oferta que genera una factura simulada y una confirmación válida que concede acceso específico. Documenta persistencia, protección y conservación de referencias históricas.

La revisión permite publicar una composición aprobada mientras se preparan cambios posteriores. Las evaluaciones y certificados conservan reglas, intentos y evidencia de finalización por versión. También comprobamos preguntas privadas, avisos persistentes y paneles con datos de prueba; estos resultados técnicos no prueban dominio educativo.

La investigación documenta alternativas de monetización y condiciones externas de costos. Todavía no demuestra preferencia por BTC.EDU, disposición real a pagar, frecuencia de compra o mejora educativa.

## Logros

Definimos unidades de compra, muestras, permisos y responsabilidades de publicación. Conectamos creación, revisión, oferta, compra simulada y aprendizaje, conservando versiones históricas. Incorporamos evaluaciones con resultados persistentes, certificados históricos, acompañamiento por preguntas y avisos, y paneles con consultas verificadas, conservando las compras existentes.

Ampliamos la comparación de modelos y costos, y preparamos instrumentos para entrevistas, usabilidad y precios. Es un avance de investigación documental y preparación, no una validación externa terminada.

Los resultados de mercado y aprendizaje se incorporarán cuando exista evidencia suficiente.

## Próximos pasos

Preparar reclutamiento y consentimiento; ejecutar entrevistas y tareas con la versión identificada; analizar dificultades y objeciones; comprobar los cambios relevantes.

Contrastar rangos de precio con costos y preparar escenarios de sostenibilidad. Preparar la demostración y los manuales de la entrega esencial; completar operación y especificaciones de las ampliaciones pendientes. Extender analítica solo cuando los nuevos eventos tengan reglas y utilidad definidas.

Actualizar el documento con cada entrega, vinculando decisiones y resultados a sus evidencias reales.

## Conclusiones

BTC.EDU propone una plataforma integral que conecta contenido, aprendizaje, acompañamiento y comunidad, con micropagos para acceder a unidades específicas. El desarrollo registrado permite verificar publicación, pago simulado, acceso persistente y módulos educativos asociados a versiones.

La revisión encuentra una base técnica sólida y recorridos todavía centrados en cursos. La siguiente etapa debe conectar formatos, biblioteca, práctica y ayuda, contrastar su utilidad con alumnos y creadores y evaluar calidad educativa, operación y sostenibilidad.

Mantendremos las conclusiones comerciales como provisionales hasta reunir esa evidencia.

## Referencias

Las fuentes externas se enlazan junto a las afirmaciones que sustentan. Los precios y condiciones comerciales se consultaron el 5 de octubre de 2026; deben revisarse antes de contratar o publicar una recomendación final.

La revisión de cuentas consultó documentación primaria de autenticación y accesibilidad el 12 de octubre de 2026. Estas fuentes orientaron el diseño de la gestión de cuentas; las pruebas de implementación y sus límites se registran por separado.

Los documentos originales de CUBO+ definen el reto y la evaluación. La investigación funcional, las decisiones y los registros técnicos del proyecto conservan el detalle y los límites de cada entrega.

La bitácora y los anexos reunirán las evidencias de desarrollo, instrumentos y resultados reales. El enlace al Google Doc y la validación con participantes siguen pendientes de incorporar.
