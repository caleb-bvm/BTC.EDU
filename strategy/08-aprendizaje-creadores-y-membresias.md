# Funciones de aprendizaje y creación

Este documento amplía el alcance e invalida exclusiones anteriores. Es diseño sustentado en 07, no requisitos adicionales del assignment. Cuentas, publicación, creadores y progreso básico están registrados como implementados al 4 de octubre; las evaluaciones se entregaron el 7 de octubre; certificados, preguntas, notificaciones y paneles esenciales se entregaron el 10 de octubre. Comunidad, membresías, reproducción medida y operación pública siguen pendientes. Ver [estado](../src/README.md).

La [comparación comercial](13-monetizacion-precios-y-muestras.md) documenta posibilidades, no demanda. Las [sesiones propuestas](16-validacion-con-usuarios.md) deberán evaluar necesidades y comprensión. No cambia renovación manual de 30 días ni derechos históricos. Probar módulos pendientes en prototipos identificados.

La [arquitectura y experiencia del 2 de octubre](10-arquitectura-y-experiencia-btc-edu.md) conserva este alcance completo y escalona las entregas: primero academia con cursos/tutoriales/recursos, compra y progreso básico; luego operación por creadores y módulos ampliados. Las estimaciones de este documento preceden esa definición; deben revisarse, no reutilizarse como compromiso para el alcance nuevo.

## Evaluaciones entregadas

Al 7 de octubre funcionan selección única/múltiple, preguntas con igual peso y coincidencia exacta, límites, espera, guardado/retoma y soluciones al entregar o al aprobar. Iniciar consume un intento; el abierto se retoma sin consumir otro. La evaluación obligatoria exige aprobación antes de completar la lección. Autorizar un intento adicional conserva motivo e historia y no borra notas ni elimina espera. Preguntas y reglas se congelan con la composición enviada a revisión. [Recorrido, pruebas y límites](../src/docs/evaluaciones-2026-10-07.md).

## Entrega esencial

Las reglas efectivamente implementadas se conservan en [15](15-especificaciones-modulos-pendientes.md) y [evidencia técnica](../src/docs/esenciales-2026-10-10.md). El alumno confirma su nombre antes de emitir; compartir es voluntario y la revocación conserva motivo. Corregir o reemplazar credenciales queda pendiente. Preguntas privadas y avisos internos funcionan; el foro comunitario y correo no forman parte de esta entrega. Las condiciones futuras descritas abajo, como porcentaje observado de video y membresías, siguen siendo diseño.

## Alumno

Puede explorar sin cuenta. Necesita cuenta para conservar progreso, participar, realizar evaluaciones y comprar. Inscribirse en un curso gratuito es gratis y no compra sus extras. La pantalla principal muestra Continuar aprendiendo, cursos inscritos, compras, membresías, preguntas, notificaciones y certificados.

Progreso: guardar la posición del video y el estado de cada lección por cuenta. Marcar una lección como completada no demuestra dominio. Las lecciones sin evaluación pueden completarse manualmente; el creador puede exigir un porcentaje de video observado, indicando la regla. No contar saltar al final como observarlo completo. Las evaluaciones obligatorias requieren aprobar para completar la lección. El aprendizaje se conserva aunque termine el acceso temporal.

Evaluaciones: preguntas de selección única y múltiple, explicaciones y nota mínima entre 0 y 100; número de intentos y espera configurables. Antes de empezar se muestran reglas. Corregir en el servidor, guardar intentos y devolver explicaciones al cerrar el intento según configuración. Los reinicios de intentos por creador se registran con motivo. La primera versión no incluye vigilancia remota ni corrección automática de ensayos.

Certificados: un curso indica si ofrece certificado y cuáles son sus lecciones y evaluaciones obligatorias. Completar el conjunto requerido y aprobar las evaluaciones emite una sola credencial por alumno y versión del curso. Comprar o terminar un video individual no emite el certificado del curso. Descargar PDF y consultar una página de verificación con identificador no predecible. Mostrar nombre del alumno, curso, creador, fecha y condición de finalización; el usuario elige compartir el enlace. No afirmar acreditación oficial.

## Creador y publicación

Una persona registra una cuenta de creador independiente de su cuenta de estudiante y solicita aprobación al administrador. El creador gestiona únicamente sus cursos y materiales: perfil, objetivos, requisitos, temario, videos, textos, archivos, subtítulos, muestras, precios, evaluaciones, certificados y comunidad. Esta separación fue confirmada el 3 de octubre; reutilizar correo no comparte contraseña, perfil ni actividad entre cuentas.

Estados de publicación: Draft, InReview, Published, ChangesRequested y Archived. El creador puede guardar borradores y verlos como alumno sin hacerlos públicos. Envía a revisión cuando contiene los campos, muestras y archivos necesarios. El administrador aprueba o devuelve observaciones. Modificar un curso publicado prepara otra versión; no cambia silenciosamente lo incluido en compras o los requisitos de certificados ya emitidos.

El creador puede archivar una oferta sin eliminar compras previas. Los cambios de precio solo afectan nuevas facturas. Los cambios de composición no alteran compras confirmadas. Para el primer lanzamiento, congelar la composición publicada y permitir correcciones que no retiren recursos; la ampliación de un curso requiere versionar y declarar si se concede a alumnos existentes.

Panel: cursos y borradores, revisión, preguntas por responder, comunidad, alumnos inscritos, progreso agregado, resultados de evaluaciones, compras y volumen simulado. No hay pagos reales a creadores ni liquidaciones todavía.

## Comunidad

Espacios por curso o creador con publicaciones y respuestas; además preguntas vinculadas a una lección. Definir si el espacio es público para leer, requiere inscripción gratuita, compra de curso o membresía activa. Escribir requiere cuenta y el permiso del espacio.

