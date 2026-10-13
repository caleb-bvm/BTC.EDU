# Mejoras integrales de BTC.EDU

## Punto de partida

El usuario autorizó exportar el análisis a otro chat y comenzar las mejoras el 12 de octubre de 2026. El informe completo quedó en el chat Análisis integral de BTC.EDU, id `01a132e7-41ec-7082-8246-729fd816f8b5`, dentro del proyecto Micropayments. Ese chat conserva la referencia; las implementaciones continúan en el chat de origen.

El [análisis](20-analisis-integral-plataforma-educativa.md) conserva el estado observado y sus 227 pruebas. El desarrollo continúa en `main`, sin cambiar de rama ni sustituir los cambios locales anteriores. La documentación se mantiene en `business/teorica`, en un worktree separado. No se interpreta la autorización como validación educativa, aprobación de precios o permiso para contactar participantes.

## Estado actual

Se implementaron registro con retorno seguro, identidad pública coherente del creador y tema de recurso asociado a la revisión aprobada. La entrega pasó 238 pruebas, Ruff, consistencia de migraciones y cuatro controles de concurrencia. La migración local tuvo respaldo y conservó todos los valores anteriores de 496 filas. Se verificaron pantallas con datos temporales. [Comportamiento, migración y límites](../src/docs/registro-identidad-y-clasificacion-2026-10-12.md).

Los pendientes se organizan por recorridos, para que cada entrega aporte utilidad completa. No se asignan fechas o responsables ficticios. Las decisiones que requieran una persona real, contenido original o evidencia con usuarios conservan esa dependencia.

## Trabajo y aceptación

La [entrega de cuentas y servicio](22-usuarios-creadores-y-estudiantes.md) implementa US-01 a US-06, fotos opcionales, guardados y orientación del creador. Pasaron 310 pruebas completas, 39 relacionadas tras el ajuste final y cinco controles de concurrencia. US-04 conserva la dependencia de entrega real de correo y procesos supervisados; la validación con personas continúa pendiente. El diagnóstico anterior de 169 pruebas se conserva como historial separado.

