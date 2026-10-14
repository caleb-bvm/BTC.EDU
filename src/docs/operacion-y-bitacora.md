# Operación y bitácora

## Dónde estoy

Ya tengo una plataforma local que conecta publicación, micropagos y aprendizaje. Puedo preparar contenido como creador, enviarlo a revisión, publicar una versión, ofrecerla en sats y conservar la compra y el avance del estudiante. También incorporé evaluaciones, certificados, preguntas privadas, avisos internos, paneles y conversaciones por curso y lección.

El catálogo local tiene seis cursos de Bitcoin y Lightning y 24 lecciones. Tres cursos son gratuitos; los otros tres tienen una primera lección gratuita y contenido de pago. Mantengo la identidad visual de BTC.EDU, el modo claro y oscuro y una navegación que cambia según el espacio que esté usando.

La entrega de fichas del 13 de octubre pasó 319 pruebas, las comprobaciones de configuración y migraciones, la revisión estática y cinco controles de concurrencia. Después de los últimos ajustes repetí 32 pruebas de fichas y creadores. Ensayé edición, envío y consulta de muestras en navegador con datos temporales. Todavía necesito comprobar la compra desde ZEUS dentro de BTC.EDU y validar la utilidad educativa con participantes.

No he validado la propuesta con participantes ni los precios con compradores. Las pruebas con FakeWallet y Polar/regtest no acreditan cobros con fondos reales. Mantengo el propósito y la investigación en el [informe](../../strategy/19-recomendacion-y-entrega-final.md) y en [investigación y requisitos](../../strategy/investigacion-y-requisitos.md).

<a id="guia-local-anterior"></a>

## Cómo trabajo en local

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

Para revisar o cargar el catálogo editorial, ejecuto desde `src`:

```powershell
./.venv/Scripts/python.exe manage.py load_editorial_catalog --dry-run
./.venv/Scripts/python.exe manage.py load_editorial_catalog
./.venv/Scripts/python.exe scripts/verify-editorial-catalog.py
```

La carga crea un respaldo y omite los cursos editoriales que ya existen. No actualiza textos publicados ni compras o progreso. Para cambiar contenido sigo el editor y la revisión editorial. El verificador consulta una copia temporal de la base.

Para ensayar recorridos uso los scripts `preview-academy.py`, `preview-creators.py`, `preview-commerce.py`, `preview-assessments.py`, `preview-regtest.py`, `preview-essential.py`, `preview-community.py`, `preview-learning.py` y `preview-lesson-community.py` de `src/scripts`. Cada uno prepara datos temporales. Los accesos rápidos de estas vistas pertenecen exclusivamente a la demostración y no sustituyen el login de la plataforma.

<a id="base-tecnica"></a>
<a id="arquitectura-btc-edu"></a>
<a id="diseno-plataforma"></a>

## Decisiones que mantengo

### Fichas educativas

Ahora preparo resultado, requisitos, actividad, muestra y acompañamiento en cada unidad. Puedo guardar un borrador incompleto, pero debo completar su ficha para enviar o publicar. La revisión y las páginas del alumno conservan la información de la versión publicada. La muestra es pública; el cuerpo y las soluciones mantienen su acceso. Las fichas antiguas siguen vacías hasta que prepare una nueva revisión.

### Enfoque de la plataforma

Decidí orientar BTC.EDU a educación de distintas áreas desde el inicio. Mi catálogo de Bitcoin y Lightning es la primera colección demostrable; todavía no tengo contenido publicado de otras áreas. Busco que cada unidad ayude a resolver una tarea concreta y pueda relacionarse con un recorrido más amplio. No considero la compra individual, los certificados o el pago en sats una ventaja suficiente por sí solos.