El creador modera sus espacios; el administrador puede intervenir globalmente. Reportar, ocultar, cerrar conversación y suspender escritura, con motivo y registro. Sanear texto, limitar frecuencia y paginar. No incluir chat privado ni archivos en comentarios en la primera versión. Conservar historial de decisiones. La cancelación de membresía conserva progreso y compras, pero puede terminar el permiso de participar en un espacio exclusivo al vencer el periodo.

## Membresías y suscripciones

Un creador ofrece planes con precio, duración y contenidos enumerados. Una membresía concede acceso temporal al conjunto incluido y a los espacios indicados. Puede coexistir con compras individuales permanentes. Un curso gratuito sigue gratis aunque el creador tenga planes.

Implementación inicial: periodos de 30 días con facturas LNbits simuladas; renovación mediante una nueva factura confirmada por el usuario. Cancelar la renovación no quita el periodo ya pagado. Al vencer, deja de abrir contenidos disponibles solo por membresía; conserva compras permanentes, progreso y certificados. No borrar datos educativos por impago.

La primera versión demuestra suscripciones renovables, pero no cobra automáticamente una wallet. Una renovación automática real requiere un mecanismo autorizado y una integración específica que LNbits no proporciona por el mero hecho de crear facturas. No presentar un cobro manual como automático.

Confirmar dos veces la misma factura no extiende dos veces la membresía. Renovar antes de vencer extiende desde la fecha final vigente; renovar después de vencer inicia desde la confirmación. Una compra permanente permite abrir aunque la membresía haya vencido. Cambiar precio o contenidos crea una nueva versión del plan y muestra condiciones antes del siguiente pago.

## Cuentas y soporte

Separar roles y permisos por propiedad. Añadir recuperación de contraseña con token de un solo uso, con vencimiento y correo transaccional configurable. En desarrollo usar una bandeja local de correo; en despliegue se necesita configurar el proveedor y probar entrega. Notificaciones internas por respuesta, revisión, certificado y próxima renovación. No enviar mensajes reales desde esta investigación.

## Compra parcial de curso

Mantener provisionalmente el bloqueo de oferta conjunta si hay propiedad parcial y ofrecer lo faltante. Las referencias consultadas no justifican esa regla como estándar. Probar comprensión y conveniencia frente a cobrar únicamente recursos faltantes; si elegimos el segundo comportamiento, definir cálculo de precio y conflictos antes de implementarlo. No cambiar la regla silenciosamente.

## Criterios adicionales

| ID | Prueba | Resultado esperado |
|---|---|---|
| AC-21 | Retomar en otro dispositivo | Misma posición guardada y lecciones completadas |
| AC-22 | Abrir curso gratuito | Inscripción sin compra; extras de pago siguen identificados |
| AC-23 | Enviar evaluación | Nota calculada en servidor; intento registrado y límite aplicado |
| AC-24 | Comprar curso sin terminarlo | No se emite certificado |
| AC-25 | Completar requisitos y repetir solicitud | Un certificado verificable por alumno y versión |
| AC-26 | Creador modifica curso ajeno | Acceso denegado |
| AC-27 | Enviar borrador a revisión | No es público hasta aprobación; observaciones visibles al autor |
| AC-28 | Reportar comentario | Moderación autorizada con registro; terceros no leen espacio restringido |
| AC-29 | Activar membresía mediante pago | Acceso temporal solo al contenido incluido |
| AC-30 | Cancelar renovación | Acceso hasta fin del periodo; no se crea renovación posterior |
| AC-31 | Vencer membresía con compra individual | Compra, progreso y certificado permanecen |
| AC-32 | Repetir confirmación de renovación | Un solo periodo añadido |
| AC-33 | Cambiar temario después de certificado | Certificado conserva su versión y requisitos cumplidos |
| AC-34 | Recuperar contraseña | Token vence y no se reutiliza; no se revelan claves |
| AC-35 | Pregunta y respuesta por lección | Alumno ve respuesta y aviso; creador ve su bandeja |

## Fases y esfuerzo orientativo

Una jornada significa un día de trabajo técnico concentrado de una persona. Son estimaciones preliminares del equipo, no datos de las plataformas ni una promesa de plazo. No incluyen producir cursos, investigación con participantes ni operación del sitio.

| Fase | Entrega verificable | Jornadas estimadas |
|---|---|---|
| 1 | Cuentas, catálogo, cursos, compra y protección de contenido | 5–7 |
| 2 | Creador, editor, cargas, revisión y versiones básicas | 4–6 |
| 3 | Progreso, evaluaciones y certificados | 4–6 |
| 4 | Preguntas, comunidad y moderación | 3–5 |
| 5 | Membresías, renovación y convivencia con compras | 3–5 |
| 6 | Métricas, accesibilidad, integración, pruebas y documentación | 4–6 |

Total orientativo: 23–35 jornadas técnicas, con trabajo de diseño y pruebas de Business en paralelo. Hasta el 3 de noviembre hay 33 días transcurridos desde el 1 de octubre; eso no equivale a 33 jornadas disponibles. Con un Dev, la capacidad y las dependencias deben comprobarse con las primeras entregas. El cierre del 15 de octubre no es una base realista para comprometer toda esta lista sin estimación adicional. Proponemos usar el sprint completo como planificación de trabajo, sujeto al acuerdo del equipo.

Hito del 13 de octubre: demostrar plataforma navegable, curso gratuito, compra de capítulo o video, acceso protegido y editor de creador en el estado alcanzado. Registrar lo que de verdad esté construido. Después integrar las otras funciones por dependencia y cerrar cambios antes de la entrega confirmada. Revisar las estimaciones al terminar la fase 1; mantener todo en el diseño y declarar honestamente lo implementado en la entrega.
