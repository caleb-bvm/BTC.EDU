# Experiencia de compra

Actualización del **4 de octubre de 2026**, El Salvador, solicitada por el usuario: desarrollar una experiencia de producto con lenguaje y estados propios de una compra. Commit funcional: `d36b152`.

## Recorrido entregado

Revisar contenido y resumen → **Continuar al pago** → factura con importe, referencia y vencimiento → **Pagar [importe] sats** → **Tu compra está confirmada** → abrir contenido o biblioteca.

Catálogo, opciones de acceso, historial, estudio y revisión comercial muestran precios en sats. Se retiraron «Simular pago», «Crear factura de prueba», «compra de prueba» y avisos antiguos que afirmaban que las compras no estaban disponibles. Los ejemplos temporales usan descripciones educativas sin repetir el lenguaje de demostración.

Al enviar un formulario se deshabilita su botón y se muestra «Preparando tu pago», «Procesando tu pago» o «Comprobando el pago», durante la petición real. Volver mediante el historial restaura el botón. No se simulan porcentajes de avance ni resultados exitosos. La acción de pago viaja en un campo oculto para conservarla aunque el botón esté deshabilitado. El formulario también funciona sin JavaScript.

La confirmación muestra la fecha registrada de compra y acceso permanente; el vencimiento solo se presenta mientras el pago está pendiente. Ante respuesta incierta se indica consultar la misma factura antes de pagar otra vez. Una incidencia informa que el pago requiere revisión y que no se activó acceso nuevo, sin exponer claves ni detalles de infraestructura.

## Entorno y operación

Cuando `COMMERCE_SIMULATION` está activo, la plantilla común muestra una sola indicación: **«ENTORNO DE DESARROLLO · Pagos con saldo de prueba.»** Sustituye el aviso de vista previa en este entorno. No se repite en los precios ni en cada acción comercial. Depende de configuración del servidor, no de parámetros del navegador.

Los pagos siguen usando exclusivamente LNbits local con FakeWallet verificado. Se mantienen comprobación del proveedor, importe e inventario congelados, permisos, CSRF, idempotencia y registro de incidencias. La nueva acción de formulario es `pay`; se acepta `simulate` por compatibilidad con formularios abiertos previamente. Los nombres técnicos de simulación permanecen en el adaptador, pruebas y documentación donde describen su comportamiento real.

No se habilitaron fondos reales, QR Lightning ni una wallet externa del estudiante. El método actual paga con la wallet ficticia del entorno. Eliminar el aviso o cambiar una variable no convierte este adaptador en un proveedor para producción. Integrar el método de pago del cliente, supervisión periódica y operación comercial sigue pendiente. La base principal no recibió cuentas ni contenido de demostración; el navegador usó la base temporal de preview.

## Verificación

- **60 pruebas relacionadas aprobadas:** comercio, base/páginas, descubrimiento y archivos/versiones. Se adaptaron las pruebas existentes al formulario y precios nuevos; no se repitió la suite completa de 129 del bloque previo.
- Ruff y comprobación de migraciones pasan. No hay migraciones nuevas.
- Smoke contra LNbits FakeWallet pasa con `action=pay`, sesión y CSRF; conserva comprobaciones de respuesta perdida, derechos y compra única.
- Navegador: resumen → continuar reutilizando factura → pagar 150 sats → compra confirmada con acceso. Se comprobó móvil/escritorio sin desbordamiento horizontal de la confirmación, con anchos efectivos de 325/1200 px. El formulario con JavaScript habilitado pagó y confirmó correctamente.
- Capturas del resultado visible: [escritorio](evidence/checkout-confirmado-escritorio.jpg) y [móvil](evidence/checkout-confirmado-movil.jpg).

Las capturas anteriores de comercio conservan el aspecto histórico del bloque inicial. Este registro actualiza su lenguaje y presentación. No se hizo push ni despliegue.
