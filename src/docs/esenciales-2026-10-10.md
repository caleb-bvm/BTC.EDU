# Certificados, preguntas, notificaciones y paneles

Entrega del 10 de octubre de 2026, desarrollada en `main`, commit funcional `bb3745c`, sobre el recorrido de publicación, compra y aprendizaje existente. Esta entrega cierra los cuatro bloques esenciales solicitados. Comunidad, membresías y operación pública conservan su alcance pendiente. La documentación y el ajuste de textos del pie de página se guardan en el commit de cierre.

## Certificados

El creador abre su curso en el estudio y selecciona «Certificado». Puede habilitarlo y elegir al menos una lección incluida en la publicación. El formulario controla revisiones para impedir que otra pestaña sobrescriba requisitos recientes. El envío editorial conserva la política junto a la composición revisada; modificar el borrador no altera publicaciones anteriores.

El alumno ve los requisitos en el curso y en Mi aprendizaje. Debe completar las lecciones seleccionadas y aprobar todas las evaluaciones obligatorias de esa versión, incluso si pertenecen a una lección no seleccionada. Comprar contenido o inscribirse no satisface estos requisitos. Una versión antigua sin política no recibe certificados retroactivamente.

Cuando cumple las condiciones, confirma el nombre antes de emitir. Se guarda una credencial por inscripción, con UUID, nombre, curso, creador, fecha y evidencia de lecciones e intentos aprobados. Repetir o enviar solicitudes concurrentes devuelve la misma credencial. Desmarcar progreso después no reescribe la evidencia de emisión.

El titular descarga un PDF privado. La verificación pública comienza desactivada y solo se habilita desde su cuenta. Puede volver a ocultarla; la URL devuelve 404 cuando no está compartida. La página pública muestra los datos de la credencial y su estado, sin correo, respuestas, notas ni identificador de cuenta. Envía directivas de no indexación, sin referencia y sin caché; compartir implica divulgar el nombre mostrado.

La administración necesita el permiso `learning.add_certificaterevocation` para revocar con motivo. Se conserva actor, fecha y motivo; la credencial continúa en el historial, su estado público indica revocación si sigue compartida y ya no permite descargar el PDF. No hay corrección o reemplazo automático de credenciales: el nombre se confirma antes de emitir y una incidencia requiere revisión administrativa. Una descarga anterior no puede retirarse del dispositivo del titular. Es un certificado de finalización, sin acreditación oficial.

## Preguntas y notificaciones

La lección accesible de un curso inscrito permite preguntar. El alumno consulta sus conversaciones; el creador aprobado consulta únicamente las de sus cursos y responde desde su bandeja. Los demás alumnos, creadores y cuentas de administración no pueden abrir la conversación por estas rutas. Las cuentas suspendidas no escriben. El alumno conserva lectura de su historial, pero necesita acceso a la lección para añadir mensajes.

Los mensajes son texto escapado, de hasta 2.000 caracteres, sin archivos adjuntos. No se editan ni eliminan: una corrección se añade como aclaración. Hay paginación y un límite combinado de 30 preguntas/respuestas por cuenta y hora. Cada formulario tiene una clave de envío; un reintento idéntico no duplica el mensaje y reutilizarla con otro contenido se rechaza.

Las preguntas y respuestas generan avisos internos al otro participante. También se notifican decisiones editoriales, autorización de otro intento, emisión y revocación del certificado. La bandeja y el contador son propios de cada cuenta. Abrir y marcar leído requiere POST con CSRF; repetirlo conserva la fecha original. No se envía correo ni se garantiza un tiempo de respuesta.

## Métricas y paneles

El estudio incluye `/crear/estadisticas/`, limitado al contenido del creador. La administración dispone de `/administracion/estadisticas/`, con enlace desde su inicio, y exige permisos de lectura de facturas, inscripciones y actividad. El intervalo se presenta según `America/El_Salvador`; ambos días son inclusivos y se rechazan fechas inválidas, invertidas o intervalos mayores de 366 días.

Las compras confirmadas usan `Purchase` como fuente de verdad. Se muestran finalización de pago, volumen en sats, pendientes/vencidas/fallidas, conversión desde oferta, apertura después de adquirir permisos, regreso a Mi aprendizaje y compra repetida. Una compra conjunta cuenta una transacción y varios permisos. Los cocientes muestran numerador y denominador; cero se presenta como «Sin datos».

Conversión usa la intersección de pares sesión-oferta con vista y factura nueva en el intervalo. Las facturas reutilizadas no generan otro evento. Regreso exige una apertura de biblioteca en otra sesión después de confirmar la compra, y utiliza solo compradores con sesión de compra registrada; los no observables se informan aparte. Apertura considera cada par alumno-recurso una vez, con acceso ocurrido después de adquirirlo. Estas cohortes reflejan resultados posteriores hasta el momento de consulta, no una foto histórica del cierre del periodo.

