# Producto y especificaciones

El proyecto es una plataforma web de cursos, videos y materiales, con contenido gratis y de pago. Un curso gratuito puede ofrecer capítulos o materiales adicionales de pago. También se pueden comprar videos individuales y cursos completos. El catálogo inicial es ficticio y los precios son de prueba.

La [arquitectura de producto y experiencia](10-arquitectura-y-experiencia-btc-edu.md) es la referencia vigente de estructura: cursos, tutoriales y biblioteca de recursos en la primera academia funcional, eventos educativos después. Distingue lo implementado del diseño y organiza las ampliaciones por entregas.

## Documentos

- [Documento de BTC.EDU](19-recomendacion-y-entrega-final.md): texto completo para copiar a Google Docs y actualizar con cada entrega.
- [Monetización, precios y muestras](13-monetizacion-precios-y-muestras.md): comparación, fuentes, cálculos y límites.
- [Validación con usuarios](16-validacion-con-usuarios.md): guiones, tareas, precios y registro; ejecución pendiente.
- [Plan de documentación Business → Desarrollo (5 de octubre)](12-plan-documentacion-business-a-desarrollo.md): brechas, entregables, dependencias y condiciones de paso.
- [Producto y negocio](01-producto-y-negocio.md)
- [Catálogo de prueba](02-catalogo-de-prueba.md)
- [Reglas y criterios de aceptación](03-especificacion-funcional.md)
- [Pantallas y recorrido](04-pantallas-y-recorrido.md)
- [Métricas y validación](05-metricas-y-validacion.md)
- [Plan y decisiones](06-plan-y-decisiones.md)
- [Investigación y necesidades de alumnos y creadores](07-investigacion-y-necesidades.md)
- [Aprendizaje, creadores, comunidad y membresías](08-aprendizaje-creadores-y-membresias.md)
- [Identidad visual](09-identidad-visual.md)
- [Arquitectura y experiencia de BTC.EDU](10-arquitectura-y-experiencia-btc-edu.md)
- [Enfoque integral para creadores](11-enfoque-creadores.md)

## Qué exige el assignment y qué decidimos

El assignment exige plataforma con contenidos gratis y de pago, facturas simuladas, protección en el servidor, acceso persistente, administración, eventos, diseño adaptable y documentación técnica. Permite lecciones, videos y descargas; no obliga a desarrollar todas las funciones de una plataforma educativa.

El equipo eligió organizar el producto en cursos, capítulos, lecciones, videos y materiales con compras individuales y de cursos completos. El acceso comprado será permanente dentro del MVP, asociado a una cuenta con correo y contraseña. El creador aprobado prepara su contenido y el administrador revisa su publicación. Los contenidos parcialmente adquiridos se ofrecen por separado sin descuentos personalizados.

Al 4 de octubre de 2026, LNbits FakeWallet está integrado: ofertas y revisión, facturas, compra simulada, derechos permanentes sobre revisiones, biblioteca, inscripción y progreso funcionan en desarrollo. No hay fondos reales. Se verificaron vencimientos, pagos en conflicto, recuperación de respuesta perdida y actualizaciones simultáneas. Hay un comando de conciliación; su ejecución periódica supervisada queda pendiente. [Estado, 129 pruebas y evidencia](../src/docs/comercio-y-aprendizaje-2026-10-04.md).

Todo el código y la documentación técnica están en [src](../src/README.md). Esta carpeta conserva investigación, requisitos, prototipo y decisiones de Business. Los documentos originales del assignment permanecen en docs sin modificaciones.

## Pendientes

La comparación documental de modelos/tarifas/costos y los instrumentos de entrevistas/usabilidad/precios están preparados al 5 de octubre. Hay una recomendación provisional y un documento principal integrado. Siguen pendientes sesiones externas, precios validados, prototipos nuevos, presupuesto completo, recomendación final y enlace al Google Doc con historial. El usuario incorporará el texto manualmente. Revisar capacidad, equipo y fechas oficiales. No se añadieron funciones ni se modificaron precios por esta actualización.

## Alcance ampliado

Se incluyen progreso, evaluaciones, certificados, preguntas, comunidad, panel de creador y membresías con renovación simulada manual. Los detalles están en el documento 08 y el diseño técnico en src/docs/diseno-plataforma.md. Las funciones observadas en otras plataformas respaldan el diseño, pero todavía deben validarse con usuarios. El estudio de creadores y el progreso básico ya están implementados; evaluaciones, certificados, preguntas, comunidad y membresías siguen en la siguiente fase. La documentación de diseño no acredita funciones entregadas.

