# Enfoque integral para creadores

Definición del 3 de octubre de 2026. El proyecto se aborda como una plataforma completa. Este documento amplía el recorrido de creación de los documentos 08 y 10; define producto y orden de construcción, no funciones ya implementadas ni una fecha de entrega comprometida.

**Estado de implementación al 4 de octubre:** cuentas independientes, aprobación/perfil, estudio/editor/archivos, revisión, versiones, ofertas y compras simuladas, biblioteca, inscripción y progreso básico ya funcionan. 129 pruebas pasan. [Entrega y límites verificados](../src/docs/comercio-y-aprendizaje-2026-10-04.md). Evaluaciones, certificados, preguntas, comunidad, membresías y métricas completas permanecen pendientes; las secciones siguientes definen el horizonte del producto.

## Propósito

El creador es un docente y responsable de su oferta educativa. BTC.EDU debe permitirle preparar, publicar, mantener y comercializar contenido, acompañar a sus alumnos y mejorar a partir de resultados. El panel será su espacio de trabajo cotidiano, con identidad visual compartida con la academia y navegación propia.

Decisión confirmada el 3 de octubre: estudiante y creador tienen cuentas independientes, perfiles propios y entradas separadas. Una persona puede usar ambos espacios registrando una cuenta para cada uno; puede reutilizar correo, pero cada identidad conserva contraseña, permisos y datos propios. El registro de creador no transforma una cuenta de estudiante. La aprobación del perfil habilita herramientas; cada operación comprueba además propiedad y permiso en el servidor. La administración tiene su propio acceso.

## Recorrido completo

Solicitud y aprobación → configurar perfil → preparar contenidos y archivos → definir oferta y requisitos educativos → previsualizar y enviar a revisión → resolver observaciones → publicar → atender alumnos y comunidad → consultar resultados → preparar una nueva versión.

La incorporación explica responsabilidades, derechos de los materiales y proceso editorial. El perfil público presenta biografía, especialidad, enlaces y contenido publicado; el correo de la cuenta permanece privado. La solicitud muestra estado y observaciones.

## Espacio de trabajo

| Área | Responsabilidad |
|---|---|
| Inicio | Priorizar observaciones de revisión, preguntas pendientes, incidencias y contenido por terminar; resumen de actividad real |
| Contenido | Gestionar cursos, tutoriales y recursos; filtrar borradores, revisiones, publicaciones y archivados |
| Biblioteca de archivos | Cargar y reutilizar videos, materiales, subtítulos y transcripciones; mostrar validación, uso y límites de almacenamiento |
| Alumnos | Consultar inscripciones y avance de sus contenidos; revisar intentos y ofrecer acompañamiento con datos personales mínimos |
| Preguntas y comunidad | Responder por lección, gestionar espacios y moderar reportes con motivo e historial |
| Ventas y membresías | Configurar ofertas y planes; consultar compras confirmadas, periodos y volumen en sats de prueba |
| Estadísticas | Consultar alcance, inscripciones, avance, finalización, resultados y conversión con periodos y definiciones explícitas |
| Perfil y notificaciones | Mantener identidad pública y preferencias; recibir avisos de revisión, preguntas e incidencias |

Las áreas se habilitan cuando sus recorridos funcionan. El diseño contempla todas desde el principio; las pantallas entregadas muestran datos reales y acciones operativas.

## Editor educativo

El curso se organiza en Información, Temario, Materiales, Acceso y precios, Evaluaciones y certificado, Comunidad, y Revisión y versiones. El creador configura objetivos, público, requisitos, tema, nivel, portada, muestra y duración; ordena capítulos y lecciones; redacta texto y vincula recursos reutilizables.

El tutorial usa una variante centrada en resultado práctico y pasos. El recurso independiente tiene su propia ficha, procedencia, archivo o enlace y oferta. Se comparten componentes y revisiones para evitar duplicaciones y mantener consistencia entre publicaciones.

Los formularios conservan trabajo ante errores, muestran estado de guardado y advierten de cambios pendientes. Las cargas muestran progreso, resultado y reintento. La vista previa permite inspeccionar el recorrido de alumno y sus bloqueos mediante permisos expresos, sin generar compras ficticias ni alterar progreso.

