# Interfaz de academia — 2 de octubre de 2026

**Actualización posterior:** [versiones y archivos](contenido-versiones-y-archivos-2026-10-02.md) conecta reproducción, subtítulos, transcripción y descarga cuando existe revisión publicada. Este registro describe el bloque visual previo; sus avisos de archivos/versiones pendientes son el estado de esa entrega.

Dirección confirmada por el usuario: **estética industrial más marcada**, conservando nombre y fuentes aprobadas. Primera implementación de la [arquitectura de producto](../../strategy/10-arquitectura-y-experiencia-btc-edu.md); las siguientes funciones se distinguen de las pantallas construidas.

## Sistema visual y componentes

Blanco cálido, superficies blancas, líneas finas, retícula y naranja en selección/foco; botones negros. Numeración y marcas de registro organizan la interfaz. La lectura tiene ancho limitado y menos decoración. Se conservan Ndot77 para marca, NType82 para lectura, NType82 Headline para títulos y Space Mono para etiquetas.

Descripciones de tarjetas y controles de 14 px, lectura de 16 px y títulos adaptables. Los códigos pequeños son secundarios. Tokens/componentes en `static/css/academy.css`, sobre `site.css`. Portadas esquemáticas originales en SVG por tipo, decorativas: no son portadas editoriales específicas ni archivos subidos. No se copiaron ilustraciones, precios, estadísticas o reseñas de la referencia.

Plantilla compartida de academia, menú móvil, pestañas, tarjeta, fila de tutorial, filtros, temario, resumen de especificaciones y vacíos. Mi aprendizaje, login y página para creadores adoptan esa estructura. La portada conserva el concepto anterior aprobado.

## Pantallas funcionales

| Ruta | Comportamiento |
|---|---|
| `/cursos/` | Temas, tarjetas, búsqueda, tema/nivel/acceso y 12 resultados por página |
| `/cursos/selector/` | Tema → cursos por nivel → resumen; mismos datos que el catálogo |
| `/tutoriales/` | Filas por tema, búsqueda/filtros y motor de lectura compartido |
| `/recursos/` | Todo/Videos/Materiales/Enlaces externos, búsqueda/filtros y fichas |
| `/cursos/<id>/` | Ficha de curso o tutorial, objetivos, requisitos, metadatos opcionales, acceso y temario |
| `/lecciones/<id>/` | Lectura o bloqueo, anterior/siguiente y temario plegable |
| `/referencias/<id>/` | Descripción/fuente, aviso de salida y enlace HTTP/HTTPS validado |
| `/recursos/videos/<id>/`, `/recursos/materiales/<id>/` | Fichas con aviso de reproducción/descarga pendiente |
| `/mi-espacio/` | Mi aprendizaje vacío, sin fingir biblioteca o progreso existentes |
| `/cuenta/entrar/`, `/para-creadores/` | Login actual e información de creación con la misma estructura visual |

`/explorar/` conserva el catálogo combinado y filtros anteriores. Las rutas numéricas existentes no se rompen.

## Reglas de interacción

- Menú con sección activa y enlaces reales; sin enlaces a eventos, comunidad, certificados o compras aún sin función.
- En móvil: menú plegable, `aria-expanded`, foco al primer enlace, cierre con Escape/fondo. Sin JS se conserva navegación. Al volver a escritorio se cierra el estado móvil.
- Selector apilado: elegir tema conduce a cursos; elegir curso al resumen, mediante anclas. Mantiene filtros y descarta selección incompatible. Niveles ordenados.
- Filtros en URL y regreso local validado desde ficha/lección. El selector conserva la búsqueda después de actualizar por HTMX; se recupera foco del buscador. El regreso nunca acepta destino externo.
- Formulario usable sin HTMX. Error de conexión conserva filtros y permite reintentar; no anuncia éxito. Vacío inicial y búsqueda sin coincidencias tienen acciones distintas.
- Cursos mixtos indican lecciones gratis/de pago. Precios y compra no se simulan visualmente como funciones disponibles.
- Una referencia externa no se considera gratuita por conocer su URL; filtros gratis/pago solo describen acceso propio. Fuente externa informa sus condiciones.
- El cuerpo pagado no llega a la pantalla bloqueada. Borradores ajenos siguen ocultos. Compras archivadas/versiones se implementarán después.

