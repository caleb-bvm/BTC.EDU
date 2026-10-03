# Componentes visuales de BTC.EDU

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
