# Catálogo de Bitcoin y Lightning

## Entrega

El 12 de octubre de 2026 se publicaron en la base local seis cursos introductorios, dos capítulos y cuatro lecciones por curso. La base consultada antes de la carga no contenía cursos ni perfiles de creadores. No se alteraron cuentas o cursos preexistentes. Desarrollo en `main`, sin commit ni push en esta entrega.

| Curso | Acceso | Duración estimada de actividades |
|---|---|---|
| Bitcoin desde cero: unidades, red y transacciones | Gratis | 60 minutos |
| Wallets y autocustodia: claves, respaldo y recepción | Gratis | 60 minutos |
| Lightning desde cero: canales, rutas y liquidez | Gratis | 75 minutos |
| Facturas Lightning: del QR a la confirmación | Primera lección gratis; curso 120 sats; cada lección restante 50 sats | 75 minutos |
| LNbits: organiza un laboratorio de micropagos | Primera lección gratis; curso 120 sats; cada lección restante 50 sats | 90 minutos |
| Contenido con micropagos: compra, acceso y versiones | Primera lección gratis; curso 120 sats; cada lección restante 50 sats | 90 minutos |

Cada texto incluye explicación, ejemplo, práctica y solución. Las referencias para profundizar se incluyen al final de cada lección. Los ejercicios no requieren fondos reales; los cursos avanzan desde lectura y cálculos hasta diseño de pruebas. No hay videos, archivos adjuntos ni afirmaciones de sesiones ejecutadas. Precios y tiempos son hipótesis iniciales, sin validación comercial ni medición con alumnos.

## Publicación y aprendizaje

El importador utiliza los servicios existentes de envío y decisión editorial y de ofertas, conservando sus versiones selladas. Las nueve lecciones pagadas tienen ofertas individuales y los tres cursos tienen oferta conjunta, doce ofertas activas en total. El catálogo reúne quince lecciones gratuitas y nueve pagadas.

El perfil público BTC.EDU identifica la colección institucional. Su cuenta técnica no tiene contraseña utilizable. La identidad técnica de revisión tiene permisos mínimos durante la transacción; termina inactiva, sin staff, sin permisos ni contraseña utilizable. El registro de publicación indica carga editorial solicitada y revisión educativa externa pendiente; no representa una revisión humana independiente.

Cada curso tiene una pregunta final obligatoria, tres intentos y nota mínima de 100 para esa pregunta. La política de certificado exige completar las cuatro lecciones y aprobar la comprobación. Una pregunta comprueba un concepto y no evalúa dominio completo. No se emiten certificados durante la carga.

## Carga y respaldo

Desde `src`, con el entorno virtual preparado:

```powershell
./.venv/Scripts/python.exe manage.py load_editorial_catalog --dry-run
./.venv/Scripts/python.exe manage.py load_editorial_catalog
./.venv/Scripts/python.exe scripts/verify-editorial-catalog.py
```

La vista previa solo lista títulos e inventario. La carga crea un respaldo SQLite consistente en `.local` con marca de tiempo y usa una transacción para el catálogo. Reconoce cursos existentes por perfil editorial y título y los omite; no actualiza textos ya publicados, compras ni progreso. Cambiar el archivo de contenido no actualiza automáticamente una versión existente: los cambios posteriores deben seguir el editor y revisión habituales. No se ejecuta automáticamente al arrancar ni aplica migraciones.

El respaldo de la primera carga fue `src/.local/platform-before-editorial-20261012-150754-710455.sqlite3`. La colección está en `content/editorial_catalog.py` y el comando en `content/management/commands/load_editorial_catalog.py`.

## Verificación

El script verifica una copia temporal de la base, por lo que no registra visitas de comprobación en la base principal. Dos recargas consecutivas conservaron los recuentos de cursos, versiones, lecciones, revisiones, ofertas y decisiones. Catálogo, exploración, selector y las seis fichas respondieron correctamente. Las quince lecciones gratuitas entregaron sus soluciones; las nueve pagadas devolvieron 403 sin exponer soluciones a una visita anónima. Se comprobaron ofertas individuales y conjuntas, preguntas válidas y las seis políticas de certificado. La cuenta técnica de revisión quedó sin acceso de login. Ruff pasó para los archivos añadidos.

Esta comprobación no reejecuta pagos contra LNbits, no completa los cursos como alumno ni verifica una nueva emisión de certificado. No se atribuyen resultados de la batería histórica de 210 pruebas a esta entrega. Hay cambios paralelos en perfiles y comunidad que quedan fuera de este catálogo.

## Límites y próximos pasos

Revisar el contenido con una persona experta, ampliar evaluaciones y medir duración y comprensión con alumnos. Verificar una compra y finalización de estos cursos desde navegador con el proveedor configurado. Añadir videos o materiales solo cuando estén producidos y revisados. La ampliación deja contenido recorrible en el sitio local; no acredita operación pública, demanda ni disponibilidad de atención por el perfil editorial. Las preguntas dirigidas a ese perfil requieren asignar un responsable operativo antes de abrir al público.

Las referencias técnicas consultadas son la [guía Bitcoin](https://developer.bitcoin.org/devguide/), las [especificaciones BOLT](https://github.com/lightning/bolts), el [formato BOLT 11](https://github.com/lightning/bolts/blob/master/11-payment-encoding.md) y la [guía de LNbits](https://docs.lnbits.org/). Los textos de la colección son explicaciones originales y no copias de esos manuales.
