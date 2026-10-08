# Evaluaciones por versión

Entrega del 7 de octubre de 2026, El Salvador. Añade el recorrido creador → borrador → revisión → evaluación del alumno → resultado y autorización de otro intento. Conserva compras, inscripción y progreso existentes. Certificados y preguntas por lección continúan como próximos módulos.

## Reglas implementadas

Cada lección puede tener una evaluación de 1 a 20 preguntas, con 2 a 6 opciones diferentes por pregunta. Admite selección única y múltiple. Todas las preguntas tienen el mismo peso; selección múltiple exige coincidencia exacta, sin crédito parcial ni penalización adicional. La nota mínima admite 0…100. El servidor compara `aciertos × 100` con `nota mínima × preguntas`; redondear a dos decimales es solo presentación.

El creador configura 1…10 intentos iniciales, espera de 0…10 080 minutos, obligatoriedad y soluciones al entregar o solo al aprobar ese intento. No hay ponderaciones, orden aleatorio, ensayos, vigilancia ni temporizador.

Iniciar consume un intento. Solo existe uno abierto por inscripción/evaluación. Repetir inicio recupera el existente. Se pueden guardar respuestas parciales y retomar con otra sesión; no hay vencimiento automático. Salir sin guardar pierde las modificaciones locales. Entregar exige responder todas las preguntas y cierra el intento. No se acepta nota ni aprobación del navegador.

Una entrega repetida devuelve el resultado conservado. Un guardado con revisión obsoleta se rechaza, sin sobrescribir respuestas más recientes. Si hay espera, empieza al entregar el intento anterior y termina antes de iniciar otro; no impide retomar uno abierto.

Una evaluación obligatoria bloquea «Marcar lección completada» hasta que exista un intento aprobado. Leer, guardar continuación y estudiar otras lecciones accesibles siguen disponibles. Aprobar no marca automáticamente la lección: el alumno conserva la acción explícita. Una nota posterior menor no revoca una aprobación anterior. La evaluación opcional no bloquea el completado.

El creador puede autorizar un intento adicional cuando los anteriores están agotados, indicando motivo de hasta 500 caracteres. No borra resultados ni reinicia el contador o la espera. La autorización conserva responsable, fecha, evaluación, inscripción y límite anterior; repetir la solicitud no añade dos intentos.

## Publicación e historia

`QuizDraft` pertenece a la lección editable. Guardarlo reserva el mismo bloqueo de escritura del curso que la publicación; rechaza borradores obsoletos. Al preparar el envío, se copia a `VersionQuiz`, unido a la lección de esa composición antes de sellarla. La revisión editorial muestra preguntas, soluciones y reglas de la copia enviada.

Las ediciones posteriores no cambian lo enviado ni lo publicado. Una nueva publicación conserva sus propias reglas. Desactivar la evaluación solo la excluye de la siguiente composición. Intentos, aprobaciones y autorizaciones siguen asociados a inscripción/evaluación históricas; no se copian a otra versión.

`QuizAttempt` conserva respuestas, número, revisión, fechas, aciertos, nota y aprobación. Una restricción garantiza un intento abierto por inscripción/evaluación y otra impide repetir su número. `ExtraQuizAttempt` conserva las autorizaciones. La administración ofrece consulta de evaluaciones, intentos y autorizaciones, sin acciones de creación, eliminación o edición de esos registros desde sus formularios.

## Permisos y privacidad

El alumno necesita cuenta activa de estudiante, inscripción en esa versión y acceso a la lección. Inscribirse no desbloquea una evaluación de una lección de pago. Ni conocer un identificador ni aprobar una evaluación concede contenido comprado. Las versiones enviadas pero no publicadas no son evaluables por estudiantes.

El creador aprobado solo edita evaluaciones y consulta resultados de sus cursos. Ve nombre/correo del alumno relacionado, versión, número de intento, fecha y resultado; los resultados están paginados. No se expone una lista global de estudiantes. El revisor autorizado ve el contenido del envío mediante los permisos editoriales existentes.

Todas las escrituras requieren POST con CSRF. Las soluciones no se incluyen en el HTML del intento abierto. Si se eligió mostrarlas solo al aprobar, una entrega fallida muestra la nota y las respuestas propias, sin soluciones ni explicaciones.

## Recorridos de uso

### Creador

