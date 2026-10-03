# Contenido, versiones y archivos — 2 de octubre de 2026

Entrega local autorizada para cerrar el día, sobre la interfaz de academia industrial. Compras, inscripciones y progreso no se incorporan en este bloque.

## Comportamiento implementado

- `Course`, `Chapter` y `Lesson` conservan IDs y rutas, y funcionan como espacio de edición. Una acción de administración publica una composición completa.
- `CourseVersion`, `VersionChapter` y `VersionLesson` conservan metadatos, orden y revisiones de texto. Se sella la composición dentro de una transacción. La versión pública vigente se apunta explícitamente desde el curso.
- `ResourceVersion` conserva título, descripción, acceso, texto/transcripción y archivos exactos. Los textos sin cambios reutilizan revisión; los cambios de texto/acceso crean otra. Video/Material mantienen identidad y apuntan a su revisión vigente.
- `LessonResource` organiza adjuntos de la edición. `VersionAttachment` congela esas asociaciones. Reemplazar un video/material no cambia el archivo enlazado por una versión de curso anterior.
- Los registros de revisión rechazan modificación/eliminación mediante los modelos y gestores públicos. Los hijos rechazan adiciones a composiciones selladas, también a anteriores. `PROTECT` conserva referencias. La administración permite consultar revisiones, sin editarlas o eliminarlas.
- Las fichas, catálogo y selector usan los valores publicados; editar un borrador no cambia silenciosamente texto, acceso o temario del alumno. Los enlaces numéricos de lección siguen resolviendo la composición vigente incluso si se elimina la lección de edición.

La inmutabilidad es una regla de aplicación, no una protección contra SQL directo o cambios manuales del disco. El servicio interno de publicación tiene acceso para sellar la composición. Respaldar juntos base y almacenamiento privado; no eliminar archivos antiguos por reemplazar una revisión.

## Carga y entrega privada

Nueva aplicación `media`: `Asset` almacena propietario, nombre original seguro, nombre interno aleatorio, tamaño, MIME derivado y SHA-256. Archivos en `src/.local/private-media`, fuera de `static`, sin ruta pública `/media/`. El almacenamiento rechaza generar URL directa.

Primera lista de formatos: **MP4, PDF, TXT UTF-8 y WebVTT**. Límite por archivo: **256 MiB**, configurable en `CONTENT_MAX_UPLOAD_BYTES`. Se comprueban extensión, firma/tipo declarado y tamaño; MP4 requiere contenedor completo con `ftyp`, `moov` y `mdat`; TXT/VTT comprueban UTF-8 y caracteres de control. Los adjuntos y subtítulos deben corresponder al formato y propietario. No se admite HTML, ejecutables, ZIP ni fragmentos MP4 sueltos.

No es un antivirus, decodificador ni verificador semántico completo de PDF/VTT. No hay transcodificación: el codec MP4 debe ser compatible con el navegador. Las cargas ocurren en administración, no en un panel público de creador. La base puede revertir una transacción sin revertir el disco; una carga fallida después de escribir puede dejar un archivo sin referencia. No hay limpieza automática de huérfanos ni cuotas por creador en este bloque.

Cada entrega valida acceso antes de abrir el archivo, incluso al solicitar subtítulos, una porción, HEAD o respuesta condicional. Video MP4 con controles nativos, subtítulos españoles cuando se asocian y transcripción cuando existe. PDF/TXT se descargan con nombre seguro. Respuestas `private, no-store` y `nosniff`; ETag identifica el archivo inmutable. Range único admite `206`, extremos abiertos/sufijos, `416` y HEAD, con If-Range. Los archivos ausentes no revelan rutas internas; la interfaz muestra incidencia o fallo de reproducción.

## Acceso y versiones históricas

Gratis publicado: acceso anónimo. De pago: bloqueo, excepto inspección del propietario activo. Staff por sí solo no equivale al alumno propietario. Una lección gratuita no desbloquea un adjunto de pago; entregar un adjunto requiere autorización tanto de la lección como de su recurso. La misma revisión puede reutilizarse sin duplicar archivos.

Las versiones anteriores se conservan y tienen rutas estables; por ahora solo el propietario puede inspeccionarlas. La versión vigente se descubre públicamente cuando el curso está publicado. Retirar publicación o sustituir versión la oculta para terceros. El acceso adquirido/inscrito a versiones anteriores **se conectará con comercio/aprendizaje**; todavía no existen compradores ni derechos persistentes. No se afirma que la conservación ya implemente acceso poscompra.

