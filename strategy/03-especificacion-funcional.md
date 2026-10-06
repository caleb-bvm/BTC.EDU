# Especificación funcional

**Referencia vigente de estructura, 2 de octubre de 2026:** [arquitectura y experiencia](10-arquitectura-y-experiencia-btc-edu.md). Incorpora tutoriales y biblioteca de referencias/recursos, selector por tema/nivel, versiones y reglas de disponibilidad. Se conservan AC-01…35. Archivar para descubrimiento no equivale a convertir en borrador ni retirar acceso adquirido; evidencia de pago tardío o solapado se conserva para conciliación aunque no conceda permisos. El diseño no demuestra implementación.

## Plataforma y cuentas

La investigación del 5 de octubre se incorpora en [13](13-monetizacion-precios-y-muestras.md) y [16](16-validacion-con-usuarios.md). Mantiene AC-01…35 y reglas vigentes. Publicidad, tarifas externas o equivalencia USD son investigación/propuestas de prueba, sin introducir funciones ni cambiar ofertas, acceso permanente o proveedor. Auditar cobertura analítica antes de informar resultados del embudo.

El sitio incluye catálogo de cursos y contenidos, páginas de cursos con capítulos y lecciones ordenados, reproductor de video, materiales descargables, cuenta, pago, Mis cursos y compras, y administración. Permite filtrar por formato, tema y contenido gratuito o de pago.

El visitante explora cursos, abre contenidos gratuitos y ve muestras sin cuenta. Para comprar se registra con correo y contraseña. Al iniciar sesión desde otro dispositivo recupera sus compras. La recuperación de contraseña se implementa con un token de un solo uso y correo configurable según el documento 08. La verificación de correo para publicación pública se definirá al configurar el despliegue; las pruebas usan cuentas ficticias.

Los creadores aprobados tienen perfil y panel para crear y gestionar su propio contenido. El administrador revisa las publicaciones. El comprador no puede consultar compras o facturas ajenas ni acceder al panel. Ser administrador no equivale a tener una compra.

## Cursos y compras

Un curso organiza capítulos, lecciones, videos y materiales. Cada recurso tiene formato y condición gratuita o de pago. Los capítulos pueden agrupar varias lecciones y videos. Un video puede venderse individualmente. El usuario no debe comprar un curso para comprar un video individual o un material que se ofrece por separado.

Las ofertas de curso completo o capítulo enumeran los recursos incluidos. Los materiales adicionales pueden quedar fuera y venderse aparte. Las relaciones del catálogo se distinguen de los permisos: estar asociado a un curso no concede acceso por sí mismo.

Cada compra concede permisos permanentes a los recursos incluidos. Una oferta completamente adquirida muestra enlaces para abrir su contenido. Si una oferta de curso o capítulo está parcialmente adquirida, su compra conjunta queda bloqueada y se ofrecen los contenidos faltantes que tengan oferta individual. El catálogo de prueba garantiza esas ofertas. No hay descuentos personalizados.

Los permisos, compras y fechas se conservan en la base de datos. Las versiones publicadas conservan su composición para compras existentes; nuevas versiones y sus condiciones se gestionan según el documento 08.

## Facturas y LNbits

LNbits con FakeWallet genera y verifica pagos internos de prueba. No se transfieren fondos reales. Las claves se usan únicamente en el servidor de la plataforma.

La factura pertenece a una cuenta y una oferta: curso, capítulo, video o material. Guarda una copia del importe y los recursos incluidos. Cambiar el precio no modifica facturas existentes.

Estados: Pending, Paid, Expired y Failed. Nace Pending, vence en 15 minutos y solo puede pasar a un estado terminal. Una cuenta solo mantiene una factura Pending vigente por oferta; solicitar otra devuelve la existente.

El servidor verifica propietario, plazo y pago. La confirmación válida concede acceso automáticamente, en una operación que no puede duplicar compras, permisos ni eventos. El navegador no concede permisos.

Antes de crear y confirmar una factura se comprueba lo ya adquirido. Ante solapamiento por compras concurrentes, la segunda factura falla sin conceder permisos. Esta regla está diseñada para la simulación; una integración real debe resolver los cobros confirmados antes de aplicar bloqueos comerciales.

La demostración permite confirmar, fallar y expirar mediante controles claramente identificados. El vencimiento también se aplica por tiempo. FakeWallet no resuelve por sí sola todos los estados ni la recuperación de pendientes tras reiniciar: se debe implementar y probar en el servicio de pagos de la plataforma.

Un fallo o vencimiento permite reintentar con una nueva factura si la oferta sigue siendo elegible. Un error de conexión permite consultar la misma factura; no se presume fallo ni se crea otra automáticamente.

## Protección de contenido

El servidor verifica permiso antes de entregar textos, videos completos y descargas de pago. No se incluyen en HTML público, datos iniciales ni archivos estáticos accesibles sin autorización. El reproductor obtiene el video a través de una ruta protegida que permite reproducción y solicitudes parciales. Las muestras públicas usan contenido separado. No se promete impedir que un comprador copie lo que ya puede ver.

## Administración

Crear y editar cursos, orden de capítulos y lecciones, textos, videos, archivos, descripciones, muestras, precios y visibilidad. Validar formato y tamaño de archivos. Los archivos de pago se guardan fuera del almacenamiento público.

Ocultar contenido lo retira del catálogo pero conserva el acceso de quienes lo compraron. No se eliminan recursos adquiridos. El panel muestra facturas, cuenta compradora, oferta, importe, estado y fecha; permite filtrar por estado y consultar actividad y métricas. No muestra contraseñas ni claves de LNbits.

## Criterios de aceptación

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

## Fuera de esta primera versión

Bitcoin/Lightning con fondos reales, comisiones y liquidaciones, recomendaciones automáticas, vigilancia de exámenes y descuentos personalizados. Se incluyen creación por usuarios aprobados, progreso, evaluaciones, certificados, comunidad y membresías; ver documento 08. Las renovaciones iniciales se pagan manualmente con facturas simuladas.

## Ampliación de requisitos

El documento [08](08-aprendizaje-creadores-y-membresias.md) forma parte de esta especificación: define progreso, evaluaciones, certificados, roles de creador, publicación, comunidad, membresías y criterios AC-21 a AC-35. El acceso se concede por recurso gratuito, compra permanente o membresía vigente. La inscripción gratuita no concede recursos de pago. Para compras individuales se mantienen los criterios anteriores.


