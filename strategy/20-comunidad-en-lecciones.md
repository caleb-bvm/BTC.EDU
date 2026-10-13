# Comunidad en las lecciones

## Decisión

El estudiante puede plantear dudas y compartir aportes al terminar una lección, dentro de su contexto de estudio. Comunidad conserva la vista central del curso. Ambas entradas muestran la misma conversación, vinculada a una lección de una versión publicada; no crean copias ni trasladan comentarios cuando se publica una versión nueva.

El patrón se contrastó con documentación oficial de [Teachable](https://support.teachable.com/en/articles/11682464-course-comments) y [Thinkific](https://support.thinkific.com/hc/en-us/articles/360030351434-On-Lesson-Discussions), consultada el 12 de octubre de 2026. Teachable documenta comentarios y respuestas dentro de lecciones; Thinkific describe discusiones habilitadas por lección. Estas referencias respaldan una decisión de diseño, no resultados educativos ni disponibilidad de un plan comercial para BTC.EDU.

## Comportamiento implementado

«Conversación de esta lección» aparece después del contenido y los controles de avance. Permite iniciar comentarios, responder en un solo nivel, seguir conversaciones y reportar mensajes. Las respuestas del creador se identifican con su rol. La pregunta privada conserva un acceso y una explicación separados.

El lector presenta cinco conversaciones por página y hasta tres respuestas recientes por conversación. «Abrir conversación» ofrece el historial paginado completo. Los envíos regresan a la conversación y a su página correspondiente. Las validaciones conservan el texto enviado; no anuncian publicación cuando existe un error. No exige participar para completar la lección.

Comunidad integra los comentarios de lecciones junto a los temas generales. Identifica la lección y permite volver a su contenido. La búsqueda y los recuentos excluyen conversaciones de lecciones sin acceso y actividad oculta para los estudiantes. El creador puede utilizar los filtros existentes para revisar conversaciones sin respuesta; ese filtro significa ausencia de respuestas de cualquier participante, no ausencia de una respuesta del creador ni solución confirmada.

## Permisos y atención

Leer o escribir requiere inscripción en la misma versión y acceso a la lección. Comprar un material adicional no desbloquea automáticamente el texto de la lección. Los visitantes y estudiantes no inscritos reciben una invitación, sin ver mensajes. El creador aprobado participa en sus cursos y la administración conserva su permiso específico de moderación.

El creador recibe un aviso interno por un nuevo comentario de lección. El autor de la conversación y sus seguidores reciben avisos por respuestas de otras personas, comprobando nuevamente los permisos de acceso. Los reintentos idénticos no duplican mensajes ni avisos. Se conservan límites de publicación, protección CSRF, escape de texto y decisiones de moderación con motivo e historial.

Ocultar, cerrar o suspender escritura mantiene las reglas de la comunidad existente. Suspender escritura permite continuar leyendo, siguiendo conversaciones y estudiando. Los temas generales anteriores conservan su contenido y no se asignan retrospectivamente a una lección.

## Evaluación pendiente

La hipótesis es que conversar junto al contenido facilitará expresar dudas y aprovechar aclaraciones previas. Falta observar con usuarios si encuentran el espacio, entienden quién lee sus mensajes y distinguen comentarios compartidos de preguntas privadas. También debe evaluarse si el creador puede atender el volumen de consultas.

Marcar soluciones, destacar aclaraciones, avisos por correo y plazos de respuesta quedan fuera de esta entrega. Una prueba técnica o una revisión con cuentas ficticias no demuestra demanda, satisfacción ni aprendizaje. La verificación y sus límites se registran en [la entrega técnica](../src/docs/comunidad-en-lecciones-2026-10-12.md).