Abrir Mi contenido, entrar al curso y elegir «Evaluación» en la lección. Configurar reglas y preguntas; cada opción va en una línea y las correctas se indican con números desde 1, separados por comas. Guardar conserva el borrador. «Añadir pregunta» agrega campos; sin JavaScript se puede guardar y aprovechar la pregunta vacía que aparece al volver. Marcar «Eliminar» quita una pregunta del borrador al guardar. Para publicar, volver al curso y enviar la versión a revisión.

El enlace «Ver resultados de evaluaciones» del curso reúne sus versiones. Tras agotar el límite, el último intento presenta el formulario de autorización con motivo. Los intentos anteriores y las últimas autorizaciones permanecen visibles.

### Alumno

Añadir el curso a Mi aprendizaje y abrir una lección accesible con evaluación. Elegir «Ver evaluación e intentos», leer las reglas y empezar. Guardar respuestas antes de salir; continuar desde el intento en curso. Entregar cuando todas las preguntas estén respondidas. Tras aprobar una evaluación obligatoria, volver a la lección y marcarla como completada.

### Demostración aislada

Desde `src`, ejecutar `./.venv/Scripts/python.exe scripts/preview-assessments.py`. Crea SQLite/archivos temporales dentro de `.local` y escucha en `127.0.0.1:8015`. Imprime enlaces de estudiante, editor y revisión. Las cuentas temporales no tienen contraseña utilizable. El cambio de identidad `?vista=...` existe exclusivamente en ese script; no forma parte de las rutas normales. No necesita emitir facturas ni realizar pagos. Detener la demostración libera su base temporal.

## Verificación

La comprobación completa aprobó **148 pruebas Django**, consistencia de migraciones, Ruff y concurrencia comercial. Incluye **19 pruebas nuevas de evaluaciones**: publicación/historia, inmutabilidad, reglas inválidas, guardado/retoma, selección exacta, cálculo, límites/espera, autorizaciones, permisos, CSRF, privacidad y completado obligatorio/opcional. Después de corregir el bloqueo de autorización concurrente, las 19 pruebas se reejecutaron y aprobaron.

`scripts/verify-assessment-concurrency.py` aprobó con conexiones SQLite independientes sobre archivo temporal: inicio único, guardados simultáneos con uno rechazado por obsoleto, entregas conflictivas con un único resultado, autorización adicional idempotente y nuevo inicio único. Se incorpora a `scripts/check-platform.ps1`. No es una prueba de capacidad pública.

Navegador Chromium sin interfaz visible, conectado mediante un puente de prueba al cliente Django con CSRF: guardar/recuperar respuestas, selección múltiple parcial con nota 50, nuevo intento con nota 100, completado tras aprobar, editor dinámico y revisión congelada. Se inspeccionaron capturas a 1366×900 y 390×844 y no hubo desbordamiento horizontal en las pantallas comprobadas. Las peticiones y respuestas proceden de Django; el puente adapta las redirecciones para el navegador y entrega archivos estáticos locales. La conexión HTTP directa al servidor local no pudo verificarse por un fallo de acceso en este entorno. No sustituye dispositivos físicos, auditoría completa de accesibilidad ni sesiones externas.

### Capturas

- [Reglas en escritorio](evidence/evaluacion-reglas-escritorio.png)
- [Intento guardado en móvil](evidence/evaluacion-intento-movil.png)
- [Resultado aprobado en móvil](evidence/evaluacion-aprobada-movil.png)
- [Editor en móvil](evidence/evaluacion-editor-movil.png)
- [Editor en escritorio](evidence/evaluacion-editor-escritorio.png)
- [Resultados del creador](evidence/evaluacion-resultados-escritorio.png)

## Migración y límites

Aplicada `learning.0003_quizdraft_versionquiz_quizattempt_extraquizattempt` con respaldo SQLite en `.local/backups/platform-before-assessments-20261007-184932.sqlite3`. Se compararon todas las filas originales de 35 tablas: ninguna fue modificada o eliminada. Django añadió cuatro tipos de contenido y 16 permisos, además del registro de migración. Las cuatro tablas de evaluaciones permanecen vacías en la base principal. Integridad SQLite y claves foráneas verificadas. No se cargaron cuentas, cursos ni resultados de demostración allí.

Persiste la advertencia conocida de correo no único: el backend distingue correo y tipo de cuenta. Este bloque no cambia pagos, proveedor ni condiciones de acceso. Las pruebas verifican comportamiento técnico; no acreditan aprendizaje, demanda ni voluntad de pago.

Próximo bloque: requisitos versionados de finalización y certificados verificables, aprovechando las aprobaciones conservadas. Después, preguntas por lección. Operación pública, correo real, métricas completas, comunidad y membresías permanecen pendientes.
