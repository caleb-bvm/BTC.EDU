# Catálogo de prueba

## Colección vigente de Bitcoin y Lightning

La colección publicada localmente el 12 de octubre de 2026 sustituye los ejemplos de programación siguientes como catálogo inicial. Son seis cursos con cuatro lecciones de texto cada uno, organizadas en dos capítulos. Los textos incluyen explicación, ejemplo, ejercicio y solución, con referencias técnicas. No incluyen videos ni archivos descargables. El perfil público es BTC.EDU y no representa a un instructor ficticio.

Bitcoin desde cero: unidades, red y transacciones; Wallets y autocustodia: claves, respaldo y recepción; y Lightning desde cero: canales, rutas y liquidez son completamente gratuitos. Facturas Lightning: del QR a la confirmación; LNbits: organiza un laboratorio de micropagos; y Contenido con micropagos: compra, acceso y versiones incluyen una primera lección gratuita y tres pagadas.

Cada curso pagado cuesta 120 sats y cada lección pagada se ofrece por 50 sats. Los precios son valores de prueba; no acreditan validación ni ingresos. Cada curso requiere completar sus cuatro lecciones y aprobar una pregunta final para obtener certificado; esa comprobación no demuestra dominio exhaustivo. Las duraciones son estimaciones para leer y realizar ejercicios, no tiempos medidos. Las prácticas no requieren fondos reales.

La carga se realiza con `python manage.py load_editorial_catalog` desde `src`, crea respaldo y conserva cursos existentes. [Reglas, comprobación y límites](../src/docs/catalogo-editorial-2026-10-12.md). La revisión educativa externa sigue pendiente.

## Ejemplos históricos de programación

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

## Muestras y contenido

La investigación de [13](13-monetizacion-precios-y-muestras.md) no cambia los precios del catálogo. Mantener oferta y muestra constantes al comparar y permitir elegir ninguna compra. Probar lección útil para cursos, actividad para capítulos, fragmento para videos y extracto para materiales. Son variantes propuestas, no proporciones aprobadas. Cada activo necesita autoría/permiso y muestra separada del contenido protegido.

Cada página explica objetivo, requisitos, creador, formato y contenidos incluidos. Las lecciones gratuitas se muestran completas. Los capítulos de pago tienen una descripción y una muestra de texto separada del contenido comprado. Cada video de pago tiene una muestra pública independiente; el archivo completo no se entrega antes de verificar la compra. Los materiales describen formato y contenido y pueden mostrar un extracto público separado.

Ejemplo gratuito LES-001: `const precio = 10; const cantidad = 2;` y explicación de `precio * cantidad`.
Ejemplo de muestra de CHP-001: explicar qué son los parámetros e indicar que la compra incluye explicación completa y un video práctico.
Ejemplo de MAT-001: dos ejercicios con soluciones; la muestra muestra un enunciado y la compra entrega el archivo completo.

CUR-003 incluye únicamente CHP-002 y CHP-003 y sus lecciones y videos. MAT-003 se compra aparte. Su composición queda fija durante el MVP. La compra del curso cuesta 300 sats frente a 350 sats por los capítulos separados. Los recursos que se compran aparte también se enumeran antes de pagar.

Si ya se compró parte de CUR-003, se ofrecen los capítulos faltantes individualmente. Si ya se compró todo, se muestran los enlaces para abrirlo. No se calcula un descuento personalizado en esta versión.

## Datos adicionales para probar el alcance ampliado

Preparar un creador autorizado Aula Demo y otro creador para comprobar aislamiento; una evaluación de prueba con preguntas, nota mínima e intentos; una versión de CUR-003 con requisitos de certificado; un espacio de preguntas por lección y comunidad del curso; y un plan de 30 días con contenidos explícitos y precio ficticio. Los valores concretos de nota, intentos y precio se fijan en los datos de prueba y no representan validación comercial. Probar un alumno con compra individual y membresía que vence; no borrar su compra ni progreso.

