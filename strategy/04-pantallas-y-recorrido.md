# Pantallas y recorrido

Esta es una especificación textual para construir el prototipo visual. No sustituye los wireframes de alta fidelidad pedidos por el assignment.

## Catálogo

Encabezado: marca provisional, Educación, Entretenimiento, Mi biblioteca y acceso a cuenta. Aviso breve de pagos simulados. Tarjetas con título, creador, descripción corta, formato y precio o «Gratis». Filtro por categoría y creador. El paquete educativo se identifica como paquete de dos recursos.

## Detalle individual

Título, creador, categoría, descripción y muestra pública. Educación añade objetivo, requisitos y duración orientativa. La oferta premium indica qué incluye, precio total y acceso permanente.

Visitante: «Comprar por X sats» conduce a acceso o registro. Comprador sin permiso: genera factura. Propietario: «Abrir contenido». Pieza gratuita: contenido completo disponible.

## Detalle de paquete

Objetivo, lista de las dos piezas con enlaces, precio conjunto y suma de precios individuales. Cuenta sin recursos: «Comprar paquete». Con propiedad parcial: «Ya tienes parte de este paquete» y compra individual del recurso faltante. Propietario de ambos: enlaces para abrirlos.

## Cuenta

Registro: correo, contraseña y confirmación de contraseña. Acceso: correo y contraseña. Errores legibles; no perder el destino de compra. Mostrar la ausencia de recuperación automática de contraseña en esta versión de prueba.

## Pago simulado

Oferta, piezas incluidas, importe, identificador de factura, estado y tiempo restante. No mostrar una dirección Bitcoin o QR que sugiera transferir fondos reales. Aviso: «Pago de prueba. No envíes bitcoin».

- Pending: mensaje de espera y controles separados de simulación para confirmar, fallar o expirar.
- Paid: «Pago confirmado» y acceso a la pieza o biblioteca del paquete.
- Expired: «La factura expiró» y nueva factura si sigue siendo elegible.
- Failed: explicación y reintento; si hubo conflicto de propiedad, llevar a biblioteca u oferta actualizada.
- Error de conexión: permitir consultar de nuevo el estado de la misma factura, sin asumir fallo ni generar automáticamente otra.

## Biblioteca y lector

Biblioteca: piezas adquiridas, fecha y botón para abrir. Estado vacío: explicación y enlace al catálogo. Las compras de paquete se muestran como recursos utilizables individualmente.

Lector: título, creador y cuerpo protegido; navegación de regreso a biblioteca. No implementar progreso académico. Si la sesión vence, solicitar acceso conservando el destino.

## Administración

Listado de piezas con edición básica y visibilidad. Tabla de facturas con filtros. Resumen de métricas y actividad por categoría y modalidad. Etiquetar importes como sats simulados.

## Guiones para el prototipo

1. Visitante ve guía gratuita, revisa premium, se registra, compra y abre.
2. Comprador adquiere paquete y encuentra dos piezas en biblioteca.
3. Seguidor explora muestra de entretenimiento y compra exclusiva.
4. Pago expira o falla, se reintenta y se confirma.
5. Propietario parcial revisa paquete y compra únicamente el recurso faltante.
6. Usuario vuelve desde otro navegador y recupera biblioteca.
