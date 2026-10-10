# Conciliación periódica de pagos

Ampliación técnica del 10 de octubre de 2026 en `main`, sobre la entrega de certificados con huellas SHA-256. El estado actual añade un proceso supervisado; los registros anteriores conservan sus resultados originales.

## Funcionamiento

Desde `src`, ejecutar:

```powershell
./.venv/Scripts/python.exe manage.py reconcile_payments --watch --interval 30 --limit 100
```

El proceso revisa hasta 100 facturas por lote y espera 30 segundos después de completar cada lote. El intervalo admite de 1 a 3600 segundos; el límite, de 1 a 1000 facturas. Valores fuera de esos rangos detienen el comando antes de procesar. Sin `--watch` se ejecuta un solo lote. Ctrl+C permite detenerlo y repetir el comando para reanudar desde la base persistida.

No requiere una página de pago abierta ni una sesión del alumno. Utiliza la configuración privada del proveedor existente y los mismos servicios de confirmación que el navegador. Puede recuperar una emisión cuya respuesta se perdió. Una reserva vigente sin emitir puede generar su factura; el comando no ejecuta pagos ni mueve fondos.

Selecciona facturas no pagadas y sin evidencia de pago resuelta, ordenadas por última comprobación, creación e identificador. Materializa un lote acotado antes de actualizarlo. Cada intento guarda su fecha de revisión, incluso si el proveedor no responde o una factura vencida nunca llegó a emitirse; así no bloquea los siguientes lotes. Las facturas vencidas emitidas siguen consultándose para conservar evidencia tardía.

El vencimiento utiliza el servicio transaccional existente, evitando reescribir el estado pagado desde una copia antigua. Confirmar de nuevo no duplica compras ni permisos. Un pago observado después del vencimiento conserva su incidencia y no concede acceso. Se mantiene la regla vigente basada en el momento de observación: un pago confirmado por primera vez después del plazo se considera tardío, aunque el usuario indique que lo envió antes.

Los errores de disponibilidad del proveedor permiten continuar el lote y reintentar después. Una confirmación inválida informa el identificador de factura en la salida de errores y continúa con las otras. No se imprimen claves, facturas Lightning, datos de cuenta ni respuestas del proveedor. Los errores inesperados o de base de datos terminan el proceso para su revisión.

Cada lote informa fecha local de El Salvador, consultas terminadas, proveedor sin respuesta confirmada y confirmaciones inválidas. «Facturas conciliadas» cuenta consultas terminadas, incluidas pendientes y reservas sin factura emitida; no significa cantidad de compras aprobadas. Los resultados definitivos permanecen en facturas, compras y evidencias. Las conexiones caducadas se cierran entre lotes.

## Verificación

Las ocho pruebas nuevas cubren compra sin navegador e idempotencia, caída y recuperación del proveedor entre pasadas, rotación de reservas vencidas sin emitir, pago tardío sin permisos, aislamiento de confirmaciones inválidas, lotes vacíos, validación de argumentos y parada con Ctrl+C. Utilizan la base de pruebas y un proveedor controlado; no modifican la base principal ni acreditan una ejecución nueva contra LNbits o ZEUS.

La comprobación integrada terminó correctamente: 192 pruebas Django en 99,791 segundos, Ruff sin errores, migraciones consistentes y los tres controles de concurrencia comercial, evaluaciones y certificados/preguntas aprobados. La salida se conserva en [evidencia de verificación](evidence/conciliacion-check-2026-10-10.txt). No hay cambios de esquema ni migraciones nuevas. Se mantiene el aviso conocido `auth.W004` por correos reutilizables entre tipos de cuenta y backend propio.

## Operación y próximos pasos

Mantener un terminal dedicado mientras se supervisa el entorno local y revisar las incidencias en la administración. El proceso no se inicia con Django ni instala una tarea de Windows. Al cerrar el terminal deja de comprobar; al arrancarlo de nuevo retoma las facturas pendientes. El navegador conserva su consulta silenciosa existente.

La puesta en marcha como servicio, reinicio automático, alertas, retención de registros y una política para detener consultas históricas siguen pendientes. Ejecutar un único proceso supervisado evita consultas redundantes; la idempotencia de los servicios protege las compras frente a consultas concurrentes. No se realizó una medición de capacidad ni una prueba nueva de reinicio transaccional de LNbits. Correo, respaldos/restauración, comunidad y membresías conservan sus pendientes propios.
