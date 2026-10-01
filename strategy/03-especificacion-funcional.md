# Especificación funcional

Todos los requisitos de este documento son obligatorios para el MVP. Las decisiones técnicas quedan a cargo del Dev siempre que cumplan estas reglas.

## Identidad y permisos

Visitante: catálogo, perfiles informativos, recursos gratuitos y muestras. Comprador: lo anterior, compras y biblioteca propia. Administrador: gestión básica del catálogo, transacciones y métricas globales.

Registro con correo y contraseña; inicio y cierre de sesión. El correo identifica la cuenta, pero no prueba que su propietario haya sido verificado. El MVP no enviará correos de verificación ni recuperación automática. La limitación será visible en la documentación; para la demo se usarán cuentas de prueba. La biblioteca debe recuperarse con las mismas credenciales desde otro navegador.

El comprador no puede consultar facturas o permisos ajenos. El administrador no obtiene automáticamente permisos de compra: usa su vista de administración para gestionar contenido.

## Facturas y simulación

Una factura pertenece a una cuenta y una oferta individual o paquete. Conserva el precio y los recursos incluidos al generarse. Una modificación posterior del precio no cambia esa factura.

Estados: Pending, Paid, Expired y Failed. Una factura nace Pending y vence 15 minutos después de su creación. Pending puede pasar a uno de los otros tres estados; los estados terminales no cambian.

El área de demostración permite confirmar, fallar o expirar la factura mediante el servicio simulado. El vencimiento también se aplica al transcurrir el plazo. La interfaz identifica estos controles como simulación. El servidor verifica propietario, estado y plazo: el navegador no puede concederse acceso directamente.

Al confirmarse antes del vencimiento, el sistema registra el pago y concede los permisos automáticamente. No habrá una confirmación manual adicional por el administrador. Cuando falla o expira, se ofrece generar una nueva factura al precio vigente, sin borrar el historial anterior.

Una cuenta solo mantiene una factura Pending vigente por oferta. Al solicitarla otra vez, se devuelve la existente. No hay devoluciones ni cancelaciones voluntarias en el MVP, y no se transfieren fondos reales.

## Acceso y paquetes

La biblioteca muestra recursos adquiridos y fecha de adquisición. El pago de paquete concede permisos para sus dos recursos. Los registros de compra y acceso sobreviven a recargas y reinicios.

Las piezas adquiridas muestran «Abrir contenido» en lugar de comprar. El paquete parcialmente adquirido queda bloqueado para compra y muestra los recursos faltantes. El completamente adquirido muestra «Ya tienes todos los recursos».

Antes de crear una factura de paquete se comprueba elegibilidad. Antes de confirmarla se vuelve a comprobar que ningún recurso se haya adquirido por otra factura: si existe solapamiento, la factura pendiente pasa a Failed con motivo de conflicto y no concede permisos. En el simulador no existe cobro externo que reembolsar. La misma regla evita compras duplicadas en facturas individuales concurrentes.

El contenido protegido se entrega únicamente tras verificar permiso en el servidor. No se incluye escondido en HTML, respuestas públicas, datos iniciales del navegador ni archivos estáticos públicos.

## Administración

Un administrador puede crear y editar piezas, descripción, muestra, contenido y precio. Puede ocultar una pieza del catálogo sin eliminar compras ni impedir el acceso de propietarios. No podrá eliminar piezas adquiridas. El paquete inicial tiene composición fija.

Ve fecha, identificador de factura, oferta, cuenta compradora, importe y estado; filtra por estado. No muestra contraseñas ni credenciales. Consulta métricas definidas en el documento 05. El panel queda protegido por rol.

## Criterios de aceptación

| ID | Escenario | Resultado verificable |
|---|---|---|
| AC-01 | Visitante explora y filtra | Puede encontrar ambas categorías y consultar contenido gratuito sin cuenta |
| AC-02 | Visitante pide contenido premium por URL o API | El servidor no entrega el cuerpo protegido |
| AC-03 | Visitante intenta comprar | Se solicita acceso o registro y se conserva el destino elegido |
| AC-04 | Comprador confirma factura individual vigente | Estado Paid, un permiso y acceso automático a la pieza correcta |
| AC-05 | Comprador confirma paquete elegible | Una transacción y dos permisos; ambas piezas aparecen en biblioteca |
| AC-06 | Factura pendiente, fallida o expirada | No concede acceso; un reintento válido crea otra factura |
| AC-07 | Se repite la misma confirmación | No duplica transacción, permisos ni evento de pago |
| AC-08 | Se recarga o reinicia el servicio | Compras, estados y biblioteca permanecen |
| AC-09 | Se entra desde otro navegador con la misma cuenta | Se recuperan los recursos adquiridos |
| AC-10 | Otra cuenta consulta factura o contenido ajeno | Se deniega el acceso |
| AC-11 | Cuenta posee parte o todo el paquete | Compra bloqueada según la regla y recursos faltantes visibles |
| AC-12 | Dos facturas generan un solapamiento | Solo la primera confirmación elegible concede acceso; la otra falla sin duplicar compra |
| AC-13 | Confirmación llega tras el vencimiento | Estado Expired y ningún permiso nuevo |
| AC-14 | Se modifica el precio después de facturar | La factura conserva el precio original |
| AC-15 | Comprador abre administración | Acceso denegado; administrador ve transacciones y métricas |
| AC-16 | Uso móvil y escritorio | Catálogo, pago y biblioteca se pueden completar sin controles inaccesibles |
| AC-17 | Se oculta una pieza comprada | Desaparece del catálogo pero sigue disponible en la biblioteca |

## Fuera del MVP

Integración Bitcoin/Lightning real, videos o archivos protegidos, carga pública por creadores, comisiones, liquidaciones, membresías, progreso de curso, certificados, recomendaciones y descuentos por propiedad parcial. Documentar posibilidades futuras sin presentar estas funciones como implementadas.
