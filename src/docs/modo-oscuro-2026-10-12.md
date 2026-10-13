# Modo oscuro

## Comportamiento

La cabecera permite alternar entre modo claro y oscuro. La primera visita sigue la preferencia del sistema. La elección explícita se conserva en el navegador y se aplica antes de cargar las hojas de estilo. Se incorpora al sitio público, academia y cabeceras del espacio de creadores.

## Verificación realizada

El 12 de octubre de 2026 se comprobó en el navegador local la apariencia de inicio y catálogo, la alternancia claro/oscuro, la persistencia tras recargar y al navegar hacia cursos, y la cabecera del catálogo con un ancho de 390 píxeles. Se revisó visualmente el contraste del catálogo y sus filtros. Las cuatro plantillas de cabecera compilan. La revisión de Django no reporta errores; mantiene el aviso existente sobre email no único y autenticación personalizada.

## Límites y próximos pasos

La preferencia no se sincroniza con la cuenta. Si el navegador bloquea el almacenamiento, la elección funciona durante la página actual. Sin JavaScript se mantiene el tema claro. La administración de Django utiliza su propia apariencia. No se realizó una auditoría completa de accesibilidad ni una revisión visual de todos los recorridos autenticados. Revisar estos recorridos en la siguiente presentación y usar las variables de la paleta al agregar componentes.

Esta comprobación técnica no constituye validación educativa ni comercial con usuarios.
