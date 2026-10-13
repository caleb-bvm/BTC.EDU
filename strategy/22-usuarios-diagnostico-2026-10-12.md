> Diagnóstico histórico previo a la implementación de esta entrega. Sus pendientes describen ese momento; consultar el informe actual para funciones disponibles.

# Cuentas de estudiantes y creadores

## Alcance

Revisión del 12 de octubre de 2026, contexto de El Salvador. Se analizó el desarrollo en `main`, base `4000ed5` más los cambios locales existentes. La documentación se mantiene en el worktree de `business/teorica`. No se cambió de rama ni se sustituyeron trabajos anteriores. Los nombres de archivos de código siguientes se refieren al desarrollo en `main`, no al código anterior de la rama documental.

Se revisaron modelos, formularios, autenticación, recuperación, autorización, plantillas, pruebas, aprendizaje, compras, solicitudes, avisos y los dos originales de CUBO+. Se hicieron veinte comprobaciones mediante el cliente HTTP de Django sobre SQLite temporal con cuentas sintéticas. La revisión no modificó la base principal ni envió correos; las entrevistas y una revisión visual nueva del navegador quedan fuera de esta evidencia. Las conclusiones de experiencia son hipótesis de diseño apoyadas en comportamientos comprobados.

El [análisis integral anterior](20-analisis-integral-plataforma-educativa.md) conserva su diagnóstico histórico. El registro con retorno seguro y la identidad pública coherente ya están corregidos en el código observado; no se presentan nuevamente como problemas pendientes. El [plan integral](21-mejoras-integrales-btc-edu.md) conserva las otras entregas y sus evidencias.

## Cómo funciona actualmente

### Identidad y sesión

Estudiante, creador y administración son cuentas distintas. El correo se normaliza y es único dentro de cada tipo; puede repetirse entre ellos. Cada cuenta tiene su contraseña, identificador, recuperación y datos. El backend autentica por correo y tipo de cuenta. El registro público no permite elegir privilegios administrativos ni aprobarse como creador.

Esta separación responde a una decisión explícita del proyecto. No conviene sustituirla por una cuenta compartida con roles sin una nueva decisión. Tampoco debe vincularse automáticamente a dos identidades por compartir correo, alias, contraseña o wallet.

El sitio mantiene una identidad activa por sesión de navegador. Entrar como creador reemplaza la sesión de estudiante, y viceversa; las otras pestañas del mismo sitio utilizan esa sesión. Los datos de ambas cuentas permanecen separados. Para sesiones simultáneas se necesitan perfiles o navegadores distintos. Cambiar de espacio es una nueva autenticación, no una conversión de cuenta.

Evidencia: `accounts.models.User`, `accounts.backends.AccountBackend`, `accounts.forms`, `accounts.views`, `accounts.recovery` y `accounts.tests`. La advertencia `auth.W004` responde a que el correo no es único por sí solo; la restricción correo/tipo y el backend específico conservan el aislamiento. No es evidencia de que una contraseña abra ambas cuentas.

### Estudiante

Puede explorar el catálogo y consultar contenido gratuito antes de registrarse. El formulario de alta solicita correo, nombre y contraseña confirmada; el apellido es opcional. El registro devuelve a un destino de aprendizaje permitido cuando venía de una oferta, búsqueda o lección. El inicio de sesión conduce por defecto a Mi aprendizaje.

El estudiante se inscribe en una versión del curso, guarda su punto de continuación y marca lecciones accesibles. Las evaluaciones obligatorias requieren aprobación antes de completar la lección. Comprar concede derechos sobre revisiones específicas; inscribirse no compra. Mi aprendizaje reúne cursos inscritos y videos/materiales adquiridos. Las preguntas privadas, la comunidad, las evaluaciones y los certificados tienen reglas propias de acceso y conservación.

El perfil comienza privado. El alumno puede utilizar un alias, presentación, intereses y sitio web; el nombre de cuenta y correo no se publican. Compartir requiere un alias. El directorio Personas exige sesión, pero una ficha compartida puede abrirse sin iniciar sesión mediante su URL. Ocultarla vuelve a bloquear ese acceso. El alias puede seguir apareciendo en mensajes de comunidades autorizadas aunque la ficha sea privada. Compartir el perfil no comparte el certificado, las compras o las notas.

