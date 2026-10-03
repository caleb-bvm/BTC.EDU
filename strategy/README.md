# Producto y especificaciones

El proyecto es una plataforma web de cursos, videos y materiales, con contenido gratis y de pago. Un curso gratuito puede ofrecer capítulos o materiales adicionales de pago. También se pueden comprar videos individuales y cursos completos. El catálogo inicial es ficticio y los precios son de prueba.

La [arquitectura de producto y experiencia](10-arquitectura-y-experiencia-btc-edu.md) es la referencia vigente de estructura: cursos, tutoriales y biblioteca de recursos en la primera academia funcional, eventos educativos después. Distingue lo implementado del diseño y organiza las ampliaciones por entregas.

## Documentos

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

## Qué exige el assignment y qué decidimos

El assignment exige plataforma con contenidos gratis y de pago, facturas simuladas, protección en el servidor, acceso persistente, administración, eventos, diseño adaptable y documentación técnica. Permite lecciones, videos y descargas; no obliga a desarrollar todas las funciones de una plataforma educativa.

El equipo eligió organizar el producto en cursos, capítulos, lecciones, videos y materiales con compras individuales y de cursos completos. El acceso comprado será permanente dentro del MVP, asociado a una cuenta con correo y contraseña. El creador aprobado prepara su contenido y el administrador revisa su publicación. Los contenidos parcialmente adquiridos se ofrecen por separado sin descuentos personalizados.

LNbits con FakeWallet será el servicio de pagos de prueba. No hay fondos reales. La conexión básica ya se probó; el sitio tiene catálogo, curso y lectura protegida, pero todavía faltan compras y permisos persistentes. El simulador de fallos y vencimientos, la recuperación de pendientes y las reglas de compra requieren trabajo adicional.

Todo el código y la documentación técnica están en [src](../src/README.md). Esta carpeta conserva investigación, requisitos, prototipo y decisiones de Business. Los documentos originales del assignment permanecen en docs sin modificaciones.

## Pendientes

Prototipos de las nuevas pantallas, entrevistas, validación, recomendación, estimación de recursos y Google Doc con historial. Hay investigación con fuentes y una dirección visual aprobada; faltan pruebas de esa propuesta con usuarios. También revisar calendario ante el alcance actualizado y aclarar composición del equipo y fecha oficial de entrega.

## Alcance ampliado

Se incluyen progreso, evaluaciones, certificados, preguntas, comunidad, panel de creador y membresías con renovación simulada manual. Los detalles están en el documento 08 y el diseño técnico en src/docs/diseno-plataforma.md. Las funciones observadas en otras plataformas respaldan el diseño, pero todavía deben validarse con usuarios. No están implementadas por estar documentadas.

