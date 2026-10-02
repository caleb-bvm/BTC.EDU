# LNbits local para Micropayments

Entorno de desarrollo Windows: LNbits 1.6.2, uv 0.12.21 y Python 3.12 gestionado por uv. LNbits se descarga del repositorio oficial, fijado al commit `9349da153c223b008f7d80453b53a54e09c8ed3d`.

## Preparar y arrancar

Desde la carpeta src del proyecto, en PowerShell:

```powershell
./scripts/setup-lnbits.ps1
./scripts/start-lnbits.ps1
```

Abrir http://127.0.0.1:5000. El servidor escucha exclusivamente en la máquina local. Detenerlo con Ctrl+C.

La preparación necesita internet, Git y PowerShell. Herramientas, Python, dependencias, credenciales y base de datos quedan dentro de `.local/`, excluida de Git. No se modifica LNbits ni se instala uv globalmente.

Windows no admite uvloop. Se omite ese paquete durante la instalación y se inicia la aplicación LNbits mediante uvicorn con asyncio. Por esa razón no usamos directamente el lanzador `uv run lnbits` en Windows.

## Prueba de factura y pago

Con el servidor activo, desde otra terminal:

```powershell
./.local/lnbits/.venv/Scripts/python.exe scripts/smoke-lnbits.py
```

En el primer uso configura el administrador local con una contraseña aleatoria y la conserva en `.local/demo-credentials.json`. Si ya configuraste manualmente el administrador, el archivo debe contener su `username` y `password`. No compartir ese archivo.

Cada ejecución crea dos wallets de prueba, acredita 1000 sats ficticios al comprador, crea una factura de 100 sats con vencimiento de 900 segundos, comprueba que está pendiente, la paga internamente y verifica `paid=true` por la API. Las ejecuciones dejan registros reales de prueba en la base de datos.

Resultado verificado el 1 de octubre de 2026: factura pendiente → pagada y confirmación por API, sin fondos reales.

## Configuración y límites

La plantilla `config/lnbits.env.example` se copia únicamente si no existe `.local/lnbits/.env`. Fuente de fondos: FakeWallet. No conectar una wallet real ni utilizar estas facturas fuera del entorno local. HTTP está permitido exclusivamente para esta instancia local.

Con el panel de administración activo, LNbits conserva muchas opciones en la base de datos: editar `.env` después del primer arranque puede no cambiar la fuente de fondos. Mantener FakeWallet en el panel.

SQLite conserva usuarios, wallets y registros de pagos. FakeWallet mantiene parte de sus datos en memoria; la recuperación de facturas pendientes tras un reinicio requiere pruebas adicionales. Este entorno no es testnet ni regtest.

Las consultas externas de precios y extensiones pueden emitir avisos si la red está restringida; la prueba en sats no depende de ellas.

La plataforma ahora tiene portada, navegación, catálogo vacío y cuentas por correo en un entorno separado. Faltan contenidos, compras, permisos, integración Django y simulación controlada de fallos y expiraciones. El administrador y las wallets de esta prueba son de infraestructura y no representan cuentas compradoras del producto. Las claves LNbits se usarán solo desde el servidor.

## Fuentes

- https://github.com/lnbits/lnbits/tree/v1.6.2
- https://docs.lnbits.org/guide/installation.html
- https://docs.lnbits.org/guide/wallets.html

