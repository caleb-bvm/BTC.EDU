# Identidad visual de BTC.EDU

## Definido por el usuario

Nombre: BTC.EDU. Referencias: Nothing Tech, Plan B Academy y diseño industrial. Colores: blancos, negros y tonos leves de naranja. El nombre no implica que el dominio esté registrado ni que la plataforma tenga acreditación educativa.

Esta dirección sustituye el uso de Micropayments como nombre visible del producto. Los documentos originales del assignment conservan su título. Durante la propuesta inicial la implementación visual estuvo pausada; la aprobación del 1 de octubre permitió construir la base actual.

**Actualización del 2 de octubre:** la pausa anterior corresponde a la propuesta inicial y ya fue superada por la aprobación registrada al final de este documento. La base visual está implementada. La [arquitectura y experiencia vigente](10-arquitectura-y-experiencia-btc-edu.md) define la organización de las nuevas pantallas; los valores efectivamente usados y fuentes están en [componentes visuales](../src/docs/componentes-visuales.md). Las propuestas de los apartados siguientes se conservan como antecedente, no como un segundo sistema de estilos.

## Propuesta para revisar

Una interfaz clara, de apariencia industrial, con fondo blanco cálido, texto negro, líneas finas, bloques ordenados y naranja reservado a detalles. Los siguientes valores son propuestas, no decisiones aprobadas:

| Uso | Color |
|---|---|
| Fondo principal | #FAFAF7 |
| Superficies | #FFFFFF |
| Texto y botones principales | #171717 |
| Texto secundario | #626262 |
| Bordes | #D8D8D2 |
| Detalle naranja | #E99555 |
| Fondo naranja suave | #FBEBDD |

Texto de botones naranja claro siempre oscuro; no usar naranja suave para texto pequeño sobre blanco. Verificar contraste en los diseños concretos antes de implementar.

Tipografía propuesta: sans serif legible para lectura y títulos; monoespaciada para precios, duraciones y etiquetas pequeñas. Una tipografía de puntos puede explorarse solo para el nombre o detalles de marca, nunca para párrafos ni instrucciones. Fuentes concretas y logotipo pendientes.

Componentes: botones sólidos negros, acciones secundarias con borde, tarjetas con poco redondeo, estados de selección discretos, formularios claros y foco visible. Iconos sencillos y consistentes. Evitar decoración que dificulte leer cursos o usar el reproductor.

## Qué tomamos de las referencias

- Nothing: explorar lettering de puntos, composición contenida y detalles visuales de producto. La inspección inicial mostró la identidad del encabezado y el aviso de cookies; falta revisar el resto de la página sin ese aviso antes de definir composiciones inspiradas en ella.
- Plan B Academy: se observó navegación lateral, filtros de tema/nivel/tipo/precio, tarjetas de curso y acentos naranja. Tomar esa claridad para organizar aprendizaje; definir un estilo propio para BTC.EDU.
- Diseño industrial: propuesta de retícula, líneas, numeración y etiquetas de apariencia técnica. El usuario todavía debe precisar cuánto protagonismo quiere darles.

Referencias consultadas el 1 de octubre de 2026: https://intl.nothing.tech/ y https://planb.academy/en/learn-anytime. No reutilizar sus logos, ilustraciones o fotografías sin permiso.

## Orden de trabajo

1. Revisar esta dirección visual, tipografía y tratamiento del nombre.
2. Preparar una lámina de estilo con colores, nombre, botones y tarjetas de ejemplo sin cursos reales.
3. Revisar la portada y la estructura vacía del catálogo en escritorio y móvil.
4. Implementar la base visual aprobada y documentar sus componentes en src.

No se cargan cursos, capítulos ni recursos durante esta etapa. No se ha creado todavía un logo ni una pantalla aprobada.

## Concepto aprobado el 1 de octubre de 2026

El usuario aprobó la imagen conceptual y autorizó comenzar la base técnica y visual en un nuevo chat. Referencia guardada en src/design/btc-edu-concepto-aprobado.png. Usar su composición, nombre de puntos, fondos claros, tipografía legible, tarjetas y objetos industriales con acentos naranja como guía. Los títulos y precios en la imagen son ejemplos; no cargar cursos todavía. La aprobación corresponde a la dirección visual, no a todas las funciones o textos de ejemplo.

