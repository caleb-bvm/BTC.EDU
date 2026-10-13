# Perfiles y comunidad

## Estado actual

Los estudiantes editan su nombre de cuenta, alias, presentación, intereses y sitio web en `/cuenta/perfil/`. El alias identifica sus mensajes, aunque mantengan privada la presentación. Sin alias se muestra «Participante»; el nombre legal y el correo no se utilizan como sustitutos en las conversaciones. Las cuentas existentes reciben campos vacíos y privacidad activada por defecto.

Compartir el perfil es voluntario y requiere un alias. `/personas/<id>/` muestra la presentación pública; un perfil privado solo lo consulta su propietario. Desactivar compartir retira el perfil del directorio y su acceso público. No publica compras, inscripciones, progreso, notas, preguntas privadas ni certificados. Los certificados conservan su mecanismo independiente de compartición. El alias no es único y no constituye verificación de identidad.

Los creadores conservan su formulario, solicitud y aprobación en `/crear/solicitud/`. Su nombre público, biografía, especialidad, sitio y catálogo provienen de `CreatorProfile`, sin una segunda presentación que pueda contradecirlo. La ruta de Personas remite a `/creadores/<id>/`; solo las cuentas de creador activas y aprobadas están disponibles. Las fichas muestran iniciales como avatar, sin cargar fotografías. La presentación del creador mantiene la navegación de su estudio cuando la consulta desde esa cuenta.

`/personas/` requiere sesión y ofrece búsqueda por nombre público, intereses o especialidad y filtro de estudiante/creador, con veinte fichas por página. Las páginas mantienen la búsqueda. Participar en el directorio no concede acceso a comunidades ni a contenido de pago. Las cuentas administrativas no tienen ficha pública de participante.

## Conversaciones

Se conservan los espacios separados por versión y la inscripción requerida. Los mensajes muestran alias o nombre del creador aprobado, iniciales y enlace a la ficha si está compartida. No se publica un historial global de aportes ni una lista de comunidades de cada persona.

La búsqueda consulta el mensaje inicial y las respuestas visibles en la versión autorizada. Hay filtros de abiertas, sin respuesta y propias/seguidas; se ordenan por última actividad o fecha de creación. El recuento y la última actividad excluyen respuestas ocultas para participantes normales. Los moderadores autorizados conservan su acceso a mensajes ocultos. Una búsqueda nunca amplía el alcance de la inscripción.

Cualquier participante con acceso puede seguir una conversación visible y dejar de seguirla. Las nuevas respuestas generan avisos internos para sus seguidores y para el autor inicial; el emisor no recibe un aviso por su propia respuesta. El aviso del autor inicial conserva el comportamiento previo y no tiene preferencia de desactivación en esta entrega. Se comprueba nuevamente la autorización de cada destinatario. Seguir no concede permiso para escribir: la suspensión de escritura conserva lectura y seguimiento.

Las suscripciones tienen una restricción única de usuario/conversación. El servidor reserva el escritor SQLite antes de modificar seguimiento o publicar, conserva el envío idempotente y evita avisos duplicados. Los formularios de seguimiento solo admiten POST con CSRF. Reportes, cierre, ocultación y suspensiones conservan su auditoría existente.

## Recorrido

El estudiante entra en Perfil de estudiante, elige alias y presentación, y decide si comparte. Puede revisar su ficha y abrir Personas. Desde Comunidad entra en una versión inscrita, busca una conversación y abre el perfil de su autor cuando esté compartido. Puede seguir conversaciones de otras personas y consultar sus avisos en Notificaciones. El creador mantiene su presentación desde Perfil de creador y consulta Personas y Comunidad dentro del estudio.

## Verificación

El 12 de octubre de 2026 se ejecutó `scripts/check-platform.ps1`: 227 pruebas Django, migraciones consistentes, Ruff y cuatro comprobaciones de concurrencia en SQLite independiente. La comprobación de comunidad incluye dos seguimientos simultáneos y una sola suscripción. Después de ajustar la búsqueda en respuestas y el guardado limitado a campos de perfil, se ejecutaron nuevamente las 35 pruebas de perfiles y comunidad. Las pruebas cubren privacidad por defecto, retirada de compartición, cuentas inactivas, creadores suspendidos, ausencia de correo/nombre privado, escape HTML, CSRF, autorización, seguimiento, avisos y búsqueda sin filtración de actividad oculta.

La revisión en navegador integrado utilizó `scripts/preview-community.py`, una base temporal y cuentas sintéticas. Se revisaron directorio, ficha de estudiante en escritorio y 390 × 844, edición de alias mediante formulario, ficha de creador enlazada desde una respuesta, filtros de comunidad y seguimiento desde el estudio con cambio confirmado a «Dejar de seguir». La revisión móvil detectó la altura heredada de las secciones y se ajustó a contenido. El recurso CSS incorpora una versión nueva para renovar su caché. No constituye validación con personas ni una prueba de capacidad de operación pública.

Las migraciones `accounts.0003` y `learning.0007` se aplicaron a la base local con respaldo SQLite mediante la API de backup. La comparación final confirmó que las 246 filas presentes en el respaldo conservaban todos sus valores anteriores. Durante la verificación aparecieron adiciones de catálogo y un respaldo editorial correspondientes a actividad concurrente en el espacio de trabajo; se conservaron. Esta entrega no atribuye esas adiciones a las migraciones de perfiles. La evidencia local queda en `.local/profiles-migration-verification.json`, con el respaldo indicado allí. Los permisos y tipos de contenido nuevos son cambios normales de Django.

## Límites y siguientes decisiones

Es una ampliación funcional local hacia la plataforma real. No añade membresías, mensajería directa, seguimiento de personas, reputación, fotografía de perfil, una comunidad general abierta ni envío de correo. Tampoco verifica identidad real, credenciales docentes o aprendizaje.

Propongo priorizar verificación de correo y recuperación operativa, preferencias de notificación, temas y respuestas marcadas como solución, y apelaciones con revisión registrada. La fotografía de perfil requerirá reglas de tamaño, formato, almacenamiento y retirada. Antes de publicar deben completarse correo, respaldos con restauración comprobada, supervisión, despliegue y procedimientos de soporte. Estas propuestas están pendientes; no se presentan como funciones entregadas.

## Registro de esta entrega

Fecha de ejecución: 12 de octubre de 2026, contexto de El Salvador. Rama observada: `main`; base Git: `4000ed5`, cambios locales sin commit al redactar este registro. Se revisaron los dos documentos originales de CUBO+; perfiles y comunidad complementan el recorrido de contenido y no sustituyen la verificación del pago ni la validación de la propuesta educativa.
