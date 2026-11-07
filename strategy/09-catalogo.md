# Catálogo

Composición del catálogo local: cursos, modalidades, tutoriales, recursos, rutas y muestras.

<a id="02-catalogo-de-prueba"></a>

## Catálogo de prueba

Registro conservado; sus fechas, cifras y pendientes corresponden a la entrega o propuesta descrita.

### Colección vigente de Bitcoin y Lightning

La colección publicada localmente el 12 de octubre de 2026 sustituye los ejemplos de programación siguientes como catálogo inicial. Son seis cursos con cuatro lecciones de texto cada uno, organizadas en dos capítulos. Los textos incluyen explicación, ejemplo, ejercicio y solución, con referencias técnicas. No incluyen videos ni archivos descargables. El perfil público es BTC.EDU y no representa a un instructor ficticio.

Bitcoin desde cero: unidades, red y transacciones; Wallets y autocustodia: claves, respaldo y recepción; y Lightning desde cero: canales, rutas y liquidez son completamente gratuitos. Facturas Lightning: del QR a la confirmación; LNbits: organiza un laboratorio de micropagos; y Contenido con micropagos: compra, acceso y versiones incluyen una primera lección gratuita y tres pagadas.

Cada curso pagado cuesta 120 sats y cada lección pagada se ofrece por 50 sats. Los precios son valores de prueba; no acreditan validación ni ingresos. Cada curso requiere completar sus cuatro lecciones y aprobar una pregunta final para obtener certificado; esa comprobación no demuestra dominio exhaustivo. Las duraciones son estimaciones para leer y realizar ejercicios, no tiempos medidos. Las prácticas no requieren fondos reales.