Evidencia: `accounts.views.student_profile`, `member_profile`, `members`, `accounts.test_profiles`, `accounts.test_destinations`, `learning.services`, `learning.views` y `commerce.services`.

### Creador

Primero crea una cuenta independiente. Después prepara nombre público, biografía, especialidad y sitio web opcional, y acepta el compromiso de autoría o autorización. La administración decide sobre la solicitud. Una cuenta nueva no tiene herramientas de publicación habilitadas.

Las solicitudes pendientes o con cambios solicitados vuelven a `/crear/solicitud/` después del login. Un creador aprobado entra al estudio y administra contenido propio, archivos, versiones, evaluaciones, certificados, ofertas, preguntas, comunidad y estadísticas. La aprobación de la persona, la publicación del contenido y la aprobación de la oferta son decisiones diferentes. Aprobar un curso no significa que su oferta ya esté disponible.

Los envíos editoriales conservan una composición y una decisión. Los borradores posteriores no sustituyen automáticamente la publicación ni el contenido adquirido. Los paneles comerciales describen compras simuladas y volumen observado; no acreditan ingresos reales, reparto ni liquidaciones al creador.

La suspensión del perfil de creador bloquea un nuevo inicio de sesión. Con una sesión anterior, la página de solicitud puede mostrar observaciones con respuesta HTTP 403. En un login nuevo se muestra un error genérico de credenciales y no el motivo. La suspensión comunitaria de escritura es otra medida: conserva lectura, compras y progreso del participante según las reglas existentes.

Evidencia: `creators.models.CreatorProfile`, `creators.views.application`, `creator_required`, `creators.services`, `creators.admin`, `accounts.forms.CreatorLoginForm` y las plantillas del estudio.

## Debilidades verificadas

### Gestión de cuenta incompleta

Los formularios permiten editar perfiles, pero no ofrecen un recorrido propio para cambiar contraseña, cambiar correo de forma confirmada, consultar sesiones o solicitar cierre de cuenta. Existe recuperación por token y tipo de cuenta; no existe un campo o recorrido de verificación inicial del correo. En desarrollo el backend de correo usa consola; esta revisión no acredita entrega real a un buzón ni configuración operativa de correo.

No se encontraron límites específicos de frecuencia para login, registro o recuperación en el backend, formularios y rutas revisados. Los límites de mensajes y comunidad no protegen estos accesos. Es una brecha antes de abrir el servicio al público, no una prueba de que se haya producido un ataque.

### Solicitud con poca continuidad

Un pendiente que abre directamente una ruta del estudio recibe 403 aunque pueda consultar su solicitud. La protección es correcta, pero falta una salida clara. La decisión administrativa de aprobar o pedir cambios guarda responsable y fecha; el guardado de `CreatorProfileAdmin` no genera un aviso interno. Se comprobó una aprobación y la cuenta conservó cero notificaciones. Las decisiones sobre contenido sí cuentan con avisos y no deben confundirse con las decisiones sobre la solicitud de creador.

El perfil conserva los campos de la última revisión y Django dispone de su registro administrativo genérico. Falta una cronología específica de solicitud, decisión, reenvío y apelación disponible para el creador. No se afirma que la administración carezca de cualquier registro.

### Privacidad y cambio de espacio poco explícitos

La ayuda de «Compartir mi perfil» explica los campos privados y la presencia en Personas, pero no dice expresamente que la ficha podrá verla alguien sin cuenta. El comportamiento no filtra información privada; el problema identificado es explicar el alcance de la elección. La comprensión real de este texto todavía debe probarse con participantes.

Los accesos permiten ir al otro espacio, pero no anticipan claramente que la identidad activa cambiará también en las demás pestañas. Esta fricción es especialmente relevante cuando alguien aprende y enseña, o conserva un formulario abierto.

### Herramientas que requieren más orientación

Mi aprendizaje muestra cursos y recursos adquiridos, pero todavía no es una biblioteca completa de materiales gratuitos guardados. El estudio reparte contenido, archivos, ofertas, preguntas y solicitudes entre secciones. El siguiente paso depende de reconocer varias aprobaciones y requisitos. Estas brechas coinciden con MI-05, MI-06 y MI-16 del plan integral; no requieren construir una segunda biblioteca o bandeja.