## Datos incorporados y límites

Tema configurable, tipo curso/tutorial, nivel y duración estimada opcionales; tema en video/material; referencia externa con fuente/enlace. Administración permite clasificar registros. Migración agrega estructura sin contenido; aún no agrega versiones, ofertas, archivos, inscripciones ni progreso.

Conteos publicados se consultan sin cargar todos los temarios/cuerpos. Filtros en base; la composición/orden y paginación de presentación aún reúnen metadatos en memoria. Para catálogo grande falta acotar también esa composición y el inventario del selector. Las portadas específicas, almacenamiento y entrega se implementarán juntos.

## Contratos visuales de las siguientes entregas

Son diseños pendientes, no interfaces funcionales en este bloque.

| Pantalla | Composición y estados |
|---|---|
| Mi aprendizaje con datos | Continuar primero; última lección, porcentaje, acceso permanente/temporal; inscritos/completados y recursos. Acceso vencido conserva avance; video individual no equivale a curso comprado |
| Oferta/pago | Resumen lateral de importe/incluidos/extras y área de estado. Pending consulta la misma factura; Paid abre; Failed/Expired explica y permite reintento elegible; error de conexión no crea factura nueva. Controles de prueba separados |
| Registro/recuperación | Campos/errores asociados y destino conservado; solicitud sin revelar existencia de correo, token usado/vencido y regreso al contenido |
| Recurso entregable | Archivo, tipo/tamaño/procedencia, acceso y acción; reproducción/descarga solo con archivo válido; incidencia sin revelar ruta privada |
| Editor de creador | Lista y pestañas Datos/Temario/Archivos/Ofertas. Guardado, vista previa, faltantes, revisión, carga y cambios sin guardar; estado editorial real |
| Evaluación | Instrucciones e intentos antes de preguntas; corrección en servidor, nota/reintento y explicación al cerrar; recuperación de errores |
| Certificado | Requisitos pendientes o credencial completada, descarga/compartir y verificación mínima; compra no emite |
| Preguntas/comunidad | Conversaciones contextualizadas y bandeja de creador; permisos, reportes, moderación y avisos pertinentes |
| Membresías | Planes con incluidos/vigencia y periodo actual; renovación manual, cancelación y compras permanentes diferenciadas |

Cada componente se conecta a datos comprobados antes de aparecer como disponible. Los eventos educativos son posteriores.

## Verificación

32 pruebas Django pasan: 24 existentes y 8 nuevas. Cubren separación de secciones, filtros, paginación, selector, acceso mixto, referencias, HTMX/métodos y regreso seguro. Migraciones consistentes y revisión estática sin errores.

Navegador: catálogo/selector, búsqueda HTMX con foco y pestañas conservadas, ficha, tutorial/lectura móvil, bloqueo de pago, recursos y menú móvil. Las vistas móviles revisadas no desbordaron horizontalmente. No equivale a auditoría WCAG completa ni a validación con alumnos.

Capturas de revisión: [selector móvil](evidence/academia-selector-movil.jpg) y [lectura móvil](evidence/academia-lectura-movil.jpg).

Respaldo SQLite antes de migrar; cantidades de registros de cuenta/contenido comparadas antes/después. No se añadieron temas, referencias ni contenidos de ejemplo a la base principal. Vista previa con SQLite temporal aparte y aviso visible en todas las pantallas; archivo eliminado al cerrar normalmente.

## Vista local

Plataforma real: desde la raíz ejecutar `./dev-platform.ps1`; abrir `/cursos/`, `/tutoriales/` o `/recursos/` en puerto 8000.

Demostración temporal: `./src/.venv/Scripts/python.exe src/scripts/preview-academy.py`; abrir **http://127.0.0.1:8012/cursos/**. Ctrl+C detiene. Si se interrumpe forzosamente puede quedar un archivo temporal ignorado en `.local`, sin datos de la base principal. Cambios Python requieren reiniciar; plantillas/estilos se revisan recargando.

No hubo publicación, push ni pagos. Quedan versiones/archivos, compra y continuidad de aprendizaje. La base visual puede revisarse antes de producir contenidos y portadas definitivos.
