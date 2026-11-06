# Compra y comercio

Carrito, checkout, pedidos, prevención de compras duplicadas y funciones comerciales añadidas tras comparar plataformas.

<a id="experiencia-comercial"></a>

## Compra y experiencia comercial

### Punto de partida

El 14 de octubre de 2026, después del overhaul, el usuario pidió analizar un carrito para cursos, tutoriales y recursos, un checkout y otras comodidades de negocio. Tras autorizar el desarrollo, implementamos el recorrido en `main`, base `687a773`, conservando los cambios locales de la entrega anterior. Esta sección describe la entrega actual y distingue las ampliaciones pendientes; el análisis original permanece en la bitácora.

La plataforma vende ofertas individuales y conjuntos, muestra inclusiones y precio y conserva acceso por versión. El visitante prepara una selección sin cuenta y la incorpora al entrar como estudiante. La cuenta conserva su carrito, y cada pedido guarda líneas de distintos educadores con una sola factura por el total. Las facturas anteriores mantienen su oferta y sus derechos. Guardados admite cursos, tutoriales, recursos y referencias; las fichas y compras enlazan al perfil público permitido del educador. La ayuda de plataforma conserva el contexto comprobado del pedido o recurso adquirido; las dudas educativas de una lección mantienen su recorrido propio. No hay liquidación al educador.