Los paneles agregan inscripciones, finalización de todo el temario, aprobación por intento y por inscripción con al menos un aprobado, certificados emitidos, preguntas respondidas, tiempo hasta la primera respuesta del creador, envíos editoriales y desglose por versión. Completar temario y cumplir un subconjunto para certificado son condiciones distintas. Los certificados contados incluyen emisiones posteriormente revocadas.

`ActivityEvent` registra vistas de ofertas, nuevas facturas, aperturas autorizadas gratuitas/compradas y biblioteca, con fecha UTC, sesión aleatoria y referencias internas pertinentes. No incluye IP, correo ni contenido de mensajes. Se excluyen navegación de creadores y administradores; un error de telemetría no bloquea la lectura. Los estados comerciales mantienen su historial existente. No se reconstruyeron visitas anteriores, no se instrumentaron reproducción o muestras como eventos separados y no hay una política automática de eliminación/retención. Aperturas y marcas de progreso no demuestran aprendizaje.

## Verificación

La ejecución final integrada terminó correctamente: 179 pruebas en 95,773 segundos, Ruff sin errores, ninguna migración pendiente y los tres scripts de concurrencia aprobados. [Salida completa de la comprobación](evidence/esenciales-check-2026-10-10.txt).

La comprobación integrada `scripts/check-platform.ps1` ejecuta 179 pruebas Django, migraciones, Ruff y tres scripts de concurrencia con conexiones SQLite independientes. La ampliación aporta 28 pruebas sobre elegibilidad, historia, privacidad, revocación, permisos, idempotencia, CSRF, límites, notificaciones, cohortes, denominadores, fechas y fallos de telemetría. Se verificó específicamente que entrar a biblioteca antes de confirmar un pago no cuenta como regreso posterior.

Se navegó por HTTP real en Chrome con una base temporal: acceso por tipo de cuenta, 10 vistas de escritorio/móvil, sin errores JavaScript ni desbordamiento del documento. Se enviaron formularios reales con CSRF para ocultar y compartir el certificado, responder y marcar avisos leídos; se descargó el PDF autenticado y se comprobó su formato. El PDF normal y otro con nombres/títulos largos se renderizaron e inspeccionaron: una página A4 horizontal, acentos legibles y sin texto cortado.

La migración principal aplicó `core.0001` y `learning.0004`, con respaldo SQLite previo en `.local/backups/platform-before-essential-20261010-094200.sqlite3`. Se preservaron las 211 filas originales de 40 tablas; integridad y claves foráneas correctas. Las nueve tablas nuevas quedaron vacías. Los datos de demostración viven exclusivamente en la base temporal.

El aviso existente `auth.W004` responde a cuentas independientes por tipo con correo reutilizable y backend propio; no cambió el esquema de autenticación. Las verificaciones locales no acreditan capacidad para tráfico público, validación comercial ni resultados con usuarios.

## Evidencias y reproducción

Las capturas están en [evidence](evidence/): certificado y verificación, configuración del creador, preguntas, avisos, paneles y [PDF renderizado](evidence/certificado-pdf.png). [Respuesta por HTTP](evidence/pregunta-respuesta-http.png) y [lectura persistente](evidence/aviso-leido-http.png) documentan los formularios reales. Las cifras corresponden a ejemplos temporales, sin usuarios externos ni fondos reales.

Desde `src`, `./.venv/Scripts/python.exe scripts/preview-essential.py` prepara una base y archivos temporales y sirve la demostración en `http://127.0.0.1:8018/`. Usa las cuentas ficticias `lucia@demo.invalid`, `ana@demo.invalid` y `revision@demo.invalid` con contraseña temporal `EssentialQA_42!`. Ctrl+C termina y limpia el directorio temporal. No requiere LNbits ni modifica la base principal. Para comprobar el producto con datos propios, iniciar normalmente y configurar/publicar una nueva versión con sus requisitos.

## Próximos pasos

El usuario comprobará posteriormente el pago completo desde ZEUS dentro de BTC.EDU; esta entrega no reejecuta esa integración ni acredita fondos reales. Para terminar la preparación esencial de una demostración quedan catálogo y derechos comprobados, manuales y ensayo del recorrido. Para operación pública: entrega de correo, conciliación supervisada, procedimientos de respaldo/restauración, presupuesto, capacidad y seguimiento de incidencias. Comunidad, membresías, corrección de credenciales y eventos de reproducción siguen como ampliaciones explícitas.
