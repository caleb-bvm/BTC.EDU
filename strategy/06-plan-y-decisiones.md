# Plan y registro de decisiones

## Alcance

Plataforma con cursos, capítulos, videos y materiales gratis o de pago, cuentas de alumnos y creadores, progreso, evaluaciones, certificados, preguntas, comunidad y membresías. Las compras individuales son permanentes; las membresías tienen acceso por periodo y renovación manual con pagos simulados de LNbits. Los documentos 07 y 08 sustentan y detallan esta ampliación.

## Calendario propuesto

El objetivo anterior de cerrar desarrollo el 15 de octubre se debe revisar con el equipo ante el alcance solicitado. Proponemos trabajar durante el sprint completo hasta la entrega planificada el 3 de noviembre. No se garantiza que todo esté terminado: el documento 08 estima 23–35 jornadas técnicas y la disponibilidad real aún debe comprobarse.

Construir según la [arquitectura vigente](10-arquitectura-y-experiencia-btc-edu.md): primero modelo/versiones, estructura visual y descubrimiento (cursos, selector, tutoriales y recursos); cerrar cuenta, archivos protegidos, compras, inscripción y progreso básico; después panel de creador/revisión, evaluaciones/certificados, preguntas, comunidad y membresías. Accesibilidad y pruebas acompañan cada entrega. Eventos educativos después. Investigación, contenido y validación de Business avanzan en paralelo. La prioridad inmediata de documentar arquitectura sustituye el siguiente paso anterior de implementar pagos sin este marco.

Mentoría del 13 de octubre: demostrar el curso gratuito, una compra de contenido y protección en el servidor, junto al editor y las demás funciones que estén realmente terminadas. Revisar el plazo al completar la primera fase. Reservar los últimos días antes de la entrega para correcciones y evidencia.

## Estado verificado

LNbits 1.6.2 funciona localmente con uv y FakeWallet. Se verificó creación de factura, pago interno y consulta por API, también después de mover todo el entorno técnico a src. Al 2 de octubre, el sitio cuenta con cuentas por correo, modelos de contenido, catálogo publicado con búsqueda y filtros, detalle de curso y lectura protegida de lecciones. Los pagos integrados y los módulos educativos adicionales siguen pendientes.

La investigación oficial de Udemy, Teachable, Thinkific y Patreon se registra con fuentes y fecha en el documento 07. No hay entrevistas ni resultados de validación externos todavía. La publicación por creadores, certificados, comunidad, progreso y membresías sustituyen las exclusiones anteriores.

## Trabajo diario y requisitos oficiales

**2 de octubre de 2026 — versiones y archivos:** se implementaron composiciones publicadas selladas, revisiones reutilizables, carga privada validada en administración, reproducción MP4 con VTT/transcripción y descarga PDF/TXT con autorización por contexto. Se preservan IDs, texto y archivos anteriores; editar no cambia el contenido publicado hasta la siguiente publicación. 54 pruebas, migraciones y revisión estática pasan; reproducción/descarga y vistas móvil/escritorio verificadas con temporales separados. Respaldo antes de migrar y cantidades originales conservadas. [Registro y límites](../src/docs/contenido-versiones-y-archivos-2026-10-02.md). Siguiente: comercio simulado y derechos sobre revisiones, incluido acceso adquirido a versiones históricas; después inscripción/progreso. Panel de creador y despliegue siguen pendientes.

**2 de octubre de 2026 — interfaz de academia:** el usuario eligió estética industrial más marcada. Se construyeron cursos, selector, tutoriales y recursos con metadatos configurables y navegación común, fichas/lectura/cuenta integradas, filtros y regreso conservados, temario plegable y estados vacíos. 32 pruebas y revisión estática pasan; revisión en navegador de escritorio/móvil con datos temporales separados. Respaldo/migración preservaron los registros y no se cargó catálogo real. Evidencia: [registro de interfaz](../src/docs/interfaz-academia-2026-10-02.md). Archivos, versiones, compras y progreso permanecen pendientes.

**2 de octubre de 2026 — definición de arquitectura:** se revisaron código, documentación y cuatro capturas de referencia. El usuario confirmó cursos, tutoriales y recursos en la primera versión, eventos después. Se documentaron navegación, selector, recursos reutilizables, biblioteca/progreso, versiones, compras y protección, con módulos y criterios UX-01…12. Se aclararon acceso a compras archivadas, integridad SQLite y evidencia de pagos en conflicto. Evidencia: [producto y experiencia](10-arquitectura-y-experiencia-btc-edu.md) y [arquitectura técnica](../src/docs/arquitectura-btc-edu.md). Son decisiones de diseño; no se implementaron módulos ni se cargó contenido. Próximo paso: modelo/versionado y prototipo de estructura de academia con datos temporales.

**2 de octubre de 2026 — desarrollo con Codex:** se implementó el recorrido catálogo → curso → lección siguiendo las necesidades propuestas de claridad del acceso, objetivos, requisitos y navegación del documento 07. Evidencia: 24 pruebas, revisión estática y [registro técnico](../src/docs/recorrido-aprendizaje-2026-10-02.md). No se cargó contenido en la base del usuario. Próximo paso: ofertas, precios y compras simuladas con permisos persistentes. La validación con personas sigue pendiente.

Registrar fecha, responsable, trabajo real, evidencia, decisiones, bloqueo y próximo paso. No crear actividad retroactiva. El assignment pide avances diarios en GitHub y un Google Doc con historial para Business; el enlace sigue pendiente.

Aclarar equipo de dos integrantes frente a cuatro exigidos, fecha de cierre interna y fecha oficial de entrega: el documento indica tanto 3 como 8 de noviembre. Planificar con el 3 hasta confirmar. Demo prevista el 8 de noviembre.
