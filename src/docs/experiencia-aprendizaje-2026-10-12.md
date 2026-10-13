# Cursos, lectura y continuidad del aprendizaje

Revisión y entrega del 12 de octubre de 2026, en El Salvador. Trabajo sobre `main`, base `4000ed5`, con cambios locales anteriores conservados. Este registro documenta cambios sin commit propio; no atribuye actividad retrospectiva ni validación externa.

## Qué encontramos

La ficha del curso abría la primera lección accesible sin considerar la posición guardada. La biblioteca sí tenía continuación, pero no compartía esa decisión con la ficha. El temario no distinguía lecciones completadas ni evaluaciones; el lector mostraba explicación, práctica y solución como párrafos similares. El avance, las compras, las preguntas y la navegación se repartían entre paneles con acciones de peso parecido. En móvil el temario aparecía después del texto, dificultando orientarse antes de estudiar.

Son hallazgos de inspección del código y de las pantallas locales. No se midieron abandono, tiempo de tarea o satisfacción con participantes.

## Referencias y decisiones

Se consultaron fuentes primarias el 12 de octubre de 2026. [Las heurísticas de NN/g](https://www.nngroup.com/articles/ten-usability-heuristics/) respaldan visibilidad del estado, control del usuario y reconocimiento. Se aplican mediante progreso visible, estados expresados con palabras y acciones reversibles. [La divulgación progresiva de NN/g](https://www.nngroup.com/articles/progressive-disclosure/) orienta a presentar las acciones principales y desplegar opciones secundarias cuando se necesitan; se aplica al acceso, requisitos detallados y soluciones. [W3C sobre estructura de página](https://www.w3.org/WAI/tutorials/page-structure/) respalda regiones, títulos y navegación comprensible. [La ayuda de Udemy sobre finalización](https://support.udemy.com/hc/en-us/articles/229607188-How-to-Mark-or-Unmark-Lectures-as-Complete-on-a-Browser) ofrece una referencia de estados visibles junto a la lección y reversión de la marca.

Estas fuentes orientan decisiones de diseño; no prueban que BTC.EDU aumente retención, finalización o aprendizaje. Se conserva la regla propia: abrir una lección guarda la continuación, pero completarla requiere una acción del estudiante y la aprobación de una evaluación obligatoria cuando exista.

## Comportamiento vigente

La ficha ordena descripción, nivel, duración estimada del curso, objetivos y requisitos. Ofrece navegación directa al temario y al certificado. La acción principal distingue empezar, continuar, repasar o revisar acceso. Un estudiante que empieza añade la versión a su biblioteca y abre una lección accesible mediante un formulario con CSRF. Leer contenido gratuito sin cuenta sigue siendo posible.

Ficha y biblioteca comparten una función de continuación. Retoma la última lección accesible si está pendiente; después busca una pendiente accesible posterior y, si hace falta, vuelve a una anterior. Con todas las lecciones completadas permite repasar. Si solo queda contenido inaccesible, muestra opciones de acceso. La inscripción y los derechos existentes siguen asociados a su versión. La presentación consulta la regla de autorización existente y no concede permisos.

El temario muestra capítulos plegables, numeración, lectura, evaluaciones, finalización y acceso. Los estados incluyen texto: no dependen únicamente del color o del símbolo. Las tarjetas del catálogo muestran la cantidad de lecciones y el precio de la oferta de curso completo cuando existe; si solo hay ofertas parciales, identifican capítulo o lección individual. El precio se expresa como cantidad y sats, separado de la unidad que incluye. Para la cuenta inscrita en esa versión publicada, muestran su propio progreso.

El lector mantiene el temario junto al contenido en escritorio. En tamaños compactos lo coloca antes del texto y lo pliega cuando hay JavaScript; sin JavaScript permanece disponible. El modo de lectura enfocada oculta la navegación general y conserva el recorrido del curso. Escape devuelve la vista y el foco al control.

El texto editorial se presenta como explicación, ejemplo, práctica, solución desplegable y referencias. Solo se reconocen títulos editoriales explícitos; el texto genérico permanece legible. El contenido se escapa y los enlaces se generan con los filtros de Django. No se añaden soluciones ni se modifica el texto sellado. Desplegar una solución no completa la lección ni reemplaza su evaluación.

La finalización reúne evaluación, marca de avance y continuación. Tras confirmación del servidor, se actualizan recuento, porcentaje, estado del temario y acción siguiente. Puede desmarcarse una lección. Durante el guardado se evita un envío repetido. La posición se guarda sin mensajes sucesivos de éxito; los errores muestran reintento y los conflictos entre sesiones requieren recargar, preservando la revisión más reciente. Sin JavaScript siguen funcionando formularios, guardado manual y navegación.

Mi aprendizaje muestra totales de cursos, lecciones completadas y cursos completados. Destaca un recorrido accesible ya iniciado antes que uno sin empezar dentro de la página de resultados; los cursos se ordenan por actividad reciente. Permite buscar por título y filtrar por estado. La paginación conserva búsqueda, estado y página de recursos. La finalización de todas las lecciones no emite un certificado automáticamente: su pantalla sigue comprobando los requisitos.

El encabezado compacto conserva sus acciones. La posición del menú móvil se calcula a partir de su altura real, incluida cualquier segunda fila. Se conserva el tema claro/oscuro incorporado mediante cambios concurrentes y su paleta compartida.

## Verificación

Pasaron 39 pruebas enfocadas de aprendizaje, texto, catálogo, navegación, destinos de acceso, coherencia pública y presentación de compras. Se repitieron después de los últimos ajustes. Cubren continuidad coherente, muestras parcialmente completadas, inscripción idempotente, rechazo de destinos inaccesibles, privacidad del catálogo, versiones históricas, búsqueda/estados, precios y escape del texto. Pasaron también los cuatro controles de concurrencia con conexiones SQLite independientes: comercio/progreso, evaluaciones, certificados/preguntas y comunidad. La comprobación del cliente con respuestas controladas verificó guardado silencioso, finalización confirmada, prevención de envíos duplicados, conflicto de revisiones y recuperación; las comprobaciones de sintaxis JavaScript pasaron.

La última suite conjunta ejecutada por esta tarea registró 271 pruebas, cinco fallos y un error en cuentas y creadores: recuperación de correo/token y expectativas de acceso de creadores pendientes o suspendidos. Esos módulos están cambiando en paralelo. Este registro no declara la aplicación completa verificada. Ruff de los archivos de esta entrega pasó. La consistencia global de migraciones pasó en una revisión intermedia; durante el cierre se estaba añadiendo Guardados en paralelo, con SavedItem y su migración pendiente. El estado global de ese módulo pertenece a su entrega y no se considera verificado aquí. Los resultados anteriores fallidos se conservaron en registros locales y no se presentan como pruebas exitosas.

Los cambios de cursos y lectura no requieren esquema nuevo. La integración requirió generar los archivos de migración pendientes de los cambios concurrentes de cuentas y creadores. Antes de aplicar el esquema local se creó `platform-before-learning-20261012-214817.sqlite3`; se aplicaron accounts.0004, creators.0002/0003 y learning.0009. Las 54 tablas anteriores no redujeron sus filas; el conteo agregado pasó de 478 a 518, incluida la incorporación de permisos del esquema. La ficha local respondió 200 con el nuevo temario. Las cuentas y los avances sintéticos se crearon exclusivamente en bases temporales, no en la base principal.

La revisión en navegador utiliza `scripts/preview-learning.py`, una base SQLite temporal y cuentas sintéticas. El catálogo de prueba se carga exclusivamente allí. Se comprueban continuación, finalización y cambio de porcentaje, siguiente acción, soluciones desplegables, lectura enfocada, salida con Escape, filtros y variantes adaptables. Los datos de prueba no representan alumnos reales ni validación educativa. El ensayo de cliente se ejecuta con `node scripts/verify-learning-client.mjs`; no sustituye la prueba del navegador. La vista temporal usa cookies de sesión y CSRF propias para evitar interferencias con otros servidores locales.

Capturas de la versión revisada: [finalización](evidence/aprendizaje-completada-2026-10-12.jpg), [lectura enfocada](evidence/aprendizaje-lectura-enfocada-2026-10-12.jpg), [lector móvil](evidence/aprendizaje-lectura-movil-2026-10-12.jpg). Se añadieron la [ficha con continuación](evidence/aprendizaje-curso-2026-10-12.jpg) y la [biblioteca con curso iniciado prioritario](evidence/aprendizaje-biblioteca-2026-10-12.jpg). Se comprobó el filtro Completados sin cambiar los totales del resumen. En móvil se comprobó una anchura de 390 px y que el menú comenzara debajo del encabezado (76 px); no hubo desbordamiento horizontal. Durante la revisión compartida también se observó una anchura compacta de 325 px y se ajustó la disposición del encabezado para esos tamaños. No se afirma una comprobación visual final a 325 px tras ese último ajuste.

## Límites y próximos pasos

No se afirma conformidad integral con WCAG: falta una auditoría con tecnologías de asistencia. La comprobación de pantallas y formularios es técnica. No demuestra comprensión, satisfacción, aprendizaje ni mejora de conversión. La duración publicada pertenece al curso; no se inventan tiempos por lección, rachas, experiencia, valoraciones o logros.

La continuación destacada se elige entre los resultados de la página actual, no constituye una recomendación pedagógica global. Los filtros clasifican como iniciado un curso que ya tiene una posición guardada o alguna lección completada. La solución desplegable usa el contenido editorial existente; la comprobación obligatoria conserva su corrección en servidor.

Próximos pasos: ejecutar tareas de continuidad, comprensión de acceso, ejercicios y evaluación con participantes; registrar ayudas y errores; comparar dificultades con una versión identificada. Después ajustar el recorrido con esas evidencias. Las preguntas, comunidad y certificados conservan sus permisos; esta entrega no vuelve a verificar pagos desde ZEUS ni operación pública.

## Corrección del marcador del temario

El 12 de octubre se corrigió una regresión visual reportada con captura: la regla heredada `.lesson-list a>span:first-child { flex: 1 }` hacía crecer el marcador hasta formar una elipse. Se limitó esa regla a listas anteriores y se fijó el marcador del temario con `flex: 0 0 auto` y relación de aspecto 1:1. Se renovó la referencia de caché de las hojas de estilo afectadas.

Se comprobó en navegador el curso abierto a 1280 px y en móvil a 390 px: los cuatro marcadores conservaron aproximadamente 34 × 34 px, con crecimiento flex igual a cero. En el lector conservaron aproximadamente 24 × 24 px. [Captura de la corrección](evidence/marcadores-circulares-2026-10-12.jpg). Es un ajuste de presentación; el documento principal y su exportación mantienen el mismo comportamiento descrito. No requiere migración ni cambia acceso o avance.
