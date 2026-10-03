# Base de contenido — 1 de octubre de 2026

**Entrega posterior del 2 de octubre:** [versiones y archivos privados](contenido-versiones-y-archivos-2026-10-02.md) amplía esta base con publicación sellada y entrega autorizada. Los apartados siguientes registran la implementación inicial.

Primera etapa del backend de BTC.EDU. Implementación local con SQLite; no se crean datos educativos ni cuentas de ejemplo.

## Estructura implementada

- Curso: creador, título, descripción, objetivo, requisitos y estado.
- Capítulo: curso, título, descripción, estado y orden único dentro del curso.
- Lección de texto: capítulo, título, descripción, estado, orden único, acceso gratis/de pago y cuerpo.
- Video y material: fichas independientes con creador, título, descripción, estado y acceso. Todavía sin archivos, reproductor ni descarga.

Los registros nacen como borradores. Curso, capítulo y lección deben estar publicados para entregar una lección a un visitante. La publicación se gestiona en la administración por usuarios con los permisos correspondientes. No hay todavía panel de creador ni flujo de revisión de versiones. El creador puede previsualizar su propio contenido a través de la regla de acceso, pero eso no concede permisos de administración.

Los capítulos y lecciones se ordenan por posición; el administrador debe asignar posiciones distintas dentro de cada padre. No hay reordenamiento automático. La eliminación de un curso elimina sus capítulos y lecciones; la eliminación de una cuenta con contenido asociado queda protegida.

## Acceso y entrega

`content/access.py` centraliza la decisión. Permite una lección publicada gratuita sin cuenta y una vista previa al creador activo, incluso si es borrador o de pago. Otro creador o un usuario staff no recibe acceso especial por su rol. Los permisos de la administración son independientes.

`GET /lecciones/<id>/contenido/` entrega JSON con título, cuerpo y motivo del acceso autorizado. Devuelve 404 para contenido inexistente o no publicado, y 403 para contenido de pago sin permiso. Incluye instrucciones de no almacenar la respuesta en caché. El cuerpo es texto, no HTML aprobado para renderizar sin escape.

Una lección gratuita no exige comprar otras lecciones. Los cursos y capítulos representan estructura pública; su acceso no concede acceso a todas sus lecciones. Precios, ofertas, compras, permisos permanentes y membresías todavía no existen. El contenido de pago permanece bloqueado para alumnos.

No hay URLs públicas de archivos ni campos para introducir enlaces a videos protegidos. La carga, validación, almacenamiento y entrega autorizada de archivos se implementarán juntos en una etapa posterior. Tampoco hay asociación de materiales adicionales a lecciones todavía.

## Comprobaciones

La comprobación del proyecto incluye `core` y `content`: 17 pruebas pasan (7 anteriores y 10 nuevas). Se verifican acceso anónimo gratuito, pago bloqueado sin filtración del texto, ancestros no publicados, vista previa propia, aislamiento entre creadores, creador inactivo, lecciones mixtas, fichas independientes, posiciones únicas, método HTTP y permisos de administración. Migraciones consistentes y revisión estática sin errores.

Los datos de prueba viven en una base temporal y se destruyen al terminar. No se verificaron todavía reproducción, descargas, pagos ni concurrencia comercial.

## Próxima etapa

El 2 de octubre se conectaron catálogo, detalle de curso y pantalla de lección a los modelos publicados y a la misma decisión de acceso. Ver [recorrido de aprendizaje](recorrido-aprendizaje-2026-10-02.md). El catálogo real permanece vacío hasta que el usuario autorice crear contenido. La próxima etapa es implementar ofertas, precios, facturas simuladas y acceso comprado persistente.
