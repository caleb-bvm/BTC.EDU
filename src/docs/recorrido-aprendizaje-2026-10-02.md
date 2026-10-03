# Recorrido de aprendizaje — 2 de octubre de 2026

Implementado: catálogo → curso → lección. Se conserva la identidad visual aprobada de BTC.EDU.

## Investigación aplicada

Las necesidades propuestas en [la investigación](../../strategy/07-investigacion-y-necesidades.md) orientan estas decisiones. Todavía son hipótesis del equipo; no hay entrevistas ni validación de usabilidad con alumnos.

| Necesidad | Comportamiento implementado |
|---|---|
| Entender qué aprenderá y qué necesita | Ficha con descripción, objetivos, requisitos, creador y temario ordenado |
| Distinguir acceso gratuito y de pago | Etiquetas por lección y resumen que identifica cursos mixtos; filtro «Con contenido gratis» incluye cursos con lecciones gratuitas y otras de pago |
| Encontrar contenido | Búsqueda por título o descripción, formato y acceso combinables; filtros conservados en la URL y formulario usable sin JavaScript |
| Estudiar sin perder el contexto | Temario, lección actual, posición en el temario, enlaces anterior/siguiente y regreso al curso |
| Leer desde móvil o con teclado | Columnas adaptables, texto con ancho de lectura, etiquetas de formulario, foco visible y navegación semántica |
| Comprender estados pendientes | Estados vacíos, búsqueda sin resultados, temario en preparación y bloqueo de pago con regreso a lecciones gratuitas |

No se presentan como disponibles progreso guardado, certificados, preguntas, comunidad, evaluaciones ni membresías. La posición en el temario no mide finalización. No se han añadido temas, niveles o duraciones ficticios a los modelos.

## Rutas y límites

- `/` y `/explorar/`: muestran únicamente registros publicados. Una respuesta HTMX reemplaza el catálogo; la navegación normal devuelve la página completa.
- `/cursos/<id>/`: metadatos, capítulos y lecciones publicados, sin cuerpos de lecciones. El creador activo puede previsualizar sus borradores desde la ruta directa.
- `/lecciones/<id>/`: lectura de texto gratuito y vista previa propia. Pago sin permiso devuelve 403 con explicación y sin cuerpo protegido. Borradores y ancestros no publicados devuelven 404 a otros usuarios.
- `/recursos/videos/<id>/` y `/recursos/materiales/<id>/`: fichas informativas publicadas, con aviso de reproducción o descarga pendiente.

No hay precios ni compras implementados. La etiqueta de pago se deriva del acceso de las lecciones y no equivale a una oferta comercial de curso. No se muestran correos del creador en las fichas: se usa su nombre o una etiqueta genérica. El cuerpo de texto se escapa al renderizar. Las páginas de curso y lección no permiten almacenamiento en caché para proteger las vistas previas.

## Verificación

24 pruebas Django pasan: las 17 existentes y 7 nuevas que cubren el recorrido, filtros combinados, respuesta HTMX, cursos mixtos, exclusión de cuerpos y correos en el catálogo, escape del texto, bloqueo de pago, ocultación de borradores, vista previa propia y fichas independientes. No hay migraciones nuevas y la revisión estática pasa.

Revisión en navegador del catálogo, detalle y lectura, incluyendo el bloqueo de pago y distribución móvil. Se usó un servidor separado con SQLite en memoria y datos temporales de prueba; no se añadieron cursos, cuentas ni lecciones a la base local del usuario. Esto comprueba presentación y navegación, no valida necesidades del público ni constituye una auditoría completa de accesibilidad.

Próxima etapa: ofertas y precios, integración de facturas simuladas con LNbits y permisos persistentes tras confirmar una compra. La entrega de videos y archivos requiere almacenamiento y autorización propios.