El editor de evaluaciones define preguntas, respuestas, explicaciones, nota mínima, intentos y espera. El certificado se configura mediante requisitos explícitos de la versión del curso y es de finalización, sin afirmar acreditación oficial.

## Revisión y mantenimiento

Borrador → En revisión → Publicado o Cambios solicitados. Archivar retira el contenido del descubrimiento sin eliminar el acceso adquirido. El administrador revisa calidad, derechos, archivos, accesibilidad, coherencia educativa y condiciones de acceso; devuelve observaciones vinculadas al contenido y registra sus decisiones.

Enviar a revisión fija la composición a revisar. Las ediciones posteriores preparan un borrador distinto; aprobar publica exactamente la composición revisada. El creador puede retirar un envío pendiente para corregir y reenviar. Una publicación vigente permanece disponible mientras se revisa su sustituta.

Actualizar prepara otra versión. Se muestran diferencias, motivo del cambio y efecto para alumnos existentes antes de publicar. Compras, inscripciones, progreso, evaluaciones y certificados conservan sus referencias históricas. La concesión de una nueva versión a alumnos existentes debe ser explícita y no reemplaza silenciosamente sus registros anteriores.

Una retirada excepcional de acceso por contenido problemático requiere intervención administrativa, motivo, registro y explicación al afectado. Suspender a un creador no elimina automáticamente archivos, compras ni aprendizaje; la administración resuelve la continuidad del contenido.

## Comercio y relación con alumnos

El creador define contenido gratuito, muestras, ofertas individuales, paquetes y membresías conforme a las reglas comerciales vigentes. Antes de enviar a revisión ve lo incluido, lo excluido, precio en sats de prueba y duración del acceso. Cambiar precio afecta nuevas facturas; las pendientes conservan sus condiciones.

Las compras individuales son permanentes para la composición adquirida. Las membresías conceden acceso temporal y se renuevan manualmente con facturas simuladas de 30 días. Vencimiento conserva compras, progreso y certificados. El panel distingue ventas confirmadas, pendientes e incidencias; no presenta volumen simulado como ingreso real ni saldo disponible para retirar. Fondos reales y liquidaciones requerirán una definición comercial y operativa propia.

El acompañamiento reúne preguntas por lección, avisos, evaluaciones y comunidad. El creador solo consulta alumnos relacionados con sus contenidos y la información necesaria para acompañarlos. Las estadísticas agregadas separan inscripción, actividad, finalización y aprobación; una apertura o reproducción no demuestra aprendizaje. No se incluyen conversaciones privadas en esta definición.

## Orden de construcción

1. Diseñar navegación, pantallas y contratos para todo el estudio de creador, incluidos estados vacíos, errores, permisos y relación con academia y administración.
2. Implementar solicitud/aprobación, perfil, gestión de contenido, biblioteca de archivos, editor, vista previa y revisión sobre el versionado existente.
3. Integrar ofertas, facturas, permisos adquiridos, inscripciones y progreso para cerrar el recorrido creador → publicación → compra o inscripción → aprendizaje.
4. Integrar evaluaciones, certificados, preguntas, notificaciones, comunidad y moderación.
5. Integrar membresías y métricas completas; preparar operación pública con cuotas, respaldos/restauración, tratamiento de archivos huérfanos, incidencias y soporte.

Cada entrega debe cerrar un recorrido utilizable y verificar sus permisos. Este orden conserva el alcance completo; no reduce el producto a un panel de cargas ni compromete plazos sin revisar capacidad.

## Condiciones de aceptación

- Un creador aprobado prepara y envía contenido desde su espacio, sin depender de la administración de Django para editarlo.
- Ninguna ruta o carga permite consultar o modificar borradores, archivos, alumnos o ventas de otro creador.
- La publicación corresponde a la composición aprobada y las observaciones permiten corregir y reenviar.
- Una actualización no rompe contenido adquirido, progreso o certificados anteriores.
- Un creador puede comprobar qué puede ver un visitante, un inscrito, un comprador y un miembro, sin concederse derechos ajenos.
- Las métricas corresponden a registros verificables y las operaciones simuladas se identifican claramente.
- Los recorridos principales funcionan con teclado y en móvil; fallos de sesión, red y carga permiten recuperar el trabajo.
- La validación con creadores comprueba preparar una lección, organizar un curso, entender su oferta, resolver una revisión y responder a un alumno. Se registran dificultades reales.
