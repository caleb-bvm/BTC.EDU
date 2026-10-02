# Verificación — 1 de octubre de 2026

Fecha del usuario: Guatemala. Evidencia local de esta fase, sin publicaciones ni actividad inventada.

## Comprobaciones ejecutadas

- Setup con uv y lockfile: dependencias instaladas; segunda ejecución no cambia `.env` ni repite migraciones.
- Python 3.12.14, Django 5.2.17 comprobados.
- Migraciones accounts/auth/admin/contenttypes/sessions aplicadas en SQLite; makemigrations --check no detecta cambios.
- Check Django: sin incidencias. Ruff: sin errores.
- Siete pruebas en base SQLite temporal: **7/7 OK**. Se destruye la base de test; no deja usuarios de prueba en la base local.

| Prueba | Evidencia |
|---|---|
| Páginas públicas y health | HTTP 200 en portada, explorar, creadores, login y health |
| Espacio privado y admin | Visitante redirigido; cuenta sin staff no entra a admin |
| Base no disponible | Health devuelve 503 y JSON genérico sin detalles privados |
| Cuenta por correo y redirección | Login correcto; next externo rechazado a favor de Mi espacio |
| Correo duplicado por mayúsculas | Restricción de base rechaza segundo usuario |
| CSRF y logout | Login POST sin token: 403; logout GET: 405 |
| HTMX | Filtro videos devuelve solo fragmento y estado vacío correcto |

## Navegador real

Inspección de portada, página de creadores y formulario. Las dos imágenes cargan. Click en filtros Videos, Materiales y Cursos actualiza estado vacío mediante HTMX; recargar la URL de Cursos mantiene selección y muestra página completa. Enlaces de navegación funcionan. No se observaron errores de consola.

Se revisaron anchos efectivos de navegador 1440, 1200, 390 y 325 px. Se comprobó ancho de documento sin desbordamiento horizontal. Se ajustó título en pantallas de hasta 400 px. Las capturas guardadas son de la vista visible y no incluyen necesariamente toda la página:

- [Portada escritorio](evidence/portada-fuentes-escritorio.jpg)
- [Portada móvil](evidence/portada-fuentes-movil.jpg)

Hay foco visible, labels, salto al contenido y navegación semántica. No se realizó auditoría integral de accesibilidad ni prueba física en teléfonos.

## Límites y pendientes

PostgreSQL 18 tiene servicio activo y puerto accesible, pero falta base/rol configurado: todas las pruebas Django fueron SQLite. No existen pruebas de pagos o concurrencia de compras integradas, porque no hay comercio construido.

La prueba independiente LNbits de 100 sats pendiente a pagada fue verificada anteriormente el mismo día y está documentada en lnbits-local.md; no se repitió ni se atribuye aquí una nueva ejecución. Su entorno y datos se conservaron.

Check --deploy local: cinco advertencias de DEBUG, HTTPS, cookies Secure y HSTS. Esta entrega es local, no producción. Ver base-tecnica.md.

Los originales del assignment se leyeron sin modificarse. Esta fase aporta base, arquitectura, contratos existentes, documentación, pruebas e interfaz adaptable. Faltan recursos gratuitos/de pago, facturas y permisos, persistencia de compras, eventos y demo completa. GitHub diario y Google Doc con historial siguen pendientes; no se hizo commit, push ni despliegue. Fechas 3/8 noviembre y equipo dos/cuatro no resueltos.

## Próximo punto de revisión

El usuario revisa la portada antes de avanzar con contenido. No se importó el catálogo ficticio ni se crearon cursos, capítulos o materiales. Después de esa revisión se podrá definir la siguiente fase y definir y probar la concurrencia comercial respetando los límites de SQLite.

## Cambio de motor solicitado por el usuario

Después de las pruebas anteriores, el usuario eligió MySQL directamente y un servidor existente. Se eliminó el fallback SQLite y el controlador PostgreSQL; mysqlclient 2.3.0 instalado y lockfile actualizado. Ruff pasa. Los resultados SQLite anteriores se conservan como historia, no como prueba de MySQL. Se detuvo el servidor anterior que todavía usaba SQLite. El puerto local 3306 responde MariaDB 10.4.32 (XAMPP), incompatible con Django 5.2; no se lo usó como reemplazo. Falta dirección y configuración del otro MySQL para ejecutar migraciones y pruebas. No se eliminaron bases locales anteriores ni datos LNbits.

## Decisión vigente: volver a SQLite

El usuario decidió usar SQLite. Se restauró la base local conservada, sin borrar ni importar datos. Se retiraron controlador, variables y scripts MySQL. Se volvió a ejecutar setup y comprobación: siete pruebas pasan, migraciones sin pendientes y Ruff sin errores. Se reanudó el servidor local. El intento MySQL anterior queda como registro histórico y ya no es la configuración vigente.

## Sustitución de fuentes

Se localizaron las tres familias en las fuentes del usuario y se copiaron los originales a static/fonts. NType82 Regular en lectura/controles, Headline en títulos, Space Mono en etiquetas y Ndot77 JP Extended en la marca como texto. Se comprobaron familias aplicadas en el navegador y render final de Ndot77 tras cargar su archivo. Revisadas vistas escritorio y móvil sin desbordamiento horizontal. Capturas nuevas: evidence/portada-fuentes-escritorio.jpg y evidence/portada-fuentes-movil.jpg. No se añadieron tests para el cambio visual.

## Limpieza de archivos sin uso

Se retiraron el wordmark SVG anterior, su generador, los estilos para ese SVG y las capturas sustituidas por las de fuentes actuales. Se retiraron las variables LNbits reservadas de settings y del ejemplo de configuración de Django, que aún no tiene integración de pagos. Se conservaron datos y credenciales locales, dependencias de ejecución, fuentes activas, concepto aprobado, documentación y evidencia vigente.
