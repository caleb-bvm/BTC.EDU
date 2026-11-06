# Plan y decisiones

Plan de trabajo, calendario, decisiones registradas y plan de documentación de Business a desarrollo.

<a id="06-plan-y-decisiones"></a>

## Plan y registro de decisiones

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Alcance

Plataforma con cursos, capítulos, videos y materiales gratis o de pago, cuentas de alumnos y creadores, progreso, evaluaciones, certificados, preguntas, comunidad y membresías. Las compras individuales son permanentes; las membresías tienen acceso por periodo y renovación manual con pagos simulados de LNbits. Los documentos 07 y 08 sustentan y detallan esta ampliación.

### Calendario propuesto

El objetivo anterior de cerrar desarrollo el 15 de octubre se debe revisar con el equipo ante el alcance solicitado. Proponemos trabajar durante el sprint completo hasta la entrega planificada el 3 de noviembre. No se garantiza que todo esté terminado. Las 23–35 jornadas de 08 son una estimación histórica anterior y no representan el trabajo restante. Desde el 7 de octubre, el usuario confirma que trabaja solo en Business y Dev; las horas disponibles aún no están definidas.

Construir según la [arquitectura vigente](05-arquitectura-de-producto.md#10-arquitectura-y-experiencia-btc-edu): primero modelo/versiones, estructura visual y descubrimiento (cursos, selector, tutoriales y recursos); cerrar cuenta, archivos protegidos, compras, inscripción y progreso básico; después panel de creador/revisión, evaluaciones/certificados, preguntas, comunidad y membresías. Accesibilidad y pruebas acompañan cada entrega. Eventos educativos después. Investigación, contenido y validación de Business avanzan en paralelo. El registro diario siguiente determina el avance vigente; el calendario y la disponibilidad todavía requieren revisión.

Mentoría del 13 de octubre: demostrar el curso gratuito, una compra de contenido y protección en el servidor, junto al editor y las demás funciones que estén realmente terminadas. Revisar el plazo al completar la primera fase. Reservar los últimos días antes de la entrega para correcciones y evidencia. Desde el 5 de noviembre, las sesiones con estudiantes y educadores quedan como la última etapa, después del desarrollo y la documentación pendientes.

### Estado verificado

**12 de octubre de 2026 — catálogo Bitcoin y Lightning:** seis cursos publicados localmente, 24 lecciones con explicación, ejemplo, práctica y solución. Tres cursos gratuitos y tres con primera lección gratuita, ofertas de 120 sats por curso y 50 sats por lección. Seis preguntas finales y políticas de certificado. Carga con respaldo y sin duplicados; comprobación HTTP en copia temporal de catálogo, selector, fichas y lecciones, incluidos nueve bloqueos del texto pagado. Ruff aprobado para archivos nuevos. Sin nueva prueba de pago, certificado emitido ni validación con usuarios; precios y duraciones son hipótesis. [Entrega y evidencia reproducible](../src/docs/operacion-y-bitacora.md#catalogo-editorial-2026-10-12). Cambios paralelos de perfiles y comunidad fuera de esta entrega.

**10 de octubre de 2026 — conciliación periódica:** `reconcile_payments --watch` consulta lotes sin navegador, reintenta indisponibilidad, rota reservas sin emitir y conserva incidencias tardías sin permisos. 192 pruebas, migraciones, Ruff y los tres controles de concurrencia aprobados. Desarrollado en `main`, sin migración nueva ni cambios en la base principal. [Registro y evidencia](../src/docs/operacion-y-bitacora.md#conciliacion-2026-10-10). Requiere un terminal supervisado; servicio, alertas y prueba adicional de ZEUS siguen pendientes.

**10 de octubre de 2026 — ampliación SHA-256:** huella persistente por certificado, comparación web y exportación reproducible privada o compartida por decisión del titular. 184 pruebas, migraciones, Ruff y concurrencia aprobados; comprobación independiente con Node y formularios HTTP. La migración conservó 258 filas originales en 50 tablas, con respaldo. [Entrega vigente](../src/docs/operacion-y-bitacora.md#certificados-sha256-2026-10-10). El registro anterior conserva el estado del bloque esencial antes de añadir las huellas.

**10 de octubre de 2026:** bloque esencial de certificados, preguntas, notificaciones y paneles implementado. 179 pruebas, migraciones, revisión estática y tres comprobaciones de concurrencia pasan. Navegación y formularios por HTTP, escritorio/móvil y PDF comprobados; migración con respaldo conservó 211 filas originales, sin ejemplos en la base principal. [Entrega vigente y límites](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). Comunidad, membresías, operación pública y validación externa siguen pendientes. El usuario comprobará después el pago completo desde ZEUS.

**4 de octubre de 2026:** cuentas independientes, estudio y revisión editorial, ofertas, compra simulada integrada, derechos históricos, biblioteca, inscripción y progreso por versión. 129 pruebas pasan; integración real contra FakeWallet y concurrencia SQLite en archivo verificadas. Próxima fase: evaluaciones/certificados y preguntas; operación supervisada y validación siguen pendientes. Los párrafos fechados anteriores conservan su contexto histórico.

LNbits 1.6.2 funciona localmente con uv y FakeWallet. Se verificó creación de factura, pago interno y consulta por API, también después de mover todo el entorno técnico a src. Al 2 de octubre, el sitio cuenta con cuentas por correo, modelos de contenido, catálogo publicado con búsqueda y filtros, detalle de curso y lectura protegida de lecciones. Los pagos integrados y los módulos educativos adicionales siguen pendientes.

La investigación funcional se conserva en 07. Al 5 de octubre, [13](04-producto-y-monetizacion.md#13-monetizacion-precios-y-muestras) incorpora modelos, tarifas y costos con fuentes; [16](10-metricas-y-validacion.md#16-validacion-con-usuarios), métodos y guiones. No hay entrevistas, resultados externos ni precios validados. La publicación por creadores, certificados, comunidad, progreso y membresías conservan su lugar en el alcance.

### Organización actual

El 7 de octubre el usuario confirmó que BTC.EDU continúa como proyecto individual. Caleb asume Business y Dev: investigación, decisiones, desarrollo, verificación y documentación. La disponibilidad semanal no está definida; no se asignan jornadas ni fechas de cierre de módulos sin estimación. Se prioriza cerrar brechas del núcleo oficial y preparar el recorrido de mentoría antes de comprometer ampliaciones. El requisito original de cuatro integrantes sigue pendiente de aclaración con CUBO+; no se presupone una excepción autorizada.

### Trabajo del 7 de octubre

Se revisaron rama, historial, plan, requisitos originales y registros técnicos. La documentación anterior está integrada en main mediante d0bb7e4; se continuó en business/teorica actualizada a esa base. Se creó la matriz inicial 14 con requisitos oficiales, AC-01…35 y UX-01…12, evidencias relacionadas y tareas. La matriz identifica cobertura parcial de progreso de video, recuperación tras reinicio, accesibilidad y analítica administrativa. No se reejecutaron las 129 pruebas ni se realizaron entrevistas. D01 sigue abierto por disponibilidad y aclaración del equipo; D04 por auditoría de pruebas y recorridos específicos. Próximo paso: T-02/T-03, comprobar cobertura por criterio y especificar eventos/panel; preparar demo del núcleo para el 13 de octubre. El informe y la exportación copiable incorporan esta organización. Google Docs permanece a cargo del usuario; no se editó directamente.
### Trabajo diario y requisitos oficiales

**5 de octubre de 2026 — documentación de Business:** por autorización del usuario se incorporó la investigación presentada sobre monetización, tarifas, muestras, video y métodos de validación. Se actualizaron las referencias y pendientes, y se preparó el [documento principal](01-informe.md) con títulos sencillos y sin campos de portada añadidos. El usuario copiará el contenido a Google Docs; no se editó allí ni se creó historial retroactivo. Trabajo realizado en `business/teorica`; cambios locales, sin publicación. Evidencias: documentos 13 y 16 con fuentes y cálculos; informe 19 y documentos relacionados. Las 129 pruebas siguen siendo el registro del 4 de octubre. No hay participantes ni validación externa. Próximo paso: responsables, reclutamiento/consentimiento, ejecución y análisis; completar presupuesto y trazabilidad. Esta entrada se actualiza si los cambios se versionan o publican posteriormente.

**4 de octubre de 2026 — experiencia de compra:** el usuario pidió lenguaje realista y preparación como producto. Se entregó resumen → continuar → pagar con importe → confirmación → biblioteca; precios en sats, estados de procesamiento y errores comprensibles. Una indicación común identifica el entorno de desarrollo con saldo de prueba; FakeWallet y sus comprobaciones permanecen activos. 60 pruebas relacionadas, Ruff, consistencia de migraciones, smoke del proveedor y compra en navegador pasan. No hay migraciones ni datos de ejemplo en la base principal. Commit funcional `d36b152`; [registro y evidencia](../src/docs/operacion-y-bitacora.md#experiencia-compra-2026-10-04). Wallet externa, pagos reales y operación pública siguen pendientes.

**4 de octubre de 2026 — comercio y continuidad de aprendizaje:** por autorización del usuario se cerró el recorrido creador → revisión/publicación → oferta → compra simulada → biblioteca → aprendizaje. Precio e inventario se congelan por factura; derechos y progreso permanecen en su versión aunque cambie la publicación. Incluye alternativas individuales, prevención de recompras, evidencia de incidencias, recuperación de emisión incierta y avance sin sobrescritura entre sesiones. 129 pruebas, migraciones, revisión estática y concurrencia con conexiones SQLite separadas pasan. Compra integrada contra LNbits FakeWallet, petición autenticada con CSRF y respuesta perdida verificadas; escritorio/móvil inspeccionados en navegador. Respaldos y migraciones aplicados sin poblar la base principal. Commits funcionales `1e470de` y `aa70fca`; documentación/evidencia en un commit adicional. [Registro y límites](../src/docs/operacion-y-bitacora.md#comercio-y-aprendizaje-2026-10-04). Conciliación disponible como comando, aún sin supervisor periódico. Evaluaciones, certificados, preguntas, comunidad, membresías y métricas conservan el alcance del proyecto completo.

**4 de octubre de 2026 — cierre con commits:** por petición del usuario, cada bloque terminado debe quedar guardado en commits al cerrar el trabajo. El estudio de creadores y las cuentas independientes se versionan juntos por sus dependencias de acceso; documentación y evidencia se guardan en otro commit. Publicar los commits al remoto es un paso separado.

**3 de octubre de 2026 — cuentas independientes:** el usuario confirmó separar las cuentas de estudiante y creador. Se implementaron registro/login, recuperación y perfiles por espacio, autenticación por correo/tipo, menú propio del estudio y administración independiente. La aprobación sigue siendo necesaria para operar como creador. 96 pruebas pasan, incluida migración con datos históricos y recuperación sin afectar la otra identidad. Base local respaldada/migrada sin cuentas ni ejemplos. [Evidencia y límites](../src/docs/operacion-y-bitacora.md#cuentas-independientes-2026-10-03). Esta decisión sustituye las referencias anteriores a una cuenta compartida con roles.

**3 de octubre de 2026 — estudio de creadores:** se definió el enfoque integral y se implementaron solicitud/aprobación, perfil público, panel, edición de cursos/tutoriales/capítulos/lecciones, recursos, cargas privadas, vista previa y revisión editorial con observaciones. Los envíos congelan contenido; aprobar publica la copia revisada y conserva las publicaciones anteriores. 77 pruebas, migraciones y revisión estática pasan; recorrido verificado en navegador con datos temporales. Respaldo y migración aplicados sin añadir cuentas ni contenido a la base real. [Registro y límites](../src/docs/operacion-y-bitacora.md#estudio-creadores-2026-10-03). Próximo bloque: ofertas/compras y derechos históricos, inscripción/progreso; después acompañamiento y módulos ampliados del [enfoque de creadores](08-aprendizaje-creadores-y-comunidad.md#11-enfoque-creadores).

**2 de octubre de 2026 — versiones y archivos:** se implementaron composiciones publicadas selladas, revisiones reutilizables, carga privada validada en administración, reproducción MP4 con VTT/transcripción y descarga PDF/TXT con autorización por contexto. Se preservan IDs, texto y archivos anteriores; editar no cambia el contenido publicado hasta la siguiente publicación. 54 pruebas, migraciones y revisión estática pasan; reproducción/descarga y vistas móvil/escritorio verificadas con temporales separados. Respaldo antes de migrar y cantidades originales conservadas. [Registro y límites](../src/docs/operacion-y-bitacora.md#contenido-versiones-y-archivos-2026-10-02). Siguiente: comercio simulado y derechos sobre revisiones, incluido acceso adquirido a versiones históricas; después inscripción/progreso. Panel de creador y despliegue siguen pendientes.

**2 de octubre de 2026 — interfaz de academia:** el usuario eligió estética industrial más marcada. Se construyeron cursos, selector, tutoriales y recursos con metadatos configurables y navegación común, fichas/lectura/cuenta integradas, filtros y regreso conservados, temario plegable y estados vacíos. 32 pruebas y revisión estática pasan; revisión en navegador de escritorio/móvil con datos temporales separados. Respaldo/migración preservaron los registros y no se cargó catálogo real. Evidencia: [registro de interfaz](../src/docs/operacion-y-bitacora.md#interfaz-academia-2026-10-02). Archivos, versiones, compras y progreso permanecen pendientes.

**2 de octubre de 2026 — definición de arquitectura:** se revisaron código, documentación y cuatro capturas de referencia. El usuario confirmó cursos, tutoriales y recursos en la primera versión, eventos después. Se documentaron navegación, selector, recursos reutilizables, biblioteca/progreso, versiones, compras y protección, con módulos y criterios UX-01…12. Se aclararon acceso a compras archivadas, integridad SQLite y evidencia de pagos en conflicto. Evidencia: [producto y experiencia](05-arquitectura-de-producto.md#10-arquitectura-y-experiencia-btc-edu) y [arquitectura técnica](../src/docs/operacion-y-bitacora.md#arquitectura-btc-edu). Son decisiones de diseño; no se implementaron módulos ni se cargó contenido. Próximo paso: modelo/versionado y prototipo de estructura de academia con datos temporales.

**2 de octubre de 2026 — desarrollo con Codex:** se implementó el recorrido catálogo → curso → lección siguiendo las necesidades propuestas de claridad del acceso, objetivos, requisitos y navegación del documento 07. Evidencia: 24 pruebas, revisión estática y [registro técnico](../src/docs/operacion-y-bitacora.md#recorrido-aprendizaje-2026-10-02). No se cargó contenido en la base del usuario. Próximo paso: ofertas, precios y compras simuladas con permisos persistentes. La validación con personas sigue pendiente.

Registrar fecha, responsable, trabajo real, evidencia, decisiones, bloqueo y próximo paso. No crear actividad retroactiva. El assignment pide avances diarios en GitHub y un Google Doc con historial para Business; el enlace sigue pendiente.

Aclarar equipo de dos integrantes frente a cuatro exigidos, fecha de cierre interna y fecha oficial de entrega: el documento indica tanto 3 como 8 de noviembre. Planificar con el 3 hasta confirmar. Demo prevista el 8 de noviembre.

### Trabajo del 10 de octubre

Commit funcional local: `bb3745c`. La documentación y evidencia se conservan en el commit de cierre de esta entrega. No se publicaron al remoto.

Por petición del usuario se implementaron certificados, preguntas, notificaciones, métricas y paneles para cerrar el desarrollo esencial. Se congelan requisitos con el envío editorial; emisión histórica única, PDF privado, compartir voluntario y revocación auditada. Se añadieron conversaciones privadas, avisos idempotentes y consultas con cohortes/denominadores explícitos. Pruebas y evidencias reales en el registro técnico; base temporal para ejemplos y respaldo de la base principal. Se actualizaron 05/08/11/12/14/15/19 y la exportación de texto. No se ejecutaron entrevistas, pruebas con fondos reales ni despliegue público. El cierre se guarda en commits locales, sin publicar al remoto.

### Ampliación de certificados del 10 de octubre

El usuario solicitó SHA-256 para verificar certificados. Se adoptó una huella de datos históricos guardada al emitir, visible en PDF/web y reproducible con JSON; comparación con el registro de BTC.EDU, conservando privacidad y revocación. Se documenta la diferencia entre hash y firma y no se presenta como registro Bitcoin. Evidencia técnica y pruebas específicas en el registro de certificados SHA-256. Se guardará el bloque en commit local, sin push.

### Comunidad y moderación del 10 de octubre

Por elección del usuario se continúa desarrollo técnico con comunidad por versión, acceso por inscripción, respuestas y reportes, moderación con motivo e historial y suspensión reversible de escritura. Se mantienen compras, progreso y lectura. Se añaden avisos internos y pruebas de permisos, privacidad, reintentos y concurrencia. [Reglas y evidencia](../src/docs/operacion-y-bitacora.md#comunidad-2026-10-10). Implementación en commit local 3a465c3, sobre main; se preservan los archivos de revisión integrada que ya estaban sin seguimiento. Membresías y operación pública siguen pendientes. No se ejecutan sesiones externas ni se publica al remoto.

**12 de octubre de 2026 — cursos, lectura y continuidad:** inspección del recorrido actual y consulta de NN/g, W3C y ayuda oficial de Udemy. Se implementaron continuación compartida entre ficha y biblioteca, estados del temario, prácticas con solución desplegable, lectura enfocada, búsqueda/estados y actualización confirmada del avance. Base Git `4000ed5`, rama `main`, cambios locales anteriores conservados; sin commit propio en esta entrega. [Decisiones, comprobaciones y límites](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12). Las sesiones externas y los resultados educativos continúan pendientes.

### Conversación al final de cada lección

El 12 de octubre de 2026 el usuario autorizó implementar la propuesta de comunidad vinculada a lecciones. Se reutiliza la comunidad por versión: una misma conversación puede abrirse en el lector y en Comunidad, sin copias. Los comentarios de lecciones de pago exigen acceso al contenido incluso desde búsqueda o un enlace directo; la inscripción por sí sola no desbloquea ese intercambio. La pregunta privada conserva su función. [Propuesta y alcance](08-aprendizaje-creadores-y-comunidad.md#20-comunidad-en-lecciones). El registro técnico conserva las pruebas y las limitaciones reales de esta ejecución.

**12 de octubre de 2026 — corrección visual del temario:** una captura del usuario reveló que una regla heredada estiraba el marcador circular. Se corrigió la herencia de flex y se verificaron proporciones 1:1 en curso y lector, incluido móvil. [Causa y evidencia](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12). El texto principal mantiene sus secciones, pues no cambia el comportamiento educativo.

**12 de octubre de 2026 — UI/UX de evaluaciones:** se inspeccionó la interfaz actual y se consultaron referencias primarias de LatitudeLearning, GOV.UK y Duolingo. Se implementaron preparación separada, pregunta por pantalla, opciones amplias, avance, revisión previa, resultados de repaso y editor plegable. Rama `main`, cambios locales previos conservados, sin commit propio en esta entrega. Pasaron 29 pruebas enfocadas y se verificó el recorrido por HTTP en una base temporal. [Decisiones, evidencias y límites](../src/docs/operacion-y-bitacora.md#experiencia-evaluaciones-2026-10-12). Validación externa pendiente.

<a id="12-plan-documentacion-business-a-desarrollo"></a>

## Plan de documentación: Business → Desarrollo

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

Fecha: 5 de octubre de 2026 (El Salvador). Rama de trabajo: `business/teorica`, creada desde `main` en `c0ac528`. El plan se actualiza con la investigación documental incorporada en 13, los instrumentos de 16 y el informe de 19. No acredita sesiones externas ni nuevas funciones.

### Objetivo y punto de partida

Preparar un paquete de decisiones, especificaciones y evidencias que permita continuar el desarrollo sin ambigüedades y cumplir los entregables estratégicos del assignment. El desarrollo ya comenzó: la documentación registra cuentas separadas, publicación versionada, compras simuladas, biblioteca y progreso. Las 129 pruebas son un resultado registrado al 4 de octubre, no una ejecución nueva de esta revisión.

Las fuentes de alcance son los originales de `docs/Micropayments for Content.docx` y `docs/assignment final evaluation.docx`, los documentos 01–11 de esta carpeta y los registros de `src/docs`. La documentación existente debe completarse y armonizarse antes de duplicarla.

El assignment exige investigación de modelos de monetización, usuarios, precios, muestras, recorrido de pago, prototipo, métricas y recomendación; además, oportunidad/impacto, operación/recursos y Google Doc con historial. Evaluaciones, certificados, comunidad y membresías son ampliaciones del equipo: se conservan en el alcance, con entregas separadas del núcleo exigido.

### Documento principal del proyecto exigido para la entrega

La evaluación exige entregar un **PDF que detalle la solución estratégica del caso de estudio**, junto con un archivo `.txt` que contenga el enlace al repositorio público. El documento principal del proyecto será ese informe integrado: explicará BTC.EDU a un evaluador que no conoce el repositorio y remitirá a evidencias concretas. Su preparación empieza ahora y se actualiza durante el trabajo; la exportación final depende de los resultados disponibles. D13 incluye este informe además de la recomendación y preparación de entrega.

El PDF, los documentos de trabajo de `/strategy` y el Google Doc con historial cumplen funciones distintas. El informe presenta la solución y sus resultados; los documentos de trabajo permiten construirla y verificarla; el Google Doc acredita evolución diaria real. La evaluación también exige especificaciones claras y una prueba de concepto funcional: describirlas en el informe debe ir acompañado de evidencia accesible.

#### Índice propuesto del informe

Este índice es una propuesta del equipo alineada con los originales; CUBO+ no fija un índice, extensión ni plantilla en los archivos recibidos.

La estructura acordada posteriormente con el usuario sustituye la propuesta inicial: Introducción; La idea; El problema; Cómo consolidamos la idea; Investigación; Objetivos; Enfoque; Desarrollo; A dónde queremos llegar; Qué demostramos; Logros; Próximos pasos; Conclusiones; Referencias. El [informe](01-informe.md) desarrolla esta estructura investigativa.

Usar títulos naturales y omitir campos de país, caso, fecha de actualización, estado, equipo y repositorio en la portada; el usuario los añadirá si corresponde. Mantener fechas/versiones en bitácora y evidencias. Los criterios de evaluación siguen cubiertos por el contenido y anexos: oportunidad, monetización, prototipo/especificaciones, métricas, operación, colaboración y recomendación. No se eliminan requisitos del assignment por esta preferencia editorial.

#### Relación con los pilares de evaluación

| Pilar del original de evaluación | Cómo lo cubrirá el informe | Evidencia acompañante |
|---|---|---|
| Transparencia y evolución | Avances y decisiones fechados, con límites explícitos | Commits publicados y Google Doc con historial accesible |
| Ejecución técnica | Explicación de funcionamiento y verificación | Código organizado, README técnico, pruebas y demo funcional |
| Colaboración real | Contribuciones de Business y Dev al mismo problema y decisiones compartidas | Trabajo por integrante, especificaciones, validación y prueba de concepto |
| Documentación | Informe comprensible y recorridos reproducibles | Reportes de avance y manuales de usuario |
| Propuesta de valor | Utilidad e innovación justificadas para el ecosistema Bitcoin en El Salvador | Investigación, hallazgos, comparación de alternativas y resultados |

No se asignan pesos ni puntuaciones: los originales proporcionados no los especifican. Antes de exportar, comprobar que cada afirmación de resultado tiene evidencia, que los enlaces son accesibles al jurado y que el contenido coincide con la versión demostrada.

### Inventario y brechas

| Área | Base existente | Brecha para desarrollo o entrega |
|---|---|---|
| Producto y oportunidad | 01, 07 | Problema respaldado por usuarios; segmento prioritario; impacto práctico para el ecosistema de Bitcoin en El Salvador |
| Mercado y monetización | 07 funcional; 13 modelos/tarifas/costos | Contrastar con usuarios y presupuesto; recomendación comercial final |
| Catálogo y precios | 02, precios ficticios | Justificación, límites de muestra, inventario editorial y derechos de cada archivo |
| Requisitos y reglas | 03, 08, 10, 11 | Matriz única de trazabilidad, decisiones abiertas y detalle de los módulos pendientes |
| Experiencia | 04, 09, 10 y pantallas implementadas | Prototipo navegable de nuevas vistas, estados alternativos y resultados de pruebas con personas |
| Métricas | 05 | Contrato de eventos, cobertura implementada, consultas verificables y especificación del panel administrativo |
| Operación | Referencias en 13, 01/11 y documentos técnicos | Presupuesto completo, escenarios de consumo, sostenibilidad y responsabilidades |
| Plan y evidencia | 06 y registros técnicos | Capacidad real, responsables, riesgos, enlace a Google Doc e historial diario auditable |
| Entrega | README técnico y evidencias fechadas | Recomendación final, manuales, PDF estratégico y guion de demostración |

### Paquetes de trabajo

P0 prepara la próxima entrega de desarrollo; P1 completa la validación y preparación de entrega; P2 consolida resultados finales. Los responsables son funciones propuestas, pendientes de asignar a personas. Business redacta las decisiones de producto; Dev revisa viabilidad y documenta contratos técnicos; ambos verifican aceptación.

| ID / prioridad | Documento y ubicación propuesta | Contenido que debe producirse | Criterio para darlo por terminado | Dependencia / responsable |
|---|---|---|---|---|
| D01 / P0 | Actualizar 06: alcance, decisiones y capacidad | Núcleo del assignment, ampliaciones por entrega, disponibilidad, responsables, riesgos y decisiones abiertas con fecha | Cada entrega tiene alcance, responsable, dependencia y condición de cierre; fechas inciertas visibles | Ninguna / Business + Dev |
| D02 / P0 | Actualizar 01 y 07: oportunidad y usuarios | Segmento inicial, problema concreto, alternativas actuales, hipótesis e impacto local; guion y reclutamiento | Cada afirmación se identifica como fuente, hipótesis o hallazgo; no se inventan entrevistas | D01 / Business |
| D03 / P0 | `13-monetizacion-precios-y-muestras.md` | Comparación de cuatro modelos, precios de referencias, propuesta, compras repetidas, muestras por formato y preguntas de validación | Matriz con fuentes/fechas; precio e inclusión de cada oferta justificados como hipótesis o evidencia; acceso permanente/temporal claro | D02 / Business; revisión Dev |
| D04 / P0 | `14-trazabilidad-y-backlog.md`; armonizar 03/08/10/11 | Requisito oficial o ampliación → regla → historia → aceptación → pantalla → evidencia → estado | Todos los requisitos oficiales y AC-01…35/UX vigentes están vinculados; cada brecha tiene una tarea y prioridad | D01 y D03 / Business + Dev |
| D05 / P0 | Actualizar 04; prototipos en `strategy/prototipos/` | Recorridos de alumno, creador y administrador; estados vacíos, errores, permisos, móvil y teclado | Prototipo ejecutable/navegable y enlace o instrucciones; cada tarea se puede recorrer y cada pantalla tiene aceptación | D04 / Business; revisión Dev |
| D06 / P0 por módulo | `15-especificaciones-modulos-pendientes.md`; detalle técnico en `src/docs/` | Evaluaciones/certificados, preguntas/avisos, comunidad/moderación y membresías; matriz de roles y estados | Para cada módulo: entradas, reglas, transiciones, datos históricos, errores y escenarios aceptados; Dev puede estimarlo sin decidir políticas de producto | D04/D05 / Business + Dev |
| D07 / P0 | Actualizar 05; contrato técnico en `src/docs/` | Eventos del embudo, propiedades, deduplicación, permisos, retención propuesta, denominadores y panel básico | Cada KPI tiene evento/fuente/consulta, ejemplo calculable y manejo de cero; cobertura real distinguida de diseño | D04 / Business + Dev |
| D08 / P1 | `16-validacion-con-usuarios.md` | Consentimiento, guiones, tareas, notas, resultados y cambios priorizados | Sesiones reales fechadas; muestra y limitaciones explícitas; hallazgo → decisión → cambio → nueva comprobación cuando corresponda | D02/D03/D05 / Business |
| D09 / P1 | `17-modelo-operativo-y-recursos.md` | Recursos humanos, alojamiento, video/archivos, correo, soporte, moderación, mantenimiento, costos y sostenibilidad | Escenarios de uso y costos con supuestos/fuentes; responsable y frecuencia de cada operación; separación entre volumen simulado e ingresos | D01/D03/D06 / Business + Dev |
| D10 / P1 | Completar 02; `18-politica-editorial-y-contenido.md` | Catálogo de demostración, procedencia/licencias, muestras, subtítulos, revisión y continuidad de acceso | Cada activo tiene permiso, autor, versión, formato y estado; ofertas coherentes; datos de demo aislados de la base principal | D03/D05 / Business; revisión Dev |
| D11 / P0–P1 | Actualizar 06 y crear registro de trabajo en Google Docs | Bitácora real por fecha: persona, cambio, evidencia, decisión y siguiente paso | Enlace accesible y permisos comprobados; historial de edición continuo desde su creación; vínculo a commits/evidencias reales | Iniciar desde ahora / Business + equipo |
| D12 / P1 | Manuales en `strategy/manuales/`; operación técnica en `src/docs/` | Alumno: compra/recuperación/biblioteca; creador: revisión/publicación; administrador: incidencias; instalación, respaldo/restauración y límites | Otra persona puede completar las tareas documentadas; capturas coinciden con la entrega; pasos técnicos verificados por Dev | Entrega funcional correspondiente / Business + Dev |
| D13 / P0 → P2 | Informe principal en `01-informe.md` y PDF estratégico | Redacción progresiva del documento del proyecto según el índice de este plan; caso estratégico, evidencia, recomendación, resultados y anexos; guion de demo de 10 minutos | Cobertura de los cinco pilares; recomendación sustentada en D03/D08/D09; PDF revisado; archivo .txt del repositorio público y enlaces comprobados | Iniciar con fuentes existentes; cierre con D08–D12 / equipo |

Estado del 5 de octubre: D03 tiene comparación y recomendación provisional en 13, pendiente de validar precios y sostenibilidad; D08 tiene instrumentos en 16, pendiente de ejecución/resultados; D13 tiene informe integrado en 19, pendiente de resultados finales, PDF y anexos. D02 sigue pendiente de evidencia con usuarios y D09 del presupuesto completo. Los otros archivos propuestos no se crean como encabezados vacíos. Este avance no cierra los criterios de aceptación de paquetes todavía incompletos.

### Decisiones que deben cerrarse antes de programar cada módulo

| Tema | Decisión/documentación necesaria |
|---|---|
| Evaluaciones | Puntuación de selección múltiple, redondeo, intentos interrumpidos, momento de mostrar respuestas, espera y reinicio autorizado; mantener corrección en servidor |
| Certificados | Requisitos congelados por versión, nombre mostrado, privacidad de verificación, correcciones/revocación y su evidencia; una credencial por alumno/versión |
| Preguntas y avisos | Quién lee/escribe/responde, acceso tras vencer membresía, estados, edición/eliminación y avisos internos; responsabilidades y tiempo objetivo de atención |
| Comunidad | Alcance del espacio, participación, reportes, escalamiento, suspensión y conservación de historial; permisos propios del creador |
| Membresías | Versión del plan, inicio/fin, zona horaria de presentación, factura pendiente al vencer, cambios de plan, cancelación y acceso histórico; renovación manual de 30 días |
| Analítica | Qué eventos existen realmente, fuente de verdad, visibilidad por creador/administrador y tratamiento de datos; no inferir aprendizaje de aperturas |
| Operación | Conciliación periódica supervisada, correo, cuotas, respaldo/restauración, archivos huérfanos, incidencias y condiciones para operación pública |

No reabrir decisiones confirmadas sin motivo y registro: cuentas independientes, compras permanentes por versión, pagos simulados, conservación de derechos históricos y bloqueo provisional de compras conjuntas parcialmente adquiridas.

### Orden de ejecución y calendario propuesto

1. **5–7 de octubre:** D01/D02 y matriz inicial D04; iniciar D11 y la redacción del informe principal D13 con hechos y fuentes existentes. Armonizar documentos que mezclan diseño y estado actual. Identificar responsables, participantes y capacidad disponible.
2. **8–12 de octubre:** D03, D05, contrato D07 y primeras sesiones D08. Preparar el paquete de la siguiente entrega con D06. Para mentoría, reunir evidencias del núcleo ya construido y declarar pendientes.
3. **13 de octubre:** mentoría: demostrar un recorrido real y explicar oportunidad, reglas de acceso, hipótesis comerciales y evidencia disponible. Registrar observaciones sin simular validación externa.
4. **14–23 de octubre:** completar D06 por orden de desarrollo; iterar D05/D08; cerrar D09/D10. Entregar cada módulo a Dev cuando cumpla sus condiciones, sin esperar a terminar todo Business.
5. **24–30 de octubre:** verificar D04 contra la entrega, probar manuales D12 y consolidar D13. Corregir contradicciones y enlaces.
6. **31 de octubre–3 de noviembre:** revisar/exportar PDF estratégico, archivo .txt del repositorio, permisos e historial; ensayar demostración. Planificar entrega para el 3 de noviembre mientras se confirma la contradicción del original, que también menciona envío el 8. Demo prevista el 8 de noviembre.

Estas ventanas ordenan trabajo, no prometen capacidad. Si falta disponibilidad, mantener el alcance completo documentado y declarar qué entrega se construye y qué queda pendiente. No reutilizar las 23–35 jornadas antiguas como estimación del trabajo restante.

### Condiciones de paso a desarrollo

Una entrega está preparada cuando: tiene objetivo y prioridad; reglas y dudas bloqueantes resueltas; historias con aceptación; pantallas y estados revisados; datos/permisos/versiones definidos; eventos necesarios especificados; dependencias y estimación técnica revisadas; y evidencia de revisión registrada. Una hipótesis aún no validada puede pasar a un experimento identificado, con riesgo y prueba previstos; no se presenta como demanda comprobada.

La rama de desarrollo debe recibir una entrega trazable: versión/commit de los documentos, resumen de decisiones, tareas concretas, prototipo y escenarios de aceptación. El nombre de la rama destino y el mecanismo de integración se acuerdan antes de integrar; no se presume que exista una rama `development`. Este plan no incorpora cambios de código.

### Cierre documental de la entrega final

- Cada exigencia del assignment tiene documento y evidencia localizable en D04, incluidos analítica administrativa, arquitectura/API, pruebas y posibilidades futuras de Bitcoin/Lightning.
- La validación externa, pruebas internas y resultados simulados se distinguen; la recomendación reconoce límites y decisiones pendientes.
- `/strategy` contiene oportunidad/impacto, especificaciones y prototipo funcional, operación/recursos y enlace al Google Doc con historial real.
- `/src` conserva instalación, arquitectura, lógica, pruebas, limitaciones y manuales técnicos actualizados; el historial diario remoto se verifica, no se infiere del historial local.
- La entrega incluye PDF estratégico, enlace público del repositorio en .txt y demo de 10 minutos ensayada.
- Equipo y fecha se confirman: el original exige cuatro personas (2 Dev y 2 Business) y contiene fechas de envío contradictorias. Registrar la respuesta oficial en 06.

### Próxima acción

Ejecutar D01/D04: responsables, capacidad y matriz requisito → evidencia → tarea. Usar 13/16 para reclutar con consentimiento, ejecutar sesiones y analizar hallazgos; estimar presupuesto antes de cerrar precios. Entregar a Dev módulos listos mientras avanza la validación. Cada entrega debe actualizar estado, evidencia y secciones afectadas del informe 19; proporcionar al usuario texto completo para copiar a Google Docs. Conservar historial en 06 y registros técnicos, sin actividad retroactiva.

### Revisión del 7 de octubre

El usuario confirma continuidad individual: Caleb asume Business y Dev, con horas disponibles por definir. D01 registra esta organización en 06; la condición de cuatro integrantes requiere aclaración con CUBO+. D04 tiene una matriz inicial en 14 con los requisitos oficiales y 47 criterios AC/UX; sigue abierto hasta auditar pruebas y recorridos específicos. La siguiente tarea documental es T-02/T-03: precisar cobertura y contrato de analítica administrativa. No se ejecutaron sesiones ni nuevas pruebas. El calendario continúa siendo orientativo y se ajustará a capacidad real.

### Entrega esencial del 10 de octubre

Por prioridad del usuario, certificados, preguntas, notificaciones y paneles quedaron implementados y verificados sobre main, sin cambiar de rama. D06 dispone de reglas adoptadas en 15 y evidencia técnica; mantiene comunidad, membresías y correcciones de credenciales pendientes. D07 dispone de contrato actualizado en 05, consultas, permisos y paneles probados; no declara reproducción, muestras ni actividad histórica inexistente. D04 enlaza los nuevos criterios en 14. D13 refleja la versión disponible en 19 y el texto plano para copia manual. D08 sigue sin sesiones externas y D09 sin presupuesto completo.

La siguiente prioridad esencial es catálogo/derechos, manuales y ensayo de la demostración; posteriormente correo, conciliación supervisada y procedimientos operativos. El usuario conserva la comprobación móvil del pago. La entrega no cierra automáticamente el assignment completo ni las ampliaciones pendientes; resultados y límites en [registro](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10).

### Avance técnico posterior del 10 de octubre

Por petición del usuario de continuar el desarrollo técnico, se implementó conciliación periódica con `reconcile_payments --watch`. Se verificaron reintentos, rotación de lotes y conservación de reglas de acceso: 192 pruebas, revisión estática, migraciones y tres controles de concurrencia aprobados. [Evidencia y límites](../src/docs/operacion-y-bitacora.md#conciliacion-2026-10-10). La herramienta se ejecuta en un terminal supervisado; instalación como servicio, alertas y comprobación de pago desde ZEUS siguen pendientes. Este avance no acredita validación externa ni cierra D09/D12.

### Comunidad y moderación del 10 de octubre

Por elección del usuario se continúa desarrollo técnico con comunidad por versión, acceso por inscripción, respuestas y reportes, moderación con motivo e historial y suspensión reversible de escritura. Se mantienen compras, progreso y lectura. Se añaden avisos internos y pruebas de permisos, privacidad, reintentos y concurrencia. [Reglas y evidencia](../src/docs/operacion-y-bitacora.md#comunidad-2026-10-10). Trabajo en main; se preservan los archivos de revisión integrada que ya estaban sin seguimiento. Membresías y operación pública siguen pendientes. No se ejecutan sesiones externas ni se publica al remoto.
