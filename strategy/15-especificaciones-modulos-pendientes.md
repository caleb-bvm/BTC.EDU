# Reglas de los módulos educativos

## Cobertura actual

Evaluaciones entregadas el 7 de octubre. Certificados, preguntas, notificaciones internas y paneles esenciales entregados el 10 de octubre de 2026. [Implementación, rutas, pruebas y límites](../src/docs/esenciales-2026-10-10.md). Esta especificación registra las reglas efectivamente adoptadas; comunidad y moderación se incorporan el 10 de octubre; las membresías y el acceso temporal siguen pendientes.

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

La entrega esencial solicitada queda implementada y verificada. Mantener separadas las ampliaciones pendientes: membresías de renovación manual de 30 días, correcciones de credenciales, reproducción medida y operación pública. Las pruebas con cuentas temporales no equivalen a sesiones con personas ni a validación de precios o demanda.

## Huellas de certificados

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital ni un registro en Bitcoin.

Implementado y verificado el 10 de octubre. [Contrato, privacidad, migración y pruebas](../src/docs/certificados-sha256-2026-10-10.md). La exportación permite recalcular exactamente los bytes JSON; no representa el hash de todo el PDF.

## Comunidad y moderación

Se adopta un espacio por versión publicada y sellada, accesible a alumnos activos inscritos en esa versión y al creador aprobado propietario. La inscripción habilita comunidad, sin conceder contenidos de pago. Las versiones históricas conservan su comunidad; no hay espacios públicos ni acceso por membresía en esta entrega. La administración requiere staff y el permiso learning.moderate_community.

Conversaciones con respuestas de un nivel, texto escapado hasta 2000 caracteres, 30 publicaciones por cuenta/hora y paginación de 20. Los mensajes enviados no se editan ni borran; las correcciones son aclaraciones. Reintentos con UUID conservan un solo mensaje. Reportar requiere motivo, con un reporte por cuenta/mensaje y límite de 30 nuevos por hora. No hay archivos ni chat privado.

Ocultar/mostrar, cerrar/reabrir y descartar reportes requieren motivo e historial. Suspender escritura afecta a un alumno inscrito y una versión, preservando lectura, compras y progreso; restablecer requiere otra decisión. Ocultar una raíz impide leer sus respuestas a los alumnos, conservando acceso para moderadores. La suspensión permanece hasta revisión manual. El creador atiende reportes y la administración puede intervenir; no hay plazo garantizado, apelación por formulario ni escalamiento automático. Los avisos internos cubren respuestas al autor, reportes al creador y decisiones al participante afectado.

Aceptación y límites verificables en [registro técnico](../src/docs/comunidad-2026-10-10.md), learning/test_community.py y scripts/verify-community-concurrency.py. No equivale a operación pública ni validación con personas.
