# Requisitos y alcance

Requisitos de CUBO+, decisiones de alcance, especificación funcional y trazabilidad entre requisitos, implementación y evidencias.

<a id="readme"></a>

## Alcance inicial

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

El proyecto es una plataforma web de cursos, videos y materiales, con contenido gratis y de pago. El catálogo local reúne diez cursos y 72 lecciones: seis cursos iniciales de Bitcoin y Lightning y cuatro cursos completos en Creación y Tecnología. De los seis iniciales, tres son gratuitos y tres combinan una lección gratuita y contenido de pago; los cuatro nuevos tienen todas sus lecciones de pago. Los precios nuevos son decisiones editoriales sin validación comercial. La revisión educativa externa sigue pendiente; los ejemplos históricos de programación permanecen documentados por separado.

La [revisión de interfaz](06-interfaz-e-identidad-visual.md#revision-ui-ux) reúne la organización vigente para estudiantes y educadores. La [arquitectura de producto y experiencia](05-arquitectura-de-producto.md#10-arquitectura-y-experiencia-btc-edu) conserva la estructura educativa y los antecedentes: cursos, tutoriales y recursos en la primera academia funcional, eventos educativos después. Las entregas fechadas distinguen lo implementado de los siguientes pasos.

### Qué exige el assignment y qué decidimos

El assignment exige plataforma con contenidos gratis y de pago, facturas simuladas, protección en el servidor, acceso persistente, administración, eventos, diseño adaptable y documentación técnica. Permite lecciones, videos y descargas; no obliga a desarrollar todas las funciones de una plataforma educativa.

El equipo eligió organizar el producto en cursos, capítulos, lecciones, videos y materiales con compras individuales y de cursos completos. El acceso comprado será permanente dentro del MVP, asociado a una cuenta con correo y contraseña. El creador aprobado prepara su contenido y el administrador revisa su publicación. Los contenidos parcialmente adquiridos se ofrecen por separado sin descuentos personalizados.

Al 4 de octubre de 2026, LNbits FakeWallet está integrado: ofertas y revisión, facturas, compra simulada, derechos permanentes sobre revisiones, biblioteca, inscripción y progreso funcionan en desarrollo. No hay fondos reales. Se verificaron vencimientos, pagos en conflicto, recuperación de respuesta perdida y actualizaciones simultáneas. Hay un comando de conciliación; su ejecución periódica supervisada queda pendiente. [Estado, 129 pruebas y evidencia](../src/docs/operacion-y-bitacora.md#comercio-y-aprendizaje-2026-10-04).

Todo el código y la documentación técnica están en [src](../src/docs/operacion-y-bitacora.md#guia-local-anterior). Esta carpeta conserva investigación, requisitos, prototipo y decisiones de Business. Los documentos originales del assignment permanecen en docs sin modificaciones.

### Pendientes

La comparación documental de modelos/tarifas/costos y los instrumentos de entrevistas/usabilidad/precios están preparados al 5 de octubre. Hay una recomendación provisional y un documento principal integrado. Siguen pendientes sesiones externas, precios validados, prototipos nuevos, presupuesto completo, recomendación final y enlace al Google Doc con historial. El usuario incorporará el texto manualmente. Revisar capacidad, equipo y fechas oficiales. No se añadieron funciones ni se modificaron precios por esta actualización.

### Alcance ampliado

Se incluyen progreso, evaluaciones, certificados, preguntas, comunidad, panel de creador y membresías con renovación simulada manual. Los detalles están en el documento 08 y el diseño técnico en src/docs/diseno-plataforma.md. Las funciones observadas en otras plataformas respaldan el diseño, pero todavía deben validarse con usuarios. El estudio de creadores, progreso, evaluaciones, certificados, preguntas y comunidad por versión están implementados. La entrega de perfiles integra Personas, presentación voluntaria, búsqueda y seguimiento de conversaciones; las membresías siguen pendientes. La documentación de diseño no acredita funciones entregadas.

La comunidad también se integra al final de cada lección con comentarios, respuestas del creador, seguimiento y avisos internos, respetando inscripción y acceso al contenido. [Decisión y alcance](08-aprendizaje-creadores-y-comunidad.md#20-comunidad-en-lecciones) y [entrega técnica](../src/docs/operacion-y-bitacora.md#comunidad-en-lecciones-2026-10-12). La validación con usuarios permanece pendiente.

La experiencia de cursos, lectura y continuidad fue ampliada el 12 de octubre: temario con estados, continuación compartida, prácticas con solución desplegable, lectura enfocada y biblioteca con filtros. [Entrega, fuentes, evidencias y alcance de las pruebas](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12). La revisión técnica no equivale a validación educativa o comercial.

<a id="14-trazabilidad-y-backlog"></a>

## Trazabilidad y trabajo pendiente

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Base de esta revisión

Matriz inicial preparada el 7 de octubre de 2026. Se consultaron los dos originales de CUBO+ en `docs`, los criterios de 03/08/10 y los registros técnicos. La base documental está integrada en `main` mediante `d0bb7e4`; esta revisión continúa en `business/teorica`. No se reejecutaron pruebas ni se realizaron sesiones con personas.

«Registrado» significa que existe evidencia técnica anterior relacionada; no certifica que cada criterio se haya auditado individualmente. «Parcial» identifica una diferencia o cobertura incompleta. «Pendiente» indica diseño sin entrega acreditada. D04 permanece abierto hasta vincular pruebas específicas, comprobar recorridos y revisar toda la cobertura contra la versión final.

### Requisitos de los originales

| ID | Exigencia | Regla o documento | Evidencia disponible | Brecha y tarea |
|---|---|---|---|---|
| O-01 | Usuario, oportunidad e impacto local | 01, 07, 19 | Hipótesis y análisis documental | D02/D08: contrastar con alumnos y creadores de El Salvador |
| O-02 | Comparar suscripción, publicidad, freemium y micropagos | 13 | Comparación y fuentes del 5 de octubre | D03: contrastar recomendación con usuarios y costos |
| O-03 | Muestras, precios y contenido | 02, 13 | Catálogo ficticio y muestras propuestas | D03/D10: probar comprensión y documentar derechos de activos |
| O-04 | Descubrimiento, pago y desbloqueo con estados completos | 03, 04, AC-01…20 | Registros de comercio y experiencia de compra del 4 de octubre | D05/D08: tareas observadas y estados alternativos |
| O-05 | Persistencia, recompra y datos mínimos de usuario | 03, 08, 13 | Cuentas separadas, biblioteca y derechos por versión | D08: comprobar recuperación y comprensión de compra parcial |
| O-06 | KPIs de conversión, consumo, pago y retención | 05, 19 | Paneles y consultas probados en core/test_analytics.py; entrega del 10 de octubre | D07: extender reproducción/muestras y retención cuando se definan; no reconstruir visitas históricas |
| O-07 | Wireframes/prototipo y prueba de concepto funcional | 04, 10, 11 | Aplicación y capturas en src/docs/evidence | D05: enlazar tareas y aceptación; identificar contribuciones de Business |
| O-08 | Recursos gratuitos/protegidos y control en servidor | 03, AC-01…06 | Registros de versiones/archivos y comercio | D04: enlazar pruebas específicas de entrega directa y permisos |
| O-09 | Facturas simuladas, confirmación y base de acceso | 03, AC-08…17 | Comercio, FakeWallet y concurrencia registrados | D04/D12: verificar recuperación tras reinicio; documentar supervisión |
| O-10 | Administración de transacciones y actividad; eventos del embudo | 03, 05 | Panel administrativo, ActivityEvent y compras; permisos, cohortes y HTTP verificados el 10 de octubre | Implementado el panel esencial; mantener límites de eventos y probar capacidad antes de operación pública |
| O-11 | Diseño adaptable | AC-19, UX-08 | Capturas y recorridos escritorio/móvil | D05: auditoría de teclado y dispositivos; no inferirla de capturas |
| O-12 | API, arquitectura, pruebas, límites y futuro Bitcoin/Lightning | src/README.md, src/docs | Documentación y resultados fechados | D04/D12: revisar correspondencia con versión demostrada |
| O-13 | Operación, mantenimiento y recursos | 12, 13 | Referencias de costos y límites operativos | D09: presupuesto completo, responsables y procedimientos |
| O-14 | Evolución diaria y colaboración; Google Doc con historial | 06 | Commits existentes y bitácora local | D01/D11: confirmar equipo; usuario incorpora texto y comparte enlace; no reconstruir historial |
| O-15 | Manuales y reportes claros | 06, src/docs | Reportes técnicos | D12: manuales probados por otra persona |
| O-16 | PDF estratégico, TXT de repositorio público y demo de 10 minutos | 19, original de evaluación | Informe progresivo y exportación copiable | D13: PDF/anexos, acceso público y ensayo; confirmar plazo contradictorio 3/8 de noviembre |

### Responsabilidad actual

Caleb asume todas las tareas de Business y Dev por confirmación del 7 de octubre. Las funciones de la tabla describen el tipo de trabajo, no integrantes adicionales. La capacidad semanal está por definir y el requisito oficial de cuatro personas requiere aclaración con CUBO+.

### Orden de trabajo

| Tarea | Prioridad | Resultado de cierre | Función propuesta |
|---|---|---|---|
| T-01 | P0 | Horas disponibles y alcance de mentoría confirmados; condición de equipo aclarada | Caleb (Business + Dev) |
| T-02 | P0 | AC/UX enlazados a pruebas o a una brecha explícita, con versión | Business + Dev |
| T-03 | P0 | Contrato de eventos y cobertura del panel administrativo, con consultas verificables | Dev + Business |
| T-04 | P0 | Políticas de evaluaciones/certificados y preguntas listas para estimación | Business + Dev |
| T-05 | P1 | Consentimiento, reclutamiento y sesiones reales; hallazgos separados de hipótesis | Business |
| T-06 | P1 | Escenarios de costos, catálogo con derechos y procedimientos operativos | Business + Dev |
| T-07 | P1 | Manuales y recorrido de mentoría comprobados contra la versión disponible | Business + Dev |
| T-08 | P2 | Informe consolidado, PDF revisado, enlaces accesibles y demo ensayada | Equipo |

La analítica administrativa pertenece al núcleo oficial. Evaluaciones, certificados, comunidad y membresías son ampliaciones del equipo; su prioridad debe considerar las brechas oficiales antes de comprometer nuevas fechas.

### Criterios de producto y experiencia

Cada fila conserva el escenario y aceptación originales. La columna final indica el registro relacionado y la comprobación que falta; no constituye una nueva ejecución.

| ID | Escenario | Aceptación | Estado documental y siguiente comprobación |
|---|---|---|---|
| AC-01 | Explorar un curso gratis | Todas sus lecciones gratuitas abren sin cuenta | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-02 | Curso gratis con capítulo de pago | Lo gratuito sigue disponible; el capítulo se compra y abre por separado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-03 | Material de pago de un curso gratis | Se compra el archivo sin exigir comprar el curso | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-04 | Comprar video individual | Se abre el video completo sin comprar otros contenidos | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-05 | Comprar curso completo | Se conceden todos los recursos enumerados y ningún extra excluido | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-06 | Pedir texto, video o archivo de pago sin compra | El servidor deniega entrega, incluso por URL directa | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-07 | Comprar sin iniciar sesión | Se solicita cuenta y se conserva el destino | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-08 | Confirmar factura válida | Paid y acceso automático a los recursos correctos | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-09 | Fallo, pendiente o vencimiento | No hay permisos nuevos; reintento según elegibilidad | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-10 | Repetir confirmación | Una sola compra, permisos sin duplicados y un evento de pago | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-11 | Reiniciar y volver a iniciar sesión | Compras y permisos permanecen; pendientes se concilian sin conceder acceso indebidamente | Parcial: persistencia y comando de conciliación registrados; no se probó reinicio de LNbits durante transacción. T-02/T-07: verificar reinicio y supervisión. |
| AC-12 | Entrar desde otro navegador | Se recuperan cursos y compras | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-13 | Consultar facturas de otra cuenta | Acceso denegado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-14 | Tener parte de un curso de pago | Se bloquea compra conjunta y se ofrecen capítulos faltantes | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-15 | Confirmaciones concurrentes con solapamiento | Solo la primera elegible concede permisos; la otra falla | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-16 | Confirmar después del plazo | Expired, sin permisos nuevos | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-17 | Cambiar precio después de facturar | Se conserva el importe facturado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-18 | Entrar a administración como comprador | Acceso denegado | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-19 | Usar móvil y escritorio | Catálogo, lecciones, video, compras y biblioteca funcionan | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-20 | Ocultar contenido comprado | Sigue disponible para su comprador | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-21 | Retomar en otro dispositivo | Misma posición guardada y lecciones completadas | Parcial: completadas y continuación por lección; segundos de video no implementados. T-02/T-04: separar aceptación y tarea restante. |
| AC-22 | Abrir curso gratuito | Inscripción sin compra; extras de pago siguen identificados | Registrado: comercio/aprendizaje y experiencia de compra del 4 de octubre. T-02: enlazar prueba específica y recorrido. |
| AC-23 | Enviar evaluación | Nota calculada en servidor; intento registrado y límite aplicado | Implementado: evaluaciones por versión, corrección, límites e historia. learning/tests.py y learning/test_essential.py; entrega del 7 de octubre y regresión del 10. |
| AC-24 | Comprar curso sin terminarlo | No se emite certificado | Implementado: comprar/inscribirse no basta. test_certificate_requires_completion_and_approval_not_only_enrollment; entrega del 10 de octubre. |
| AC-25 | Completar requisitos y repetir solicitud | Un certificado verificable por alumno y versión | Implementado: credencial única, PDF y verificación voluntaria. Pruebas de reintento/privacidad y verify-essential-concurrency.py; recorrido HTTP del 10 de octubre. |
| AC-26 | Creador modifica curso ajeno | Acceso denegado | Registrado: estudio de creadores del 3 de octubre. T-02: enlazar permisos y revisión congelada. |
| AC-27 | Enviar borrador a revisión | No es público hasta aprobación; observaciones visibles al autor | Registrado: estudio de creadores del 3 de octubre. T-02: enlazar permisos y revisión congelada. |
| AC-28 | Reportar comentario | Moderación autorizada con registro; terceros no leen espacio restringido | Implementado: comunidad por versión, reportes, ocultación/cierre y suspensión reversible con motivo e historial. learning/test_community.py y verify-community-concurrency.py; entrega del 10 de octubre. |
| AC-29 | Activar membresía mediante pago | Acceso temporal solo al contenido incluido | Implementado: plan de la plataforma pagado por Lightning; abre las lecciones de pago de la versión vigente de cursos marcados. commerce/test_membership.py; entrega del 24 de octubre. |
| AC-30 | Cancelar renovación | Acceso hasta fin del periodo; no se crea renovación posterior | Resuelto por diseño: no hay renovación automática; cada periodo requiere una factura nueva y una factura pendiente simplemente vence. Entrega del 24 de octubre. |
| AC-31 | Vencer membresía con compra individual | Compra, progreso y certificado permanecen | Implementado: la compra se evalúa antes que la membresía y el vencimiento no borra avance ni certificados. test_expired_membership_keeps_individual_purchases; entrega del 24 de octubre. |
| AC-32 | Repetir confirmación de renovación | Un solo periodo añadido | Implementado: la confirmación repetida devuelve el mismo periodo y la renovación empieza al final del vigente. commerce/test_membership.py; entrega del 24 de octubre. |
| AC-33 | Cambiar temario después de certificado | Certificado conserva su versión y requisitos cumplidos | Implementado: requisitos y evidencia congelados por versión. test_certificate_name_and_course_version_remain_after_edits y prueba de edición de políticas; entrega del 10 de octubre. |
| AC-34 | Recuperar contraseña | Token vence y no se reutiliza; no se revelan claves | Registrado: cuentas independientes del 3 de octubre; correo público pendiente. T-02/T-06: enlazar tokens y verificar entrega antes de operación pública. |
| AC-35 | Pregunta y respuesta por lección | Alumno ve respuesta y aviso; creador ve su bandeja | Implementado: preguntas privadas, bandeja del creador y avisos. Pruebas de acceso/reintentos/lectura/CSRF y formularios HTTP; entrega del 10 de octubre. |
| UX-01 | Filtrar por tema/nivel, abrir y regresar | Contexto conservado y resultados coherentes | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-02 | Elegir desde el selector | Misma ficha, precio y acceso que el catálogo | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-03 | Buscar tutorial y finalizarlo | Resultado práctico claro, progreso guardado con cuenta | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-04 | Abrir referencia externa y recurso propio | Origen/acción diferenciados; protección solo donde corresponde | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-05 | Encontrar curso mixto en filtro gratis | Se entiende qué está gratis y qué se compra | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-06 | Comprar video reutilizado en una lección | Un permiso abre el mismo recurso; no exige nueva compra | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-07 | Retirar un curso adquirido del catálogo | Sigue accesible en la versión comprada; borradores ajenos siguen ocultos | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-08 | Usar selector, pago y temario con teclado y móvil | Sin controles inaccesibles ni pérdida de selección | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-09 | Perder conexión o sesión al guardar avance | Aviso recuperable; no se anuncia éxito inexistente | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-10 | Actualizar temario/nota mínima | Inscripción y certificado anteriores conservan versión | Implementado para inscripción, evaluaciones y certificado: versiones y reglas históricas inmutables. Pruebas de edición y evidencia en esenciales-2026-10-10.md. |
| UX-11 | Navegar sin resultados o con archivo ausente | Mensaje y siguiente acción útil, sin botones engañosos | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-12 | Recibir evidencia tardía o solapada de pago de prueba | Incidencia conservada, sin permiso indebido ni compra duplicada | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |

### Auditoría de la entrega esencial

Al 10 de octubre, O-06/O-10 y T-03 disponen de paneles de creador/administración, fuentes ORM, ActivityEvent y pruebas específicas en core/test_analytics.py. No se cierra cobertura completa de eventos: reproducción/muestras y retención automática siguen pendientes. T-04 queda cubierto para evaluaciones/certificados/preguntas mediante 15; comunidad y membresías conservan diseño pendiente. 179 pruebas pasan, con concurrencia y evidencia HTTP de formularios y permisos. [Registro y capturas](../src/docs/operacion-y-bitacora.md#esenciales-2026-10-10). El resto de criterios parciales conserva sus brechas: esta entrega no acredita auditoría completa de teclado, reinicio transaccional de LNbits ni usuarios externos.

### Huellas de certificados

Cada credencial conserva una huella SHA-256 de sus datos y evidencia histórica. El PDF y la página de verificación muestran esa huella; quien recibe el certificado puede compararla con el registro y descargar los datos para recalcularla. La comprobación detecta diferencias y mantiene visible cualquier revocación. La huella verifica integridad frente a la referencia de BTC.EDU; la autenticidad del emisor depende de consultar su página legítima. No constituye una firma digital ni un registro en Bitcoin.

Implementado y verificado el 10 de octubre. [Contrato, privacidad, migración y pruebas](../src/docs/operacion-y-bitacora.md#certificados-sha256-2026-10-10). La exportación permite recalcular exactamente los bytes JSON; no representa el hash de todo el PDF.

Desde el 23 de octubre de 2026, la huella puede sellarse con OpenTimestamps cuando `CERTIFICATE_TIMESTAMPS=true`. La prueba `.ots` corresponde al archivo de datos, cuyo SHA-256 es la huella, y se descarga desde el certificado y su verificación pública. Prueba la existencia de esos datos en una fecha anclada en Bitcoin; no firma la emisión ni refleja revocaciones posteriores. No se ensayó contra los calendarios reales. [Ampliación](07-compra-y-comercio.md#ampliacion-comparativa).

### Perfiles y comunidad

Entrega del 12 de octubre de 2026 sobre `main`, base `4000ed5`, con cambios locales. Estudiantes con alias, presentación e intereses, perfil privado por defecto y compartición reversible. Creadores con ficha y catálogo existentes integrados en Personas y conversaciones. Comunidad por versión con búsqueda que respeta ocultación, filtros y seguimiento con avisos internos. Cubre ampliación de AC-28 sin abrir espacios a terceros ni publicar información académica privada. 227 pruebas, Ruff, migraciones y cuatro controles de concurrencia; 35 pruebas específicas repetidas tras ajustes. [Contrato y evidencia](../src/docs/operacion-y-bitacora.md#perfiles-y-comunidad-2026-10-12). Verificación de correo, preferencias de avisos, soluciones, apelaciones y operación pública siguen pendientes. Este registro no convierte preparación de instrumentos en sesiones con usuarios.

### Conversaciones en lecciones

Entrega del 12 de octubre de 2026 en `main`, base `4000ed5`, cambios locales. Amplía AC-28 y el acompañamiento de AC-35 con comentarios compartidos ligados a una lección y versión; conserva las preguntas privadas. Incluye respuestas, seguimiento, avisos al creador y permisos de lección en lectura, búsqueda, reportes, respuestas y notificaciones. [Diseño y criterios](08-aprendizaje-creadores-y-comunidad.md#20-comunidad-en-lecciones) y [verificación técnica](../src/docs/operacion-y-bitacora.md#comunidad-en-lecciones-2026-10-12). Marcar soluciones, destacar respuestas y evaluar utilidad con participantes siguen pendientes.

### Evidencia del recorrido de aprendizaje

Entrega del 12 de octubre de 2026: continuidad compartida entre ficha y biblioteca, inscripción para empezar, estados del temario, práctica/solución, lectura enfocada, filtros y precios por unidad. Se verificaron 39 pruebas enfocadas, la recuperación del cliente y cuatro controles de concurrencia. Las capturas usan cuentas temporales; las sesiones externas siguen pendientes. El chequeo general de esta tarea registró seis incidencias en cambios concurrentes de cuentas/creadores, por lo que no acredita verificación global. [Comportamiento, respaldo, resultados y límites](../src/docs/operacion-y-bitacora.md#experiencia-aprendizaje-2026-10-12).

<a id="03-especificacion-funcional"></a>

## Especificación funcional

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

**Referencia vigente de estructura, 2 de octubre de 2026:** [arquitectura y experiencia](05-arquitectura-de-producto.md#10-arquitectura-y-experiencia-btc-edu). Incorpora tutoriales y biblioteca de referencias/recursos, selector por tema/nivel, versiones y reglas de disponibilidad. Se conservan AC-01…35. Archivar para descubrimiento no equivale a convertir en borrador ni retirar acceso adquirido; evidencia de pago tardío o solapado se conserva para conciliación aunque no conceda permisos. El diseño no demuestra implementación.

### Plataforma y cuentas

La investigación del 5 de octubre se incorpora en [13](04-producto-y-monetizacion.md#13-monetizacion-precios-y-muestras) y [16](10-metricas-y-validacion.md#16-validacion-con-usuarios). Mantiene AC-01…35 y reglas vigentes. Publicidad, tarifas externas o equivalencia USD son investigación/propuestas de prueba, sin introducir funciones ni cambiar ofertas, acceso permanente o proveedor. Auditar cobertura analítica antes de informar resultados del embudo.

El sitio incluye catálogo de cursos y contenidos, páginas de cursos con capítulos y lecciones ordenados, reproductor de video, materiales descargables, cuenta, pago, Mis cursos y compras, y administración. Permite filtrar por formato, tema y contenido gratuito o de pago.

El visitante explora cursos, abre contenidos gratuitos y ve muestras sin cuenta. Para comprar se registra con correo y contraseña. Al iniciar sesión desde otro dispositivo recupera sus compras. La recuperación de contraseña se implementa con un token de un solo uso y correo configurable según el documento 08. La verificación de correo para publicación pública se definirá al configurar el despliegue; las pruebas usan cuentas ficticias.

Los creadores aprobados tienen perfil y panel para crear y gestionar su propio contenido. El administrador revisa las publicaciones. El comprador no puede consultar compras o facturas ajenas ni acceder al panel. Ser administrador no equivale a tener una compra.

### Cursos y compras

Un curso organiza capítulos, lecciones, videos y materiales. Cada recurso tiene formato y condición gratuita o de pago. Los capítulos pueden agrupar varias lecciones y videos. Un video puede venderse individualmente. El usuario no debe comprar un curso para comprar un video individual o un material que se ofrece por separado.

Las ofertas de curso completo o capítulo enumeran los recursos incluidos. Los materiales adicionales pueden quedar fuera y venderse aparte. Las relaciones del catálogo se distinguen de los permisos: estar asociado a un curso no concede acceso por sí mismo.

Cada compra concede permisos permanentes a los recursos incluidos. Una oferta completamente adquirida muestra enlaces para abrir su contenido. Si una oferta de curso o capítulo está parcialmente adquirida, su compra conjunta queda bloqueada y se ofrecen los contenidos faltantes que tengan oferta individual. El catálogo de prueba garantiza esas ofertas. No hay descuentos personalizados.

Los permisos, compras y fechas se conservan en la base de datos. Las versiones publicadas conservan su composición para compras existentes; nuevas versiones y sus condiciones se gestionan según el documento 08.

### Facturas y LNbits

LNbits con FakeWallet genera y verifica pagos internos de prueba. No se transfieren fondos reales. Las claves se usan únicamente en el servidor de la plataforma.

La factura pertenece a una cuenta y una oferta: curso, capítulo, video o material. Guarda una copia del importe y los recursos incluidos. Cambiar el precio no modifica facturas existentes.

Estados: Pending, Paid, Expired y Failed. Nace Pending, vence en 15 minutos y solo puede pasar a un estado terminal. Una cuenta solo mantiene una factura Pending vigente por oferta; solicitar otra devuelve la existente.

El servidor verifica propietario, plazo y pago. La confirmación válida concede acceso automáticamente, en una operación que no puede duplicar compras, permisos ni eventos. El navegador no concede permisos.

Antes de crear y confirmar una factura se comprueba lo ya adquirido. Ante solapamiento por compras concurrentes, la segunda factura falla sin conceder permisos. Esta regla está diseñada para la simulación; una integración real debe resolver los cobros confirmados antes de aplicar bloqueos comerciales.

La demostración permite confirmar, fallar y expirar mediante controles claramente identificados. El vencimiento también se aplica por tiempo. FakeWallet no resuelve por sí sola todos los estados ni la recuperación de pendientes tras reiniciar: se debe implementar y probar en el servicio de pagos de la plataforma.

Un fallo o vencimiento permite reintentar con una nueva factura si la oferta sigue siendo elegible. Un error de conexión permite consultar la misma factura; no se presume fallo ni se crea otra automáticamente.

### Protección de contenido

El servidor verifica permiso antes de entregar textos, videos completos y descargas de pago. No se incluyen en HTML público, datos iniciales ni archivos estáticos accesibles sin autorización. El reproductor obtiene el video a través de una ruta protegida que permite reproducción y solicitudes parciales. Las muestras públicas usan contenido separado. No se promete impedir que un comprador copie lo que ya puede ver.

### Administración

Crear y editar cursos, orden de capítulos y lecciones, textos, videos, archivos, descripciones, muestras, precios y visibilidad. Validar formato y tamaño de archivos. Los archivos de pago se guardan fuera del almacenamiento público.

Ocultar contenido lo retira del catálogo pero conserva el acceso de quienes lo compraron. No se eliminan recursos adquiridos. El panel muestra facturas, cuenta compradora, oferta, importe, estado y fecha; permite filtrar por estado y consultar actividad y métricas. No muestra contraseñas ni claves de LNbits.

### Criterios de aceptación

| ID | Escenario | Resultado |
|---|---|---|
| AC-01 | Explorar un curso gratis | Todas sus lecciones gratuitas abren sin cuenta |
| AC-02 | Curso gratis con capítulo de pago | Lo gratuito sigue disponible; el capítulo se compra y abre por separado |
| AC-03 | Material de pago de un curso gratis | Se compra el archivo sin exigir comprar el curso |
| AC-04 | Comprar video individual | Se abre el video completo sin comprar otros contenidos |
| AC-05 | Comprar curso completo | Se conceden todos los recursos enumerados y ningún extra excluido |
| AC-06 | Pedir texto, video o archivo de pago sin compra | El servidor deniega entrega, incluso por URL directa |
| AC-07 | Comprar sin iniciar sesión | Se solicita cuenta y se conserva el destino |
| AC-08 | Confirmar factura válida | Paid y acceso automático a los recursos correctos |
| AC-09 | Fallo, pendiente o vencimiento | No hay permisos nuevos; reintento según elegibilidad |
| AC-10 | Repetir confirmación | Una sola compra, permisos sin duplicados y un evento de pago |
| AC-11 | Reiniciar y volver a iniciar sesión | Compras y permisos permanecen; pendientes se concilian sin conceder acceso indebidamente |
| AC-12 | Entrar desde otro navegador | Se recuperan cursos y compras |
| AC-13 | Consultar facturas de otra cuenta | Acceso denegado |
| AC-14 | Tener parte de un curso de pago | Se bloquea compra conjunta y se ofrecen capítulos faltantes |
| AC-15 | Confirmaciones concurrentes con solapamiento | Solo la primera elegible concede permisos; la otra falla |
| AC-16 | Confirmar después del plazo | Expired, sin permisos nuevos |
| AC-17 | Cambiar precio después de facturar | Se conserva el importe facturado |
| AC-18 | Entrar a administración como comprador | Acceso denegado |
| AC-19 | Usar móvil y escritorio | Catálogo, lecciones, video, compras y biblioteca funcionan |
| AC-20 | Ocultar contenido comprado | Sigue disponible para su comprador |

### Fuera de esta primera versión

Bitcoin/Lightning con fondos reales, comisiones y liquidaciones, recomendaciones automáticas, vigilancia de exámenes y descuentos personalizados. Se incluyen creación por usuarios aprobados, progreso, evaluaciones, certificados, comunidad y membresías; ver documento 08. Las renovaciones iniciales se pagan manualmente con facturas simuladas.

### Ampliación de requisitos

El documento [08](08-aprendizaje-creadores-y-comunidad.md#08-aprendizaje-creadores-y-membresias) forma parte de esta especificación: define progreso, evaluaciones, certificados, roles de creador, publicación, comunidad, membresías y criterios AC-21 a AC-35. El acceso se concede por recurso gratuito, compra permanente o membresía vigente. La inscripción gratuita no concede recursos de pago. Para compras individuales se mantienen los criterios anteriores.
