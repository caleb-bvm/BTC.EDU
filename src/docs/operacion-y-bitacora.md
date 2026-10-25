# Operación y bitácora

## Dónde estoy

Ya tengo una plataforma local que conecta publicación, micropagos y aprendizaje. Puedo preparar contenido como creador, enviarlo a revisión, publicar una versión, ofrecerla en sats y conservar la compra y el avance del estudiante. También incorporé evaluaciones, certificados, preguntas privadas, avisos internos, paneles y conversaciones por curso y lección.

El catálogo local tiene diez cursos y 72 lecciones. Conservo los seis cursos iniciales de Bitcoin y Lightning y añadí cuatro cursos completos de pago en Creación y Tecnología. Los nuevos recorridos enseñan fotografía, edición con Shotcut, desarrollo web y Python, con ejercicios, evaluaciones y proyecto final. La interfaz usa ahora un lenguaje monocromo en blanco y negro con un único acento naranja, en modos claro y oscuro, con un menú principal estable para cada tipo de cuenta y navegación local por tarea.

La entrega de interfaz del 14 de octubre pasó 359 pruebas, las comprobaciones de configuración y migraciones, la revisión estática y cinco controles de concurrencia. También comprobé nueve escenarios del cliente de guardado y el cliente de progreso. Ensayé compra simulada y retorno a la lección, aprendizaje, certificados pendientes, estudio, edición, recuperación de errores y búsqueda con datos temporales. Todavía necesito comprobar la compra desde ZEUS dentro de BTC.EDU y validar la utilidad educativa con participantes. Conservo el detalle en la [entrega del overhaul](#overhaul-ui-ux-2026-10-14).

No he validado la propuesta con participantes ni los precios con compradores. Las pruebas con FakeWallet y Polar/regtest no acreditan cobros con fondos reales. Mantengo el propósito y la investigación en el [informe](../../strategy/19-recomendacion-y-entrega-final.md) y en [investigación y requisitos](../../strategy/investigacion-y-requisitos.md).

Implementé el [plan de mejora para estudiantes y educadores](../../strategy/investigacion-y-requisitos.md#revision-ui-ux). Mi aprendizaje prioriza continuar, la compra conserva la lección de origen y el estudio reúne contenido, preguntas y observaciones pendientes. El editor separa sus tareas y los formularios conservan lo escrito cuando falla el guardado. Registro abajo la entrega, sus pruebas y las capturas; todavía no he medido la facilidad de uso con participantes.

Implementé la [etapa comercial](#etapa-comercial-2026-10-14): carrito de visitante y cuenta, compra directa, revisión del pedido y una factura por el total. Incorporé Guardados para cursos y tutoriales, autores enlazados, escaparates y ayuda contextual. Ventas atribuye a cada educador únicamente sus líneas; todavía no distribuyo ingresos ni calculo liquidaciones. Las facturas anteriores mantienen su oferta y sus derechos.

Estandaricé la [barra lateral](#barra-lateral-2026-10-14): academia y estudio comparten marco y geometría, el menú reúne destinos principales y las opciones de cada tarea quedan junto al contenido. Retiré cuenta y ayuda duplicadas y mantuve el avatar también en móvil. El panel móvil controla el foco y abre durante la lectura enfocada. Una batería completa pasó 441 pruebas y comprobé los ajustes posteriores con las pruebas de cuentas y navegación; el registro distingue cada ejecución.

Añadí colecciones dentro de Guardados y prácticas con entregas privadas, criterios y plazos por versión, adjuntos protegidos y una bandeja de revisión para el educador. Conservo las correcciones y la retroalimentación; la aprobación de estas prácticas no cambia los requisitos actuales del progreso ni de los certificados. [Recorrido y comprobaciones](#colecciones-practicas-2026-10-14).

Después de comparar BTC.EDU con otras plataformas de cursos, añadí crédito para completar un curso pagando la diferencia, cupones, regalos, propinas, reembolsos por Lightning, sello de certificados con OpenTimestamps, reseñas verificadas, galería de proyectos, rutas de varios cursos y lectura sin conexión. Las probé técnicamente; ninguna está validada con participantes. Dejé pendientes la entrada con Lightning, el pago por minuto, las liquidaciones, la IA y otros idiomas. [Registro](#23-de-octubre-de-2026).

<a id="guia-local-anterior"></a>

## Cómo trabajo en local

### Categorías del catálogo

Entro a Cursos, Tutoriales o Recursos y elijo entre seis categorías: Bitcoin y Lightning, Desarrollo de software, Datos e inteligencia artificial, Ciberseguridad, Infraestructura y nube, y Diseño y creación digital. Cada categoría reúne subcategorías; dentro de Bitcoin y Lightning encuentro Fundamentos de Bitcoin, Lightning, Seguridad y autocustodia, Desarrollo Lightning y Nodos y minería. Inicio también muestra las categorías de cursos. Puedo buscar directamente, usar «Ver todos» o acotar por subcategoría. Al abrir una ficha, conservo mi selección al regresar. Los enlaces anteriores por tema siguen funcionando y cada catálogo cuenta únicamente sus propias publicaciones.

Mantengo visibles las categorías aunque tengan cero contenidos. Dentro de una categoría encuentro sus subcategorías con publicaciones y, al elegir una, puedo abrir «Cambiar subcategoría». Si la categoría está vacía, despliego todas sus áreas desde «Ver subcategorías» y veo su estado vacío; no añadí cursos ficticios para llenarlas. El educador elige la subcategoría en un selector agrupado por categoría. Desde administración preparo nombres, identificadores, descripciones e ilustraciones integradas; los conteos respetan el tema publicado y no los cambios del borrador. Lo que todavía no tiene tema queda en «Por descubrir». El [inventario inicial](../../strategy/investigacion-y-requisitos.md#categorias-del-catalogo) recoge las áreas incorporadas.

La búsqueda indica qué catálogo y categoría o subcategoría estoy consultando. Abro «Filtros» solo si necesito acotar más: veo las opciones que aportan una elección sobre el contenido publicado. Puedo retirar la búsqueda o un filtro sin perder la categoría, y «Limpiar filtros» conserva también la subcategoría. El panel comienza cerrado y, al actualizar la lista sin recargar la página, mantiene la apertura y el foco. Uso esta barra en los catálogos, Explorar y Comparar cursos; el perfil público del educador conserva su búsqueda propia. Sus cuatro iconos de búsqueda, filtros, cierre y flecha usan Font Awesome Free integrado localmente; mantengo la flecha centrada y con tamaño fijo en ambos desplegables.

Distribuyo los campos y «Aplicar filtros» en una fila flexible cuando hay espacio; en móvil los campos ocupan todo el ancho. Mantengo el panel plano, con un separador superior fino. Identifico el foco de teclado por un fondo suave y el subrayado de la etiqueta o del texto, conservando el borde habitual del control.

### Cursos de Creación y Tecnología

Ya publiqué dos cursos en Creación y dos en Tecnología. Cada uno tiene cuatro capítulos y doce lecciones de pago, con explicaciones originales, ejemplos resueltos, prácticas y soluciones. Puedo comprar una lección, un capítulo o el curso completo. La ficha muestra primero la oferta del curso y agrupa las opciones por unidad en un desplegable.

Los precios del curso completo son 1800 sats para fotografía, 2400 sats para Shotcut y 3000 sats para web o Python. Son precios editoriales iniciales sin validación comercial; la configuración local de pagos sigue siendo la misma. Las fotografías se sirven desde los archivos locales y sus créditos aparecen en las fichas. Los videos son complementos externos atribuidos; no son archivos propios ni sustituyen las explicaciones.

Para completar un curso necesito marcar sus doce lecciones y aprobar cuatro cuestionarios con nota mínima de 75 %. Cada proyecto incluye instrucciones y cinco criterios para autoevaluación. No prometo tutoría ni corrección personal; mantengo cerrada la recepción hasta asignar atención. El proyecto no condiciona el certificado.

La carga ya está hecha. En otra instalación, desde `src`, uso `.venv/Scripts/python.exe manage.py load_complete_courses --dry-run` para comprobar el inventario y el mismo comando sin `--dry-run` para publicarlo. Creo un respaldo antes de escribir, uso los servicios de envío, revisión y ofertas, y conservo lo existente. Repetir la carga no duplica cursos ni cambia versiones publicadas. Los textos, fuentes y evaluaciones están en `content/course_catalog`; las portadas están en `static/images/courses`.

### Colecciones y prácticas

Organizo lo guardado desde Mi aprendizaje → Guardados. Creo una colección, selecciono «Organizar en colecciones» en cada contenido y marco uno o varios objetivos. Si elimino la colección, sus contenidos siguen guardados.

Preparo una práctica desde Contenido → curso o tutorial → Evaluaciones. Defino lo que pediré, los criterios que comprobaré y mi plazo previsto de respuesta antes de enviar el curso a revisión. La publicación anterior conserva sus reglas. Como estudiante, entro desde la lección o Mi aprendizaje → Prácticas; puedo enviar texto, enlace y un archivo de hasta 10 MB. Una corrección debe incluir la solución completa y volver a adjuntar el archivo que quiera conservar en esa entrega.

Atiendo las soluciones en Alumnos → Entregas, de la más antigua a la más reciente. Veo pendientes y plazos superados, marco criterios cumplidos y explico la aprobación o las correcciones necesarias. Puedo pausar la recepción y continuar revisando lo recibido. Los avisos son internos. Mantengo pendiente comprobar mi capacidad real de atención, definir retención y cuotas de adjuntos e incorporar análisis antivirus antes de una operación pública.

### Arranque

Desde la raíz del proyecto, en PowerShell, inicio la plataforma y LNbits con FakeWallet:

```powershell
./dev.ps1
```

Si solo necesito la plataforma, uso:

```powershell
./dev-platform.ps1
```

Abro Django en `http://127.0.0.1:8000/` y FakeWallet en `http://127.0.0.1:5000/`. Mantengo libres ambos puertos y detengo los procesos con Ctrl+C. La preparación conserva las bases y los archivos de configuración existentes; el primer arranque necesita internet y Git para descargar LNbits.

También puedo preparar e iniciar cada servicio por separado, desde la raíz:

```powershell
./src/scripts/setup-platform.ps1
./src/scripts/start-platform.ps1
./src/scripts/setup-lnbits.ps1
./src/scripts/start-lnbits.ps1
```

Si Windows bloquea los scripts, uso `powershell -ExecutionPolicy Bypass -File .\dev.ps1` o `powershell -ExecutionPolicy Bypass -File .\dev-platform.ps1`. Ese permiso se limita al proceso que estoy iniciando.

Para crear mi cuenta administrativa, ejecuto desde `src`:

```powershell
./.venv/Scripts/python.exe manage.py createsuperuser
```

Los registros de estudiante y creador están separados. Crear una cuenta de creador no la aprueba: reviso su solicitud desde administración. Para usar ambas identidades al mismo tiempo, abro perfiles o navegadores distintos.

<a id="lnbits-local"></a>

### Pagos con FakeWallet

Con LNbits activo, ejecuto desde la raíz:

```powershell
./src/.local/lnbits/.venv/Scripts/python.exe src/scripts/smoke-lnbits.py
./src/.venv/Scripts/python.exe src/scripts/setup-commerce.py
./src/.venv/Scripts/python.exe src/scripts/smoke-commerce.py
```

La primera prueba crea wallets y pagos ficticios en LNbits. La preparación comercial reutiliza las wallets y guarda las credenciales en `src/.local/commerce.env`; la prueba de comercio usa una base temporal de plataforma. Si vence la autenticación administrativa del proveedor, repito la preparación.

Mantengo FakeWallet como fuente de fondos en LNbits. Algunas opciones quedan guardadas en su base, por lo que cambiar `.env` puede no cambiar el proveedor. Sus datos y credenciales permanecen fuera de Git. Todavía tengo pendiente comprobar la recuperación de facturas al reiniciar LNbits durante una transacción.

<a id="lnbits-regtest"></a>

### Pagos con Polar y ZEUS

Para trabajar en regtest, mantengo Docker y la red Polar activos. Desde `src`, inicio la instancia separada:

```powershell
./scripts/start-lnbits-regtest.ps1
```

Uso LNbits en `http://127.0.0.1:5001/`, conectado mediante LndRestWallet al nodo bob en `https://127.0.0.1:8082`. El lanzador comprueba regtest, certificado TLS y macaroon. Puedo revisar la conexión sin iniciar el servicio con `--check-only` y ajustar el nodo con `--endpoint` y `--node-folder`.

Después de configurar el administrador de esa instancia, preparo el comercio desde `src`:

```powershell
./.venv/Scripts/python.exe scripts/setup-commerce-regtest.py
```

El script solicita la contraseña y guarda la clave de recepción en `.local/commerce.env`, sin conservar la contraseña ni asignar una clave de pago al comercio. Respalda la configuración anterior en `.local/commerce-fake.env.backup`. Reinicio Django para aplicar el cambio; `commerce.env` tiene prioridad sobre `.env`.

En este modo uso facturas `lnbcrt` y un QR generado localmente. Conecto ZEUS al nodo alice, comprador. No necesito exponer LNbits al teléfono. Antes de cambiar de proveedor, reviso las facturas pendientes en su entorno original: el cambio no las migra.

### Conciliación

Para revisar un lote de facturas desde `src`, uso:

```powershell
./.venv/Scripts/python.exe manage.py reconcile_payments --limit 100
```

Si necesito mantener la revisión activa, dejo un terminal supervisado:

```powershell
./.venv/Scripts/python.exe manage.py reconcile_payments --watch --interval 30 --limit 100
```

El proceso consulta hasta 100 facturas y espera 30 segundos entre lotes. No realiza pagos ni necesita una página abierta. Reintenta cuando el proveedor no responde y conserva las incidencias de pagos tardíos sin conceder acceso. Puedo detenerlo con Ctrl+C y reanudarlo con el mismo comando.

No se inicia con Django. Al cerrar el terminal deja de revisar; todavía necesito instalar supervisión como servicio, reinicio automático y alertas. En administración reviso las incidencias, porque el número de consultas terminadas no equivale al número de compras aprobadas.

### Comprobaciones y catálogo

Desde la raíz ejecuto el verificador del proyecto:

```powershell
./src/scripts/check-platform.ps1
```

Compruebo pruebas Django, revisión estática, migraciones y los controles de concurrencia incluidos en el script. Anoto el resultado de cada ejecución con su alcance; las cifras históricas de la bitácora no sustituyen una revisión de la versión que voy a presentar.

Desde la raíz también verifico los clientes de guardado y progreso, con Node disponible:

```powershell
node src/scripts/verify-authoring-forms.cjs
node src/scripts/verify-learning-client.mjs
```

Para revisar o cargar el catálogo editorial, ejecuto desde `src`:

```powershell
./.venv/Scripts/python.exe manage.py load_editorial_catalog --dry-run
./.venv/Scripts/python.exe manage.py load_editorial_catalog
./.venv/Scripts/python.exe scripts/verify-editorial-catalog.py
```

La carga crea un respaldo y omite los cursos editoriales que ya existen. No actualiza textos publicados ni compras o progreso. Para cambiar contenido sigo el editor y la revisión editorial. El verificador consulta una copia temporal de la base.

Para ensayar recorridos uso los scripts `preview-academy.py`, `preview-creators.py`, `preview-commerce.py`, `preview-assessments.py`, `preview-regtest.py`, `preview-essential.py`, `preview-community.py`, `preview-learning.py` y `preview-lesson-community.py` de `src/scripts`. Cada uno prepara datos temporales. Los accesos rápidos de estas vistas pertenecen exclusivamente a la demostración y no sustituyen el login de la plataforma.

Para repetir la revisión integral de interfaz uso `preview-overhaul.py` en `src/scripts`. Prepara cuentas sintéticas, una base y archivos temporales, e inicia el puerto 8030. Entro por el formulario normal; las credenciales temporales aparecen al arrancar. El proveedor controlado funciona sin conexión externa y simula la confirmación, sin mover fondos ni modificar la base principal. Al detenerlo se retiran sus datos temporales.

### Funciones de la ampliación

La preparación con FakeWallet guarda ahora `LNBITS_REFUND_KEY`, la clave de pago de la wallet receptora. Sin esa clave no puedo aprobar reembolsos; en regtest no la asigno. Reviso las solicitudes desde Administración → Reembolsos, que enlaza a la página de decisión. Si el pago queda incierto, compruebo la wallet y cierro la solicitud con el hash del pago o la rechazo con una nota.

El sello de certificados está desactivado por defecto porque envía la huella a calendarios públicos. Lo activo con `CERTIFICATE_TIMESTAMPS=true` y, desde `src`, envío los pendientes y actualizo las pruebas con:

```powershell
./.venv/Scripts/python.exe manage.py stamp_certificates --limit 50
```

Creo rutas desde Administración → Rutas de aprendizaje, eligiendo cursos y su orden. Modero reseñas y proyectos de la galería desde Administración con las acciones de ocultar y mostrar.

La aplicación instalable necesita `127.0.0.1`, `localhost` o HTTPS para registrar el service worker. Si cambio `static/js/sw.js`, subo su versión para que los navegadores descarten la copia anterior.

<a id="base-tecnica"></a>
<a id="arquitectura-btc-edu"></a>
<a id="diseno-plataforma"></a>

## Decisiones que mantengo

### Fichas educativas

Ahora preparo resultado, requisitos, actividad, muestra y acompañamiento en cada unidad. Puedo guardar un borrador incompleto, pero debo completar su ficha para enviar o publicar. La revisión y las páginas del alumno conservan la información de la versión publicada. La muestra es pública; el cuerpo y las soluciones mantienen su acceso. Las fichas antiguas siguen vacías hasta que prepare una nueva revisión.

### Enfoque de la plataforma

Decidí orientar BTC.EDU a educación de distintas áreas desde el inicio. Mi catálogo de Bitcoin y Lightning es la primera colección demostrable; todavía no tengo contenido publicado de otras áreas. Busco que cada unidad ayude a resolver una tarea concreta y pueda relacionarse con un recorrido más amplio. No considero la compra individual, los certificados o el pago en sats una ventaja suficiente por sí solos.

Si ya compré parte de un capítulo o curso, lo completo pagando la diferencia. Reconozco lo pagado en compras propias que pertenecen por completo a ese paquete, excluyo regalos y reembolsos y nunca cobro menos de 1 sat. Es una política provisional que debo observar con participantes. Conservo la comparación y el plan de validación en [investigación](../../strategy/investigacion-y-requisitos.md#posicionamiento-y-validacion).

### Base y archivos

Trabajo con Python 3.12, Django 5.2 LTS y SQLite. Fijo las dependencias en `uv.lock` y mantengo separados los entornos de Django y LNbits. Uso plantillas, HTMX y Bootstrap con estilos propios y archivos locales, sin depender de un CDN durante las visitas.

Conservo la base en `src/.local/platform.sqlite3` y los archivos privados en `src/.local/private-media`. Antes de aplicar migraciones respaldo la base y comparo los datos anteriores. Para recuperar contenido completo necesito conservar también los archivos; reemplazar una revisión no me permite borrar los que siguen ligados a compras históricas.

Mantengo `.local`, `.env`, credenciales y respaldos fuera de Git. No publico el directorio privado como una ruta de archivos. Compruebo la autorización antes de entregar textos, videos, subtítulos o descargas. Admito MP4, PDF, TXT UTF-8 y WebVTT, con un límite inicial de 256 MiB por archivo. Estas comprobaciones no sustituyen antivirus, transcodificación ni revisión completa del contenido.

### Publicación y cuentas

Separé las cuentas de estudiante, creador y administración. Puedo usar el mismo correo en espacios distintos, con identidades y recuperación independientes. Mantengo la aprobación de creador separada del registro. El aviso `auth.W004` responde al correo reutilizable entre tipos de cuenta y al backend propio; conservo las pruebas de esa separación.

Al enviar contenido a revisión congelo una copia. Aprobar publica exactamente esa copia; editar después no modifica lo enviado ni una versión anterior. Mantengo revisiones y composiciones históricas para que una publicación nueva no cambie lo que alguien compró o estudió.

### Compra y aprendizaje

Congelo precio e inventario en las líneas del pedido y en su factura total; conservo las facturas individuales anteriores. El vencimiento de 15 minutos empieza al reservar después de Preparar pago, no al explorar. Confirmo desde el servidor y compruebo proveedor, hash, importe, composición y plazo. Una confirmación repetida conserva una sola compra y sus derechos. Ante una respuesta perdida recupero la factura original. Si observo un pago después de vencer sin una hora fiable de cobro, mantengo su evidencia y revisión, bloqueando otro pago del mismo acceso.

Conservo el acceso comprado sobre revisiones concretas. Inscribirse no desbloquea contenido de pago y adquirir un archivo no equivale a comprar todo el curso. Una versión nueva tampoco reemplaza automáticamente las compras, inscripciones o avances anteriores.

Abrir una lección guarda la continuación. Completarla requiere una acción del estudiante y, cuando corresponde, aprobar su evaluación obligatoria. Rechazo guardados obsoletos para no sobrescribir un avance más reciente desde otra sesión. La ficha y la biblioteca comparten la decisión de continuar, repasar o revisar acceso. En Mi aprendizaje, la tarjeta de cada curso tiene un solo enlace al temario en el título y una sola acción principal; muestra el avance con un segmento por lección, hasta 24, y el siguiente paso. Si las lecciones restantes requieren acceso, lo indica con un recuadro discontinuo y la acción lleva a las opciones de acceso.

### Evaluaciones y certificados

Corrijo las evaluaciones en el servidor. Conservo preguntas y reglas por versión, respuestas guardadas, límites de intentos y autorizaciones adicionales con motivo. La selección múltiple exige coincidencia exacta; aprobar no marca automáticamente la lección como completada. Cada respuesta se guarda al elegirla con la misma revisión que protege el intento; si otra sesión guardó antes, pido recargar. Las marcas para revisar quedan solo en el navegador del estudiante.

Emito un certificado por inscripción cuando se cumplen los requisitos publicados y el estudiante confirma su nombre. Mantengo el PDF privado y la compartición voluntaria. Una revocación conserva el historial y bloquea nuevas descargas del PDF.

Uso SHA-256 para comparar los datos de la credencial con la huella guardada. Puedo descargar el JSON y recalcularlo con:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath './certificado-IDENTIFICADOR.json'
```

La huella corresponde a esos datos, no a todos los bytes del PDF. No incorporé una firma digital ni acreditación oficial. Una coincidencia tampoco elimina una revocación.

Cuando activo el sello, guardo una prueba OpenTimestamps del archivo de datos. Con el anclaje en Bitcoin, quien reciba el certificado puede comprobar la fecha con un cliente de OpenTimestamps sin depender de mi base. Solo confío en calendarios conocidos y no consulto direcciones que vengan dentro de una prueba.

### Pagos y complementos

Un regalo no concede acceso a quien paga ni bloquea sus compras; su enlace se canjea una vez. Las propinas no compran contenido, aceptan un pago observado tarde y se registran por educador sin liquidación. Los cupones pertenecen al educador, se aplican después del crédito y cuentan pedidos pagados o pendientes para su límite.

Un reembolso termina solo el acceso que concedía esa compra; conservo la compra, la evidencia y el avance, y una compra nueva restablece el acceso. Limito la solicitud a siete días, sin certificado ni crédito posterior con ese contenido, y pido una factura por el importe exacto. Si el pago queda incierto, mantengo el acceso hasta conciliarlo.

Las reseñas exigen compra de pago o curso completado y muestran el alias. La galería solo muestra prácticas aprobadas que el estudiante decidió compartir, sin adjuntos. Las lecciones guardadas para leer sin conexión pertenecen a una cuenta y se borran al cambiar de cuenta o cerrar sesión.

### Conversaciones y privacidad

Mantengo las preguntas privadas separadas de la comunidad. Para participar en un curso exijo inscripción en esa versión; para una conversación de lección también compruebo acceso a su texto. Buscar, seguir o recibir un aviso no concede permisos nuevos.

Registro motivos y responsables al ocultar mensajes, cerrar conversaciones o suspender escritura. La suspensión conserva lectura, compras y progreso. Los mensajes enviados no se editan ni eliminan desde el recorrido normal; las correcciones se añaden como aclaraciones. Los avisos son internos, sin correo ni un plazo de atención garantizado.

Uso el alias del estudiante en la comunidad y comparto su presentación solo si lo decide. No publico correo, compras, notas, progreso ni preguntas privadas en su ficha. El directorio no verifica identidad ni credenciales docentes.

<a id="componentes-visuales"></a>

### Interfaz y métricas

Uso un lenguaje industrial monocromo: negro, blanco y grises neutros, con el naranja `#FF6A13` solo en la acción principal, el paso actual, un estado vivo y el punto de la marca. Sobre blanco el naranja es relleno con texto negro, nunca texto. Doto, de matriz de puntos, va en la marca, cifras, precios y números de paso; Inter Tight en títulos, lectura y controles; Space Mono en etiquetas. Las tres fuentes se sirven desde `src/static/fonts` con licencia OFL. Los botones son píldoras, las tarjetas tienen 20 px de radio y líneas de 1 px, y el foco es un contorno del color del texto. Los errores conservan su rojo funcional. Presento los precios como cantidad y sats. Explico FakeWallet y regtest durante la documentación o presentación; la interfaz evita banners técnicos y comprueba el pago en silencio, salvo errores que requieren una acción.

En el catálogo y en el perfil del educador, toda la tarjeta lleva a la ficha, salvo el enlace del autor. Muestra el tipo sobre la portada, nivel, lecciones y duración en una línea, y un pie con el precio, el acceso gratuito o, si ya estudio el curso, mi avance con el precio pendiente.

Uso portadas 16:9 en catálogo, ficha, comparación y biblioteca, y miniaturas 1:1 en continuación, estudio y carrito. Preparo como referencia 1600 × 900 y 320 × 320 px. Muestro el original completo con ajuste centrado, sin estirarlo ni recortarlo; si su formato difiere, queda espacio de fondo. Mantengo los SVG actuales y el comportamiento de visibilidad móvil. La carga de portadas por curso sigue pendiente; el [criterio de imágenes](../../strategy/investigacion-y-requisitos.md#imagenes-de-contenido) separa lo implementado de ese trabajo futuro.

El estudiante encuentra Cursos, Tutoriales, Recursos, Mi aprendizaje, Compras y Comunidad; el educador aprobado encuentra Mi estudio, Contenido, Alumnos, Comunidad y Ventas, con los tres catálogos como accesos separados de sus herramientas. Cada catálogo tiene página, título y filtros propios; Comparar cursos está en Cursos. Conservo los enlaces anteriores de Explorar y el regreso a búsquedas filtradas. La barra conserva tamaño y posición para cada pantalla. La cabecera mantiene carrito para visitante y estudiante, avisos y avatar también en móvil; desde la cuenta consulto la ayuda. El contexto queda junto al contenido y las cuentas pendientes o suspendidas muestran sus tareas permitidas. El menú móvil contiene el foco, se cierra con Escape y funciona en lectura enfocada. Entrada, registro y recuperación comparten una cabecera simplificada sin lateral. Esta navegación no sustituye los permisos del servidor.

Los paneles distinguen compras, permisos, inscripciones, finalización e intentos. Conservo numeradores y denominadores y muestro ausencia de datos cuando corresponde. No reconstruyo visitas anteriores ni interpreto aperturas o marcas de progreso como prueba de aprendizaje. La instrumentación de reproducción y muestras sigue pendiente.

## Lo que me falta

Me falta comprobar con participantes si los nombres, la jerarquía y las imágenes de las categorías facilitan encontrar contenido. Incorporar Tecnología y Creación organiza la futura publicación, pero todavía necesito preparar y revisar contenido para esas áreas y contrastar su demanda. Por ahora uso ilustraciones integradas; la carga de portadas personalizadas sigue pendiente.

Necesito observar con participantes el carrito, checkout y recuperación implementados, y si el crédito para completar un conjunto se entiende. Conservé la compra de una unidad y separé pedido, factura, líneas y derechos, con reservas para evitar solapamientos. Los reembolsos con aprobación administrativa ya funcionan, pero su plazo y condiciones necesitan revisión legal; la remuneración y la liquidación siguen pendientes. Resolver automáticamente un pago observado tarde necesita evidencia fiable adicional del proveedor.

Dejé fuera de esta etapa la entrada con Lightning, porque la wallet debe alcanzar un dominio público con HTTPS, el pago por minuto, la liquidación automática a educadores, el asistente de IA, otros idiomas y el pase con créditos. Todavía no ensayé el sello contra calendarios reales, los reembolsos con una wallet ni la instalación en un teléfono.

Necesito observar tareas sobre la interfaz ya implementada con estudiantes y educadores nuevos, medir ayuda, errores y finalización, y contrastar los hallazgos con el diagnóstico anterior. Completaré la revisión de accesibilidad con tecnologías de asistencia. La comprobación técnica y visual no permite afirmar todavía que el rediseño sea intuitivo para todo el público.

Necesito preparar pequeñas colecciones en otras áreas con revisión especializada, comprobar si las unidades aportan frente a alternativas gratuitas y observar la comprensión del pago con personas que tengan distinta experiencia. También debo evaluar el nombre BTC.EDU, el paso de una unidad a un conjunto y un presupuesto que cubra remuneración, revisión, entrega y soporte. Las comisiones, liquidaciones y alianzas siguen sin definir o ejecutar.

Necesito ensayar el recorrido de creador y estudiante sobre la base comprobada, incluida la compra desde ZEUS y el acceso posterior. También debo revisar el catálogo con una persona experta, ampliar las evaluaciones y comprobar comprensión y duración con alumnos. Los precios de 120 sats por curso y 50 sats por lección siguen siendo hipótesis. Repetiré la revisión integrada al incorporar nuevas entregas.

Antes de abrir al público necesito correo con entrega comprobada, límites de abuso, despliegue con HTTPS, respaldo y restauración ensayados, supervisión de pagos y atención de incidencias. Debo definir responsables de revisión y moderación, conservación de datos y presupuesto de almacenamiento y transferencia. Las pruebas locales de concurrencia no miden capacidad para tráfico público y las revisiones visuales no constituyen una auditoría completa de accesibilidad.

Mantengo como ampliaciones pendientes las membresías, corrección de credenciales, eventos educativos y reproducción más detallada. También quedan mejoras del editor, cuotas, tratamiento de archivos huérfanos y producción audiovisual. Tengo instrumentos de validación preparados, pero no sesiones ejecutadas ni resultados comerciales o educativos que pueda atribuirles.

## Bitácora

### 1 de octubre de 2026

<a id="verificacion-2026-10-01"></a>
<a id="contenido"></a>

Preparé los entornos de Django y LNbits y la primera interfaz de BTC.EDU. Comprobé cuentas, sesiones, CSRF, administración y filtros. Pasaron siete pruebas iniciales; al incorporar la base de cursos, capítulos, lecciones y fichas de recursos, pasaron 17. Verifiqué por separado una factura ficticia de 100 sats, de pendiente a pagada, mediante la API de LNbits.

Probé la preparación para MySQL, pero el servidor disponible era MariaDB 10.4.32 y no resultaba compatible con Django 5.2. Decidí volver a SQLite, conservé la base y retiré la configuración de MySQL. Repetí las siete pruebas de la base después de ese cambio.

Incorporé NType82, Space Mono y Ndot77 desde los archivos locales y revisé la portada en escritorio y móvil. La licencia para distribución web de esas fuentes quedó pendiente de comprobar. Conservé el concepto aprobado y las [capturas de escritorio](evidence/portada-fuentes-escritorio.jpg) y [móvil](evidence/portada-fuentes-movil.jpg). LNbits quedó fijado al commit `9349da153c223b008f7d80453b53a54e09c8ed3d` de la versión 1.6.2.

### 2 de octubre de 2026

<a id="recorrido-aprendizaje-2026-10-02"></a>
<a id="interfaz-academia-2026-10-02"></a>
<a id="contenido-versiones-y-archivos-2026-10-02"></a>

Conecté catálogo, ficha y lector a los contenidos publicados; esa etapa pasó 24 pruebas. Definí cursos, tutoriales y recursos como estructura de la academia y dejé los eventos educativos para después. Incorporé selector, filtros, navegación móvil y estética industrial; la revisión de interfaz pasó 32 pruebas.

Después implementé versiones selladas, revisiones reutilizables y archivos privados. Pasaron 54 pruebas, incluidas autorización, inmutabilidad, publicación, descargas y rangos de video. Revisé reproducción, subtítulos y transcripción en una base temporal y respaldé la base principal antes de migrar, sin cargar ejemplos allí. Conservé las capturas de [lectura](evidence/leccion-archivos-versionados-movil.jpg), [video](evidence/video-protegido-movil.jpg) y [selector](evidence/academia-selector-movil.jpg).

### 3 de octubre de 2026

<a id="estudio-creadores-2026-10-03"></a>
<a id="cuentas-independientes-2026-10-03"></a>

Implementé solicitud y aprobación de creadores, estudio, edición de contenido, archivos propios, vista previa y revisión editorial. Comprobé que editar un borrador después del envío no alteraba la copia revisada. Pasaron 77 pruebas.

Separé registro, acceso, perfil y recuperación de estudiante y creador. Pasaron 96 pruebas, con comprobaciones de identidades que usan el mismo correo, aislamiento de permisos y conservación de datos al migrar. No comprobé entrega de correo real. Ensayé el estudio y la revisión con datos temporales; conservé el [panel del creador](evidence/creador-panel-escritorio.jpg), la [publicación revisada](evidence/creador-revision-movil.jpg) y el [acceso móvil](evidence/login-creador-movil.jpg). El conjunto quedó guardado el 4 de octubre en `8792c98`.

### 4 de octubre de 2026

<a id="comercio-y-aprendizaje-2026-10-04"></a>
<a id="experiencia-compra-2026-10-04"></a>

Cerré el recorrido de publicación, oferta, compra simulada, biblioteca y aprendizaje. Implementé precio e inventario congelados, recuperación de emisión incierta, derechos históricos y progreso con control de revisiones. Guardé comercio en `1e470de` y continuidad en `aa70fca`.

Pasaron 129 pruebas y el control de concurrencia con conexiones SQLite independientes. La integración contra FakeWallet comprobó compra única, derechos y recuperación de una respuesta perdida. Apliqué las migraciones con respaldo y conservé los registros anteriores.

Pulí el recorrido de compra y sus mensajes de preparación, procesamiento y confirmación en `d36b152`. Pasaron 60 pruebas relacionadas y repetí el ensayo de compra en navegador, sin repetir toda la batería de 129. Conservé la [biblioteca](evidence/biblioteca-compras-escritorio.jpg) y la [confirmación móvil](evidence/checkout-confirmado-movil.jpg). La indicación de saldo de prueba que usé entonces fue retirada del criterio actual de interfaz.

### 5 de octubre de 2026

Revisé referencias de monetización, costos e instrumentos para validar la propuesta. Dejé esa investigación en [costos y precios](../../strategy/investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras) y [validación con usuarios](../../strategy/investigacion-y-requisitos.md#16-validacion-con-usuarios). No ejecuté entrevistas ni incorporé proveedores o precios validados por esa revisión.

### 7 de octubre de 2026

<a id="evaluaciones-2026-10-07"></a>

Implementé evaluaciones por versión con selección única y múltiple, guardado y retoma, corrección en servidor, límites, espera y autorización de otro intento. Pasaron 148 pruebas y el control de concurrencia de evaluaciones. Apliqué la migración con respaldo y conservé las filas anteriores de 35 tablas. Ensayé el recorrido mediante un puente al cliente Django; la conexión HTTP directa no pudo comprobarse en esa revisión. Conservé el [intento guardado](evidence/evaluacion-intento-movil.png) y el [resultado aprobado](evidence/evaluacion-aprobada-movil.png).

En `codex/evaluaciones-versionadas` comprobé por REST y TLS que bob funcionaba en regtest y tenía un canal activo. Dejé registrada mi confirmación de conexión de ZEUS a alice y de un pago de prueba a LNbits, sin captura de ese pago. Ese reporte no acredita una compra dentro de BTC.EDU.

La integración regtest pasó 151 pruebas. Emití una factura de 100 sats y la comprobé pendiente; no la pagué. En la vista temporal revisé checkout, consulta y QR con sus permisos. Quedó pendiente pagar la factura del checkout desde ZEUS y verificar compra y acceso.

### 10 de octubre de 2026

<a id="esenciales-2026-10-10"></a>

Incorporé certificados, preguntas privadas, avisos internos y paneles en `bb3745c`. Pasaron 179 pruebas y tres controles de concurrencia. Revisé formularios por HTTP, compartición del certificado y PDF en escritorio y móvil. La migración conservó 211 filas anteriores de 40 tablas. Guardé la salida de comprobación, el [PDF](evidence/certificado-pdf.png) y la [respuesta a una pregunta](evidence/pregunta-respuesta-http.png).

<a id="certificados-sha256-2026-10-10"></a>

Añadí la huella SHA-256, comparación web y exportación reproducible. Pasaron 184 pruebas y recalculé el JSON descargado con Node, con el mismo resultado. La migración conservó 258 registros anteriores de 50 tablas. Mantuve explícitos los límites de la huella y la revocación. Conservé la comprobación y la [verificación web](evidence/certificado-sha256-verificacion.png).

<a id="conciliacion-2026-10-10"></a>

Añadí conciliación periódica con lotes rotativos, reintentos y parada con Ctrl+C. Pasaron 192 pruebas y tres controles de concurrencia, sin migración nueva. No repetí pagos contra LNbits o ZEUS en esta ampliación. Conservé la salida.

<a id="comunidad-2026-10-10"></a>

Implementé comunidad por versión, respuestas, reportes y moderación con motivo e historial en `3a465c3`. Pasaron 210 pruebas y cuatro controles de concurrencia. Revisé participación de alumno en Chrome y móvil; el recorrido completo de moderación quedó comprobado mediante pruebas Django. Conservé la comprobación y la [migración](evidence/comunidad-migracion-2026-10-10.txt).

En esa migración, las 47 tablas previas de negocio comparadas estaban vacías. No uso ese resultado para afirmar que seguían presentes los 211 registros de la entrega anterior. Cada respaldo y comparación corresponde a la base observada en su ejecución.

### 12 de octubre de 2026

Trabajé en `main`, sobre la base Git `4000ed5`, con cambios locales y concurrentes. Los registros de estas entregas no tenían un commit propio al redactarse.

<a id="catalogo-editorial-2026-10-12"></a>

Publiqué seis cursos, con dos capítulos y cuatro lecciones cada uno: Bitcoin desde cero, Wallets y autocustodia, Lightning desde cero, Facturas Lightning, LNbits y Contenido con micropagos. Los tres primeros son gratuitos; los otros tienen una lección gratuita y tres de pago, con ofertas iniciales de 120 sats por curso y 50 sats por lección. Dejé 15 lecciones gratuitas, nueve pagadas y doce ofertas activas.

Incluí explicación, ejemplo, práctica y solución, una pregunta final obligatoria por curso y requisitos de certificado. Preparé tres intentos y nota mínima de 100 para esa pregunta; una sola pregunta no demuestra dominio del curso. No cargué videos ni emití certificados. Las duraciones estimadas de 60 a 90 minutos no se midieron con alumnos.

Comprobé carga sin duplicados, catálogo, fichas y bloqueo de las nueve lecciones pagadas en una copia temporal. La identidad técnica de revisión terminó inactiva y sin permisos; no considero esa carga una revisión educativa independiente. No repetí compras ni emisión de certificados con este catálogo. Para el contenido consulté la [guía Bitcoin](https://developer.bitcoin.org/devguide/), [BOLT](https://github.com/lightning/bolts), [BOLT 11](https://github.com/lightning/bolts/blob/master/11-payment-encoding.md) y la [guía de LNbits](https://docs.lnbits.org/).

<a id="perfiles-y-comunidad-2026-10-12"></a>

Añadí alias, presentación voluntaria, directorio Personas, búsqueda en conversaciones y respuestas visibles, filtros y seguimiento con avisos. Pasaron 227 pruebas y cuatro controles de concurrencia; después de los últimos ajustes repetí 35 pruebas de perfiles y comunidad. Revisé directorio, perfil móvil y edición de alias en navegador con datos temporales. Las migraciones conservaron los valores anteriores de las 246 filas presentes en su respaldo; mantuve separadas las adiciones de catálogo concurrentes.

<a id="comunidad-en-lecciones-2026-10-12"></a>

Integré comentarios y respuestas al final de la lección, conservando inscripción, acceso al texto y preguntas privadas. Tras una comprobación aislada, repetí 57 pruebas en el espacio compartido y todas pasaron, junto con migraciones y concurrencia comunitaria. La migración conservó 227 registros previos de 52 tablas, sin insertar comentarios de ejemplo. Conservé la [comprobación](evidence/comunidad-lecciones-check-2026-10-12.txt), la [vista móvil](evidence/comunidad-leccion-movil.jpg) y la [respuesta del creador](evidence/comunidad-leccion-creador.jpg).

La primera revisión general de esa entrega ejecutó 262 pruebas y detectó una aserción desactualizada y un error de dependencia de migración. Corregí la dependencia y comprobé ambos recorridos en las pruebas enfocadas. Los cambios paralelos de cuentas impidieron dar por aprobada la revisión general compartida.

<a id="experiencia-aprendizaje-2026-10-12"></a>

Unifiqué continuación entre ficha y biblioteca, añadí estados al temario, prácticas y soluciones desplegables, lectura enfocada y filtros de aprendizaje. Pasaron 39 pruebas enfocadas, cuatro controles de concurrencia y la comprobación del cliente. Revisé finalización, porcentaje, siguiente lección, soluciones y navegación en una base temporal. Conservé la [ficha](evidence/aprendizaje-curso-2026-10-12.jpg), la [biblioteca](evidence/aprendizaje-biblioteca-2026-10-12.jpg) y el [lector móvil](evidence/aprendizaje-lectura-movil-2026-10-12.jpg).

La última revisión conjunta de esta tarea ejecutó 271 pruebas y registró cinco fallos y un error en cuentas y creadores. También había trabajo concurrente en Guardados cuya migración estaba pendiente. No considero ese conjunto aprobado. Apliqué las migraciones disponibles con respaldo y sin reducción de filas en las 54 tablas anteriores.

Corregí además una regla heredada que estiraba los marcadores del temario. Comprobé su proporción circular en curso y lector, en escritorio y móvil. Conservé la [captura de la corrección](evidence/marcadores-circulares-2026-10-12.jpg). La navegación contextual pasó siete pruebas aisladas; una revisión ampliada quedó bloqueada por un campo de cuentas sin migración en ese momento.

<a id="experiencia-evaluaciones-2026-10-12"></a>

Reorganicé preparación, pregunta por pantalla, opciones amplias, avance y revisión antes de entregar. Separé resultado y repaso y plegué las preguntas del editor. Conservé el formulario completo sin JavaScript y las reglas del servidor. Pasaron 29 pruebas enfocadas; tras los últimos ajustes repetí las 19 de evaluaciones. Ensayé por HTTP guardado, retoma, notas de 50 y 100, edición y autorización adicional, con datos temporales. Conservé la [revisión previa](evidence/evaluaciones-revision-escritorio-2026-10-12.jpg), el [resultado móvil](evidence/evaluaciones-resultado-movil-2026-10-12.jpg) y el [editor](evidence/evaluaciones-editor-2026-10-12.jpg).

Para orientar los cambios de aprendizaje y evaluaciones consulté [NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/), [W3C](https://www.w3.org/WAI/tutorials/page-structure/), [Udemy](https://support.udemy.com/hc/en-us/articles/229607188-How-to-Mark-or-Unmark-Lectures-as-Complete-on-a-Browser), [LatitudeLearning](https://www.latitudelearning.com/ai-lms/portfolio/assessment-student-user-interface/), [GOV.UK](https://design-system.service.gov.uk/patterns/question-pages/) y [Duolingo](https://blog.duolingo.com/core-tabs-redesign/). Las usé como referencias de diseño; todavía necesito comprobar el resultado con participantes.

<a id="modo-oscuro-2026-10-12"></a>

Añadí modo claro y oscuro según la preferencia del sistema, con elección guardada en el navegador. Comprobé alternancia, persistencia, navegación y catálogo móvil. Sin JavaScript mantengo el modo claro; la elección no se sincroniza con la cuenta y Django admin conserva su apariencia. No hice una auditoría completa de accesibilidad ni revisé todos los recorridos autenticados.

### 13 de octubre de 2026

Consolidé la documentación y después decidí mantener solo lo esencial en los Markdown existentes. Reescribí esta bitácora en primera persona, separé operación y estado actual del historial y eliminé repeticiones, país y horas de los registros. Conservé las fechas, referencias de versión y evidencias de cada entrega. Esta revisión documental no añade una ejecución de pruebas ni cierra los pendientes técnicos o de validación.

Después revisé la propuesta, los dos originales de CUBO+ y documentación oficial de competidores. Trabajé en `main`, sobre `2d318f6`, con cambios locales anteriores en esta bitácora, AGENTS.md y la ubicación de la captura de modo oscuro. Confirmé educación de distintas áreas desde el inicio y dejé la diferenciación, las brechas y las pruebas propuestas en los documentos existentes. Comprobé por lectura de código el bloqueo de compra parcial y documenté el ejemplo de 150 sats por lecciones frente a 120 por curso. No cambié código, catálogo, precios ni reglas de compra; no ejecuté pruebas de aplicación, sesiones con usuarios o cobros. Esta revisión no tiene un commit propio al redactarse.

Revisé después los ejercicios del catálogo editorial y concreté un primer ciclo propuesto con tres unidades en áreas distintas. Identifiqué diagramas, matrices y guiones como resultados actuales de diseño, separados de la ejecución de un laboratorio. Dejé criterios de unidad, entregas y condiciones para avanzar en la [investigación](../../strategy/investigacion-y-requisitos.md#primer-ciclo-de-enfoque). Esta preparación no publica nuevas unidades ni añade revisión experta o sesiones realizadas.

Convertí ese enfoque en una [especificación técnica](../../strategy/investigacion-y-requisitos.md#desarrollo-del-enfoque) de fichas versionadas, prácticas, descubrimiento y reconocimiento de compras previas. Después ejecuté la revisión completa sobre la base existente: pasaron 310 pruebas, configuración sin errores, migraciones sin cambios pendientes, revisión estática y cinco controles de concurrencia. Conservé la salida. La advertencia `auth.W004` mantiene el motivo ya documentado. No modifiqué código, no apliqué migraciones a la base principal y no repetí navegador, LNbits o ZEUS. Las funciones de la especificación siguen propuestas, sin un commit propio para esta revisión documental.

Implementé las fichas educativas en lecciones, videos y materiales, con datos conservados por revisión y muestra separada del contenido protegido. Pasaron 319 pruebas y cinco controles de concurrencia; después de los últimos ajustes repetí 32 pruebas de fichas y creadores. Apliqué la migración con respaldo y comprobé los valores de las 616 filas anteriores en 64 tablas. Conservé la revisión, la [migración](evidence/fichas-unidad-migracion-2026-10-13.txt) y las capturas de [escritorio](evidence/ficha-unidad-escritorio-2026-10-13.png) y [móvil](evidence/ficha-unidad-movil-2026-10-13.png). Ensayé guardado, bloqueo de envío incompleto y envío completo con datos temporales. El catálogo publicado y sus compras se conservaron; faltan sus nuevas fichas, unidades de otras áreas, prácticas registradas y compra del contenido faltante de conjuntos. Trabajé en `main` sobre `2d318f6`, sin commit propio de esta entrega ni un nuevo ensayo de pago desde ZEUS.

### 14 de octubre de 2026

<a id="revision-ui-ux-2026-10-14"></a>

Revisé la interfaz en `main`, sobre `687a773`, con el repositorio limpio al comenzar. Consulté los dos originales de CUBO+, navegación, plantillas, formularios y reglas de acceso, compra y publicación. Observé portada, catálogo, ficha, acceso con retorno al curso, Mi aprendizaje, lector y menú móvil; también portal de educadores, estudio, editor y requisitos de certificado. Usé las bases y cuentas sintéticas de `preview-learning.py` y `preview-creators.py`. Los recorridos restantes se revisaron en código, sin atribuirles un ensayo completo en navegador.

Identifiqué 16 puntos de mejora y preparé el [plan integral](../../strategy/investigacion-y-requisitos.md#revision-ui-ux): navegación estable, acciones principales, continuidad de acceso y aprendizaje, editor por tareas y acompañamiento. Conservé la identidad visual y las reglas por versión. Consulté fuentes de NN/g, W3C, Moodle, edX, Teachable y GOV.UK, enlazadas en el plan. Actualicé el informe, la investigación y esta bitácora; las mejoras de interfaz siguen propuestas y esta revisión no tiene commit propio.

Conservé evidencia de la interfaz actual con datos temporales:

- [Mi aprendizaje en escritorio](evidence/ux-aprendizaje-escritorio-2026-10-14.png), [lector móvil](evidence/ux-lector-movil-2026-10-14.png) y [menú móvil](evidence/ux-menu-movil-2026-10-14.png).
- [Estudio](evidence/ux-estudio-escritorio-2026-10-14.png), [editor](evidence/ux-editor-escritorio-2026-10-14.png) y [contexto al configurar certificado](evidence/ux-contexto-certificado-2026-10-14.png).

No cambié la interfaz ni repetí la batería técnica. No ejecuté nuevos pagos ni sesiones con participantes; las migraciones de las vistas temporales sirven para preparar la observación, no acreditan una entrega de desarrollo. Me falta construir el prototipo, medir la situación actual, comprobar accesibilidad y observar tareas antes de afirmar una mejora de usabilidad.

Generé después una [propuesta visual](../design/btc-edu-ui-ux-propuesta-2026-10-14-v2.png) con ImageGen integrado: Mi aprendizaje, Mi estudio y una vista móvil, conservando la identidad. Afiné el siguiente paso del educador para vincularlo a un borrador concreto. Guardé la imagen y los [prompts utilizados](../design/btc-edu-ui-ux-propuesta-2026-10-14.json). Los datos son ilustrativos; la imagen no modifica la aplicación ni sustituye un prototipo funcional o sesiones de uso.

<a id="overhaul-ui-ux-2026-10-14"></a>

Con la autorización del usuario implementé la actualización integral sobre `main`, base `687a773`, sin cambiar de rama ni crear un commit. Cubrí los 16 hallazgos del diagnóstico: menú estable, avisos globales, Explorar y comparación explícita, continuación prioritaria, biblioteca por secciones, ofertas pertinentes y regreso a la lección tras el pago. El lector agrupa materiales y distingue conversación privada y compartida; los certificados enlazan pendientes y el resultado de evaluación permite volver a completar la lección.

Reorganicé Mi estudio, Contenido y el editor por tareas, con requisitos de publicación enlazados, archivo cargado desde su recurso, ordenación por botones, acceso y precio contextualizados y separación de publicación, borrador y envío. Unifiqué el contador de preguntas con la última actividad y añadí filtros y resultados agrupados. La vista del estudiante y la prueba de evaluación no registran progreso ni intentos. Mantuve las reglas de acceso, aprobación y conservación por versión.

Ajusté el marco visual al concepto aprobado: fondo cálido, espacio entre tareas, bordes finos, imágenes geométricas y naranja de progreso y selección. Conservé la marca Ndot y Space Mono; cambié lectura y controles a Arial/Helvetica sin serifas después de comprobar que los archivos NType82 renderizaban con serifas y se alejaban del concepto. Conservo los archivos originales. No cambié precios ni añadí mensajes técnicos al recorrido del producto.

Las revisiones iniciales detectaron regresiones de retorno después de un error de registro, selección de curso fuera de filtros y dependencias de migraciones. También corregí la pérdida posible de una edición posterior al envío y la falsa confirmación al autorizar un intento con datos inválidos. Los formularios congelan controles durante el envío, conservan valores ante errores de validación, red y sesión y enlazan el campo pendiente. La revisión final corrigió etiquetas repetidas y el regreso desde una búsqueda vacía para mantener Recursos.

Pasaron 359 pruebas Django, configuración, consistencia de migraciones, Ruff y cinco controles de concurrencia. Conservo la revisión integrada final. Después de los últimos ajustes de navegación y plantillas repetí 29 pruebas de descubrimiento, navegación y autoría, con [resultado correcto](evidence/overhaul-ajustes-finales-2026-10-14.txt), y Ruff. Pasaron nueve escenarios del cliente de guardado, registrados en la [evidencia de formularios](evidence/overhaul-formularios-2026-10-14.json), el verificador de progreso y la comprobación de sintaxis de los cinco clientes modificados. La advertencia conocida `auth.W004` conserva el motivo y las pruebas de cuentas independientes. Los registros previos de revisión fallida o interrumpida no se presentan como ejecuciones correctas.

Apliqué `commerce.0003_invoice_return_lesson` con `migrate-overhaul.py`, después de ensayarla en una copia. El respaldo quedó en `.local/backups/overhaul-20261014T151738Z-5164f3543a/before.sqlite3`, con `verification.json` en el mismo directorio. Comparé las huellas de todas las columnas y filas anteriores de 65 tablas; se conservaron. Solo añadí el destino nullable, su relación e índice y el registro de migración. Las facturas históricas mantienen ese destino vacío; las comprobaciones de integridad y claves foráneas pasaron. El segundo control confirmó la migración aplicada sin más cambios. Conservo la [salida de la migración](evidence/overhaul-migracion-2026-10-14.txt); no cargué ejemplos en la base principal.

En navegador, con `preview-overhaul.py` y cuentas sintéticas, ensayé acceso, continuación, factura pendiente y confirmación simulada que abre la lección elegida, requisitos de certificado, pendientes de revisión y preguntas, error de título que conserva la descripción, enfoque del campo y guardado corregido. Comprobé búsqueda sin resultados y recuperación de Recursos, temas claro/oscuro y menú móvil con cierre por Escape y retorno del foco. Las pantallas comprobadas con viewport de 320 px no desbordaron el documento; sus pestañas conservan desplazamiento local. No observé errores de consola en la revisión final.

Conservé capturas de la aplicación:

- [Mi aprendizaje en escritorio](evidence/overhaul-aprendizaje-escritorio-2026-10-14.png) y [móvil](evidence/overhaul-aprendizaje-movil-2026-10-14.png), [lector móvil](evidence/overhaul-lector-movil-2026-10-14.png) y [compra confirmada](evidence/overhaul-compra-confirmada-2026-10-14.png).
- [Mi estudio](evidence/overhaul-estudio-escritorio-2026-10-14.png), [publicación](evidence/overhaul-publicacion-escritorio-2026-10-14.png), [editor oscuro](evidence/overhaul-editor-oscuro-2026-10-14.png) y [error recuperable del formulario](evidence/overhaul-formulario-error-2026-10-14.png).
- [Pendientes del certificado en móvil](evidence/overhaul-certificado-movil-2026-10-14.png).

Actualicé los tres documentos principales con el estado entregado y cerré los entornos temporales de revisión. No repetí pagos mediante LNbits o ZEUS ni moví fondos. La entrega tiene comprobación técnica y visual; faltan sesiones con estudiantes y educadores nuevos, revisión educativa y una auditoría completa de accesibilidad para medir comprensión y detectar dificultades adicionales.

<a id="analisis-comercial-2026-10-14"></a>

Después analicé la petición de carrito para cursos, tutoriales y recursos, checkout y nuevas comodidades de negocio. Trabajé en `main`, sobre `687a773`, conservando el overhaul local sin commit. Revisé ofertas, facturas, derechos, guardados, perfiles, acompañamiento y analítica, y consulté las fuentes de Udemy, Baymard y Shopify enlazadas en el [plan comercial](../../strategy/investigacion-y-requisitos.md#experiencia-comercial).

Propuse preparar el carrito sin cuenta, mantener Comprar ahora, usar un pedido con varias líneas y un pago total y conectar confirmación, Compras y Mi aprendizaje. Identifiqué la necesidad de detectar duplicados y solapamientos, definir cómo reconocer compras previas y registrar importes por educador sin prometer liquidación. Añadí prioridades para fichas y autor enlazado, Guardados ampliado, ayuda por pedido/recurso, descubrimiento y escaparates. Dejé opiniones, promociones, regalos y recordatorios para etapas con reglas y necesidad comprobadas.

Revisé también la distinción entre hora de cobro y hora de consulta al vencer una factura. La fuente local de LNbits no aporta una fecha efectiva fiable en el adaptador actual; `time` registra creación y `updated_at` otras actualizaciones. Dejé ese caso como requisito de conciliación y recuperación, sin cambiar la política actual ni presentar una corrección implementada.

Actualicé únicamente los tres documentos principales y distinguí propuesta de desarrollo. No cambié código, migraciones, datos, precios ni reglas comerciales, ni repetí pruebas de aplicación, pagos o sesiones con participantes. Las fuentes externas ayudan a diseñar, sin demostrar conversión, demanda o ingresos de BTC.EDU.

<a id="etapa-comercial-2026-10-14"></a>

Después de autorizar el desarrollo, implementé el recorrido comercial en `main`, sobre `687a773`, conservando el trabajo local anterior sin cambiar de rama ni crear un commit. El visitante reúne ofertas de cursos, tutoriales y recursos sin abandonar la exploración; al entrar, incorporo su selección a la cuenta de estudiante. El carrito permite revisar inclusiones, quitar y deshacer, guardar para después y continuar al checkout. Comprar ahora mantiene la selección directa y la lección de origen.

Separé carrito, pedido, líneas y factura. Congelo precios, educador, versión e inventario por línea y preparo un solo pago por el total. La revisión firmada exige comprobar de nuevo una selección cambiada. Los reintentos reutilizan la operación original. Reservo las revisiones pagadas tanto para pedidos nuevos como para facturas anteriores, evitando solapamientos. Confirmo derechos, compras e inscripciones en una sola operación y retiro únicamente las líneas compradas, conservando cambios posteriores del carrito y el progreso anterior.

Amplié Guardados a cursos y tutoriales por versión, sin conceder acceso ni inscribir. Enlacé autores a sus perfiles públicos permitidos y añadí búsqueda y filtros a sus escaparates. La ayuda de plataforma conserva contexto comprobado de factura, pedido o recurso adquirido. Ventas cuenta una transacción por pedido y limita título e importe a las líneas propias del educador; no representa dinero disponible ni liquidaciones.

Los contenidos adquiridos, las inclusiones repetidas, los paquetes parcialmente adquiridos, los cambios de precio y las ofertas retiradas requieren resolver o revisar la selección antes de pagar. Una solicitud desconocida conserva su referencia; un pago observado después del plazo, sin una hora fiable de cobro, permanece en revisión con evidencia y ayuda, sin inducir otro pago. Completar conjuntos con crédito, comisiones, liquidaciones y devoluciones siguen pendientes. El carrito admite 20 artículos; un excedente al incorporar la selección de visitante permanece solo en la sesión privada de esa cuenta hasta resolverlo y puede perderse al cerrar esa sesión.

Ensayé en navegador con cuentas sintéticas y un proveedor local controlado: tres artículos de dos educadores, 250 sats en total, selección conservada después del acceso a la cuenta, retiro y deshacer, tutorial guardado, confirmación única, apertura del curso, tutorial y material, historial y ayuda contextual. Ventas del primer educador mostró únicamente sus 150 sats. Comprobé escritorio, temas claro y oscuro, navegación con teclado hacia compra y ayuda y pantallas a 320 px sin desbordamiento en las vistas comprobadas. Estas comprobaciones no son sesiones con participantes, una auditoría completa de accesibilidad ni un pago desde ZEUS o con fondos reales.

Conservo las pantallas de [carrito en escritorio](evidence/comercial-carrito-escritorio-2026-10-14.png) y [móvil](evidence/comercial-carrito-movil-2026-10-14.png), [revisión del pedido](evidence/comercial-checkout-escritorio-2026-10-14.png) y [revisión oscura móvil](evidence/comercial-checkout-oscuro-movil-2026-10-14.png), [confirmación](evidence/comercial-confirmacion-escritorio-2026-10-14.png) y [confirmación móvil](evidence/comercial-confirmacion-movil-2026-10-14.png), [ayuda móvil](evidence/comercial-ayuda-movil-2026-10-14.png), [escaparate](evidence/comercial-escaparate-2026-10-14.png) y [ventas del educador](evidence/comercial-ventas-educador-2026-10-14.png).

Pasaron 429 pruebas Django, configuración, consistencia de migraciones y Ruff. Los cuatro controles de concurrencia de comercio, evaluaciones, certificados/preguntas y comunidad quedaron correctos en la revisión integrada; comprobé por separado el [quinto control, de cuentas](evidence/comercial-concurrencia-cuentas-2026-10-14.txt), también correcto. Pasaron [cinco escenarios del cliente de carrito](evidence/comercial-carrito-cliente-2026-10-14.json), [nueve de guardado de formularios](evidence/comercial-formularios-2026-10-14.json), el verificador de progreso y la sintaxis del cliente nuevo. El primer integrado detectó tres expectativas de texto anteriores; las corregí conservando los controles de permisos, destino y privacidad. Ese registro no representa la ejecución final correcta. Se conserva la advertencia conocida `auth.W004` por correos reutilizables entre tipos de cuenta.

Apliqué `commerce.0004_orderline_alter_invoice_offer_cart_cartitem_order_and_more` y `learning.0012_saveditem_course_version` con `migrate-commercial.py`. Antes ensayé aplicación, repetición, contadores de identificadores y restauración ante fallos en copias. El respaldo principal quedó en `.local/backups/commercial-20261015T032732Z-5cf8e18ec6/before.sqlite3`, con `verification.json` en el mismo directorio. Comparé todas las columnas y filas anteriores de 65 tablas: se conservaron; las cuatro tablas comerciales nuevas quedaron vacías y las columnas nuevas de facturas y guardados quedaron NULL en sus registros anteriores. Añadí únicamente los dos registros de migración y cuatro tipos de contenido con 16 permisos oficiales de administración, sin asignarlos a usuarios o grupos. La integridad y las claves foráneas quedaron correctas. Conservo la [salida de migración](evidence/comercial-migracion-2026-10-14.txt).

El control posterior verificó 69 tablas, metadatos completos y ninguna migración pendiente. Actualicé los tres documentos principales y cerré el servidor y la pestaña temporales de revisión. No cargué ejemplos en la base principal ni moví fondos. La siguiente comprobación es observar selección, comprensión, recuperación y acceso con estudiantes y educadores nuevos; continúan pendientes la prueba integrada desde ZEUS, la auditoría completa de accesibilidad y las decisiones de operación comercial.

<a id="barra-lateral-2026-10-14"></a>

Estandaricé la barra lateral después de la revisión y la autorización del usuario. Trabajé en `main`, base `687a773`, conservando los cambios locales del overhaul y de la etapa comercial, sin cambiar de rama ni crear un commit. El diagnóstico previo identificó alturas distintas de 572 y 393 px entre Explorar y Notificaciones en la misma pantalla móvil, opciones duplicadas de Mi cuenta y Ayuda y un menú oculto al abrirlo durante la lectura enfocada.

Unifiqué el marco de academia y estudio, mantuve la geometría bajo la cabecera y reservé la barra para destinos principales. Moví el contexto a las pestañas y controles del contenido, dejé Mis preguntas dentro de Mi aprendizaje y separé Explorar academia de las herramientas del educador. Mantuve cuenta y ayuda desde el avatar también en móvil. El panel móvil contiene el foco y la interacción, se cierra con botón, fondo o Escape y devuelve el foco al control que lo abrió. Corregí la apertura desde lectura enfocada y compartí una estructura sin barra lateral para entrada, registro y recuperación de estudiante y educador.

La revisión de navegador pasó 1.882 comprobaciones sin fallos sobre 184 cargas de páginas, con visitante, estudiante y educadores aprobado, pendiente y suspendido, cuatro tamaños de pantalla y los temas claro y oscuro. Comprobé geometría constante entre páginas, enlaces de 48 px, ausencia de duplicados y desbordamiento, avatar a 320 px, foco y cierre del panel, fondo no interactivo y recuperación al cambiar de tamaño. A 1440 × 900 px, la barra midió 224 × 822 px bajo la cabecera de 78 px; a 390 × 844 px, 320 × 776 px bajo la cabecera de 68 px. No observé errores del cliente en esas comprobaciones. El entorno utilizó una base desechable, se limpiaron sus datos y se cerró su servidor.

La comprobación adicional de lectura enfocada pasó nueve controles en escritorio y móvil, incluida apertura visible, Escape y recuperación del foco. Conservé [estudiante en escritorio](evidence/navegacion-estudiante-escritorio-2026-10-14.png) y [móvil](evidence/navegacion-estudiante-movil-2026-10-14.png), [estudio oscuro](evidence/navegacion-educador-oscuro-escritorio-2026-10-14.png), [estado de cuenta móvil](evidence/navegacion-solicitud-movil-2026-10-14.png) y [menú del lector enfocado en móvil](evidence/navegacion-lector-enfocado-movil-2026-10-14.png) y [escritorio](evidence/navegacion-lector-enfocado-escritorio-2026-10-14.png).

La revisión adicional de acceso y altura pasó 181 controles sobre 33 cargas de páginas, con los formularios de entrada, registro y recuperación de ambos espacios a 320 y 1440 px y en ambos temas. Comprobé también una pantalla de 390 × 360 px, anclas bajo la cabecera fija, desplazamiento independiente y recuperación del foco al cancelar una salida con cambios. Conservé [acceso de estudiante en móvil](evidence/navegacion-acceso-estudiante-movil-2026-10-14.png), [acceso de educador en escritorio](evidence/navegacion-acceso-educador-escritorio-2026-10-14.png) y [menú móvil de poca altura](evidence/navegacion-altura-corta-movil-2026-10-14.png). Se limpiaron los datos temporales y se cerró el servidor de esta revisión.

El control final de poca altura pasó 13 comprobaciones, incluida la visibilidad del foco al recorrer el menú con Tab. Los controles de acceso y desplazamiento comprobaron también el retorno al cancelar una salida con cambios, sin perder el lugar de trabajo.

Pasaron 441 pruebas Django en la batería completa, la consistencia de migraciones sin cambios nuevos, Ruff de los archivos Python modificados y la sintaxis del cliente. Después del ajuste final de retorno del educador pasaron las 75 pruebas de cuentas y las 24 de navegación. Las cuatro pruebas nuevas de acceso, incluidas en cuentas, comprobaron la conservación de un destino permitido al entrar o corregir credenciales y el rechazo de destinos externos o de otro espacio; una cuenta sin aprobación conserva su estado y no obtiene permisos de edición. No sumo estas pruebas enfocadas a las 441 como si fueran otra ejecución completa. Conservo comandos, alcance y resultados en la [evidencia integrada de navegación](evidence/navegacion-integracion-2026-10-14.json). Permanece la advertencia conocida `auth.W004` por correos reutilizables entre tipos de cuenta.

Actualicé los tres documentos existentes y sustituí la descripción obsoleta de una barra que cambiaba según la página. No ejecuté sesiones con participantes ni una auditoría completa de accesibilidad. Me falta observar la recuperación de compras, preguntas y ayuda y el retorno al curso o al estudio con personas nuevas.

<a id="catalogos-separados-2026-10-14"></a>

Después de la entrega de navegación, separé Cursos, Tutoriales y Recursos a petición del usuario. Seguí en `main`, sobre `687a773`, con los cambios locales anteriores. Los tres catálogos tienen accesos directos, títulos, filtros y selección propios; retiré las pestañas que los repetían y mantuve Comparar cursos dentro de Cursos. El educador conserva sus herramientas y encuentra los catálogos en un grupo separado. Una cuenta suspendida ve únicamente los destinos que su estado permite abrir, conforme a la restricción existente.

Conservé los enlaces anteriores de Explorar y los regresos a búsquedas filtradas. La ficha pública identifica Cursos, Tutoriales o Recursos según el contenido; el recorrido inscrito permanece en Mi aprendizaje. Pasaron 41 pruebas de navegación, descubrimiento y continuidad con `manage.py test core.test_navigation content.test_academy content.test_journey --noinput`, además de Ruff en los cuatro archivos Python afectados.

La comprobación de catálogos pasó 445 controles sin fallos sobre 48 cargas en visitante, estudiante y educadores aprobado y pendiente; también verificó la restricción de los tres destinos para la cuenta suspendida. Revisé ambos temas, escritorio y 320 px, el regreso desde tutoriales con su búsqueda y el menú del educador a 390 × 360 px. Conservé capturas de [escritorio](evidence/navegacion-catalogos-escritorio-2026-10-14.png) y [móvil](evidence/navegacion-catalogos-movil-2026-10-14.png). Los datos de prueba eran temporales y se limpiaron al cerrar el servidor. Esta revisión técnica no sustituye las sesiones pendientes con participantes.

Eliminé 17 volcados de navegador y registros extensos de pruebas a petición del usuario. Retiré sus enlaces y conservé los resultados esenciales en esta bitácora y en el resumen integrado existente. Cambié el verificador para mostrar solo resultados breves en consola; el reporte opcional queda limitado a `src/.local/`, ignorado por Git. Registré la preferencia en `AGENTS.md` y añadí exclusiones para impedir nuevas incorporaciones de esos volcados. Una comprobación focalizada pasó nueve controles; el resumen temporal ocupó 223 bytes, se rechazó una ruta de salida versionada y se limpió el entorno. No repetí la batería completa para esta limpieza.

Unifiqué las imágenes de contenido en un componente: portadas 16:9 y miniaturas 1:1, con ajuste centrado que conserva el original completo. Retiré las alturas y recortes que competían entre catálogo, comparación, ficha, continuación, biblioteca, estudio y carrito. Conservé los SVG y revisé los tres documentos principales. Trabajé en `main`, sobre `687a773`, respetando los cambios locales anteriores y sin crear un commit propio. La carga de portadas personalizadas queda pendiente.

Pasaron 12 pruebas existentes seleccionadas de descubrimiento, ficha, continuación, estudio y carrito. Volví a comprobar los dos casos de estudio y carrito tras incluir el tema en sus consultas, para evitar una consulta adicional por imagen. La revisión temporal `node .local/check-content-images.cjs` pasó 349 controles y observó 86 marcos de imagen en siete superficies, a 320, 768, 1280 y 1920 px, con ambos temas y originales 16:9, cuadrados, verticales y panorámicos. Comprobé también el icono de las filas de tutorial y revisé capturas de catálogo, biblioteca, estudio y carrito. No encontré desbordamiento horizontal ni errores de JavaScript. Ruff en los dos archivos Python afectados y `git diff --check` pasaron; permanece la advertencia previa `auth.W004`. Usé datos desechables y conservé únicamente la comprobación y capturas locales, ignoradas por Git; no generé reportes versionados. Esta evidencia comprueba presentación técnica, no comprensión ni resultados educativos.

<a id="colecciones-practicas-2026-10-14"></a>

### Colecciones y prácticas — 2026-10-14

Implementé colecciones personales dentro de Guardados y prácticas con entregas privadas. Conservé todos los guardados anteriores sin asignarlos automáticamente. Cada práctica publica instrucciones, criterios y plazo de revisión junto a la versión de su lección. Añadí texto, enlace y un adjunto por entrega, revisión con retroalimentación obligatoria, correcciones con historial, avisos internos, una bandeja ordenada por antigüedad y recepción que puedo pausar. La práctica complementaria no bloquea progreso ni certificados.

Apliqué `learning.0013_collections_practice_deliveries` en la base local, con respaldo `src/.local/platform-before-study-features-20261014-17cad589.sqlite3`. Comparé los valores de las 672 filas anteriores en 68 tablas: se conservaron, y pasaron integridad y claves foráneas. Trabajé en `main` sobre `687a773`, conservando los cambios locales anteriores y sin crear un commit propio.

Pasaron 23 pruebas específicas de colecciones y prácticas y 26 de navegación. La comprobación de funciones existentes cubrió otras 61 pruebas de guardados, cursos guardados, evaluaciones y funciones esenciales. Actualicé las expectativas de navegación para incluir Prácticas y Entregas y corregí su selección contextual. Comprobé privacidad entre cuentas, acceso a lecciones de pago, suspensión del educador, CSRF, formularios de otra cuenta, conservación de versiones, reintentos, archivos válidos e inválidos, limpieza del archivo al fallar la transacción y exportación de soluciones y revisiones. La advertencia existente `auth.W004` conserva su motivo previo.

El verificador `node scripts/verify-study-workflows.cjs` pasó 21 controles con datos desechables: crear colección, organizar un guardado, enviar un adjunto, descargarlo, solicitar cambios, corregir, aprobar y pausar la recepción. Revisé escritorio a 1280 px, móvil a 320 px y el formulario oscuro; no hubo desbordamiento horizontal ni errores de JavaScript. El verificador imprime un resumen en consola y limpia su base y archivos al terminar; no guarda volcados ni reportes. La consistencia de migraciones y la revisión de espacios también pasaron.

No añadí prácticas automáticamente al catálogo publicado: primero debo definirlas y publicar una nueva versión mediante revisión. Falta validar los criterios y la carga de atención con participantes, acordar retención y cuotas globales e incorporar análisis antivirus para una operación pública. El plazo es una previsión en días naturales; no he demostrado cumplimiento de atención ni resultados educativos. Los avisos permanecen dentro de la plataforma.

<a id="categorias-2026-10-14"></a>

Organicé Cursos, Tutoriales y Recursos con tarjetas de categorías antes del listado. Inicio también muestra las categorías de cursos. Reutilicé los temas existentes, preparé cuatro ilustraciones para las categorías actuales y una por defecto, y añadí descripción e imagen seleccionable desde administración. Los conteos incluyen todas las publicaciones de cada sección y respetan las versiones publicadas. Conservé búsqueda directa, «Ver todos», filtros, comparación y retorno desde las fichas; el contenido sin tema sigue accesible. Trabajé en `main`, base `687a773`, conservando los cambios locales anteriores y sin crear un commit.

Apliqué `content.0007_topic_category_presentation`, con respaldo en `src/.local/categories-before.sqlite3`. Comparé el número de filas de las 74 tablas anteriores y se conservó. La migración añade dos campos de presentación al tema; no reclasifiqué el contenido ni modifiqué publicaciones, compras o progreso.

Pasaron 72 pruebas con `manage.py test content.test_academy core.test_navigation content.test_journey content.test_versions_media --verbosity 0`, Ruff de los archivos Python afectados, `makemigrations --check --dry-run` y revisión de espacios. Comprobé conteos superiores a una página, borradores, categorías vacías, contenido sin tema, imágenes por defecto, categorías en Inicio y temas de versiones y revisiones. Ajusté las expectativas que antes abrían el listado directamente. Se mantiene la advertencia conocida `auth.W004`.

En navegador revisé las cuatro tarjetas del catálogo local, los dos cursos de Lightning, búsqueda dentro de esa categoría y regreso desde una ficha conservando la consulta. También comprobé comparación, imágenes completas, temas claro y oscuro y una columna móvil, sin desbordamiento horizontal. Los anchos CSS observados fueron 1200 y 325 px. Tutoriales y Recursos aún no tienen publicaciones locales: comprobé sus estados vacíos y sus categorías con datos temporales en las pruebas. Conservo una [captura seleccionada](evidence/categorias-2026-10-14.jpg). Todavía no he evaluado esta organización con participantes.

<a id="categorias-2026-10-15"></a>

### 15 de octubre de 2026

Organicé el catálogo en Bitcoin, Tecnología y Creación, con subcategorías dentro de cada una. Reubiqué los temas anteriores bajo Bitcoin y preparé las áreas de hardware, redes, desarrollo, sistemas y herramientas de creación. Mantengo visibles las áreas sin publicaciones con un conteo de cero y un estado vacío. Esta ampliación organiza el catálogo; no añadí cursos ni representa una validación de demanda.

Conservé los enlaces anteriores por `tema` y añadí la selección de categoría, con búsqueda, filtros y regreso desde las fichas. Cada sección reúne solo sus publicaciones y mantiene el tema de la versión o revisión publicada. El educador selecciona una subcategoría dentro del grupo correspondiente. Trabajé en `main`, base `687a773`, sobre los cambios locales existentes y sin crear un commit.

Apliqué `content.0008_category_hierarchy` en la base local después de crear el respaldo `src/.local/backups/categories-before-2026-10-15-t_9rj91m.sqlite3`. Quedaron tres categorías y veinte subcategorías. Comparé los conteos de cursos, versiones, revisiones de recursos y lecciones antes y después: se conservaron, al igual que los identificadores y slugs de los temas anteriores.

Pasaron 73 pruebas con `.venv/Scripts/python.exe manage.py test content.test_academy content.test_catalog_taxonomy content.test_taxonomy content.test_public_coherence core.test_navigation creators.test_overhaul --noinput --verbosity 0`, además de Ruff focalizado y la comprobación de consistencia de migraciones. Después pasó una prueba adicional de compatibilidad del importador: reutiliza el tema reconocido por nombre y conserva su identificador personalizado, categoría y clave, sin duplicarlo; Ruff volvió a pasar. Solo apareció la advertencia previa `auth.W004`.

En navegador de escritorio y modo oscuro comprobé la base local: Bitcoin muestra seis cursos; Tecnología y Creación, cero. Abrí Tecnología, sus nueve subcategorías y Hardware de PC con su estado vacío. Comprobé que cambiar la categoría limpia la subcategoría anterior, elegir una subcategoría selecciona su categoría y la actualización parcial carga la lista correcta. No repetí la revisión móvil en esta entrega ni guardé capturas como evidencia. Mantengo las 72 pruebas y la captura del día anterior como evidencia de aquella versión. Todavía necesito observar la comprensión de los nombres y la navegación con participantes y preparar contenido revisado para las nuevas áreas.

<a id="filtros-catalogo-2026-10-15"></a>

#### Filtros del catálogo

Simplifiqué la barra de Cursos, Tutoriales, Recursos, Explorar y Comparar cursos. Dejé la búsqueda contextual como acción principal y agrupé las opciones útiles en «Filtros», cerrado al entrar. Conservo la categoría y subcategoría sin repetir sus selectores; los refinamientos y la búsqueda se pueden retirar sin perder ese contexto. Las opciones proceden de las publicaciones que coinciden con el catálogo y la búsqueda antes de aplicar nivel, formato y acceso. Mantengo recuperable una selección sin resultados y conservo el panel abierto y el foco al actualizar la lista. El perfil público del educador mantiene su barra propia.

Reduje la navegación de subcategorías a las que tienen publicaciones y reuní el cambio de una selección en «Cambiar subcategoría». Una categoría vacía permite consultar todas sus áreas configuradas desde un desplegable. Trabajé sobre los cambios locales en `main`, base `687a773`, sin crear un commit ni aplicar migraciones o escribir datos en la base.

Pasaron 69 pruebas con `.venv/Scripts/python.exe manage.py test content.test_catalog_filters content.test_catalog_taxonomy content.test_academy core.test_navigation --noinput --verbosity 0` y Ruff de los archivos afectados. Después pasaron por separado dos pruebas adicionales: «Todas» conserva búsqueda, nivel, acceso y formato al retirar la subcategoría, la página y el curso seleccionado; «Por descubrir» mantiene la opción «Sin subcategoría» y la selección de enlaces anteriores en un catálogo mixto. La revisión final de Ruff y consistencia de migraciones también pasó. Se mantuvo únicamente la advertencia previa `auth.W004`; esta ejecución es independiente de las 73 pruebas de la ampliación anterior.

En escritorio y modo oscuro comprobé Tutoriales dentro de Bitcoin sin publicaciones: aparece solo la búsqueda. En Cursos, Bitcoin muestra seis cursos y «Filtros» ofrece únicamente Acceso. Abrí el panel con Enter y comprobé tres cursos con contenido de pago, seis con contenido gratuito, la selección activa y el contexto de la URL. Después de actualizar la lista, verifiqué el panel abierto y el foco en «Aplicar filtros». Recursos vacío mostró solo «Buscar recursos»; Comparar cursos conservó «Buscar cursos en Bitcoin», envío normal y controles pertinentes, sin desbordamiento.

En móvil a 390 × 844 px y modo oscuro corregí el solapamiento de botones; la barra quedó sin desbordamiento, con campos de 16 px y la opción disponible a todo el ancho. La revisión adicional a 320 × 740 px también confirmó ausencia de desbordamiento y solapamiento. No revisé modo claro ni guardé capturas como evidencia. La comprensión y facilidad de uso con participantes siguen pendientes.

<a id="iconos-filtros-2026-10-15"></a>

#### Iconos de filtros

Incorporé cuatro SVG de Font Awesome Free 7.3.1 para búsqueda, filtros, cierre y flecha en un componente reutilizable, con los originales y su licencia conservados localmente. Corregí el tamaño y la alineación de la flecha y reservé espacio para el texto del botón en escritorio y móvil. Los dos desplegables muestran una sola flecha, que gira al abrir y respeta la preferencia de movimiento reducido. Los SVG se incluyen en el HTML y utilizan los estilos locales. Mantengo esta corrección separada de las pruebas anteriores de la barra.

Pasaron las 18 pruebas existentes con `.venv/Scripts/python.exe manage.py test content.test_catalog_filters --noinput --verbosity 0` y la revisión de espacios; solo apareció la advertencia previa `auth.W004`. Comprobé los cuatro SVG originales, su atribución y licencia, y la retirada del carácter anterior de las plantillas del catálogo. En navegador oscuro revisé escritorio y 320 × 740 px: la flecha conservó 12 px, el control midió 144 y 128 px respectivamente, y no hubo desbordamiento ni solapamiento de botones. Verifiqué el giro de 180 grados, la apertura por Enter de «Cambiar subcategoría» en Lightning y la ausencia de una segunda flecha nativa. La revisión visual confirmó la alineación; no repetí 390 px ni modo claro en esta corrección. Conservé los datos y modelos existentes.

<a id="panel-filtros-2026-10-15"></a>

#### Distribución del panel

Reorganicé los campos de filtros y su acción en una fila flexible: una sola opción mantiene un ancho acotado junto al botón y varias comparten el espacio. En móvil los campos ocupan el ancho disponible. Aplané el panel y dejé un separador fino en la parte superior. Ajusté el foco de la barra con fondo suave y subrayado de etiqueta o texto, manteniendo estable el borde de los controles. La corrección modifica los estilos; conserva la búsqueda, los filtros y el contexto del recorrido.

La revisión visual y funcional en modo oscuro comprobó Acceso a 320 px junto a «Aplicar filtros», separados por 12 px, y tres campos alineados con la acción en Comparar cursos. En móvil a 320 × 740 y 390 × 844 px, campo y botón quedaron apilados a todo el ancho, sin desbordamiento. Con Tab comprobé el subrayado de foco y el borde estable, sin contorno ni resplandor añadido. Al aplicar el filtro de pago, se conservaron Bitcoin, el panel abierto y el foco en «Aplicar filtros», con tres resultados. La revisión de espacios pasó. Esta comprobación corresponde a los estilos y su actualización de caché; las 18 pruebas anteriores conservan su alcance propio.

<a id="cursos-completos-2026-10-15"></a>

#### Cursos completos de Creación y Tecnología

Investigué fuentes primarias y publiqué cuatro cursos originales: fotografía con celular, edición con Shotcut, desarrollo web accesible y reportes CSV con Python. Añadí 48 lecciones en dieciséis capítulos, con 20 383 palabras de enseñanza, dieciséis evaluaciones de cuatro preguntas y cuatro proyectos con cinco criterios. Todas las lecciones son de pago. Incorporé cuatro portadas fotográficas con licencia y créditos, tres videos de YouTube y dos páginas oficiales con apoyo audiovisual. Los complementos externos conservan sus condiciones; los textos permiten estudiar sin depender de ellos.

Usé un perfil editorial de BTC.EDU y el recorrido habitual de preparación, envío, revisión, versión sellada y aprobación de ofertas. Dejé 48 ofertas de lección, dieciséis de capítulo y cuatro de curso completo. La revisión registra la autorización editorial y las comprobaciones técnicas, sin atribuir una evaluación a un especialista externo. Desactivé la identidad administrativa de la carga y retiré sus permisos al terminar.

Trabajé en `main`, base `687a773`, conservando los cambios locales previos y sin crear un commit. Antes de la carga hice el respaldo `src/.local/backups/before-complete-courses-20261015-194924-245895.sqlite3`. Comparé los registros anteriores mediante huellas de sus valores en once modelos de contenido, comercio, publicaciones y aprendizaje: permanecieron intactos. La segunda carga añadió cero cursos. La base quedó con diez cursos, 72 lecciones, tres categorías y 21 subcategorías. También comprobé que los 48 textos, sus evaluaciones y sus instrucciones de proyecto coinciden con los archivos finales.

Pasaron 68 pruebas con `.venv/Scripts/python.exe manage.py test content.test_complete_courses content.test_journey content.test_catalog_taxonomy content.test_catalog_filters learning.test_collections_practices --noinput --verbosity 0`. Después del ajuste de opciones de compra pasaron otras 29 con `content.test_complete_courses commerce.test_experience`. Estas ejecuciones comprueban acceso denegado antes de comprar, inventario individual y completo, desbloqueo de la versión exacta, evaluaciones, progreso y emisión del certificado para los cuatro cursos. Las compras y certificados de las pruebas se hicieron en bases temporales. Ruff focalizado y la consistencia de migraciones pasaron; sigue la advertencia previa `auth.W004`, sin cambios de esquema.

En navegador oscuro revisé las dos categorías y la ficha de fotografía, sus créditos, temario y precio. Las cuatro portadas se sirven localmente. En una copia aislada comprobé la lectura comprada de web, los bloques de código escapados, las soluciones cerradas y el reproductor complementario de YouTube. A 390 × 844 px, el código conserva los espacios y permite desplazamiento dentro del bloque sin desbordar la página. Agrupé las opciones por capítulo y lección para evitar una ficha excesivamente larga y corregí los mensajes que sugerían lecciones gratuitas en cursos totalmente pagados. No comprobé reproducción audiovisual de principio a fin ni repetí todos los recorridos en modo claro.

Los proyectos se conservan como expedientes de autoevaluación; mantengo cerrada su recepción hasta asignar atención y no vendo revisión personal. El certificado exige las doce lecciones y cuatro evaluaciones aprobadas con al menos 75 %, sin exigir aprobación del proyecto. Los precios y las duraciones siguen sin validación comercial o educativa. Me queda revisar los cursos con especialistas y participantes y mantener sus enlaces; esta entrega publica contenido completo en local, sin cambiar el entorno de pagos ni acreditar cobros reales. Actualicé el informe y la investigación con el contenido efectivamente publicado, sus fuentes, derechos y límites.

### 23 de octubre de 2026

Revisé la batería completa sobre la carpeta local. Pasaban 517 de 524 pruebas con `DJANGO_DEBUG=true`, y sin esa variable fallaban 94 por la redirección a HTTPS y la verificación obligatoria de correo. Las siete pruebas que fallaban seguían esperando el listado directo en `/cursos/`, que ahora abre con las categorías, y textos o migraciones anteriores.

Ajusté esas pruebas para consultar el listado con `vista=todos`, comprobar la sección de guardados por su identificador y excluir los descendientes de `content.0006_educational_units` al retroceder migraciones. En la configuración, las pruebas desactivan la redirección a HTTPS y la verificación de correo; las pruebas que la comprueban la activan explícitamente. Silencié `auth.W004` porque un mismo correo puede tener una cuenta por tipo y `AccountBackend` filtra siempre por tipo. Corregí con Ruff el orden de imports y un import sin uso.

Pasaron las 524 pruebas con `manage.py test --parallel 4`, con y sin `DJANGO_DEBUG=true`, además de `manage.py check` sin avisos, `makemigrations --check` y Ruff. No repetí los controles de concurrencia ni los verificadores de navegador, y no cambié el comportamiento visible de la plataforma.

Más tarde revisé una comparación de BTC.EDU con Udemy, Coursera, Platzi, Domestika, Saylor y Mi Primer Bitcoin e implementé las funciones que podía comprobar en local, sobre la misma carpeta y sin commit propio. Añadí crédito por compras anteriores, cupones, regalos, propinas, reembolsos por Lightning, sello OpenTimestamps, reseñas verificadas, galería de proyectos, rutas de varios cursos y la aplicación instalable con lectura sin conexión. Creé las migraciones `commerce.0005_coupons_gifts_tips_refunds` y `learning.0014_reviews_gallery_paths_timestamps`; las dejé depender de migraciones anteriores de contenido para no romper las pruebas que retroceden la taxonomía. No las apliqué a la base principal.

Cambié tres pruebas que esperaban el bloqueo de paquetes parcialmente comprados y las de navegación por los menús nuevos. Pasaron 559 pruebas con `manage.py test --parallel 4`, con y sin `DJANGO_DEBUG=true`, además de `manage.py check`, `makemigrations --check`, Ruff y `node --check` de los scripts nuevos. Las 34 pruebas nuevas cubren crédito y huella del pedido, cupones, regalos, propinas, reembolsos, lectura de BOLT11, formato y actualización de pruebas `.ots`, reseñas, galería, rutas y la página sin conexión.

En una base temporal con proveedor controlado pagué una lección de 70 sats y completé su curso de 150 por 64, con 70 de crédito y el cupón LANZA20. También envié una propina de 500 sats, compré un regalo en vista móvil sin desbordamiento, abrí su enlace de canje y revisé Cupones y Propinas del educador. Guardé una lección, detuve el servidor y la abrí sin conexión; otra página mostró la lista de guardadas. Al entrar con otra cuenta se borraron las lecciones guardadas. No repetí los controles de concurrencia, no contacté calendarios de OpenTimestamps ni wallets reales y no instalé la aplicación en un teléfono.

### 24 de octubre de 2026

Las migraciones `commerce.0005_coupons_gifts_tips_refunds` y `learning.0014_reviews_gallery_paths_timestamps` quedaron aplicadas en la base principal a las 05:41, al iniciar la plataforma: `setup-platform.ps1` ejecuta `migrate` sin respaldo previo. Respaldé la base un minuto después en `src/.local/platform-before-features-20261024-054239.sqlite3`; ese respaldo ya incluye las migraciones. Comprobé integridad y claves foráneas sin errores, las mismas 86 tablas y 1366 filas antes y después de volver a ejecutar `migrate`, sin migraciones pendientes. Las tablas alteradas, pedidos y líneas, estaban vacías y las tablas nuevas siguen vacías. Se conservan 10 cursos, 72 lecciones, 3 inscripciones, 1 certificado y 5 cuentas. No tengo una copia anterior a la migración para comparar fila por fila.

Rehíce el lenguaje visual: blanco y negro con un solo acento naranja, inspirado en la estética industrial de Nothing. Primero lo diseñé como lienzo con la hoja del sistema, inicio, curso, pago y lección móvil; después lo apliqué a la plataforma. Reemplacé los tokens de color en `overhaul.css` y regeneré en `theme.css` los tonos claros y oscuros por luminancia, de modo que los tonos cálidos anteriores quedan en grises neutros. Cambié NType82 y Ndot77 por Doto e Inter Tight con licencia OFL. Con eso queda resuelta la licencia de distribución web que tenía pendiente; los archivos anteriores siguen en el repositorio, aunque ya no se cargan. Rediseñé botones, cabecera, barra lateral, tarjetas, insignias y la pantalla de pago: pasos numerados con matriz de puntos, total en Doto, estado pendiente con un punto que parpadea y QR en marco blanco. La acción principal de compra, pago y comienzo usa la nueva clase `btn-accent`. Mantuve en el texto «N sats» seguido, porque las pruebas lo comprueban.

Pasaron 559 pruebas de `accounts`, `commerce`, `content`, `core`, `creators`, `learning` y `media` con `--parallel 4`. Revisé inicio, catálogo y tarjetas en escritorio, en ambos modos y a 375 px. Las facturas pendiente y confirmada las rendericé desde una base temporal de pruebas, porque la base local no tiene una cuenta de estudiante que pueda usar. La comprobación del sistema no encontró problemas y Ruff pasó sobre el único archivo Python modificado. No repetí la revisión de accesibilidad con lector de pantalla y no agrupé los miles en los precios.

Después, sobre `de7c75e`, rediseñé la tarjeta de curso de Mi aprendizaje. La portada, el título, «Ver temario» y «Ver acceso» llevaban al mismo temario; ahora la portada queda fuera del orden de tabulación y el temario se enlaza desde el título y el pie. El avance usa una cifra en Doto y una barra con un segmento por lección; en un curso en progreso, el segmento de la siguiente lección va en naranja y el estado lleva un punto naranja. Cuando no queda una lección accesible, la tarjeta dice cuántas lecciones requieren acceso y la acción cambia a «Ver opciones de acceso», como en la ficha. Quité los estilos anteriores de la tarjeta en `learning-experience.css` y `overhaul-learning.css` y añadí un icono de candado. Pasaron 447 pruebas de `learning`, `commerce`, `content` y `core`; actualicé tres comprobaciones de texto. Revisé los cuatro estados con datos sintéticos en escritorio, en modo oscuro y a 375 px, con las hojas de estilo del proyecto pero sin las fuentes locales. No revisé la tarjeta con una cuenta real ni con lector de pantalla.

Sobre `0671dca` rediseñé también la tarjeta del catálogo (`core/_card.html`). Antes repetía el número de lecciones, añadía «A tu ritmo», usaba «↗» aunque el enlace es interno y separaba el precio y el acceso con dos divisiones. Ahora el tipo va en una píldora sobre la portada; nivel, lecciones y duración van en una línea, y el resumen se limita a dos líneas. El pie muestra el precio en Doto con el tipo de oferta, o «Gratis», y un círculo con flecha que se rellena al pasar o enfocar la tarjeta. Si el estudiante está inscrito, el pie muestra su avance con una barra naranja (negra al completar) y conserva el precio si aún le falta terminar. El enlace del autor queda por encima del enlace que cubre la tarjeta; antes ese enlace lo tapaba. No cambié `.card-price` ni `.card-meta`, porque Compras los usa. Pasaron las 559 pruebas; una detectó que el precio desaparecía para un estudiante inscrito y lo corregí. Revisé el catálogo de Bitcoin en escritorio con modo oscuro y a 375 px en modo claro. No revisé el perfil del educador, Tutoriales ni Recursos.

Sobre `755302c` rediseñé las tres pantallas de evaluación del estudiante con una hoja propia, `quiz.css`. Antes comparé con Moodle y con guías de accesibilidad de Canvas; las decisiones y lo que queda pendiente están en [evaluaciones del estudiante](../../strategy/investigacion-y-requisitos.md#evaluaciones-del-estudiante). El resumen muestra preguntas, nota mínima, intentos y mejor nota en Doto, cómo funciona el intento y el historial con una barra de nota por intento. El intento guarda cada respuesta en segundo plano: la vista devuelve JSON con la nueva revisión y solo muestro un aviso si el guardado falla, sin «Reintentar» cuando otra sesión guardó antes. Añadí marcas para revisar, atajos de teclado (1–6, flechas y M) y un resumen previo a la entrega. El resultado invierte el panel de la nota, marca en naranja la nota mínima, compara con el intento anterior y permite filtrar las preguntas por repasar; las opciones solo indican la correcta cuando las reglas muestran soluciones. Quité de `assessments.css` las reglas del estudiante que ya no usaba ninguna plantilla y conservé las del educador. Amplié `preview-assessments.py` a cinco preguntas y tres intentos. Pasaron 561 pruebas, dos nuevas para el guardado en segundo plano y la revisión sin clave. En esa vista previa, con base temporal, respondí con teclado, recargué el intento, entregué y revisé el resultado en escritorio oscuro y a 375 px en claro, y forcé un conflicto de revisión. No probé con lector de pantalla ni revisé de nuevo el editor ni los resultados del educador.

Sobre `cee64b5` reorganicé las categorías para preparar cursos de pago, freemium y de membresía en cada área. Tecnología agrupaba nueve áreas en una sola tarjeta; ahora tengo seis categorías, todas tecnológicas: Bitcoin y Lightning, Desarrollo de software, Datos e inteligencia artificial, Ciberseguridad, Infraestructura y nube, y Diseño y creación digital. Las áreas de Tecnología pasaron a las categorías nuevas y añadí once subcategorías, entre ellas Nodos y minería, APIs y backend, Análisis de datos, Hacking ético y Computación en la nube. La migración `content.0009_technology_categories` conserva los identificadores de las subcategorías y los enlaces por `tema`, respeta nombres y descripciones editados en administración y retira Tecnología solo si queda vacía. Dibujé cuatro ilustraciones con el estilo de las existentes y moví los cursos de desarrollo web y Python a Desarrollo de software en sus catálogos JSON. Pasaron 561 pruebas; actualicé las que esperaban Tecnología y la prueba de migración, que detectó que la primera versión sobrescribía descripciones editadas. Apliqué la migración a la base local sin respaldo previo; quedaron seis categorías y los mismos diez cursos. Revisé las tarjetas de categoría en escritorio, sin vista móvil ni lector de pantalla. Las categorías nuevas siguen sin cursos hasta la siguiente entrega.
