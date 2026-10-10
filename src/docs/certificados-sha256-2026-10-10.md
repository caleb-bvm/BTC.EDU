# Huella SHA-256 de los certificados

Ampliación de la entrega esencial del 10 de octubre, por petición del usuario. Cada certificado conserva una huella SHA-256 de sus datos al emitirlo. Se muestra en el PDF, en la vista privada y en la verificación compartida. «Huella» es el término usado en la interfaz: no se trata de una clave secreta, firma digital ni transacción Bitcoin.

## Qué permite comprobar

La página de BTC.EDU recalcula la huella del registro y la compara con la guardada. Si no coincide, no anuncia validez y bloquea la generación del PDF y la exportación de datos con respuesta 409. El visitante puede introducir los 64 caracteres del certificado recibido; se aceptan mayúsculas/minúsculas y se distingue coincidencia, diferencia y formato inválido. Coincidir nunca elimina el estado de revocación.

Una huella verifica la coincidencia de datos con una referencia confiable. La emisión y vigencia se consultan en la página auténtica de BTC.EDU. Alguien que controle la base y sustituya simultáneamente datos y huella puede producir otra referencia coherente: esto no es verificación independiente del emisor. Las firmas digitales añaden autenticación del origen; no se incorporaron claves o firmas en esta entrega. [NIST: hash functions](https://csrc.nist.gov/Projects/Hash-Functions), [NIST: digital signature](https://csrc.nist.gov/glossary/term/digital_signature).

No se afirmó registro en Bitcoin ni prueba de existencia en blockchain. Tampoco es el hash de los bytes del PDF: cambiar su presentación o metadatos no modifica los datos de la credencial. Para comprobar íntegramente un PDF externo habría que verificar también sus campos visibles o introducir una firma del documento, en otro alcance.

## Datos reproducibles

`learning/certificate_integrity.py` define `btc.edu.certificate.v1`. El registro incluye UUID de certificado, nombre confirmado, título, creador, número de versión, fecha UTC con seis dígitos de microsegundos y `Z`, y SHA-256 de la evidencia histórica. La evidencia detallada continúa privada: no se exportan respuestas, notas, identificadores de alumno o correo.

La evidencia y el registro usan JSON con claves ordenadas, UTF-8, caracteres Unicode sin escape ASCII, separadores coma/dos puntos sin espacios, sin NaN y sin salto final. Se respetan los textos almacenados, sin normalización Unicode adicional. Las claves se ordenan; el orden de las listas es significativo. El archivo descargado contiene exactamente esos bytes y omite el campo de la propia huella para evitar autorreferencia.

La huella se guarda al crear la credencial, antes de validarla y persistirla. `issued_at` usa un valor inicial explícito que se conserva, en vez de un segundo tiempo calculado al guardar. El modelo inmutable impide cambios posteriores por la API ordinaria. La migración `learning.0005` añade la huella a certificados anteriores según sus datos existentes, sin modificar fecha, nombre, versión ni evidencia; este cálculo no certifica por sí solo que esos datos nunca hayan sido alterados antes de migrar.

## Recorrido y privacidad

El titular descarga datos desde `/aprendizaje/certificados/<uuid>/datos/`. Solo su cuenta tiene permiso. La ruta `/aprendizaje/verificar/<uuid>/datos/` permite descarga pública únicamente cuando habilita compartir; desactivar vuelve a producir 404. Ambas respuestas evitan caché e indexación y no envían referencias. La huella no habilita acceso ni sirve como contraseña.

Para comparar en la web, abrir la URL de verificación del certificado y pegar la huella del PDF. Para una comprobación independiente, descargar el JSON y calcular SHA-256 sobre el archivo sin editarlo. En PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath './certificado-IDENTIFICADOR.json'
```

El resultado, sin importar mayúsculas/minúsculas, debe coincidir con los 64 caracteres mostrados. La página sigue mostrando cualquier revocación aunque la huella coincida. El PDF se mantiene privado y las notas/respuestas no se publican.

## Verificación y migración

La comprobación integrada pasó 184 pruebas en 100,191 segundos, Ruff, migraciones y los tres controles de concurrencia. Después del ajuste para huellas dañadas y legibilidad se reejecutaron las 23 pruebas de funciones esenciales y la comprobación del navegador. [Salida completa](evidence/certificados-sha256-check-2026-10-10.txt).

Se añadieron cinco pruebas: persistencia y sensibilidad a cambios en identidad/evidencia; exportación reproducible y permisos; formulario válido/inválido/distinto y revocación; alteración fuera de la API inmutable; cálculo histórico sin cambiar los datos originales. También se comprueba que una huella dañada con caracteres no hexadecimales devuelve fallo de integridad. La concurrencia valida que la credencial única emitida conserva una huella correcta.

Se recalculó el archivo descargado con `crypto.createHash('sha256')` de Node, independiente del código Python, y coincidió con la huella publicada. El navegador real envió el formulario para una coincidencia y una diferencia. Escritorio y móvil no presentaron errores JavaScript ni desbordamiento horizontal. Se renderizaron los PDF normal y con textos largos: ambos conservaron una página A4 horizontal. [Verificación web](evidence/certificado-sha256-verificacion.png), [móvil](evidence/certificado-sha256-movil.png), [PDF](evidence/certificado-sha256-pdf.png).

La base principal se respaldó en `.local/backups/platform-before-certificate-sha256-20261010-095629.sqlite3` y se aplicó `learning.0005`. Se conservaron los 258 registros existentes en 50 tablas, con integridad y claves foráneas correctas. La base principal no tenía certificados que completar y no recibió ejemplos; la conservación de certificados históricos se verificó con la prueba de migración. Las filas adicionales respecto del respaldo anterior corresponden a migraciones y permisos del bloque esencial.