| ID | Trabajo | Estado | Qué debe comprobarse |
|---|---|---|---|
| MI-01 | Conservar destino entre login, registro y acceso | Implementado | Oferta/filtros conservados; externos y otros roles rechazados; alta de creador conserva aprobación requerida. |
| MI-02 | Unificar presentación pública del creador | Implementado | Alias aprobado consistente; un perfil suspendido no muestra nombre privado; versiones y certificados conservan sus créditos históricos. |
| MI-03 | Separar tema publicado del borrador de recurso | Implementado | Envío y aprobación exactos; filtros usan la revisión; tema nulo no hereda borrador; migración conserva campos anteriores. |
| MI-04 | Abrir todos los formatos desde Inicio | Pendiente | La exploración permite encontrar cursos, tutoriales, materiales y fuentes; filtros y regreso mantienen contexto. |
| MI-05 | Continuar igual desde ficha y biblioteca | Pendiente | Una regla común elige la lección pendiente y accesible; incluye cursos gratuitos, mixtos, completados y versiones conservadas. |
| MI-06 | Biblioteca con guardados gratuitos y adquiridos | Guardados implementados; ampliación de filtros pendiente | Guardar no compra ni concede permisos; conservar revisión/procedencia; filtros de estado y formato; retirar guardado no elimina compras. |
| MI-07 | Criterios de publicación educativa | Pendiente | Objetivo y requisitos útiles, información suficiente y revisión por formato; compatibilidad de publicaciones históricas. |
| MI-08 | Tutoriales y recursos con propósito propio | Pendiente | Un tutorial resuelve una tarea; material y fuente aportan utilidad; autoría y condiciones revisadas; sin archivos ficticios presentados como producción. |
| MI-09 | Ayuda contextual y resolución de preguntas | Pendiente | Volver a la lección; estados y búsqueda; marcar resolución con permisos e historial; no abrir preguntas privadas al foro. |
| MI-10 | Responsable de acompañamiento institucional | Requiere asignación humana | Cuenta habilitada y responsabilidades reales para preguntas, moderación e incidencias; no confundir cuenta técnica con atención disponible. |
| MI-11 | Comunidad útil entre formatos | Pendiente | Título, tema, vínculo al contenido, fijados y solución; conservar versiones y acceso; definir moderadores para espacios por tema. |
| MI-12 | Avisos con contexto y preferencias | Implementado para avisos internos; correo real pendiente | Identificar curso/conversación antes de abrir; filtrar; seguir y dejar de recibir avisos de conversaciones; entrega de correo solo cuando esté preparada. |
| MI-13 | Práctica y retroalimentación ligadas a objetivos | Pendiente | Explicación, intento, comprobación y siguiente acción; evaluación formativa diferenciada de requisitos de certificado; cubrir objetivos con evidencia suficiente. |
| MI-14 | Corrección de credenciales | Pendiente | Sustitución relacionada con original, motivo y estado verificable; mantener datos y huellas anteriores; portabilidad después de definir criterios. |
| MI-15 | Indicadores que ayuden a mejorar aprendizaje y atención | Pendiente | Cobertura por formato, tareas, preguntas resueltas y pendientes; fuente/cohorte/denominador; no convertir vistas o marcas en dominio educativo. |
| MI-16 | Bandejas de trabajo para creador y administración | Bandeja del creador y atención de cuentas implementadas; operación general pendiente | Publicación, dudas, reportes e incidencias con responsable y cierre; permisos de soporte privado explícitos. |
| MI-17 | Operación y recuperación comprobadas | Pendiente | Correo, límites de acceso, respaldo/restauración, conciliación supervisada, alertas, almacenamiento y atención de pagos; preservar SQLite hasta contar con mediciones. |
| MI-18 | Accesibilidad, móvil y conexión | Pendiente | Teclado, foco, zoom/reflujo, lector de pantalla, errores y controles; archivos/subtítulos; tamaño de descarga y opciones de consumo apropiadas. |
| MI-19 | Validación educativa y comercial | Requiere participantes | Consentimiento, tareas reales y versión identificada; separar resultados técnicos, satisfacción, aprendizaje y voluntad de pago. |
| MI-20 | Revisar documentación y demostración de cada entrega | Continuo | Documento principal, texto plano, comportamiento actual, historial real y criterios de aceptación coherentes con la versión demostrada. |

## Orden de continuación

El próximo recorrido reúne MI-04 y MI-05: encontrar distintos formatos y retomar desde cualquier entrada. Los guardados de MI-06 ya permiten conservar recursos y fuentes; sus filtros adicionales y MI-08 requieren continuidad propia. MI-07, MI-09, MI-10 y MI-13 conectan calidad, práctica y ayuda; la asignación institucional debe resolverse antes de prometer atención.

Comunidad, avisos y bandejas se ampliarán manteniendo los permisos existentes. Evaluación, credenciales y analítica deberán expresar evidencia educativa adecuada al objetivo. Operación y accesibilidad se comprueban antes de abrir al público. Membresías, eventos, mensajería directa y reputación conservan su condición de ampliaciones posteriores que necesitan necesidad demostrada y capacidad de mantenimiento.

## Registro de entregas

El 12 de octubre de 2026 se completaron MI-01, MI-02 y MI-03 sobre la base `4000ed5` y los cambios locales existentes, sin commit ni push. Pasaron 11 pruebas nuevas y la revisión completa de 238 pruebas, junto con Ruff, migraciones y cuatro controles de concurrencia. La migración conservó 496 filas anteriores; el navegador usó datos temporales. No se atribuyen a esta entrega los cambios previos de perfiles, seguimiento o contenido editorial.

El resto conserva estado pendiente. Esta tabla se actualizará con evidencia de cada implementación, sin convertir una propuesta, un prototipo o una prueba técnica en un resultado externo.
