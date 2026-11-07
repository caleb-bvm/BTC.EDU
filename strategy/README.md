# Documentación de BTC.EDU

Esta carpeta reúne la investigación, los requisitos y las decisiones de producto. El [informe](01-informe.md) describe el producto vigente y es el texto que se copia al Google Doc; los demás archivos conservan el respaldo de cada tema en el orden en que se lee el proyecto: qué se pidió, qué investigamos, qué propusimos, cómo lo diseñamos y cómo lo validaremos.

## Documentos

| Archivo | Contenido |
|---|---|
| [01 · Informe](01-informe.md) | Idea, investigación, objetivos, enfoque, desarrollo, operación, logros, manual de uso y próximos pasos. |
| [02 · Requisitos y alcance](02-requisitos-y-alcance.md) | Lo que exige CUBO+, alcance elegido, especificación funcional, criterios de aceptación y trazabilidad. |
| [03 · Investigación y posicionamiento](03-investigacion-y-posicionamiento.md) | Comparación con otras plataformas, necesidades de alumnos y creadores, diferencias y orden recomendado. |
| [04 · Producto y monetización](04-producto-y-monetizacion.md) | Propuesta, formas de ofrecer contenido, modelos de cobro, costos, muestras y precios por validar. |
| [05 · Arquitectura de producto](05-arquitectura-de-producto.md) | Estructura del producto, tipos de contenido, reglas de compra y acceso, pantallas y recorridos. |
| [06 · Interfaz e identidad visual](06-interfaz-e-identidad-visual.md) | Diagnóstico y cambios de interfaz, navegación, catálogos, criterios de aceptación e identidad visual. |
| [07 · Compra y comercio](07-compra-y-comercio.md) | Carrito, checkout, pedidos, compras duplicadas y funciones añadidas tras comparar plataformas. |
| [08 · Aprendizaje, creadores y comunidad](08-aprendizaje-creadores-y-comunidad.md) | Recorrido del creador, aprendizaje, certificados, preguntas, avisos, paneles y comunidad. |
| [09 · Catálogo](09-catalogo.md) | Cursos, modalidades, tutoriales, recursos, rutas y muestras del catálogo local. |
| [10 · Métricas y validación](10-metricas-y-validacion.md) | Eventos e indicadores, plan de investigación e instrumentos para sesiones con usuarios. |
| [11 · Plan y decisiones](11-plan-y-decisiones.md) | Plan de trabajo, calendario, decisiones registradas y plan de documentación. |
| [12 · Guion de presentación](12-guion-de-presentacion.md) | Guion del Demo Day en inglés y español, lista para la demostración, cifras clave y preguntas probables. Presentación de 11 diapositivas en `12-presentacion-btc-edu.pptx`. |

Fuera de esta carpeta:

- [Operación y bitácora](../src/docs/operacion-y-bitacora.md): cómo ejecuto el proyecto en local, decisiones técnicas, pendientes e historial por día con sus evidencias.
- [Guía técnica](../src/README.md): instalación, arquitectura y lógica del código.
- `docs/`: los dos documentos originales de CUBO+, sin modificar.
- `BTC-EDU-para-Google-Docs.txt`: exportación anterior del informe, conservada como antecedente; no se actualiza.

## Cómo mantener esta documentación

El informe mantiene el estado actual. Los archivos 02 a 11 conservan fuentes, cálculos, criterios y decisiones; muchas de sus secciones son registros fechados de una entrega o propuesta, y sus cifras y pendientes corresponden a ese momento. Ante una diferencia, manda el informe y la entrega técnica fechada de la bitácora.

En cada entrega se actualizan las secciones afectadas del informe y del archivo temático correspondiente, sin crear un documento nuevo por función. En `src/docs/evidence` quedan capturas seleccionadas y resúmenes breves; no se guardan volcados completos ni registros extensos de pruebas. La preparación de instrumentos no se registra como sesiones ejecutadas, y las pruebas técnicas no equivalen a validación comercial o educativa.
