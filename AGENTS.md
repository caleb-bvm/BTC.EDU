# Preferencias del usuario para BTC.EDU

Estas instrucciones conservan las preferencias expresadas por el usuario para el trabajo futuro en este proyecto. Las nuevas instrucciones del usuario tienen prioridad.

## Contexto

- El usuario es de El Salvador. Usar El Salvador como contexto del proyecto y evitar atribuirle otro país por la zona horaria del entorno.
- La zona horaria de la aplicación es `America/El_Salvador`.
- Documentar solo lo esencial en los archivos `.md` existentes de `strategy` y `src/docs`. Revisar la rama y el estado del repositorio antes de realizar cambios; no asumir el nombre de la rama de desarrollo ni cambiar de rama sin considerar la tarea vigente.

## Documento del proyecto

- Actualizar los documentos Markdown existentes; no generar exportaciones TXT ni entregas para Google Docs salvo una nueva petición explícita. No editar Google Docs directamente salvo petición explícita.
- Tratarlo como un documento investigativo completo y vivo, que acompañará el proyecto a largo plazo.
- Usar títulos y subtítulos naturales y breves. Por ejemplo, «Resumen» en lugar de «Resumen ejecutivo».
- No incluir por defecto campos de país, caso de estudio, fecha de actualización, estado, equipo o repositorio en el documento principal. El usuario los añadirá si los necesita. Esta preferencia no elimina fechas y referencias necesarias para las evidencias técnicas o la bitácora.
- Centrar el contenido en: la idea; cómo se consolidó; qué investigamos para evaluar su validez; objetivos; enfoque; desarrollo; a dónde queremos llegar; qué demostramos; y logros.
- Explicar las relaciones entre problema, investigación, decisiones, implementación y resultados. Evitar repeticiones, títulos inflados y lenguaje innecesario.
- No inventar entrevistas, resultados, demanda, precios validados ni logros. Distinguir hipótesis, diseño, implementación y verificación. Las pruebas técnicas no equivalen a validación comercial o educativa.

## Actualizaciones

- No guardar ni versionar volcados extensos de pruebas, matrices completas por página, snapshots repetidos o registros verbosos de consola. Los verificadores deben mostrar un resumen en consola por defecto. Conservar solo resultados esenciales, comandos y límites en la documentación existente; cualquier reporte opcional debe ser breve y guardarse dentro de `src/.local/`, ignorado por Git. No crear otro archivo por cada ejecución ni trasladar los volcados eliminados a archivos comprimidos o copias versionadas.
- Limitar las salidas de herramientas y las comprobaciones al cambio solicitado. No leer registros completos ni repetir baterías extensas sin una razón concreta; preferir búsquedas precisas, resúmenes y pruebas focalizadas.

- En la interfaz del producto, evitar banners y textos técnicos sobre desarrollo, demostración, saldo de prueba, regtest o wallets específicas. Explicar el entorno en documentación o durante la presentación, sin distraer al usuario o evaluador dentro de la aplicación. Mostrar los precios únicamente como cantidad y sats; no añadir «Pago único». La comprobación automática del pago debe ser silenciosa; mostrar mensajes cuando exista un error que requiera una acción.

- Cada entrega de desarrollo debe incluir una revisión de la documentación afectada: comportamiento, decisiones, recorridos, pruebas, límites y próximos pasos.
- Actualizar únicamente las secciones afectadas y revisar otras secciones cuando sea necesario para mantener la coherencia.
- Mantener el estado actual separado del historial de cambios. La bitácora debe conservar fechas, versión o commit y evidencias reales; no crear actividad retroactiva.
- Antes de la entrega final, consolidar un documento que corresponda a la versión efectivamente demostrada.

## Referencias

- El texto principal listo para copiar a Google Docs está en `strategy/19-recomendacion-y-entrega-final.md`. Mantenerlo coherente con cada entrega. Investigación comercial y costos: `strategy/investigacion-y-requisitos.md#13-monetizacion-precios-y-muestras`; guiones, tareas y resultados pendientes: `strategy/investigacion-y-requisitos.md#16-validacion-con-usuarios`. No presentar preparación de instrumentos como ejecución de sesiones.
- Consultar los originales de CUBO+ en `docs/Micropayments for Content.docx` y `docs/assignment final evaluation.docx` para requisitos y evaluación.
- El plan de trabajo está en `strategy/investigacion-y-requisitos.md#12-plan-documentacion-business-a-desarrollo`. La estructura y el estilo del informe principal deben seguir las indicaciones posteriores del usuario conservadas aquí, aunque el plan inicial proponga metadatos o títulos distintos.

## Consolidación documental

- Escribir `src/docs/operacion-y-bitacora.md` en primera persona, con un tono natural, como si lo escribiera el usuario. Sintetizar todo el contenido y usar una estructura sencilla que separe operación, decisiones, pendientes e historial por día. En los registros incluir solo la fecha del día, sin país, hora ni zona horaria; conservar las referencias técnicas necesarias y las evidencias reales. Aplicar estas preferencias a futuras actualizaciones de la bitácora.
- Mantener los tres documentos `.md` principales existentes entre `strategy` y `src/docs`: informe, investigación y requisitos, operación y bitácora. Actualizar sus secciones con lo esencial en lugar de crear informes por entrega. La exportación TXT existente se conserva como antecedente y no requiere actualización.
- Las fuentes CUBO+ y las evidencias seleccionadas se conservan aparte. Los volcados extensos de pruebas no se conservan ni versionan. Los documentos de origen integrados son antecedentes; consultar el estado actual y las entregas fechadas antes de interpretar sus pendientes.
