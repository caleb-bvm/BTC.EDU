# Comercio y continuidad de aprendizaje

Estado verificado el **4 de octubre de 2026**, El Salvador. Este bloque cierra en desarrollo el recorrido creador → publicación revisada → oferta → compra simulada → biblioteca → aprendizaje. Conserva el alcance de plataforma completa. No constituye un despliegue público ni una entrega de todos los módulos previstos.

Commits funcionales: `1e470de` (ofertas, pagos y derechos) y `aa70fca` (progreso, continuación y comprobaciones adicionales). La documentación y las capturas se versionan en un commit separado.

## Ofertas del creador y revisión

El creador aprobado configura una oferta sobre su contenido publicado: curso, capítulo, texto de lección o revisión de video/material. El precio debe ser entero entre 1 y 100 000 sats de prueba. El servidor comprueba propiedad y publicación, y construye la lista exacta de revisiones incluidas.

La oferta individual de lección incluye su texto y adjuntos gratuitos; los archivos de pago tienen oferta propia. Curso/capítulo incluyen su composición completa. Para activar un paquete deben existir alternativas individuales activas para todos sus componentes de pago. El contenido enteramente gratuito no requiere oferta.

Borrador → revisión → activa o cambios solicitados. El revisor necesita permiso administrativo de ofertas; dispone de una pantalla para revisar inventario y devolver observaciones. No se edita una oferta existente para cambiar su precio/composición: se prepara otra. Activarla archiva la anterior para ese mismo destino. Las facturas pendientes conservan su precio e inventario originales, incluso después de ese cambio.

Sellar un envío editorial no lo convierte en publicación. `CourseVersion.published_at` distingue la versión aprobada de una copia pendiente de revisión, que no puede venderse ni abrirse como compra histórica.

## Factura, confirmación y derechos

Cada factura identifica comprador, destino lógico, título, precio y revisiones congeladas; vence a los 15 minutos. Reservas repetidas para el mismo comprador/destino reutilizan la pendiente. Importe, comprador y acceso se derivan del servidor; una petición del navegador no puede afirmar que pagó ni sustituir el precio.

La emisión se registra antes de contactar LNbits. Ante respuesta perdida, se busca la factura original mediante `external_id` igual al UUID de plataforma, sin emitir otra a ciegas. La confirmación consulta el estado del proveedor y exige evidencia de la wallet receptora, hash e importe correctos.

Una confirmación aceptada crea una sola compra, derechos únicos por alumno/revisión y fuentes de esos derechos. Confirmaciones repetidas no duplican compras. Un curso adquirido incorpora una inscripción sobre esa versión; un archivo individual aparece en la biblioteca de recursos.

Pagos tardíos o solapados conservan evidencia e incidencia, sin crear derechos adicionales. Contenido adquirido total o parcialmente bloquea nuevas compras del paquete y presenta alternativas faltantes. También se bloquea la simulación de una factura previamente reservada si el alumno adquirió entretanto parte de su contenido. Una confirmación externa concurrente en conflicto queda registrada para resolución administrativa; no hay reembolso automático.

Archivar una oferta o contenido retira nuevas ventas/descubrimiento, conservando las revisiones compradas. La entrega de archivos y lectura histórica comprueban derechos sobre esa revisión; una publicación nueva no expande ni reemplaza silenciosamente compras anteriores. Los datos de compras, evidencia y derechos son de consulta en administración, sin edición manual de estados pagados.

Los eventos comerciales persisten en plataforma. No equivalen a una cola de correo, avisos externos ni métricas completas de ventas del creador.

## Biblioteca, inscripción y progreso

El espacio del alumno muestra cursos/tutoriales inscritos, versiones, completadas/total, continuación y archivos adquiridos. Inscribirse gratuitamente permite estudiar contenido gratuito, sin desbloquear lecciones de pago. Una inscripción y sus derechos históricos conservan acceso a la versión correspondiente cuando se archiva o publica otra.

Abrir una lección guarda el punto de continuación; completarla requiere una acción explícita. Se puede volver a marcar pendiente. El porcentaje cuenta lecciones de la versión, excluyendo adjuntos. La inscripción conserva revisión de actualización: un guardado antiguo desde otra sesión recibe un conflicto y pide recargar, sin sobrescribir el avance nuevo.

Continuar elige una lección accesible pendiente; si la última se completó, busca la siguiente. Si solo quedan pendientes bloqueadas, muestra «Ver acceso»; al completar todo permite repasar. No se copia progreso automáticamente entre versiones. La posición es por lección: todavía no se guarda segundo de reproducción de video.

El formulario funciona sin JavaScript. Con JavaScript se guarda el punto al abrir, se serializan acciones y se informa éxito, error o conflicto. Se corrigió y verificó en navegador una colisión entre el atributo de destino del formulario y un control llamado `action`.

## Rutas principales