## Servicio propuesto

### Una cuenta que se pueda gestionar

Añadir una entrada «Mi cuenta» en cada espacio, con apartados breves para acceso, perfil, privacidad y avisos. El estudiante conserva su formulario de presentación y el creador su identidad docente; los datos no se sincronizan entre cuentas. La pantalla debe explicar qué cuenta está activa y cuál se está modificando.

La primera entrega puede permitir cambiar contraseña con la actual, confirmar que el cambio pertenece a esa cuenta y ofrecer una salida clara al terminar. Django ya dispone de vistas que conservan la sesión propia e invalidan las anteriores cuando cambia la contraseña. Debe mantenerse el alcance por tipo de cuenta. [Django: cambio de contraseña y sesiones](https://docs.djangoproject.com/en/5.2/topics/auth/default/#session-invalidation-on-password-change).

El cambio de correo requiere confirmación y controles propios, preservando el identificador de la cuenta, compras y progreso. La recuperación sin acceso al correo necesita un procedimiento humano definido; conocer un alias, una factura o un pago no debe bastar para transferir una cuenta.

### Estados de creador que indiquen qué hacer

Presentar una secuencia comprensible: preparar perfil, solicitud enviada, cambios solicitados y aprobado. Cada estado debe mostrar la siguiente acción, las observaciones pertinentes y cuándo se tomó la última decisión. El tiempo de respuesta solo se mostrará si hay capacidad real de cumplirlo.

Generar una notificación interna por cada decisión efectiva, después de confirmar la transacción, con clave que evite duplicados. Conservar eventos propios de solicitud y revisión, además de los campos actuales y del registro administrativo. Abrir un aviso nunca sustituye la comprobación de autorización.

Permitir que el creador con perfil suspendido y credenciales válidas consulte un espacio restringido de estado y atención. No debe poder editar, enviar, vender o moderar. La autenticación debe seguir rechazando credenciales incorrectas con un mensaje genérico. Una cuenta desactivada por seguridad mantiene un tratamiento diferente. La lista de rutas permitidas debe ser explícita y comprobarse también sobre sesiones anteriores.

Redirigir las entradas de lectura del estudio de un creador pendiente a su solicitud, con una explicación útil. Las operaciones de escritura siguen denegadas en el servidor. Una apelación necesita motivo, seguimiento, responsable real e historial; no reabre automáticamente la cuenta ni revierte una decisión.

### Privacidad que se entienda antes de compartir

Mantener el perfil privado por defecto y el alias como identidad comunitaria. En el control de compartición explicar: «Tu alias, presentación, intereses y sitio web podrán verse sin iniciar sesión. Tu correo, compras, progreso y notas siguen privados». Ofrecer una vista previa antes de guardar y un enlace claro para ocultarlo.

Desactivar compartir debe retirar la ficha del directorio y bloquear las siguientes consultas públicas, como ya ocurre. Hay que explicar que esta acción no elimina los mensajes enviados ni controla copias que otras personas hayan conservado. Perfil y certificado continúan con decisiones de compartición independientes.

No añadir fotografía, reputación o seguimiento de personas solo para dar una apariencia social. Son ampliaciones que necesitan utilidad, moderación y mantenimiento propios.

### Cambiar de espacio con contexto

Mostrar «Entrar como estudiante» o «Entrar como creador» junto al espacio activo. Antes de autenticar la otra cuenta, explicar que se reemplazará la sesión de este navegador. El formulario sigue pidiendo las credenciales del destino; no reutiliza la autenticación por coincidencia de correo.

Conservar destinos seguros dentro del espacio correspondiente. La protección de formularios y el aviso de cambios pendientes deben impedir que un cambio de cuenta provoque pérdidas o guardados con una identidad inesperada. Los datos de formularios no se transfieren entre identidades.

### Orientar al estudiante y al creador

El estudiante debería llegar a una acción principal: continuar una lección pendiente y accesible o encontrar su primer contenido. Puede indicar opcionalmente un objetivo, tema o nivel; esos datos orientan filtros explícitos antes de plantear recomendaciones automáticas. El alias y la biografía pueden completarse cuando quiera participar. La posibilidad de reducir campos del registro es una hipótesis para probar, no un cambio ya aprobado o una mejora de conversión medida.

La biblioteca debe integrar las entregas MI-05 y MI-06: continuación consistente, guardados gratuitos y adquiridos, búsqueda y estados claros. Guardar no compra ni modifica permisos; retirar un guardado no elimina una compra. Las preguntas privadas y la comunidad deben explicar cuándo cada vía es adecuada y ofrecer regreso al contenido.

El creador necesita una ruta de primera publicación y una bandeja diaria. Para publicar, comprobar objetivo, requisitos, lecciones, muestra, archivos, derechos, accesibilidad, evaluación y oferta, según el formato. Cada falta debe llevar al lugar donde se resuelve. Thinkific documenta comprobaciones de contenido y vista previa como estudiante antes de publicar; sirve como referencia funcional, sin importar sus cobros o su modelo de cuentas. [Thinkific: preparación de la publicación](https://support.thinkific.com/hc/en-us/articles/4640230640663-Checklist-Before-Publishing).

La bandeja reúne preguntas pendientes, decisiones que requieren cambios, reportes e incidencias del contenido propio. Los indicadores deben llevar a una tarea y respetar preguntas privadas y permisos. La prioridad educativa es que exista alguien responsable de responder, también en cursos institucionales publicados con una cuenta técnica. No debe prometerse atención por tener un buzón disponible.

### Acceso y avisos preparados para operar

Antes de publicar el servicio, comprobar correo real, verificación por cuenta, límites de solicitudes y recuperación. Los tokens deben tener propósito y vencimiento, identificar la cuenta concreta e impedir reutilización. La confirmación de correo acredita control del buzón; no certifica identidad real o competencia docente.

Aplicar límites de acceso que consideren la cuenta y su tipo, además del origen de las solicitudes, con esperas recuperables y sin bloqueo permanente provocado por terceros. Exigir autenticación reciente para cambios sensibles y priorizar un segundo factor en administración. Estas decisiones se apoyan en OWASP; Django advierte que su backend básico no incorpora límites de intentos. [OWASP: autenticación](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [Django: backends](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#specifying-authentication-backends).

Permitir gestores de contraseñas, autocompletado y pegado, con etiquetas, errores asociados y controles operables por teclado. Los formularios actuales ya declaran autocompletado en login; falta una comprobación completa de accesibilidad del recorrido. WCAG 2.2 contempla mecanismos que reduzcan el esfuerzo de recordar o transcribir credenciales. [W3C: autenticación accesible](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html).

Separar avisos necesarios de cuenta/compra de seguimiento opcional de conversaciones. Diseñar preferencias por cuenta, sin presentar un canal de correo como activo antes de verificar entrega y capacidad operativa. Solicitar exportación o cierre requiere reglas de conservación de compras, certificados y moderación; las relaciones protegidas del modelo impiden tratarlo como un borrado simple.

## Orden recomendado

| Entrega | Prioridad | Resultado que debe poder comprobarse |
|---|---|---|
| US-01: gestión y privacidad | Próximo bloque de cuentas | Cambiar contraseña de una identidad sin alterar la otra; reconocer cuenta activa; comprender y retirar el acceso público al perfil. |
| US-02: solicitud y atención de creador | Mismo recorrido, entrega separable | Decisión con aviso único, estados con siguiente acción, pendiente orientado y suspendido restringido con acceso al motivo. |
| US-03: continuidad entre espacios | Después de US-01/02 | Autenticar otro espacio de forma explícita, preservar destinos permitidos y detectar formularios pendientes. |
| US-04: correo y protección de acceso | Obligatorio antes de operación pública | Verificación y recuperación llegan al buzón correcto; tokens vencidos/reutilizados/cruzados rechazados; límites de solicitudes comprobados. |
| US-05: aprendizaje y primera publicación | Integrar con MI-05/06/07/16 | El alumno conserva y retoma; el creador entiende qué falta para publicar y qué necesita atención. |
| US-06: preferencias y ciclo de cuenta | Después de cerrar los recorridos anteriores | Avisos elegibles, exportación/cierre con reglas explícitas y evidencias históricas conservadas. |

El orden es una recomendación de desarrollo, sin estimaciones inventadas de horas o impacto. US-04 condiciona la apertura pública aunque otros cambios de experiencia se trabajen antes en el entorno local. Un responsable de revisión y atención es una dependencia humana, no una función que el software pueda reemplazar.

## Comprobación y validación

Las pruebas de autorización deben conservar cuentas con el mismo correo, contraseñas distintas, intentos de cambiar el tipo, recuperación cruzada, sesiones anteriores y solicitudes simultáneas. Compartir/ocultar debe comprobarse con visitante, propietario, otra cuenta y creador suspendido. Los permisos sobre cursos, compras y progreso tienen que conservarse tras cambios de contraseña o correo.

Para una decisión de solicitud hay que verificar estados anteriores, permisos del revisor, motivo cuando corresponda, evento y aviso únicos, reenvío y suspensión concurrente. El espacio restringido se prueba con GET y POST y con cada ruta del estudio; una interfaz sin botones no basta para protegerlo.

Con participantes, observar creación y regreso al contenido, comprensión de privacidad, cambio de espacio, recuperación, solicitud con observaciones y primera publicación. Registrar versión, ayuda, errores y explicación de lo ocurrido. Los instrumentos se amplían en [Validación con usuarios](16-validacion-con-usuarios.md); siguen pendientes de ejecución.

Proponer métricas nuevas solo con eventos disponibles: registro completado por tipo, primera inscripción y apertura accesible, primera lección completada, primera solicitud y publicación, respuesta a preguntas y correcciones pendientes. Registrar fuente, ventana y denominador; separar cuenta, sesión y persona. La cantidad de usuarios de ambos espacios no debe sumarse como cantidad de personas únicas. La finalización declarada no acredita aprendizaje.

## Evidencia y límites

Las [veinte comprobaciones](evidencias/2026-10-12-comprobaciones-usuarios.json) confirmaron separación de identidades, sustitución de sesión, privacidad por defecto y acceso anónimo a la ficha compartida; también falta de aviso de aprobación, bloqueo del nuevo login suspendido y conservación del destino en el registro. Son comprobaciones HTTP y de servicios con datos temporales.

Durante la regresión relacionada se encontró una prueba de conciliación que asumía el orden de creación de facturas. Con fechas iguales el lote se ordena por UUID y las respuestas ficticias de una lista pueden asignarse a otra factura. Una reproducción controlada falló antes del ajuste y pasó después. Se ajustó únicamente la fecha de la factura inválida en el escenario de prueba para asegurar que se procesa primero; la lógica comercial no cambió. Treinta repeticiones naturales anteriores no reprodujeron el fallo. No se registraron las fechas del primer fallo, por lo que la reproducción demuestra la dependencia del orden, sin atribuirle valores que no se observaron. [Evidencia del escenario](evidencias/2026-10-12-orden-prueba-conciliacion.json).

La ejecución final pasó 169 pruebas de cuentas, creadores, aprendizaje y comercio en 129,101 segundos. Ruff en cuentas, creadores, aprendizaje y el archivo de prueba modificado pasó; la comprobación de migraciones no detectó cambios. La advertencia `auth.W004` conserva el significado explicado anteriormente. No se ejecutó nuevamente la suite completa de 238 pruebas ni los controles de concurrencia de otras entregas. La salida se conserva en [regresión relacionada](evidencias/2026-10-12-pruebas-usuarios.txt). No constituye una nueva compra contra LNbits, prueba de carga, validación comercial o revisión completa de accesibilidad. La propuesta de servicio todavía requiere implementación; esta entrega es diagnóstico, diseño y corrección de una prueba existente.

## Registro de trabajo

El 12 de octubre de 2026 se revisó el desarrollo local sobre `4000ed5`, se consultaron fuentes primarias y los documentos originales de CUBO+, se ejecutaron comprobaciones con base temporal y se corrigió el orden del escenario de una prueba de conciliación en `main`. Se actualizaron el informe principal, su texto plano, los instrumentos y el plan en `business/teorica`. No se realizaron commit, push, despliegue, cambios de cuentas reales ni contactos con participantes desde este trabajo.