El objetivo propuesto es ayudar a elegir una compra educativa, pagarla con claridad y recuperar su utilidad. El carrito sirve para reunir varias unidades; comprar una sola debe seguir siendo sencillo. Udemy documenta ambas entradas, carrito y Comprar ahora. [Referencia](https://support.udemy.com/hc/en-us/articles/229233487-Shopping-cart-FAQ).

### Carrito y checkout

| Momento | Comportamiento implementado |
|---|---|
| Elegir | En la ficha, Añadir al carrito y Comprar ahora sobre una opción de acceso explícita. Cuando haya curso, capítulo, lección y material, explicar qué incluye cada opción. Gratis lleva a Empezar; adquirido lleva a Abrir o Continuar. |
| Añadir | Confirmación breve que permita seguir explorando y abrir el carrito; contador accesible en cabecera. Una unidad de acceso personal por producto, sin controles de cantidad. Los enlaces externos y contenidos gratuitos no generan cargos. |
| Revisar | Mostrar título, educador, tipo, alcance, versión, inclusiones, precio por línea y total en sats. Permitir quitar con recuperación y mover a Guardados. El número de productos no equivale al número de lecciones o permisos incluidos. |
| Entrar | El visitante puede preparar el carrito. Al continuar al pago entra o crea su cuenta, con selección y destino conservados. El carrito de la cuenta persiste entre sesiones; el traslado desde visitante debe revisarse sin mezclar identidades de un dispositivo compartido. Para la primera entrega no se propone pago anónimo. |
| Confirmar | Checkout con resumen editable y la cuenta que recibirá el acceso. Pedir únicamente los datos necesarios; contenido digital no requiere dirección de envío. Cualquier cargo propio debe conocerse antes de confirmar. Revalidar precio y disponibilidad; si algo cambió, pedir revisar la nueva selección. |
| Pagar | Un pedido, una solicitud de pago por el total y confirmación del servidor para todos los artículos. Se conservan QR, copia de solicitud y apertura de wallet en el modo correspondiente. El plazo de 15 minutos comienza al reservar la factura después de Preparar pago; explorar, añadir y revisar no inicia ese plazo. |
| Recuperar | Volver a la misma compra pendiente después de cerrar, entrar o perder conexión. Un resultado desconocido requiere consultar el pago original antes de generar otro. Vencimiento, indisponibilidad y pago observado con incidencia deben tener acciones distintas. |
| Aprender | Confirmación con referencia del pedido, líneas adquiridas y enlaces para abrirlas. Comprar ahora conserva la lección elegida; una compra múltiple ofrece cada contenido y Mi aprendizaje. Compras mantiene pendientes, historial, detalle y ayuda contextual. |

El recorrido visual mantiene la identidad actual y las etapas Revisar → Pagar → Aprender. En escritorio, lista y resumen; en móvil, una columna con total y acción localizables, conservando foco, lectura y espacio útil. Añadir al carrito no debe interrumpir la exploración con una página o ventana obligatoria.

Baymard respalda costes claros, selección persistente, recuperación de errores y menor esfuerzo de formulario; también señala que reducir campos importa más que reducir el número de pasos. Su evidencia corresponde a comercio electrónico externo, no a conversiones de BTC.EDU. La propuesta adapta esos principios al acceso educativo ligado a cuenta. Shopify documenta productos digitales sin envío. [Auditoría de checkout](https://baymard.com/blog/audit-checkout-flow-hidden-friction), [campos de formulario](https://baymard.com/research-articles/checkout-flow-average-form-fields), [productos digitales](https://help.shopify.com/en/manual/products/digital-service-product/selling-services-or-digital-products). Fuentes consultadas el 14 de octubre de 2026.

### Evitar compras duplicadas

La compra se valida por contenido y revisión adquiridos, además del identificador de oferta. Añadir dos veces conserva una línea. Lo adquirido ofrece abrir y se excluye del subtotal elegible, con explicación; cualquier conflicto bloquea la confirmación hasta corregir la selección. Si un curso incluye un material ya añadido o dos conjuntos se solapan, se identifican las líneas y el estudiante elige cuál quitar. No se cambia su selección automáticamente ni se inventa un descuento. Las alternativas de contenido faltante y las ofertas reemplazadas se presentan para revisión explícita.

Desde el 23 de octubre de 2026, una compra previa de parte de un capítulo o curso se reconoce como crédito al completarlo. La política implementada es provisional:

- Cuenta lo pagado en compras propias confirmadas cuyo contenido de pago pertenece por completo al paquete, que es una versión concreta. Las líneas de un pedido cuentan por separado y aportan su importe ya descontado.
- Excluye regalos y compras reembolsadas. Un paquete completo no deja crédito pendiente, por lo que el crédito se usa una sola vez.
- El paquete cobra el precio de lista menos el crédito, nunca menos de 1 sat, e incluye solo los componentes que faltan.
- La línea guarda el crédito en la huella del pedido; una compra intermedia del mismo contenido cambia la huella y obliga a revisar antes de pagar.

Si no hay crédito aplicable, por ejemplo cuando lo adquirido llegó como regalo, se mantiene el bloqueo con las alternativas individuales. Si nada necesita pago, se ofrece abrir/continuar; no se emite una factura de cero sats. Con el catálogo de ejemplo, quien compró una lección de 50 sats completa el curso de 120 por 70.

El carrito muestra una selección vigente y puede cambiar; el pedido confirmado congela sus precios e inclusiones. Modificar el carrito después de emitir un pago no cambia esa solicitud. Las líneas nuevas o retiradas permanecen correctamente identificadas después de completar el pedido anterior; no se vacía trabajo posterior del usuario.

### Base del pedido

El pedido conserva líneas por oferta, educador, precio, versión y composición, con una factura por el total y derechos referidos a esa compra. La revisión firmada vincula cuenta, selección, revisión del carrito y precios; un cambio requiere revisar nuevamente antes de reservar. La clave de solicitud reutiliza el mismo pedido ante envíos repetidos, incluso después de editar el carrito. Las facturas antiguas conservan su vínculo con una oferta; las nuevas vinculan un pedido, con exclusión mutua entre ambos destinos.

La implementación usa el receptor de pago de plataforma ya configurado, con registro del importe de cada línea. Esto no distribuye fondos automáticamente ni constituye saldo disponible del educador. Comisión, reparto, liquidaciones, devoluciones y responsabilidad de atención requieren decisiones comerciales antes de operación con fondos reales. Cada educador consulta únicamente sus líneas e importes; el estudiante recibe un resumen común. La ampliación a otros tipos de producto necesita reglas propias.

La confirmación concede todos los derechos del pedido de forma atómica y única, e inscribe las versiones de curso pertinentes sin convertir una compra de archivo en inscripción a todos los cursos que lo adjunten. La reserva compartida de revisiones pagadas impide solapamientos entre pedidos y facturas individuales anteriores. La limpieza del carrito usa los identificadores de las líneas compradas: conserva artículos añadidos, retirados y vueltos a crear mientras se pagaba. Los reintentos de emisión y confirmación reutilizan la operación original y conservan su evidencia.

La revisión de `settle` identificó una limitación: `ProviderStatus` no incluye una hora fiable de pago. Un pago observado después del vencimiento conserva evidencia y queda en revisión, sin conceder derechos ni proponer otro cobro. Los pedidos nuevos registran `payment_time_unknown`; las facturas anteriores conservan su identificador histórico `late_payment`. Emisión desconocida, pago observado e inventario inconsistente mantienen la reserva y ofrecen consultar la misma factura o pedir ayuda. Una respuesta negativa comprobada o un fallo de emisión definitivo permiten revisar una nueva solicitud. Resolver automáticamente pagos tardíos exige evidencia fiable adicional del proveedor; no se promete devolución automática.

La fuente local de LNbits confirma que `Payment.time` nace al crear el registro y `updated_at` cambia con actualizaciones; el estado expuesto por el adaptador LndRest no aporta una fecha fiable de cobro. Estas fechas no resuelven la distinción anterior. La revisión fue de código, sin un nuevo ensayo de pago. Referencias: `src/commerce/services.py`, `src/commerce/gateway.py` y los modelos, CRUD y adaptador de pagos de la instalación local fijada de LNbits.

### Otras comodidades

| Prioridad | Mejora | Propósito y límite |
|---|---|---|
| Con la compra | Ficha educativa y autor enlazado | Reutilizar resultado, requisitos, muestra y materiales; explicar extras y acompañamiento. Abrir el perfil existente del educador. Una cuenta aprobada no acredita credenciales ni revisión pedagógica externa. |
| Con la compra | Historial y ayuda por pedido/recurso | Recuperar acceso, referencia y estado; separar incidencias de pago/acceso de dudas educativas. Mostrar canales y alcance reales, sin prometer atención inmediata. |
| Implementada | Guardados para todos los formatos propios | Cursos y tutoriales por versión se integran con recursos y referencias. Guardar para después no compra ni inscribe. |
| Implementada | Completar conjuntos | Crédito por compras propias dentro del paquete, con las reglas de [evitar compras duplicadas](#evitar-compras-duplicadas). Su comprensión sigue por observar. |
| Próxima ampliación | Descubrimiento por necesidad | Mejorar búsqueda y filtros por tarea, nivel, formato, duración y acceso; indicar su alcance de precio. Probarlos con el catálogo disponible antes de aumentar opciones. |
| Implementada | Escaparate del educador | El perfil existente reúne sus publicaciones con búsqueda, filtros y fichas. Ventas distingue transacciones e importes de sus líneas. Compradores, inscritos y alumnos con evaluación siguen siendo grupos distintos. |
| Implementada | Reseñas verificadas y rutas | Solo opinan quienes compraron o completaron el curso; se muestran base, versión, alias y respuesta del educador, con ocultación administrativa. Las rutas de BTC.EDU y de los educadores ordenan cursos y pueden venderse como paquete con descuento ([rutas de aprendizaje](09-catalogo.md#rutas-de-aprendizaje)). Las recomendaciones personalizadas siguen pendientes; no se generan estrellas, testimonios ni ventas ficticios. |
| Implementada | Cupones y regalos | Cupones del educador con vencimiento, límite de usos y alcance; regalos con enlace de canje de un solo uso. Su necesidad y sostenibilidad siguen por observar. |
| Posterior | Recuperación por correo | Los recordatorios deben respetar preferencias y entrega de correo comprobada. Membresías, otros pagos y cuenta unificada para aprender/enseñar necesitan diseño propio. |

### Avance y verificación

1. Implementado: alcance de productos, solapamientos, reservas y excepciones de pago; carrito, checkout, confirmación e historial dentro de la estética actual. Completar conjuntos usa crédito por compras anteriores desde el 23 de octubre.
2. Implementado: carrito persistente, compra directa, pedido con varias líneas y un pago total, confirmación atómica, recuperación, acceso posterior y ayuda esencial. La compra de varios educadores registra sus propias líneas e importes sin liquidación.
3. Implementado: Guardados ampliado y escaparates con búsqueda y filtros. Pendiente: descubrimiento por tarea, según reglas y pruebas propias.
4. Implementado el 23 de octubre: reseñas verificadas, cupones, regalos, propinas y reembolsos. Pendiente: evaluar su necesidad, operación y sostenibilidad con participantes; los recordatorios dependen del correo.

Ensayar compra única y múltiple, cursos/tutoriales/recursos de varios educadores, gratuito/adquirido, inclusión duplicada, solapamiento parcial, cambio de precio/versión, oferta retirada, cambio de cuenta y traslado de carrito. Comprobar también sesión vencida, doble envío, dos pestañas, pago cercano al vencimiento, respuesta perdida, reintento, confirmación repetida y edición del carrito durante el pago. Conservar compras y progreso históricos. Revisar móvil, teclado, ambos temas, estados vacíos y datos extensos.

Instrumentar incorporación aceptada al carrito, inicio de checkout, pedido/factura creados, confirmación y apertura posterior. Contar pedidos únicos como transacciones; las líneas atribuyen importes al educador, y los permisos registran contenido accesible. Dos líneas del mismo pedido no son dos compras repetidas. Definir denominadores y cohortes; un carrito abandonado no demuestra por sí solo una falla de UX. Observar con participantes elección, comprensión de inclusiones/total, recuperación y acceso; las pruebas técnicas y el pago ficticio no demuestran ingresos ni preferencia comercial.

### Alcance de esta entrega

El carrito admite hasta 20 artículos de acceso personal. Si al entrar la suma supera ese límite, el excedente permanece en la sesión privada de esa cuenta y se incorpora mediante selección explícita; cerrar esa sesión puede perder esa selección excedente. El carrito principal de la cuenta sí persiste entre sesiones. No se realizan compras anónimas ni se añaden cantidades, direcciones de envío o cargos nuevos; las reseñas y promociones llegaron en la ampliación siguiente.

Los eventos internos registran incorporación aceptada, revisión de checkout y creación de factura por línea; los paneles mantienen las definiciones existentes y cuentan pedidos únicos. Estas trazas permiten investigar el recorrido, pero no representan todavía un embudo validado ni tasas de conversión comerciales. Las comprobaciones y el respaldo de la entrega se conservan en la [bitácora comercial](../src/docs/operacion-y-bitacora.md#etapa-comercial-2026-10-14).

<a id="ampliacion-comparativa"></a>

### Ampliación por comparación con otras plataformas

El 23 de octubre de 2026 el usuario compartió una comparación de BTC.EDU con Udemy, Coursera, Platzi, Domestika, Saylor y Mi Primer Bitcoin, y pidió implementar todas las funciones posibles. Las cifras de esas plataformas proceden de ese documento y de sus fuentes secundarias; no las verificamos de nuevo.

| Función | Estado | Decisión principal |
|---|---|---|
| Crédito por compras anteriores | Implementada | Diferencia sobre el precio de lista, mínimo 1 sat, solo con lo que falta |
| Propinas al educador | Implementada | Factura propia de 10 a 100 000 sats; no concede acceso ni se reembolsa |
| Sello OpenTimestamps | Implementada, desactivada por defecto | Prueba `.ots` de la huella; se envía al emitir o con `stamp_certificates` |
| Reembolso por Lightning | Implementada | Ocho días, sin certificado ni crédito posterior; reclamo sin plazo por contenido inaccesible, distinto, defectuoso o cobrado por error; aprobación administrativa y pago a una factura por el importe exacto |
| Regalar | Implementada en Comprar ahora | Enlace de canje de un solo uso; el comprador no recibe acceso |
| Reseñas verificadas | Implementada | Compra de pago o curso completado; una por curso, editable, con respuesta del educador |
| Cupones | Implementada | Del educador, por porcentaje o sats, con vencimiento, límite y alcance |
| Galería de proyectos | Implementada | Prácticas aprobadas con permiso explícito; adjuntos privados |
| Rutas de varios cursos | Implementada | Editoriales y de educadores, pasos opcionales, paquete con descuento y credencial con huella SHA-256 |
| Aplicación instalable y lectura sin conexión | Implementada | Solo lecciones guardadas por el estudiante; se borran al cambiar de cuenta |
| Entrar con Lightning (LNURL-auth) | Pendiente | La wallet debe alcanzar un dominio público con HTTPS; no es demostrable en local |
| Pago por minuto | Pendiente | Necesita medición de reproducción y pagos recurrentes |
| Pagos a educadores | Definida, sin implementar | [Reparto y liquidación](04-producto-y-monetizacion.md#remuneracion-educadores) propuestos el 6 de noviembre |
| Asistente de IA | Pendiente | Costo y proveedor por decidir |
| Inglés | Implementada | Interfaz y fichas del catálogo propio traducidas; cada curso, video y material declara el idioma de su educador; falta revisión por hablantes nativos |
| Pase con créditos | Hipótesis | Contradice la tesis de micropagos del reto |

Los reembolsos revocan solo el acceso que concedía la compra reembolsada: un derecho con otra fuente vigente se conserva y una compra nueva lo restablece. Un pago de reembolso con resultado incierto queda por conciliar sin retirar el acceso. Las propinas aceptan un pago observado tarde porque no conceden acceso. La galería y las reseñas muestran el alias público. Estas decisiones son técnicas y provisionales; plazo de reembolso, uso de cupones y utilidad de reseñas, rutas y lectura sin conexión deben observarse con participantes. [Comprobaciones](../src/docs/operacion-y-bitacora.md#23-de-octubre-de-2026).

<a id="revision-legal-reembolsos"></a>

### Revisión legal de reembolsos

Revisión del 6 de noviembre de 2026 contra el texto de la [Ley de Protección al Consumidor](https://www.defensoria.gob.sv/wp-content/uploads/2019/05/LPC.pdf) publicado por la Defensoría del Consumidor, con reformas hasta 2019. No sustituye la opinión de un abogado, que debe confirmar si existen reformas posteriores antes del piloto con fondos reales.

**Qué dice la ley.** El artículo 13-A reconoce el retracto en los contratos a distancia: el consumidor puede dejar sin efecto la compra durante ocho días, sin justificarla ni pagar penalización, siempre que no haya empezado a usar el bien o a recibir el servicio. Para servicios el plazo cuenta desde la contratación; la comunicación puede hacerse por el mismo medio de la compra y el proveedor debe devolver lo pagado en quince días. El artículo 13-D obliga además a revertir el pago, en quince días desde el reclamo, cuando el servicio no se prestó, no corresponde a lo ofrecido o es defectuoso, o hubo errores de cobro. Los artículos 21-A y 21-B piden publicar la identidad del proveedor y unos términos con las políticas de retracto y reversión, confirmar el pedido y conservar la prueba de la transacción durante diez años. El artículo 17 considera abusivas las cláusulas que limitan derechos del consumidor o imponen medios alternos de solución de controversias en contratos de adhesión, y el artículo 44 califica como infracción muy grave negarse a devolver el dinero tras un retracto o una reversión.

**Cómo queda la política actual.**

| Regla vigente | Valoración | Cambio propuesto |
|---|---|---|
| Plazo de siete días | Más corto que los ocho días legales cuando el contenido no se ha abierto | Ampliado a ocho días el 6 de noviembre |
| Reembolso aunque el estudiante haya usado el contenido, salvo certificado o crédito | Más generoso que la ley; se puede conservar como política comercial | Mantener e informar que es voluntario |
| Bloqueo por certificado o crédito posterior | Coherente: obtener un certificado o reutilizar la compra demuestra uso | Mantener para el retracto, no para reclamos por defecto |
| Sin vía para contenido defectuoso, no disponible o distinto de lo ofrecido | Incumple el artículo 13-D, que no depende del plazo ni del uso | Implementado: Reportar un problema con esta compra, con tipo y motivo, sin los bloqueos anteriores |
| Regalos excluidos | El comprador del regalo también es consumidor | Admitir reembolso del regalo no canjeado dentro del plazo |
| Decisión manual sin plazo | La ley fija quince días | Implementado: la lista y la revisión muestran la fecha límite; falta avisar a administración |
| Pago a una factura Lightning por el importe exacto en sats | Devuelve lo pagado por el mismo medio, sin cargos | Mantener; la plataforma asume la comisión de envío |
| Rechazo con nota obligatoria | Adecuado para no invertir la carga de la prueba | Mantener y conservar la evidencia en la que se apoya |
| Membresías sin reembolso | El retracto también alcanza a una membresía no usada | Reembolsar en ocho días si no se abrió contenido incluido |

**Lo que falta publicar.** Una página de términos y una de reembolsos, enlazadas desde el checkout y la factura, con la identidad y el NIT del proveedor, los medios de reclamo, el plazo legal, la política voluntaria y el efecto en el acceso. El resumen previo y la confirmación del pedido ya existen; la confirmación debe incluir impuestos cuando se definan. Ninguna condición debe imponer arbitraje.

**Efecto para el educador.** El reembolso lo decide la plataforma, que vende al estudiante. Anula la remuneración pendiente de esa venta o crea un ajuste negativo si ya se pagó, según la [liquidación](04-producto-y-monetizacion.md#remuneracion-educadores). El educador recibe un aviso con el motivo, sin datos personales del estudiante.

El importe se devuelve en sats; si el estudiante pagó cuando el bitcoin valía más o menos en dólares, recibe los mismos sats. Esta regla debe constar en la política.

El 6 de noviembre implementamos el plazo de ocho días, el reclamo, la fecha límite de respuesta y los avisos al educador. Siguen pendientes los regalos no canjeados, las membresías no usadas, el aviso a administración y las páginas de términos y reembolsos.
