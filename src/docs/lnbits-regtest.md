# LNbits con Polar en regtest

## Estado verificado

El 7 de octubre de 2026, en la rama `codex/evaluaciones-versionadas`, se verificó por REST autenticado y TLS que el nodo bob de Polar opera en Bitcoin regtest y tiene un canal activo. El usuario reportó haber creado el canal desde alice, comprador, hacia bob, comercio. No se realizó un pago durante esta preparación.

Se inició LNbits 1.6.2 en http://127.0.0.1:5001, usando LndRestWallet con bob en https://127.0.0.1:8082. El arranque informó conexión al backend y saldo de 0 msat; la página respondió HTTP 200 tras la redirección. El saldo cero del comercio no impide recibir por un canal con liquidez del lado del comprador.

## Arranque

Mantener Docker y la red Polar activos. Desde `src`, ejecutar:

```powershell
./scripts/start-lnbits-regtest.ps1
```

El lanzador comprueba la red antes de iniciar LNbits, verifica el certificado TLS y lee el macaroon directamente del archivo local. Los valores predeterminados corresponden a la red 1 y al nodo bob bajo `.polar` del usuario. Se pueden ajustar con `--endpoint` y `--node-folder`. `--check-only` comprueba la conexión sin iniciar LNbits.

Se reutiliza la instalación local de LNbits, con datos y autenticación separados en `.local/lnbits-regtest/data`. Los archivos privados y los registros permanecen excluidos de Git. La instancia FakeWallet conserva sus datos y puerto 5000. La nueva instancia solo escucha en la computadora; el teléfono se conectará al nodo comprador, no necesita acceso directo a LNbits.

El administrador inicial debe configurarse en la pantalla de LNbits. Mantener LndRestWallet y regtest; la comprobación del lanzador ocurre al arrancar, no supervisa cambios posteriores del administrador.

## Integración del checkout

El usuario confirmó conexión de ZEUS Android a alice y un pago de prueba a LNbits. Es un resultado reportado por el usuario; no se dispone de una captura de ese pago. La API base de LNbits es suficiente: no se requieren extensiones.

Desde `src`, ejecutar `.venv/Scripts/python.exe scripts/setup-commerce-regtest.py`; solicita la contraseña del administrador y obtiene la clave de recepción de la wallet existente. Guarda modo, URL y credenciales en `.local/commerce.env`, con respaldo inicial de la configuración anterior en `.local/commerce-fake.env.backup`. Este archivo tiene prioridad sobre `.env`. Reiniciar Django. Repetir la preparación si caduca el token de administración. No se guarda la contraseña ni se asigna clave de pago al comercio regtest.

El modo `regtest` requiere LndRestWallet y facturas con prefijo `lnbcrt`. El QR se genera localmente mediante qrcode, sin servicio externo. La ruta exige sesión de alumno y pertenencia de la factura; rechaza facturas vencidas, pagadas, con incidente o cuyo contenido ya fue adquirido. La pantalla permite escanear, abrir la wallet o copiar la factura. El pago simulado está bloqueado en servidor y oculto en este modo.

La página consulta el estado cada cinco segundos, con solicitudes secuenciales y pausa mientras está oculta. Al finalizar el pago o aparecer un incidente, recarga para mostrar el resultado. Un fallo de conexión detiene la consulta automática y conserva el botón manual. La concesión de derechos utiliza la conciliación existente, con comprobación de hash, importe, plazo y solapamiento. Cambiar de proveedor no migra facturas pendientes anteriores; verificar o cerrar su ciclo en el entorno original antes de cambiar.

La interfaz presenta el precio únicamente en sats y el QR sin indicaciones técnicas sobre regtest, ZEUS o el entorno de desarrollo. La comprobación automática es silenciosa; su mensaje aparece únicamente si falla y requiere actualización manual. Los detalles del entorno permanecen en esta documentación.

## Verificación del 7 de octubre de 2026

Se aprobaron las 151 pruebas de la plataforma, incluidas 26 pruebas de comercio con privacidad y vencimiento del QR, rechazo de facturas mainnet en modo regtest y bloqueo del pago simulado. La revisión estática y la comprobación de migraciones no detectaron cambios pendientes de esquema. Django conserva el aviso existente sobre el correo no único y el backend de autenticación personalizado. Se emitió una factura de prueba de 100 sats por la API real de LNbits y se verificó pendiente con 100000 msat. Esa factura no corresponde a una compra ni fue pagada.

La demostración `scripts/preview-regtest.py` crea una base temporal con un curso de muestra y una factura de 150 sats en el puerto 8016. Permite entrar como alumno con `?vista=estudiante` únicamente en esta demostración vinculada a loopback; no es una autenticación de producción. El checkout y SVG respondieron HTTP 200, la consulta devolvió pendiente sin incidente y el QR sin sesión redirigió al acceso. El archivo `.local/regtest-preview-url.txt` conserva el enlace de la sesión de demostración. Reiniciarla crea una nueva base y factura.

Falta pagar desde ZEUS la factura del checkout y verificar confirmación y acceso. No se considera realizado ese recorrido por la emisión o las pruebas automatizadas.