| Ruta | Uso |
|---|---|
| `/crear/ofertas/` | Crear y consultar ofertas propias |
| `/crear/ofertas/<id>/revision/` | Revisión administrativa con observaciones |
| `/ofertas/<id>/` | Inventario, importe y condiciones de acceso |
| `/ofertas/<id>/comprar/` | Reservar factura mediante POST de estudiante |
| `/facturas/` | Historial privado del estudiante |
| `/facturas/<uuid>/` | Estado, vencimiento y compra confirmada |
| `/facturas/<uuid>/comprobar/` | Comprobar o simular mediante POST con CSRF |
| `/mi-espacio/` | Biblioteca y continuación |
| `/aprendizaje/inscribir/<version>/` | Inscribirse mediante POST |
| `/aprendizaje/inscripciones/<id>/avance/` | Guardado de posición/completadas |
| `/aprendizaje/recursos/<revision>/` | Recurso adquirido en su revisión |

Sesión, tipo de cuenta, propiedad y permisos se comprueban en el servidor. Las cuentas de creador, estudiante y administración siguen independientes.

## Preparación y operación local

LNbits 1.6.2 corre en `127.0.0.1:5000` con FakeWallet. El adaptador requiere modo simulación y rechaza proveedores externos o un backend distinto de FakeWallet, que verifica en ejecución. Las claves de recepción, pago ficticio y autenticación administrativa permanecen en configuración privada; no se muestran en HTML. No se presenta factura Lightning/QR para fondos externos.

Con LNbits arrancado y sus credenciales locales preparadas según [LNbits local](lnbits-local.md), desde la raíz:

```powershell
./src/.venv/Scripts/python.exe src/scripts/setup-commerce.py
./src/.venv/Scripts/python.exe src/scripts/smoke-commerce.py
./src/.venv/Scripts/python.exe src/scripts/preview-commerce.py
```

Setup reutiliza wallets ficticias y escribe `.local/commerce.env`, excluido de Git. Repetirlo refresca la autenticación administrativa si vence. Smoke y preview usan SQLite y archivos temporales de plataforma, sin poblar la base principal. Los pagos ficticios realizados permanecen en LNbits. Preview escucha solo en `127.0.0.1:8014`; sus accesos `?vista=estudiante`, `pendiente`, `creador`, `revisor` o `publico` existen exclusivamente en ese script de demostración. Las cuentas temporales no tienen contraseña utilizable; ese mecanismo no se instala en las rutas normales.

Conciliar sin navegador, desde `src`:

```powershell
./.venv/Scripts/python.exe manage.py reconcile_payments --limit 100
```

El comando comprueba pendientes y registra vencimientos aun si el proveedor no responde. **No se instaló un supervisor ni un calendario automático para ejecutarlo.** La consulta de una factura también reconcilia su estado. La operación pública debe resolver supervisión, incidencias, respaldos/restauración y correo antes de desplegar.

## Migraciones y verificación

Se aplicaron `content.0004`, `commerce.0001/0002` y `learning.0001/0002`. Respaldos privados: `.local/backups/platform-before-commerce-20261004-200659.sqlite3` y `.local/backups/platform-before-progress-20261004-202949.sqlite3`. Se compararon cantidades de las tablas de cuentas, contenido, comercio y aprendizaje; los registros originales se conservaron. La base principal permanece sin cuentas/contenido de ejemplo.

`scripts/check-platform.ps1` pasó: **129 pruebas Django**, consistencia de migraciones, Ruff y prueba de concurrencia con dos conexiones independientes sobre SQLite en archivo. Esta última comprueba reserva única, paquetes/pagos solapados con evidencia conservada, confirmaciones repetidas y avance simultáneo con una actualización aceptada y otra obsoleta. No es una prueba de capacidad bajo tráfico público.

`scripts/smoke-commerce.py` pasó contra LNbits FakeWallet real: pendiente → pagada, compra única, derechos/biblioteca, reconciliación repetida, recuperación de una respuesta perdida por `external_id` y pago a través de la vista Django autenticada con CSRF. No se probó reiniciar el proceso LNbits durante la transacción.

Navegador: guardado automático separado de completadas, actualización a 2/3 y continuación hacia la lección pendiente; historial y recibo pagado, factura pendiente y ofertas del creador. Se inspeccionaron escritorio y ancho móvil, sin desbordamiento horizontal en las pantallas comprobadas. Las dimensiones de contenido observadas fueron aproximadamente 1200 y 325 px bajo escalado del sistema; no sustituye una auditoría de accesibilidad ni pruebas en dispositivos físicos.

### Capturas de la demostración temporal

- [Biblioteca, compra y avance en escritorio](evidence/biblioteca-compras-escritorio.jpg)
- [Lección con avance guardado](evidence/leccion-avance-escritorio.jpg)
- [Compra confirmada en escritorio](evidence/compra-confirmada-escritorio.jpg)
- [Compra confirmada en móvil](evidence/compra-confirmada-movil.jpg)
- [Factura pendiente en móvil](evidence/factura-pendiente-movil.jpg)
- [Ofertas del creador en móvil](evidence/ofertas-creador-movil.jpg)

## Próxima fase y alcance pendiente

Evaluaciones versionadas, intentos/corrección y requisitos de finalización; después certificados verificables y preguntas por lección. Comunidad/moderación, membresías, métricas completas y acompañamiento del creador siguen en el plan. Marcadores de recursos y notificaciones externas tampoco están implementados.

Faltan operación periódica supervisada, entrega de correo real, validación con usuarios, contenido editorial y despliegue. No se incorporaron fondos reales, liquidaciones a creadores ni retiros. No se hizo push ni publicación; el trabajo quedó en commits locales.
