# Plan de documentación: Business → Desarrollo

Fecha: 5 de octubre de 2026 (El Salvador). Rama de trabajo: `business/teorica`, creada desde `main` en `c0ac528`. El plan se actualiza con la investigación documental incorporada en 13, los instrumentos de 16 y el informe de 19. No acredita sesiones externas ni nuevas funciones.

## Objetivo y punto de partida

Preparar un paquete de decisiones, especificaciones y evidencias que permita continuar el desarrollo sin ambigüedades y cumplir los entregables estratégicos del assignment. El desarrollo ya comenzó: la documentación registra cuentas separadas, publicación versionada, compras simuladas, biblioteca y progreso. Las 129 pruebas son un resultado registrado al 4 de octubre, no una ejecución nueva de esta revisión.

Las fuentes de alcance son los originales de `docs/Micropayments for Content.docx` y `docs/assignment final evaluation.docx`, los documentos 01–11 de esta carpeta y los registros de `src/docs`. La documentación existente debe completarse y armonizarse antes de duplicarla.

El assignment exige investigación de modelos de monetización, usuarios, precios, muestras, recorrido de pago, prototipo, métricas y recomendación; además, oportunidad/impacto, operación/recursos y Google Doc con historial. Evaluaciones, certificados, comunidad y membresías son ampliaciones del equipo: se conservan en el alcance, con entregas separadas del núcleo exigido.

## Documento principal del proyecto exigido para la entrega

La evaluación exige entregar un **PDF que detalle la solución estratégica del caso de estudio**, junto con un archivo `.txt` que contenga el enlace al repositorio público. El documento principal del proyecto será ese informe integrado: explicará BTC.EDU a un evaluador que no conoce el repositorio y remitirá a evidencias concretas. Su preparación empieza ahora y se actualiza durante el trabajo; la exportación final depende de los resultados disponibles. D13 incluye este informe además de la recomendación y preparación de entrega.

El PDF, los documentos de trabajo de `/strategy` y el Google Doc con historial cumplen funciones distintas. El informe presenta la solución y sus resultados; los documentos de trabajo permiten construirla y verificarla; el Google Doc acredita evolución diaria real. La evaluación también exige especificaciones claras y una prueba de concepto funcional: describirlas en el informe debe ir acompañado de evidencia accesible.

### Índice propuesto del informe

Este índice es una propuesta del equipo alineada con los originales; CUBO+ no fija un índice, extensión ni plantilla en los archivos recibidos.

La estructura acordada posteriormente con el usuario sustituye la propuesta inicial: Introducción; La idea; El problema; Cómo consolidamos la idea; Investigación; Objetivos; Enfoque; Desarrollo; A dónde queremos llegar; Qué demostramos; Logros; Próximos pasos; Conclusiones; Referencias. El [informe](19-recomendacion-y-entrega-final.md) desarrolla esta estructura investigativa.

Usar títulos naturales y omitir campos de país, caso, fecha de actualización, estado, equipo y repositorio en la portada; el usuario los añadirá si corresponde. Mantener fechas/versiones en bitácora y evidencias. Los criterios de evaluación siguen cubiertos por el contenido y anexos: oportunidad, monetización, prototipo/especificaciones, métricas, operación, colaboración y recomendación. No se eliminan requisitos del assignment por esta preferencia editorial.

### Relación con los pilares de evaluación

| Pilar del original de evaluación | Cómo lo cubrirá el informe | Evidencia acompañante |
|---|---|---|
| Transparencia y evolución | Avances y decisiones fechados, con límites explícitos | Commits publicados y Google Doc con historial accesible |
| Ejecución técnica | Explicación de funcionamiento y verificación | Código organizado, README técnico, pruebas y demo funcional |
| Colaboración real | Contribuciones de Business y Dev al mismo problema y decisiones compartidas | Trabajo por integrante, especificaciones, validación y prueba de concepto |
| Documentación | Informe comprensible y recorridos reproducibles | Reportes de avance y manuales de usuario |
| Propuesta de valor | Utilidad e innovación justificadas para el ecosistema Bitcoin en El Salvador | Investigación, hallazgos, comparación de alternativas y resultados |

No se asignan pesos ni puntuaciones: los originales proporcionados no los especifican. Antes de exportar, comprobar que cada afirmación de resultado tiene evidencia, que los enlaces son accesibles al jurado y que el contenido coincide con la versión demostrada.

## Inventario y brechas

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

## Paquetes de trabajo

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
| D13 / P0 → P2 | Informe principal en `19-recomendacion-y-entrega-final.md` y PDF estratégico | Redacción progresiva del documento del proyecto según el índice de este plan; caso estratégico, evidencia, recomendación, resultados y anexos; guion de demo de 10 minutos | Cobertura de los cinco pilares; recomendación sustentada en D03/D08/D09; PDF revisado; archivo .txt del repositorio público y enlaces comprobados | Iniciar con fuentes existentes; cierre con D08–D12 / equipo |