| Ruta | Función |
|---|---|
| `/cursos/<id>/` | Ficha vigente; conserva ruta anterior |
| `/cursos/<id>/versiones/<n>/` | Ficha de una composición sellada |
| `/cursos/<id>/versiones/<n>/lecciones/<id>/` | Lectura y adjuntos de esa versión |
| `/lecciones/<id>/`, `/lecciones/<id>/contenido/` | Compatibilidad HTML/JSON con versión vigente |
| `/adjuntos/<id>/archivo/`, `/adjuntos/<id>/subtitulos/` | Entrega con contexto de lección y revisión |
| `/recursos/<tipo>/<id>/revisiones/<n>/archivo/` | Entrega desde recurso independiente vigente |
| Misma ruta terminada en `/subtitulos/` | Subtítulos con la misma autorización |

Los registros previos sin versión conservan el comportamiento anterior hasta su primera publicación versionada. No se convierten temarios vacíos en versiones artificiales. El catálogo sigue componiendo/paginando metadatos en memoria; optimización para un catálogo grande y revisión editorial más amplia siguen pendientes.

## Cómo publicar desde administración

1. Crear una cuenta administrativa por el procedimiento existente; no se agregan contraseñas de demo a la base real.
2. En **Archivos privados**, cargar MP4/PDF/TXT/VTT y seleccionar el propietario creador. Se valida antes de guardarlo; después se conserva, no se reemplaza en el mismo registro.
3. Crear/editar Video o Material. Elegir **archivo de la próxima revisión**, opcionalmente VTT/transcripción para video, título, descripción y acceso.
4. En la lista del recurso, ejecutar **Validar archivo y publicar una nueva revisión**. Los errores impiden crear una revisión incompleta.
5. Preparar curso, capítulos y lecciones. Marcar los capítulos/lecciones listos como Publicado. Cada lección necesita texto, aunque incorpore video. En la edición de lección, seleccionar las revisiones de recursos y su orden.
6. En la lista de cursos, ejecutar **Publicar una nueva versión del curso**. La acción requiere permiso administrativo de cambio; rechaza capítulos vacíos, texto faltante y adjuntos incompatibles.
7. Para cambios posteriores, editar y repetir publicación. Las revisiones/composiciones anteriores no se sobrescriben. No borrar sus archivos privados.

La cuenta del creador puede consultar su edición con `?borrador=1` en la ficha original. El panel de creación completo y los estados de revisión adicionales siguen siendo una entrega posterior.

## Verificación y demostración

**54 pruebas Django pasan**: las 32 previas y 22 nuevas. Incluyen preservación del historial, inmutabilidad, publicación atómica/revisada, texto/archivos reutilizados, edición sin cambios públicos, permisos de archivos/subtítulos/adjuntos, cabeceras, rangos y HEAD, archivos ausentes, cargas inválidas, acciones de administración y migración de múltiples registros existentes con UUID distintos. Configuración, migraciones y revisión estática pasan.

Navegador: curso → versión → lección, reproducción real del clip (10 segundos, `readyState=4`), subtítulos cargados (`track.readyState=2`), transcripción, descarga desde la lección y adjunto adicional bloqueado. Revisión móvil/escritorio sin desbordamiento horizontal. Capturas: [lección](evidence/leccion-archivos-versionados-movil.jpg) y [ficha de video](evidence/video-protegido-movil.jpg). No equivale a auditoría WCAG o prueba de todos los codecs/navegadores.

SQLite real respaldada antes de las dos migraciones. Se compararon cantidades de cuentas/cursos/capítulos/lecciones/videos/materiales; permanecen iguales. Las tablas nuevas no contienen ejemplos en la base real.

`scripts/preview-academy.py` crea SQLite y carpeta de archivos temporales separadas, usuarios sin contraseña utilizable y cursos versionados con video, VTT, transcripción y materiales gratis/de pago. Puerto **8012**. Al cerrar normalmente limpia solo esos temporales; una interrupción forzada puede dejar archivos ignorados en `.local`. El clip de pantalla blanca es un fixture de [Web Platform Tests](https://github.com/web-platform-tests/wpt/blob/master/media/white.mp4), con licencia/procedencia en `media/fixtures`; no es una clase. Sin nuevas dependencias de ejecución.

## Siguiente bloque

Ofertas/versiones, facturas simuladas LNbits y derechos por `ResourceVersion`; incluir acceso histórico adquirido y conciliación. Después inscripciones/progreso y Mi aprendizaje. Antes de desplegar, cerrar cuotas, tratamiento de incidentes/huérfanos, almacenamiento/transferencia de producción y verificación adicional de archivos.
