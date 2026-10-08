# Trazabilidad y trabajo pendiente

## Base de esta revisión

Matriz inicial preparada el 7 de octubre de 2026. Se consultaron los dos originales de CUBO+ en `docs`, los criterios de 03/08/10 y los registros técnicos. La base documental está integrada en `main` mediante `d0bb7e4`; esta revisión continúa en `business/teorica`. No se reejecutaron pruebas ni se realizaron sesiones con personas.

«Registrado» significa que existe evidencia técnica anterior relacionada; no certifica que cada criterio se haya auditado individualmente. «Parcial» identifica una diferencia o cobertura incompleta. «Pendiente» indica diseño sin entrega acreditada. D04 permanece abierto hasta vincular pruebas específicas, comprobar recorridos y revisar toda la cobertura contra la versión final.

## Requisitos de los originales

| ID | Exigencia | Regla o documento | Evidencia disponible | Brecha y tarea |
|---|---|---|---|---|
| O-01 | Usuario, oportunidad e impacto local | 01, 07, 19 | Hipótesis y análisis documental | D02/D08: contrastar con alumnos y creadores de El Salvador |
| O-02 | Comparar suscripción, publicidad, freemium y micropagos | 13 | Comparación y fuentes del 5 de octubre | D03: contrastar recomendación con usuarios y costos |
| O-03 | Muestras, precios y contenido | 02, 13 | Catálogo ficticio y muestras propuestas | D03/D10: probar comprensión y documentar derechos de activos |
| O-04 | Descubrimiento, pago y desbloqueo con estados completos | 03, 04, AC-01…20 | Registros de comercio y experiencia de compra del 4 de octubre | D05/D08: tareas observadas y estados alternativos |
| O-05 | Persistencia, recompra y datos mínimos de usuario | 03, 08, 13 | Cuentas separadas, biblioteca y derechos por versión | D08: comprobar recuperación y comprensión de compra parcial |
| O-06 | KPIs de conversión, consumo, pago y retención | 05, 19 | Definiciones y eventos comerciales registrados | D07: auditar eventos, consultas, deduplicación y panel |
| O-07 | Wireframes/prototipo y prueba de concepto funcional | 04, 10, 11 | Aplicación y capturas en src/docs/evidence | D05: enlazar tareas y aceptación; identificar contribuciones de Business |
| O-08 | Recursos gratuitos/protegidos y control en servidor | 03, AC-01…06 | Registros de versiones/archivos y comercio | D04: enlazar pruebas específicas de entrega directa y permisos |
| O-09 | Facturas simuladas, confirmación y base de acceso | 03, AC-08…17 | Comercio, FakeWallet y concurrencia registrados | D04/D12: verificar recuperación tras reinicio; documentar supervisión |
| O-10 | Administración de transacciones y actividad; eventos del embudo | 03, 05 | Consulta administrativa y eventos comerciales | D07: completar analítica administrativa; eventos no equivalen a panel completo |
| O-11 | Diseño adaptable | AC-19, UX-08 | Capturas y recorridos escritorio/móvil | D05: auditoría de teclado y dispositivos; no inferirla de capturas |
| O-12 | API, arquitectura, pruebas, límites y futuro Bitcoin/Lightning | src/README.md, src/docs | Documentación y resultados fechados | D04/D12: revisar correspondencia con versión demostrada |
| O-13 | Operación, mantenimiento y recursos | 12, 13 | Referencias de costos y límites operativos | D09: presupuesto completo, responsables y procedimientos |
| O-14 | Evolución diaria y colaboración; Google Doc con historial | 06 | Commits existentes y bitácora local | D01/D11: confirmar equipo; usuario incorpora texto y comparte enlace; no reconstruir historial |
| O-15 | Manuales y reportes claros | 06, src/docs | Reportes técnicos | D12: manuales probados por otra persona |
| O-16 | PDF estratégico, TXT de repositorio público y demo de 10 minutos | 19, original de evaluación | Informe progresivo y exportación copiable | D13: PDF/anexos, acceso público y ensayo; confirmar plazo contradictorio 3/8 de noviembre |

## Responsabilidad actual

Caleb asume todas las tareas de Business y Dev por confirmación del 7 de octubre. Las funciones de la tabla describen el tipo de trabajo, no integrantes adicionales. La capacidad semanal está por definir y el requisito oficial de cuatro personas requiere aclaración con CUBO+.

## Orden de trabajo

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

## Criterios de producto y experiencia

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
| AC-23 | Enviar evaluación | Nota calculada en servidor; intento registrado y límite aplicado | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-24 | Comprar curso sin terminarlo | No se emite certificado | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-25 | Completar requisitos y repetir solicitud | Un certificado verificable por alumno y versión | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-26 | Creador modifica curso ajeno | Acceso denegado | Registrado: estudio de creadores del 3 de octubre. T-02: enlazar permisos y revisión congelada. |
| AC-27 | Enviar borrador a revisión | No es público hasta aprobación; observaciones visibles al autor | Registrado: estudio de creadores del 3 de octubre. T-02: enlazar permisos y revisión congelada. |
| AC-28 | Reportar comentario | Moderación autorizada con registro; terceros no leen espacio restringido | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-29 | Activar membresía mediante pago | Acceso temporal solo al contenido incluido | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-30 | Cancelar renovación | Acceso hasta fin del periodo; no se crea renovación posterior | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-31 | Vencer membresía con compra individual | Compra, progreso y certificado permanecen | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-32 | Repetir confirmación de renovación | Un solo periodo añadido | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-33 | Cambiar temario después de certificado | Certificado conserva su versión y requisitos cumplidos | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| AC-34 | Recuperar contraseña | Token vence y no se reutiliza; no se revelan claves | Registrado: cuentas independientes del 3 de octubre; correo público pendiente. T-02/T-06: enlazar tokens y verificar entrega antes de operación pública. |
| AC-35 | Pregunta y respuesta por lección | Alumno ve respuesta y aviso; creador ve su bandeja | Pendiente: diseño en 08/11. T-04: especificar módulo; después implementar y verificar. |
| UX-01 | Filtrar por tema/nivel, abrir y regresar | Contexto conservado y resultados coherentes | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-02 | Elegir desde el selector | Misma ficha, precio y acceso que el catálogo | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-03 | Buscar tutorial y finalizarlo | Resultado práctico claro, progreso guardado con cuenta | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-04 | Abrir referencia externa y recurso propio | Origen/acción diferenciados; protección solo donde corresponde | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-05 | Encontrar curso mixto en filtro gratis | Se entiende qué está gratis y qué se compra | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-06 | Comprar video reutilizado en una lección | Un permiso abre el mismo recurso; no exige nueva compra | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-07 | Retirar un curso adquirido del catálogo | Sigue accesible en la versión comprada; borradores ajenos siguen ocultos | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-08 | Usar selector, pago y temario con teclado y móvil | Sin controles inaccesibles ni pérdida de selección | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-09 | Perder conexión o sesión al guardar avance | Aviso recuperable; no se anuncia éxito inexistente | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-10 | Actualizar temario/nota mínima | Inscripción y certificado anteriores conservan versión | Parcial: versiones/inscripciones registradas; evaluaciones y certificados pendientes. T-04: congelar requisitos y verificar historia. |
| UX-11 | Navegar sin resultados o con archivo ausente | Mensaje y siguiente acción útil, sin botones engañosos | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
| UX-12 | Recibir evidencia tardía o solapada de pago de prueba | Incidencia conservada, sin permiso indebido ni compra duplicada | Parcial: interfaz/archivos del 2 de octubre y comercio del 4. T-02/T-07: comprobar este escenario completo. |