Estado del 5 de octubre: D03 tiene comparación y recomendación provisional en 13, pendiente de validar precios y sostenibilidad; D08 tiene instrumentos en 16, pendiente de ejecución/resultados; D13 tiene informe integrado en 19, pendiente de resultados finales, PDF y anexos. D02 sigue pendiente de evidencia con usuarios y D09 del presupuesto completo. Los otros archivos propuestos no se crean como encabezados vacíos. Este avance no cierra los criterios de aceptación de paquetes todavía incompletos.

## Decisiones que deben cerrarse antes de programar cada módulo

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

## Orden de ejecución y calendario propuesto

1. **5–7 de octubre:** D01/D02 y matriz inicial D04; iniciar D11 y la redacción del informe principal D13 con hechos y fuentes existentes. Armonizar documentos que mezclan diseño y estado actual. Identificar responsables, participantes y capacidad disponible.
2. **8–12 de octubre:** D03, D05, contrato D07 y primeras sesiones D08. Preparar el paquete de la siguiente entrega con D06. Para mentoría, reunir evidencias del núcleo ya construido y declarar pendientes.
3. **13 de octubre:** mentoría: demostrar un recorrido real y explicar oportunidad, reglas de acceso, hipótesis comerciales y evidencia disponible. Registrar observaciones sin simular validación externa.
4. **14–23 de octubre:** completar D06 por orden de desarrollo; iterar D05/D08; cerrar D09/D10. Entregar cada módulo a Dev cuando cumpla sus condiciones, sin esperar a terminar todo Business.
5. **24–30 de octubre:** verificar D04 contra la entrega, probar manuales D12 y consolidar D13. Corregir contradicciones y enlaces.
6. **31 de octubre–3 de noviembre:** revisar/exportar PDF estratégico, archivo .txt del repositorio, permisos e historial; ensayar demostración. Planificar entrega para el 3 de noviembre mientras se confirma la contradicción del original, que también menciona envío el 8. Demo prevista el 8 de noviembre.

Estas ventanas ordenan trabajo, no prometen capacidad. Si falta disponibilidad, mantener el alcance completo documentado y declarar qué entrega se construye y qué queda pendiente. No reutilizar las 23–35 jornadas antiguas como estimación del trabajo restante.

## Condiciones de paso a desarrollo

Una entrega está preparada cuando: tiene objetivo y prioridad; reglas y dudas bloqueantes resueltas; historias con aceptación; pantallas y estados revisados; datos/permisos/versiones definidos; eventos necesarios especificados; dependencias y estimación técnica revisadas; y evidencia de revisión registrada. Una hipótesis aún no validada puede pasar a un experimento identificado, con riesgo y prueba previstos; no se presenta como demanda comprobada.

La rama de desarrollo debe recibir una entrega trazable: versión/commit de los documentos, resumen de decisiones, tareas concretas, prototipo y escenarios de aceptación. El nombre de la rama destino y el mecanismo de integración se acuerdan antes de integrar; no se presume que exista una rama `development`. Este plan no incorpora cambios de código.

## Cierre documental de la entrega final

- Cada exigencia del assignment tiene documento y evidencia localizable en D04, incluidos analítica administrativa, arquitectura/API, pruebas y posibilidades futuras de Bitcoin/Lightning.
- La validación externa, pruebas internas y resultados simulados se distinguen; la recomendación reconoce límites y decisiones pendientes.
- `/strategy` contiene oportunidad/impacto, especificaciones y prototipo funcional, operación/recursos y enlace al Google Doc con historial real.
- `/src` conserva instalación, arquitectura, lógica, pruebas, limitaciones y manuales técnicos actualizados; el historial diario remoto se verifica, no se infiere del historial local.
- La entrega incluye PDF estratégico, enlace público del repositorio en .txt y demo de 10 minutos ensayada.
- Equipo y fecha se confirman: el original exige cuatro personas (2 Dev y 2 Business) y contiene fechas de envío contradictorias. Registrar la respuesta oficial en 06.

## Próxima acción

Ejecutar D01/D04: responsables, capacidad y matriz requisito → evidencia → tarea. Usar 13/16 para reclutar con consentimiento, ejecutar sesiones y analizar hallazgos; estimar presupuesto antes de cerrar precios. Entregar a Dev módulos listos mientras avanza la validación. Cada entrega debe actualizar estado, evidencia y secciones afectadas del informe 19; proporcionar al usuario texto completo para copiar a Google Docs. Conservar historial en 06 y registros técnicos, sin actividad retroactiva.

## Revisión del 7 de octubre

El usuario confirma continuidad individual: Caleb asume Business y Dev, con horas disponibles por definir. D01 registra esta organización en 06; la condición de cuatro integrantes requiere aclaración con CUBO+. D04 tiene una matriz inicial en 14 con los requisitos oficiales y 47 criterios AC/UX; sigue abierto hasta auditar pruebas y recorridos específicos. La siguiente tarea documental es T-02/T-03: precisar cobertura y contrato de analítica administrativa. No se ejecutaron sesiones ni nuevas pruebas. El calendario continúa siendo orientativo y se ajustará a capacidad real.