Mantengo las reglas comerciales actuales mientras evalúo sus mejoras. Hoy no puedo comprar un conjunto si ya adquirí alguno de sus componentes; debo comprar los faltantes por separado. Quiero investigar una transición que reconozca lo comprado, pero no implementé descuentos ni ampliación automática. Conservo la comparación y el plan de validación en [investigación](../../strategy/investigacion-y-requisitos.md#posicionamiento-y-validacion).

### Base y archivos

Trabajo con Python 3.12, Django 5.2 LTS y SQLite. Fijo las dependencias en `uv.lock` y mantengo separados los entornos de Django y LNbits. Uso plantillas, HTMX y Bootstrap con estilos propios y archivos locales, sin depender de un CDN durante las visitas.

Conservo la base en `src/.local/platform.sqlite3` y los archivos privados en `src/.local/private-media`. Antes de aplicar migraciones respaldo la base y comparo los datos anteriores. Para recuperar contenido completo necesito conservar también los archivos; reemplazar una revisión no me permite borrar los que siguen ligados a compras históricas.

Mantengo `.local`, `.env`, credenciales y respaldos fuera de Git. No publico el directorio privado como una ruta de archivos. Compruebo la autorización antes de entregar textos, videos, subtítulos o descargas. Admito MP4, PDF, TXT UTF-8 y WebVTT, con un límite inicial de 256 MiB por archivo. Estas comprobaciones no sustituyen antivirus, transcodificación ni revisión completa del contenido.

### Publicación y cuentas

Separé las cuentas de estudiante, creador y administración. Puedo usar el mismo correo en espacios distintos, con identidades y recuperación independientes. Mantengo la aprobación de creador separada del registro. El aviso `auth.W004` responde al correo reutilizable entre tipos de cuenta y al backend propio; conservo las pruebas de esa separación.

Al enviar contenido a revisión congelo una copia. Aprobar publica exactamente esa copia; editar después no modifica lo enviado ni una versión anterior. Mantengo revisiones y composiciones históricas para que una publicación nueva no cambie lo que alguien compró o estudió.

### Compra y aprendizaje

Congelo precio e inventario en cada factura, con vencimiento de 15 minutos. Confirmo el pago desde el servidor y compruebo proveedor, hash, importe y plazo. Una confirmación repetida conserva una sola compra y sus derechos. Ante una respuesta perdida intento recuperar la factura original; los pagos tardíos o incompatibles quedan registrados como incidencias.

Conservo el acceso comprado sobre revisiones concretas. Inscribirse no desbloquea contenido de pago y adquirir un archivo no equivale a comprar todo el curso. Una versión nueva tampoco reemplaza automáticamente las compras, inscripciones o avances anteriores.

Abrir una lección guarda la continuación. Completarla requiere una acción del estudiante y, cuando corresponde, aprobar su evaluación obligatoria. Rechazo guardados obsoletos para no sobrescribir un avance más reciente desde otra sesión. La ficha y la biblioteca comparten la decisión de continuar, repasar o revisar acceso.

### Evaluaciones y certificados

Corrijo las evaluaciones en el servidor. Conservo preguntas y reglas por versión, respuestas guardadas, límites de intentos y autorizaciones adicionales con motivo. La selección múltiple exige coincidencia exacta; aprobar no marca automáticamente la lección como completada. El estudiante debe guardar antes de salir: no tengo guardado automático de respuestas.

Emito un certificado por inscripción cuando se cumplen los requisitos publicados y el estudiante confirma su nombre. Mantengo el PDF privado y la compartición voluntaria. Una revocación conserva el historial y bloquea nuevas descargas del PDF.

Uso SHA-256 para comparar los datos de la credencial con la huella guardada. Puedo descargar el JSON y recalcularlo con:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath './certificado-IDENTIFICADOR.json'
```

La huella corresponde a esos datos, no a todos los bytes del PDF. No incorporé una firma digital, un registro en Bitcoin ni acreditación oficial. Una coincidencia tampoco elimina una revocación ni ofrece independencia frente a alguien que controle la base y cambie datos y huella.

### Conversaciones y privacidad

Mantengo las preguntas privadas separadas de la comunidad. Para participar en un curso exijo inscripción en esa versión; para una conversación de lección también compruebo acceso a su texto. Buscar, seguir o recibir un aviso no concede permisos nuevos.

Registro motivos y responsables al ocultar mensajes, cerrar conversaciones o suspender escritura. La suspensión conserva lectura, compras y progreso. Los mensajes enviados no se editan ni eliminan desde el recorrido normal; las correcciones se añaden como aclaraciones. Los avisos son internos, sin correo ni un plazo de atención garantizado.

Uso el alias del estudiante en la comunidad y comparto su presentación solo si lo decide. No publico correo, compras, notas, progreso ni preguntas privadas en su ficha. El directorio no verifica identidad ni credenciales docentes.

<a id="componentes-visuales"></a>

### Interfaz y métricas

Mantengo la estética industrial aprobada, las fuentes locales y la navegación por contexto. Presento los precios como cantidad y sats. Explico FakeWallet y regtest durante la documentación o presentación; la interfaz evita banners técnicos y comprueba el pago en silencio, salvo errores que requieren una acción.

Los paneles distinguen compras, permisos, inscripciones, finalización e intentos. Conservo numeradores y denominadores y muestro ausencia de datos cuando corresponde. No reconstruyo visitas anteriores ni interpreto aperturas o marcas de progreso como prueba de aprendizaje. La instrumentación de reproducción y muestras sigue pendiente.

## Lo que me falta

Necesito preparar pequeñas colecciones en otras áreas con revisión especializada, comprobar si las unidades aportan frente a alternativas gratuitas y observar la comprensión del pago con personas que tengan distinta experiencia. También debo evaluar el nombre BTC.EDU, el paso de una unidad a un conjunto y un presupuesto que cubra remuneración, revisión, entrega y soporte. Las comisiones, liquidaciones y alianzas siguen sin definir o ejecutar.

Necesito ensayar el recorrido de creador y estudiante sobre la base comprobada, incluida la compra desde ZEUS y el acceso posterior. También debo revisar el catálogo con una persona experta, ampliar las evaluaciones y comprobar comprensión y duración con alumnos. Los precios de 120 sats por curso y 50 sats por lección siguen siendo hipótesis. Repetiré la revisión integrada al incorporar nuevas entregas.

Antes de abrir al público necesito correo con entrega comprobada, límites de abuso, despliegue con HTTPS, respaldo y restauración ensayados, supervisión de pagos y atención de incidencias. Debo definir responsables de revisHazión y moderación, conservación de datos y presupuesto de almacenamiento y transferencia. Las pruebas locales de concurrencia no miden capacidad para tráfico público y las revisiones visuales no constituyen una auditoría completa de accesibilidad.

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

Incorporé certificados, preguntas privadas, avisos internos y paneles en `bb3745c`. Pasaron 179 pruebas y tres controles de concurrencia. Revisé formularios por HTTP, compartición del certificado y PDF en escritorio y móvil. La migración conservó 211 filas anteriores de 40 tablas. Guardé la [salida de comprobación](evidence/esenciales-check-2026-10-10.txt), el [PDF](evidence/certificado-pdf.png) y la [respuesta a una pregunta](evidence/pregunta-respuesta-http.png).

<a id="certificados-sha256-2026-10-10"></a>

Añadí la huella SHA-256, comparación web y exportación reproducible. Pasaron 184 pruebas y recalculé el JSON descargado con Node, con el mismo resultado. La migración conservó 258 registros anteriores de 50 tablas. Mantuve explícitos los límites de la huella y la revocación. Conservé la [comprobación](evidence/certificados-sha256-check-2026-10-10.txt) y la [verificación web](evidence/certificado-sha256-verificacion.png).

<a id="conciliacion-2026-10-10"></a>

Añadí conciliación periódica con lotes rotativos, reintentos y parada con Ctrl+C. Pasaron 192 pruebas y tres controles de concurrencia, sin migración nueva. No repetí pagos contra LNbits o ZEUS en esta ampliación. Conservé la [salida](evidence/conciliacion-check-2026-10-10.txt).

<a id="comunidad-2026-10-10"></a>

Implementé comunidad por versión, respuestas, reportes y moderación con motivo e historial en `3a465c3`. Pasaron 210 pruebas y cuatro controles de concurrencia. Revisé participación de alumno en Chrome y móvil; el recorrido completo de moderación quedó comprobado mediante pruebas Django. Conservé la [comprobación](evidence/comunidad-check-2026-10-10.txt) y la [migración](evidence/comunidad-migracion-2026-10-10.txt).

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

Convertí ese enfoque en una [especificación técnica](../../strategy/investigacion-y-requisitos.md#desarrollo-del-enfoque) de fichas versionadas, prácticas, descubrimiento y reconocimiento de compras previas. Después ejecuté la revisión completa sobre la base existente: pasaron 310 pruebas, configuración sin errores, migraciones sin cambios pendientes, revisión estática y cinco controles de concurrencia. Conservé la [salida](evidence/enfoque-tecnico-check-2026-10-13.txt). La advertencia `auth.W004` mantiene el motivo ya documentado. No modifiqué código, no apliqué migraciones a la base principal y no repetí navegador, LNbits o ZEUS. Las funciones de la especificación siguen propuestas, sin un commit propio para esta revisión documental.

Implementé las fichas educativas en lecciones, videos y materiales, con datos conservados por revisión y muestra separada del contenido protegido. Pasaron 319 pruebas y cinco controles de concurrencia; después de los últimos ajustes repetí 32 pruebas de fichas y creadores. Apliqué la migración con respaldo y comprobé los valores de las 616 filas anteriores en 64 tablas. Conservé la [revisión](evidence/fichas-unidad-check-2026-10-13.txt), la [migración](evidence/fichas-unidad-migracion-2026-10-13.txt) y las capturas de [escritorio](evidence/ficha-unidad-escritorio-2026-10-13.png) y [móvil](evidence/ficha-unidad-movil-2026-10-13.png). Ensayé guardado, bloqueo de envío incompleto y envío completo con datos temporales. El catálogo publicado y sus compras se conservaron; faltan sus nuevas fichas, unidades de otras áreas, prácticas registradas y compra del contenido faltante de conjuntos. Trabajé en `main` sobre `2d318f6`, sin commit propio de esta entrega ni un nuevo ensayo de pago desde ZEUS.
