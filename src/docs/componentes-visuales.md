# Componentes visuales de BTC.EDU

**2 de octubre:** la estructura de academia adopta una estética industrial más marcada, elegida por el usuario. Cursos, selector, tutoriales, recursos, fichas, lectura, login y Mi aprendizaje vacío usan plantilla común y componentes en `academy.css`. Ver [pantallas, comportamiento y verificación](interfaz-academia-2026-10-02.md). Los apartados siguientes documentan la base visual previa que se conserva; no representan toda la navegación vigente.

Referencia inspeccionada: design/btc-edu-concepto-aprobado.png, aprobada el 1 de octubre de 2026. Se conserva nombre de puntos, encabezado, dos columnas, título grande, botones negros/con borde y objetos industriales. En móvil las columnas se apilan. Las tarjetas de ejemplo no son datos.

| Componente | Fuente | Comportamiento |
|---|---|---|
| Encabezado y pie | templates/base.html | Inicio, Explorar, Para creadores y Entrar/Mi espacio |
| Nombre de puntos | Ndot77 JP Extended / .brand-wordmark | Texto BTC.EDU con Ndot77 local; enlace accesible al inicio |
| Portada | core/home.html | Texto y enlaces HTML; numeración decorativa, no carrusel |
| Ilustración | static/images/industrial-hero.png | Imagen independiente decorativa, sin interfaz ni textos |
| Etiquetas | .eyebrow / .mono | Monoespaciadas, línea naranja y texto oscuro |
| Botones | .btn + site.css | Primario negro, secundario con borde; foco visible |
| Catálogo, búsqueda y filtros | core/_catalog.html | Formulario con etiquetas, filtros combinados, actualización HTMX y envío normal sin JS |
| Creadores | core/creators.html | Bloques explicativos y aviso de publicación pendiente |
| Login | registration/login.html | Labels, autocompletado, email/password, CSRF y error visible |
| Mi espacio | core/workspace.html | Correo escapado, biblioteca vacía y cierre POST |

Paleta: papel #FAFAF7, texto #141414, secundario #636363, borde #DCDCD7, naranja #ED9655, fondo suave #FBEADD. Naranja de filtros con texto oscuro; no párrafos naranja sobre blanco. NType82 Regular para lectura, NType82 Headline para títulos, Space Mono Regular para etiquetas y Ndot77 JP Extended para el nombre. Archivos encontrados en el sistema del usuario y servidos localmente desde static/fonts; sin CDN. Foco #A75921 de 3px; salto al contenido, headings, idioma es, aria-live en catálogo. La revisión visual no equivale a una auditoría completa con lector de pantalla.

## Procedencia y prompt de la ilustración

Generada con herramienta integrada de imágenes, usando como referencia el concepto aprobado. Concepto original conservado; resultado en static/images/industrial-hero.png. No se reutilizaron fotografías ni logos de las referencias comerciales.

Prompt utilizado:

> Use case: product-mockup. Reference image: approved BTC.EDU website concept. Generate only the industrial sculpture from the upper-right hero as a separate landscape website asset: four offset stacked brushed aluminum and off-white concrete rectangular equipment modules, perforated dot vents, screws, one translucent soft orange acrylic middle module. Preserve the reference shape, perspective, materials and quiet premium studio lighting. Plain warm white #fafaf7 background with gentle contact shadow. Entire sculpture centered and fully visible, minimal margins. No website, no logo, no lettering, no text, no UI, no cards. Output a realistic high-quality product photograph matching the approved reference.

Toda información y acción vive en HTML. No se cargó contenido educativo, precios, ventas ni testimonios.

## Fuentes incorporadas el 1 de octubre de 2026