La carga se realiza con `python manage.py load_editorial_catalog` desde `src`, crea respaldo y conserva cursos existentes. [Reglas, comprobación y límites](../src/docs/operacion-y-bitacora.md#catalogo-editorial-2026-10-12). La revisión educativa externa sigue pendiente.

<a id="cursos-completos-creacion-tecnologia"></a>

### Cursos completos de Creación y Tecnología

El 15 de octubre de 2026 añadimos cuatro recorridos originales de autoestudio: fotografía con celular (1800 sats, 360 minutos), edición con Shotcut (2400 sats, 480 minutos), desarrollo web accesible (3000 sats, 600 minutos) y reportes CSV con Python (3000 sats, 600 minutos). Cada curso tiene doce lecciones en cuatro capítulos, dieciséis preguntas y un proyecto con cinco criterios. Los textos enseñan procedimientos, ejemplos resueltos, ejercicios y comprobaciones; los enlaces amplían el contenido, no lo sustituyen. La duración es estimada, sin observación de alumnos.

Todas las lecciones son de pago. La muestra describe el resultado sin exponer el desarrollo ni la solución. Para mantener compras útiles por separado, las lecciones tienen alcance declarado, requisitos y ofertas individuales; los capítulos y cursos agrupan exactamente sus revisiones. Las lecciones cuestan 225, 300 o 375 sats según el curso y los capítulos agrupan tres lecciones a esos importes. El curso completo cuesta menos que la suma de sus capítulos. Son precios editoriales iniciales; no se midió disposición a pagar, demanda ni margen.

El material original no reproduce cursos comerciales. Las referencias primarias consultadas sustentan decisiones técnicas: [cámara del iPhone](https://support.apple.com/en-lamr/guide/iphone/-iph263472f78/ios), [Google Fotos](https://support.google.com/photos/answer/6128850?hl=es), [Nikon](https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/top-10-photo-tips-for-better-images), [Canon](https://en.canon-cna.com/get-inspired/tips-and-techniques/street-photography-tips/), [tutoriales de Shotcut](https://www.shotcut.org/tutorials/), [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development), [W3C WAI](https://www.w3.org/WAI/tutorials/), [GitHub Pages](https://docs.github.com/en/pages), [tutorial de Python](https://docs.python.org/3/tutorial/) y [Python en Microsoft Learn](https://learn.microsoft.com/en-us/shows/intro-to-python-development/). Los archivos de contenido conservan las fuentes y videos seleccionados por lección. Los procedimientos del teléfono varían según dispositivo; el curso explica alternativas generales. Los videos se enlazan o se muestran desde su reproductor autorizado, sin descargarlos ni venderlos como archivos propios. Su disponibilidad, idioma y restricciones dependen del proveedor; la lección escrita es autónoma.

Las portadas se integran como ilustraciones del curso con la [licencia Unsplash](https://unsplash.com/license), que permite el uso comercial dentro de un trabajo original. Se conservan localmente para que la ficha no dependa de una petición a terceros. No se venden como fotografías independientes ni se atribuyen a BTC.EDU.

| Portada | Fotógrafo y página de origen |
|---|---|
| Fotografía | [Marek Pospíšil](https://unsplash.com/photos/man-holding-iphone-WLBqJn2I6cQ) |
| Edición de video | [André Eusébio](https://unsplash.com/photos/a-person-edits-video-on-a-computer-25OWIrAtGMM) |
| Desarrollo web | [Emile Perron](https://unsplash.com/photos/macbook-pro-showing-programming-language-xrVDYZRGdw4) |
| Python | [Chris Ried](https://unsplash.com/photos/a-computer-screen-with-a-bunch-of-code-on-it-ieic5Tq8YMk) |

La revisión editorial registra estructura, fuentes y acceso; sigue pendiente la revisión independiente por especialistas y la validación con estudiantes. El certificado requiere doce lecciones y cuatro evaluaciones con nota mínima de 75 %. Los proyectos permiten autoevaluación; no prometemos corrección personal y mantenemos cerrada la recepción hasta asignar un responsable. Aprobar el proyecto no es requisito del certificado actual. La publicación mantiene el entorno de pagos local y no demuestra cobros con fondos reales. [Carga, pruebas y límites](../src/docs/operacion-y-bitacora.md#cursos-completos-2026-10-15).

<a id="cursos-por-modalidad"></a>

### Cursos por categoría y modalidad

El 25 de octubre de 2026 añadimos quince cursos para que cada categoría tenga una opción de pago, una freemium y una de membresía. Elegimos temas habituales en la formación de cada categoría y con documentación primaria abierta, de modo que las explicaciones pudieran apoyarse en fuentes verificables. Mantienen la profundidad de los cursos del 15 de octubre: doce lecciones de al menos 250 palabras con ejemplo, práctica y solución, dieciséis preguntas y un proyecto con criterios.

| Curso | Modalidad | Fuentes principales |
|---|---|---|
| Opera tu propio nodo Bitcoin | Pago, 3000 sats | [Bitcoin.org](https://bitcoin.org/en/full-node), [Bitcoin Developer Guide](https://developer.bitcoin.org/devguide/), [bitcoin.conf](https://github.com/bitcoin/bitcoin/blob/master/doc/bitcoin-conf.md) |
| Cobros con Lightning para negocios | Membresía | [LNbits](https://docs.lnbits.org/), [Mastering the Lightning Network](https://github.com/lnbook/lnbook) |
| Git y GitHub | Freemium, 2100 sats | [Pro Git](https://git-scm.com/book/es/v2), [referencia de Git](https://git-scm.com/docs/git-config) |
| APIs REST con FastAPI | Membresía | [FastAPI](https://fastapi.tiangolo.com/es/tutorial/first-steps/), [MDN: HTTP](https://developer.mozilla.org/es/docs/Web/HTTP/Reference/Methods) |
| SQL con SQLite | Pago, 3000 sats | [SQLite](https://sqlite.org/cli.html), [tablas STRICT](https://sqlite.org/stricttables.html) |
| IA generativa en el trabajo | Freemium, 2400 sats | [NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence), [UNESCO](https://www.unesco.org/es/artificial-intelligence/recommendation-ethics), guías de Anthropic y OpenAI |
| Análisis de datos con pandas | Membresía | [pandas](https://pandas.pydata.org/docs/user_guide/10min.html), [venv](https://docs.python.org/3/library/venv.html) |
| Seguridad de aplicaciones web | Pago, 3600 sats | [OWASP Top 10:2025](https://top10.owasp.org/2025/), [ASVS](https://owasp.org/www-project-application-security-verification-standard/), [Flask](https://flask.palletsprojects.com/en/stable/web-security/) |
| Fundamentos de ciberseguridad | Freemium, 2100 sats | [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html), [CISA](https://www.cisa.gov/secure-our-world), [INCIBE](https://www.incibe.es/ciudadania) |
| Respuesta a incidentes | Membresía | [NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), [CSF 2.0](https://www.nist.gov/cyberframework), [FIRST](https://www.first.org/standards/frameworks/csirts/csirt_services_framework_v2.1) |
| Linux para servidores | Pago, 3000 sats | [Ubuntu Server](https://documentation.ubuntu.com/server/), [WSL](https://learn.microsoft.com/es-es/windows/wsl/install) |
| Redes desde cero | Freemium, 2100 sats | [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918), [MDN](https://developer.mozilla.org/es/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work) |
| Docker y contenedores | Membresía | [Docker](https://docs.docker.com/get-started/docker-overview/), [OCI](https://opencontainers.org/) |
| Diseño UI/UX con Figma | Freemium, 2400 sats | [Design Council](https://www.designcouncil.org.uk/our-resources/the-double-diamond/), [Nielsen Norman Group](https://www.nngroup.com/articles/user-interviews/) |
| Modelado 3D con Blender | Membresía | [Manual de Blender](https://docs.blender.org/manual/es/latest/), [Blender 5.2 LTS](https://www.blender.org/releases/5-2/) |

Las lecciones de pago de los cursos de pago y freemium cuestan 1,5 veces su parte proporcional del curso (375 o 450 sats en los de pago; 350 o 400 en los freemium), los capítulos suman sus tres lecciones y el curso completo cuesta menos que esa suma. Los freemium abren tres lecciones para que se pueda juzgar el curso antes de pagar. Los de membresía abren solo la primera lección y no venden unidades, para que la diferencia entre comprar y suscribirse se vea en la ficha. Son decisiones de demostración; los precios y la proporción gratuita siguen sin validar.

Cada curso enlaza entre cuatro y ocho videos externos insertables, con el título y el canal de origen. Comprobamos la inserción con el servicio oEmbed de YouTube y reemplazamos los que la tenían desactivada; preferimos videos en español y marcamos como apoyo opcional el único en inglés. Los videos complementan las lecciones; ninguna depende de ellos. Las portadas son quince ilustraciones SVG propias, una por subcategoría, que no requieren créditos ni peticiones a terceros.

Ejecutamos los ejemplos de código antes de publicarlos: consultas en SQLite, análisis con pandas, ejemplos de seguridad con Flask, una API de FastAPI con sus pruebas, contenedores con Docker y un nodo Bitcoin Core en regtest. Esa ejecución corrigió afirmaciones concretas, como el reinicio de systemd tras una señal, la conversión de mayúsculas acentuadas en SQLite y el intervalo del halving en regtest. Los ejercicios de Blender y Figma no se ejecutaron. Comprobamos también los enlaces de las fuentes. Ninguno de los cursos tiene revisión de especialistas ni se ha probado con alumnos.

<a id="curso-avanzado-backend"></a>

### Curso avanzado de backend

El 6 de noviembre de 2026 publicamos el primer curso de nivel avanzado: **Backend avanzado con Python: PostgreSQL, fiabilidad y operación en producción**. Lo elegimos porque continúa un curso existente, APIs REST con FastAPI, y porque podíamos ejecutar todos sus ejemplos aquí. Es de pago, cuesta 3600 sats, dura unas 11 horas y sigue el formato del catálogo: cuatro capítulos, doce lecciones, una evaluación de cuatro preguntas por capítulo y un proyecto final de autoevaluación.

| Capítulo | Lecciones |
|---|---|
| Persistencia para producción | SQLAlchemy 2.0 y PostgreSQL; migraciones con Alembic; transacciones y concurrencia |
| Asincronía y rendimiento | async y await; tiempos límite y reintentos; caché con ETag y Redis |
| Trabajo fiable | Bandeja de salida; idempotencia; webhooks firmados |
| Operar en producción | OAuth2 con alcances; observabilidad; despliegue con reversión |

El proyecto de ejemplo se comprobó con FastAPI 0.162, SQLAlchemy 2.1, Alembic 1.20, PostgreSQL 17 y Redis 7, en contenedores locales. Las cifras que citan las lecciones vienen de esas ejecuciones: veinte ventas simultáneas con cinco unidades dejan cero existencias con la actualización atómica, y una versión ingenua con doce ventas vendió doce. Las fuentes son documentación oficial y RFC. De los siete videos, seis están en español; el de SQLAlchemy 2.0 está en inglés, y los de caché y métricas usan Node.js y Go. Es un paso opcional de la ruta Backend con Python. Como los demás cursos, no tiene revisión de especialistas ni se ha probado con alumnos, y su precio es una hipótesis.

<a id="tutoriales-y-recursos"></a>

### Tutoriales y recursos por categoría

Tutoriales y Recursos estaban vacíos. El 25 de octubre de 2026 publicamos cinco tutoriales y cinco recursos en cada categoría para que las tres secciones tengan contenido real con el que revisar su diferencia. Tomamos como criterio la distinción de [Diátaxis](https://diataxis.fr/) entre aprender, resolver una tarea y consultar: un curso acompaña un aprendizaje largo, un tutorial resuelve una tarea concreta en minutos y un recurso se consulta cuando hace falta.

Cada tutorial tiene de tres a cuatro pasos de entre 110 y 180 palabras, con ejemplo, práctica, solución y las fuentes oficiales del paso. Por categoría hay dos gratuitos, dos que abren el primer paso y venden los demás y uno de pago. El precio del paso sigue la regla de los cursos (1,5 veces su parte proporcional) y el tutorial completo cuesta entre 150 y 450 sats. Los recursos son dos videos de YouTube en español, una hoja de referencia gratuita en PDF, un material de pago en PDF de 120 a 160 sats y un enlace externo.

| Categoría | Tutoriales | Recursos propios y enlace |
|---|---|---|
| Bitcoin y Lightning | Explorador de bloques; respaldo de la frase semilla; leer una factura Lightning; comisión en sat/vB; factura con la API de LNbits | Hoja de unidades, direcciones y comisiones; plan de custodia de la semilla; [documento de Bitcoin en español](https://bitcoin.org/files/bitcoin-paper/bitcoin_es.pdf) |
| Ciberseguridad | Verificación en dos pasos; revisar filtraciones; analizar un correo sospechoso; verificar una descarga con SHA-256; inventario de la red doméstica con Nmap | Lista de seguridad personal; registro de incidentes; [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) |
| Datos e inteligencia artificial | Tabla dinámica; limpiar un CSV con pandas; GROUP BY y HAVING; primer modelo con scikit-learn; resumen verificable con IA | Hoja de SQL; limpieza con pandas; [curso de aprendizaje automático de Google](https://developers.google.com/machine-learning/crash-course?hl=es-419) |
| Desarrollo de software | Entorno virtual de Python; primera prueba con pytest; deshacer cambios en Git; API con fetch; probar una API con curl | Hoja de Git; códigos de estado HTTP; [MDN: usar Fetch](https://developer.mozilla.org/es/docs/Web/API/Fetch_API/Using_Fetch) |
| Infraestructura y nube | Llave SSH; tareas con cron; componentes del PC; Dockerfile para Python; subredes CIDR | Hoja de comandos de Linux; tabla de subredes IPv4; [Red Hat: ¿qué es la nube?](https://www.redhat.com/es/topics/cloud) |
| Diseño y creación digital | Contraste WCAG; imágenes para la web; regla de los tercios; histograma en Lightroom; subtítulos SRT y WebVTT | Lista de accesibilidad visual; exportación de imágenes; [comprobador de WebAIM](https://webaim.org/resources/contrastchecker/) |

Los videos son de canales que publican en español, como Dot CSV, EDteam, midulive, Telefónica o Coderhouse. Se insertan desde `youtube-nocookie.com` con el autor y un enlace al original, y la plataforma los mantiene gratuitos: no vende contenido ajeno ni copia sus archivos. Comprobamos con oEmbed que los doce permiten la inserción. Los PDF son originales, generados con el estilo de la interfaz y con sus fuentes al final.

Ejecutamos los ejemplos de pandas, scikit-learn, pytest, SQLite, Git, `ssh-keygen`, `fetch`, `curl` e `ipaddress`, y los cálculos de comisiones, subredes y contraste; las cifras publicadas son las obtenidas. No se ejecutaron los tutoriales de Docker, cron, Nmap, Lightroom, subtítulos ni LNbits. Ningún tutorial tiene revisión de especialistas; los precios y la división entre pasos gratuitos y de pago son decisiones editoriales sin validar. Falta observar con participantes si la diferencia entre curso, tutorial y recurso ayuda a elegir.

<a id="rutas-de-aprendizaje"></a>

### Rutas de aprendizaje

El 25 de octubre de 2026, con 25 cursos publicados, consideramos que el catálogo bastaba para organizar recorridos y no añadimos cursos. Cargamos seis rutas editoriales con las agrupaciones que aprobó el usuario: Bitcoin y Lightning, Desarrollo con Lightning, Backend con Python, Análisis de datos, Ciberseguridad e Infraestructura. Tienen entre cuatro y seis cursos y un curso puede estar en varias rutas.

El usuario definió cuatro condiciones: la ruta es un sendero recomendado que no bloquea pasos, los cursos se compran por separado o en un paquete con descuento, pueden crear rutas BTC.EDU y los educadores, y hay pasos opcionales. Las resolvimos así:

- Un paso opcional no cuenta para el porcentaje ni para la credencial; si se completa, figura en la evidencia marcado como opcional. Marcamos como opcionales los cursos que amplían el objetivo sin ser imprescindibles, como el nodo Bitcoin Core o Docker en Backend con Python.
- El siguiente paso sugerido es el curso en progreso o, si no lo hay, el primero pendiente después del último completado. Saltar un paso no retiene la sugerencia.
- El paquete es un pedido con una línea por curso que el estudiante aún no tiene. Cada línea descuenta el porcentaje de la ruta sobre lo que queda tras el crédito por compras anteriores y conserva al menos 1 sat, de modo que cada educador asume el descuento de sus propios cursos. No incluye cursos gratuitos, de membresía ni comprados, exige al menos dos cursos por comprar y no se combina con cupones. El servidor recalcula el precio y un cambio de cursos o de descuento invalida la revisión.
- Un educador solo incluye sus cursos publicados, elige un descuento entre 0 y 50 % y necesita dos cursos con uno obligatorio para publicar. Publica sin revisión administrativa, porque la ruta solo reordena cursos ya revisados; la administración puede retirarla.
- Las rutas editoriales se crean desde administración o con `load_learning_paths` y pueden combinar cursos de cualquier educador. Hoy solo usan cursos de las cuentas de BTC.EDU; antes de incluir en un paquete cursos de otros educadores necesitamos su acuerdo, porque el descuento reduce su ingreso.

El descuento de las rutas editoriales es de 15 %, una hipótesis sin validar. Las rutas de Python, datos, ciberseguridad e infraestructura cuestan entre 6630 y 7140 sats en paquete, frente a 7800–8400 por separado. Las dos de Lightning tienen paquetes pequeños, de 2652 y 306 sats, porque la mayoría de sus cursos editoriales son gratuitos. Cinco rutas incluyen un curso de membresía; la ruta lo indica y el paquete no lo cobra.

Falta comprobar con participantes si se entienden el paquete, los pasos opcionales y la diferencia con la membresía, y si el descuento influye en la compra. Detectamos brechas para rutas futuras: ningún curso es avanzado, Desarrollo web tiene un solo curso y Diseño y creación digital no forma todavía un recorrido.

El 6 de noviembre de 2026 cerramos dos de esas brechas sin escribir cursos nuevos, porque los cursos publicados ya permitían formar los recorridos. **Desarrollo web** reúne Desarrollo web, Git y GitHub y Seguridad de aplicaciones web como pasos obligatorios; Diseño UI/UX y APIs con FastAPI son opcionales. **Diseño y creación digital** va de Fotografía con celular a Edición de video con Shotcut y Diseño UI/UX, con Blender como paso opcional. Sus paquetes cuestan 9435 sats (11 100 por separado) y 5610 sats (6600). El paquete de Desarrollo web incluye Diseño UI/UX, aunque es opcional, porque el paquete cobra todos los cursos de pago que el estudiante no tiene. APIs con FastAPI y Blender se abren con la membresía. Ese mismo día publicamos el [primer curso avanzado](#curso-avanzado-backend), de backend con Python, como paso opcional de Backend con Python. Con él, el paquete de esa ruta pasa a 9945 sats (11 700 por separado).

### Ejemplos históricos de programación

Los títulos, creadores y precios son ficticios. No representan contenido terminado, ventas ni precios validados. Los videos y archivos deben producirse o seleccionarse con permiso de uso antes de la demo.

| ID | Contenido | Organización | Acceso y precio |
|---|---|---|---|
| CUR-001 | Primeros pasos con JavaScript | Curso completamente gratuito | Gratis |
| LES-001 | Variables y operaciones | Lección de CUR-001 | Gratis |
| VID-001 | Ejemplo con variables | Video de CUR-001 | Gratis |
| CUR-002 | Funciones en JavaScript | Curso con lecciones gratis y capítulos de pago | Explorar gratis; compras indicadas abajo |
| LES-002 | Qué es una función | Lección de CUR-002 | Gratis |
| CHP-001 | Parámetros y resultados | Capítulo de CUR-002 con una lección y un video | 100 sats |
| VID-002 | Resolver un ejercicio con funciones | Video de CUR-002 vendido por separado, fuera de CHP-001 | 80 sats |
| MAT-001 | Ejercicios y soluciones | Archivo adicional de CUR-002 | 50 sats; no obligatorio |
| CUR-003 | Construye una API sencilla | Curso completo de pago | 300 sats por CHP-002 y CHP-003 |
| LES-003 | Presentación del proyecto | Lección de muestra de CUR-003 | Gratis |
| CHP-002 | Crear una ruta | Capítulo de CUR-003, con texto y video | 150 sats individualmente |
| CHP-003 | Validar los datos | Capítulo de CUR-003, con texto y video | 200 sats individualmente |
| MAT-002 | Lista de comprobación | Material de CUR-003, fuera de la compra del curso | Gratis |
| MAT-003 | Ejercicios adicionales de API | Material de CUR-003, fuera de la compra del curso | 60 sats |

### Muestras y contenido

La investigación de [13](04-producto-y-monetizacion.md#13-monetizacion-precios-y-muestras) no cambia los precios del catálogo. Mantener oferta y muestra constantes al comparar y permitir elegir ninguna compra. Probar lección útil para cursos, actividad para capítulos, fragmento para videos y extracto para materiales. Son variantes propuestas, no proporciones aprobadas. Cada activo necesita autoría/permiso y muestra separada del contenido protegido.

Cada página explica objetivo, requisitos, creador, formato y contenidos incluidos. Las lecciones gratuitas se muestran completas. Los capítulos de pago tienen una descripción y una muestra de texto separada del contenido comprado. Cada video de pago tiene una muestra pública independiente; el archivo completo no se entrega antes de verificar la compra. Los materiales describen formato y contenido y pueden mostrar un extracto público separado.

Ejemplo gratuito LES-001: `const precio = 10; const cantidad = 2;` y explicación de `precio * cantidad`.
Ejemplo de muestra de CHP-001: explicar qué son los parámetros e indicar que la compra incluye explicación completa y un video práctico.
Ejemplo de MAT-001: dos ejercicios con soluciones; la muestra muestra un enunciado y la compra entrega el archivo completo.

CUR-003 incluye únicamente CHP-002 y CHP-003 y sus lecciones y videos. MAT-003 se compra aparte. Su composición queda fija durante el MVP. La compra del curso cuesta 300 sats frente a 350 sats por los capítulos separados. Los recursos que se compran aparte también se enumeran antes de pagar.

Si ya se compró parte de CUR-003, se ofrecen los capítulos faltantes individualmente. Si ya se compró todo, se muestran los enlaces para abrirlo. No se calcula un descuento personalizado en esta versión.

### Datos adicionales para probar el alcance ampliado

Preparar un creador autorizado Aula Demo y otro creador para comprobar aislamiento; una evaluación de prueba con preguntas, nota mínima e intentos; una versión de CUR-003 con requisitos de certificado; un espacio de preguntas por lección y comunidad del curso; y un plan de 30 días con contenidos explícitos y precio ficticio. Los valores concretos de nota, intentos y precio se fijan en los datos de prueba y no representan validación comercial. Probar un alumno con compra individual y membresía que vence; no borrar su compra ni progreso.
