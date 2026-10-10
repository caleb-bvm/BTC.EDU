# Reglas de los módulos educativos

## Cobertura actual

Evaluaciones entregadas el 7 de octubre. Certificados, preguntas, notificaciones internas y paneles esenciales entregados el 10 de octubre de 2026. [Implementación, rutas, pruebas y límites](../src/docs/esenciales-2026-10-10.md). Esta especificación registra las reglas efectivamente adoptadas; comunidad y membresías continúan en el diseño de 08/11, pendientes de implementación y de políticas detalladas de moderación y acceso temporal.

## Certificados

El creador aprobado configura únicamente sus cursos. Habilitar requiere una o más lecciones incluidas; todos los cuestionarios obligatorios también deben aprobarse. La política se conserva con el envío editorial y la versión publicada. La compra individual, inscripción o pago del conjunto no emiten la credencial.

El alumno confirma su nombre y solicita emisión cuando cumple los requisitos históricos. Una inscripción concede como máximo una credencial, independiente de reintentos y concurrencia. Se conserva nombre, título, creador, fecha, versión y evidencia de lecciones e intentos. No se modifica por ediciones futuras o por cambios posteriores en progreso.

El PDF es privado. La verificación usa UUID y requiere que el titular habilite compartir; puede desactivarlo. La página compartida no divulga correo, notas ni respuestas. La administración revoca con permiso específico y motivo, preservando historial y notificando al alumno. Revocar bloquea nuevas descargas; no borra archivos ya descargados. Corregir o reemplazar nombres después de emitir queda pendiente: se exige confirmación previa y atención administrativa de incidencias.

Aceptación comprobada: requisitos pendientes no permiten emitir; todos los obligatorios se cumplen; una solicitud repetida/concurrente no duplica; borradores ajenos y revisiones antiguas no sobrescriben políticas; versiones anteriores mantienen sus datos; compartir es voluntario; terceros no descargan; revocar conserva evidencia. Pruebas en `learning/test_essential.py` y `scripts/verify-essential-concurrency.py`.

## Preguntas

Crear requiere cuenta activa de alumno, inscripción en la misma versión y acceso a la lección. Leer corresponde al alumno participante y al creador aprobado propietario. Responder requiere esos permisos; el alumno además conserva acceso al contenido. Las conversaciones son privadas, sin foro público ni permiso administrativo general por estas rutas.

Entradas de texto de hasta 2.000 caracteres, paginación, escape HTML y 30 mensajes por cuenta/hora. El historial enviado es inmutable; se corrige mediante una aclaración. La clave del formulario permite recuperar reintentos sin duplicar; otra carga con la misma clave se rechaza. No hay archivos, edición, eliminación, cierre manual ni garantía de atención. La bandeja identifica las conversaciones cuyo último mensaje espera respuesta del creador.

Aceptación comprobada: denegación por cuenta ajena, curso ajeno, falta de acceso/inscripción y suspensión; persistencia y aislamiento; reintentos/concurrencia; escape; límite y CSRF; respuesta asociada a la lección y su versión. Los permisos de lectura conservada no acreditan que existan membresías implementadas.

## Notificaciones

Cada acontecimiento genera como máximo un aviso por clave interna. Destinatario y enlace se determinan en servidor. Los eventos implementados son preguntas/respuestas, decisiones editoriales, intentos adicionales y emisión/revocación. La cuenta consulta su propia bandeja/contador; abrir y marcar leído es POST protegido y repetirlo conserva la primera fecha. Son avisos internos, sin entrega de correo ni notificaciones push.

## Paneles

El creador consulta métricas agregadas de sus contenidos. La administración exige permisos de lectura de facturas, inscripciones y actividad. Fuentes, cohortes, denominadores, periodos y cobertura están en [05](05-metricas-y-validacion.md) y el registro técnico. Se muestran ceros y ausencia de datos sin inventar resultados anteriores. Visitas, marcas manuales, aprobaciones y certificados son hechos técnicos distintos de aprendizaje comprobado.

## Límites de alcance

La entrega esencial solicitada queda implementada y verificada. Mantener separadas las ampliaciones: comunidad con moderación, membresías de renovación manual de 30 días, correcciones de credenciales, reproducción medida y operación pública. Las pruebas con cuentas temporales no equivalen a sesiones con personas ni a validación de precios o demanda.
