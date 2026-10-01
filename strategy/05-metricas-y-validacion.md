# Métricas y validación

## Eventos

| Evento | Disparador | Fuente |
|---|---|---|
| offer_viewed | Se abre un detalle individual o de paquete | Interfaz |
| preview_viewed | La muestra se presenta al usuario | Interfaz |
| invoice_created | Se crea una factura nueva, no se reutiliza otra | Servidor |
| payment_paid | Una factura cambia a Paid | Servidor |
| payment_failed | Una factura cambia a Failed | Servidor |
| payment_expired | Una factura cambia a Expired | Servidor |
| premium_content_opened | El servidor entrega correctamente una pieza a su propietario | Servidor |
| library_viewed | Comprador abre su biblioteca | Interfaz |

Campos según corresponda: ID de evento, fecha UTC, ID de sesión, ID interno de cuenta, oferta, recurso, factura, categoría y modalidad individual o paquete. No incluir contraseña, cuerpo protegido ni correo en los eventos. Una sesión usa un identificador aleatorio; no se identifica a visitantes entre dispositivos.

La clasificación freemium es una estrategia de catálogo, no un tercer tipo de factura. Cada confirmación terminal se registra una sola vez por factura. Las aperturas repetidas son eventos separados. Se informa de aperturas, no de lectura completa ni aprendizaje.

## Indicadores

Todas las métricas muestran el intervalo de fechas aplicado y su denominador. Cuando es cero, mostrar «Sin datos». Las métricas comerciales usan cuentas compradoras; se excluyen cuentas de administrador.

| Indicador | Definición |
|---|---|
| Conversión a solicitud | Pares sesión-oferta con invoice_created / pares sesión-oferta con offer_viewed, entre ofertas de pago y eventos dentro del intervalo |
| Finalización de pago | Facturas Paid / facturas creadas durante el intervalo, considerando su estado actual y mostrando cuántas siguen Pending |
| Apertura después de compra | Permisos adquiridos en el intervalo con al menos una apertura posterior / permisos adquiridos en el intervalo |
| Regreso a biblioteca | Compradores con library_viewed en una sesión posterior a la sesión de compra / compradores del intervalo |
| Compra repetida | Compradores del intervalo con al menos dos facturas Paid al cierre de la consulta / compradores del intervalo |
| Volumen simulado | Suma del importe de facturas Paid; un paquete se cuenta una vez |

En apertura, cada paquete aporta dos permisos. En transacciones y volumen aporta una compra. Las métricas de regreso y repetición son exploratorias para muestras pequeñas; no tienen todavía objetivos numéricos validados.

## Plan de investigación

Business buscará de tres a cinco compradores educativos, de tres a cinco consumidores de entretenimiento y, si es posible, al menos un creador por categoría. Es una muestra exploratoria propuesta, no un reclutamiento realizado ni una estimación estadística.

Preguntar por la última necesidad concreta, recursos utilizados, compras anteriores, motivos para pagar o desistir y alternativas gratuitas. Explorar precios después de conocer la necesidad. Evitar presentar aceptación del concepto como compra real.

Para creadores: contenido disponible, derechos de uso, audiencia, esfuerzo de mantenimiento y preferencia entre venta individual y paquetes educativos.

## Pruebas de experiencia

Solicitar encontrar un recurso, explicar lo incluido, comprar con simulación, resolver una factura expirada y regresar a biblioteca. En educación, comparar compra individual y paquete, incluido el caso parcialmente adquirido.

Registrar tarea, resultado, dificultad, cita autorizada y cambio propuesto. Obtener consentimiento para notas o grabaciones. Separar pruebas manuales del equipo de sesiones con participantes externos.

## Entregables pendientes

Comparación documentada de suscripción, publicidad, freemium y micropagos; resultados de entrevistas; prototipo visual; informe de usabilidad; revisión de precios; recomendación final con limitaciones. No se han completado todavía. Los datos del simulador no prueban ingresos reales ni voluntad de pago.
