# Estudio de creadores — 3 de octubre de 2026

Primer bloque de implementación del [enfoque integral](../../strategy/11-enfoque-creadores.md). Cierra preparación → revisión → publicación. Las áreas de alumnos, comercio, evaluaciones, certificados, comunidad y membresías siguen dentro del proyecto y se integrarán por dependencias; no se presentan como disponibles.

## Funciones disponibles

- Solicitud de creador con nombre público, biografía, especialidad, sitio y declaración de derechos. La administración aprueba, solicita cambios o suspende. El usuario no puede asignarse aprobación. Reenviar después de observaciones devuelve la solicitud a pendiente.
- Perfil público de creadores aprobados y activos, con contenido publicado; sin correo de cuenta ni borradores. Actualizar perfil aprobado conserva su aprobación.
- Estudio en `/crear/`: cursos/tutoriales, videos/materiales, envíos recientes y conteos reales de revisión/observaciones. Navegación desde la academia y la página Para creadores.
- Editor de información de curso/tutorial, capítulos, lecciones de texto, acceso gratis/de pago y adjuntos propios. Orden numérico con validación de conflictos. Capítulos/lecciones pueden incluirse en la próxima composición o reservarse como borradores.
- Biblioteca privada de MP4/PDF/TXT/VTT con validación existente, carga con progreso/reintento y entrega autorizada, incluidos HEAD y Range. Los archivos no se sobrescriben ni se vuelven públicos por cargarlos.
- Editor de videos/materiales con archivo, subtítulos y transcripción. Las lecciones adjuntan revisiones aprobadas; conservar una revisión ya adjunta permite mantener archivos anteriores.
- Vista previa de borrador con texto, reproducción y descarga como propietario. No representa acceso comprado ni registra aprendizaje.
- Envío que congela una composición sellada o revisión de recurso sin activarla públicamente. Un envío pendiente por contenido; retirada y reenvío conservan historial. Editar después de enviar no altera la copia revisada.
- Página editorial con texto, adjuntos, observaciones y decisión. Requiere staff y permisos explícitos de revisión y cambio del tipo de contenido. Aprobar activa exactamente la copia enviada; devolver exige observaciones. Las decisiones no se repiten ni se revierten desde este recorrido.
- Una publicación administrativa posterior impide aprobar un envío antiguo que la reemplazaría. Cambiar borradores conserva las versiones publicadas.
- Guardado normal sin JavaScript; con JavaScript, fallos de red/sesión conservan los campos en la página para reintentar. Aviso antes de abandonar cambios pendientes, errores por campo y confirmación después de guardar. No hay guardado automático ni recuperación después de cerrar el navegador.

## Administración y permisos

En administración, **Creator profiles** gestiona las solicitudes y **Submissions** enlaza a las revisiones. Cambiar el estado del perfil registra administrador y fecha; las observaciones permanecen visibles al creador. Los envíos registran composición, autor, fecha, estado, observaciones y responsable/fecha de decisión.

Una cuenta existente entra a `/crear/solicitud/`; tras aprobación abre `/crear/`. La base real sigue sin cuentas: crear la cuenta administrativa por el procedimiento del README. Registro público y recuperación todavía no se incorporan en este bloque.

La propiedad se comprueba en las rutas de edición, carga, lectura y envío. Los campos de propietario/estado comercial no se aceptan desde formularios. Los selectores de archivos y revisiones se restringen al creador. Un revisor solo puede entregar archivos pertenecientes a la composición concreta que revisa. Suspensión deshabilita el estudio y publicación de envíos; no elimina datos ni sustituye una política de continuidad de acceso adquirido.

Para publicaciones anteriores sin composición congelada, se bloquea edición desde el estudio hasta que administración publique su primera versión/revisión. Esto evita modificar directamente contenido público antiguo. La herramienta administrativa existente de publicación directa sigue disponible para personal autorizado.

## Verificación

77 pruebas Django pasan: 54 existentes y 23 del recorrido de creadores. Comprueban aprobación y suspensión, propiedad, CSRF, archivos ajenos, historial, edición posterior al envío, publicación exacta, conservación de publicación anterior, decisiones repetidas, envío antiguo, campos obligatorios, conflictos de orden, adjuntos y permisos de entrega. Configuración, migraciones y revisión estática pasan.

Navegador sobre base y archivos temporales: creación de tutorial → capítulo → lección con material aprobado → envío; guardado con confirmación; vista previa con video/subtítulos; decisión administrativa registrada y composición publicada. Se verificó además que un cambio posterior de descripción no altera el envío. Se corrigió el cambio de rol del simulador de vista previa, sin modificar el mecanismo de autenticación de la plataforma.

Revisión en móvil y escritorio, sin desplazamiento horizontal global en las pantallas inspeccionadas. Las pestañas tienen desplazamiento propio. Evidencia: [panel](evidence/creador-panel-escritorio.jpg) y [publicación revisada](evidence/creador-revision-movil.jpg). No equivale a auditoría de accesibilidad, concurrencia o todos los navegadores. La recuperación de errores de red/sesión está implementada, pero no se simularon todos esos fallos en navegador.

Migración `creators.0001_initial` aplicada después de respaldo SQLite mediante su API de backup. Cantidades de cuentas/cursos/capítulos/lecciones/videos/materiales antes/después iguales: todas cero. Nuevas tablas de perfiles y envíos también vacías; no se añadieron cuentas ni catálogo de ejemplo a la base real.

## Vista temporal

Desde `src`, ejecutar `./.venv/Scripts/python.exe scripts/preview-creators.py`. Abre `http://127.0.0.1:8013/crear/` con una cuenta temporal aprobada; `?vista=revisor` o `?vista=creador` cambia rol únicamente en este servidor de demostración. Sin contraseñas utilizables ni acceso a la base real; autenticación automática definida solo en ese script. Escucha en localhost, usa una carpeta temporal propia y la limpia al cerrar normalmente. El clip blanco procede del fixture existente de Web Platform Tests.

## Pendientes del producto completo

Ofertas/precios y compras simuladas, derechos históricos adquiridos, registro/recuperación, inscripción/progreso y alumnos, evaluaciones/certificados, preguntas/notificaciones, comunidad, membresías y métricas comerciales/educativas. Archivar desde el estudio requiere conectar la continuidad de acceso con comercio; no se añade un botón que retire compras inexistentes.

El editor actual usa texto simple, selección múltiple de adjuntos y orden numérico; portadas personalizadas, orden por arrastre, paginación del estudio y guardado automático quedan pendientes. No hay limpieza automática de huérfanos, cuotas por creador, antivirus, transcodificación ni incidentes operativos completos. Los límites de validación y almacenamiento del documento de archivos continúan vigentes. Al cierre del 3 de octubre no hubo despliegue, commit ni push.

Actualización del 4 de octubre: estudio y cuentas independientes guardados en el commit `8792c98`; documentación y capturas se guardan en un commit separado. Verificación completa del estado integrado: 96 pruebas, migraciones consistentes y revisión estática pasan. No hubo despliegue ni push.