Encontradas en la carpeta de fuentes de Windows del usuario; también existen copias en Documents/Design Assets/Fonts/August 2026/nothingfont. Archivos copiados a static/fonts: NType82-Regular.otf, NType82-Headline.otf, SpaceMono-Regular.otf y Ndot77JPExtended.ttf. La variante encontrada de Ndot77 es JP Extended, cuyo nombre interno es Ndot77JPExtended. Se preservaron los originales sin modificación ni conversión. font-display: swap conserva lectura mientras cargan; Ndot77 se usa únicamente en la marca. Ndot77 JP Extended pesa aproximadamente 14.9 MB y es el archivo completo. No se publicó ni verificó licencia de distribución web; la incorporación corresponde a esta revisión local.

## Cursos y lectura

La entrega del 12 de octubre amplía la identidad aprobada con temario por capítulos, estados expresados en texto, medidor de avance, preparación del curso, biblioteca con continuación, prácticas y soluciones desplegables. Las superficies están en `learning-experience.css` y reutilizan la paleta de la academia, incluida la adaptación al tema compartido. El modo enfocado y el guardado se gestionan en `learning.js`; la altura real del encabezado determina la posición del menú móvil. [Reglas, evidencia y límites](experiencia-aprendizaje-2026-10-12.md).


## Barra lateral contextual

La configuración de navegación está en `core/navigation.py` y se entrega mediante un procesador de contexto. Usa el nombre de la ruta resuelta, no el parámetro `active` de las vistas, porque un curso y su catálogo comparten ese parámetro pero necesitan opciones distintas. Academia y estudio incluyen `_context_navigation.html`; revisión editorial conserva su acceso administrativo.

Los grupos son catálogo, aprendizaje, compras, comunidad, cuenta, acceso, curso, contenido del creador y acompañamiento de alumnos. Los detalles conservan el enlace activo de su sección. Los visitantes no reciben enlaces del espacio privado de estudiantes. Los creadores vuelven a su estudio desde las páginas compartidas; una solicitud pendiente conduce al perfil de creador. En cursos se conserva la URL de la versión consultada y el retorno al recorrido previo. Las lecciones enlazan al temario existente para evitar duplicarlo.

El menú móvil conserva el control de apertura, Escape y fondo; al elegir un enlace se cierra, incluso para el ancla del temario. La navegación no modifica permisos ni concede acceso a contenido.

Verificación: `core.test_navigation` comprueba grupos, detalles activos, visitantes, creadores, solicitud pendiente, recuperación de acceso y versión del curso. Se ejecutan también `learning.test_experience` y `accounts.test_destinations` para revisar continuidad del aprendizaje y destino de acceso. La comprobación visual en navegador y la validación con participantes quedan pendientes; las pruebas automatizadas no demuestran comprensión de la interfaz.


Registro de verificación del 12 de octubre de 2026: la primera ejecución ampliada completó 21 pruebas y detectó la pérdida del parámetro `next` en el enlace lateral de registro. Se corrigió conservando el destino en los enlaces de acceso y registro y se añadió una prueba específica. La siguiente ejecución de aprendizaje y destinos quedó impedida por una modificación concurrente del modelo de usuario: `accounts_user` no contiene la columna `avatar` en la base de pruebas creada a partir de las migraciones actuales. No se modificaron las migraciones de perfiles desde esta entrega. La comprobación de Django informa además la advertencia existente sobre el correo no único.
Resultado final de la comprobación aislada: las siete pruebas de core.test_navigation pasaron, incluida la conservación del destino de compra durante el acceso y registro.

## Evaluaciones

`assessments.css` organiza preparación, mapa de preguntas, opciones amplias, revisión previa, resultados y editor plegable. Conserva paleta, marca y fuentes locales de títulos/etiquetas; el texto funcional usa Arial del sistema. `quizzes.js` añade navegación, resumen y estado de cambios sin guardar; el formulario nativo conserva guardado y entrega sin JavaScript. Las reglas, corrección y privacidad siguen en el servidor. [Diagnóstico, referencias, evidencia y límites](experiencia-evaluaciones-2026-10-12.md).
