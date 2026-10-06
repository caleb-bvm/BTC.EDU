# Pantallas y recorrido

Este documento conserva los recorridos comerciales originales. La estructura de navegación y pantallas vigente está en [arquitectura y experiencia](10-arquitectura-y-experiencia-btc-edu.md): Cursos (Todos/Selector), Tutoriales, Recursos, Mi aprendizaje y Compras y acceso. Hay dirección visual aprobada y pantallas base implementadas; los prototipos de las nuevas vistas y su validación con usuarios siguen pendientes.

## Inicio y catálogo

Mostrar cursos, videos y materiales con filtros por tema, formato y gratis o de pago. Cada tarjeta indica título, creador, descripción y precio cuando corresponde. Un curso con lecciones gratuitas y otras de pago muestra esa combinación sin sugerir que todo está incluido gratis. Navegación: Cursos, Videos, Materiales, Mis cursos y compras, y Cuenta.

## Curso

Descripción, objetivo, requisitos, creador y capítulos ordenados. Cada lección indica formato y si es gratuita, comprada o de pago. Los cursos de pago enumeran lo incluido y el precio completo. Los materiales adicionales muestran si están incluidos, son gratis o se compran aparte.

En cursos gratuitos con compras opcionales, abrir las lecciones gratis no exige comprar nada. Un capítulo de pago muestra su precio y contenidos. Un curso parcialmente adquirido ofrece los capítulos faltantes; el totalmente adquirido permite abrirlos.

## Lección, video y material

Lección: texto o reproductor, navegación entre lecciones y materiales asociados. Video individual: descripción, muestra independiente y compra de ese video. Material: descripción, formato, muestra y botón de descarga cuando sea gratis o esté comprado. La compra no exige completar lecciones previas.

Quien ya compró ve Abrir o Descargar. Antes de comprar se muestra exactamente qué recibe y el precio en sats de prueba.

## Cuenta y compras

Registro y acceso con correo y contraseña, conservando el destino elegido. Enlace para recuperar contraseña mediante correo y token de un solo uso. Mis cursos y compras organiza cursos, capítulos, videos y materiales adquiridos, con fecha y enlaces para abrir. Muestra progreso guardado, última lección y posición de video, distinguiendo lo disponible por compra o membresía.

## Pago simulado

Oferta, contenidos incluidos, importe, identificador, estado y tiempo restante. Aviso visible: Pago de prueba. No envíes bitcoin. No mostrar QR ni instrucciones para transferir fondos reales.

Pending: espera y controles de simulación separados. Paid: confirmación y enlaces al contenido. Expired o Failed: motivo y reintento si corresponde. Conflicto por compra previa: llevar a las compras o a la oferta actualizada. Error de conexión: consultar el estado de la misma factura.

## Administración

Gestión de cursos, capítulos, lecciones, videos, materiales, muestras, precios y visibilidad. Tabla de facturas y resumen de actividad. Los importes se identifican como sats simulados.

## Recorridos para demostrar

El [plan de validación](16-validacion-con-usuarios.md) observará elección, inclusiones/extras, compra individual, vencimiento, recuperación y compra parcial, además del editor/revisión/versiones para creadores. Registrar ayudas, errores y versión; no revelar caminos en los enunciados. Probar solo módulos disponibles o prototipos identificados. Las sesiones externas siguen pendientes.

1. Abrir un curso completamente gratuito.
2. Abrir una lección gratis y comprar un capítulo del mismo curso.
3. Comprar material adicional de un curso gratuito.
4. Comprar un video individual sin comprar el curso.
5. Comprar un curso completo y comprobar lo incluido y los extras excluidos.
6. Resolver pago fallido o vencido y recuperar compras en otro navegador.
7. Comprobar que el servidor bloquea videos y archivos de pago sin compra.

## Pantallas de aprendizaje, creadores y membresías

Probar las [variantes de muestra](13-monetizacion-precios-y-muestras.md) antes de fijar proporciones. La estética aprobada no demuestra comprensión. Una equivalencia USD es solo propuesta de investigación para comprensión de sats, no una función entregada ni un cambio de moneda.

Continuar aprendiendo con posición guardada. Evaluación con instrucciones, nota requerida, intentos, envío y resultado. Certificados con requisitos pendientes, descarga y verificación. Preguntas por lección y comunidad con publicaciones, respuestas y reportes. Notificaciones internas y recuperación de contraseña.

Panel de creador con borradores, editor de temario, cargas, muestras, precios, evaluaciones, criterios de certificado, vista como alumno, revisión, respuestas y métricas propias. Panel administrador con revisión de versiones y moderación.

Membresías: comparar planes, contenidos incluidos, duración, pago de prueba, renovación manual, fecha de vencimiento y cancelación. Separar biblioteca comprada de acceso temporal sin borrar progreso.

Añadir pruebas: retomar video en otro dispositivo; aprobar evaluación y emitir certificado; publicar curso mediante revisión; preguntar y moderar; renovar o cancelar membresía conservando compras individuales.


