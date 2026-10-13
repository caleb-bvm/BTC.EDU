# Cuentas, fotos y experiencia de servicio

## Entrega y contexto

Implementación del 12 de octubre de 2026, contexto de El Salvador y zona de aplicación `America/El_Salvador`. Código en `main`, base `4000ed5aba7bcd2c5b6074d0c5c9e7e383596e85` más cambios locales; documentación en `business/teorica`. No se cambió de rama ni se sustituyeron las mejoras concurrentes de aprendizaje, comunidad, navegación y apariencia. El código de cuentas se registró posteriormente en `71a19a4eee6a165ddc2ce89c7a2d2b63307cd916`; la documentación se consolida en `business/teorica`. La entrega sigue local, sin push ni despliegue.

El usuario pidió mejorar la experiencia de estudiantes y creadores e incorporar fotografías. Se conserva su decisión anterior: las cuentas son independientes, aunque utilicen el mismo correo. Compartir correo no comparte contraseña, compras, perfil, permisos ni recuperación. El diagnóstico previo se conserva como evidencia histórica en [la revisión inicial](../../strategy/22-usuarios-diagnostico-2026-10-12.md).

## Experiencia disponible

Cada espacio tiene Mi cuenta, con Resumen, Foto, Perfil, Acceso, Avisos y Ayuda. El perfil de estudiante incluye un objetivo privado de aprendizaje, presentación y vista previa. La fotografía aparece en la cabecera, fichas, directorio, autoría del contenido y conversaciones cuando el lector tiene permiso. Sin fotografía se muestran iniciales. Las pantallas se adaptan al menú móvil y utilizan los colores de la apariencia clara y oscura existente.

La foto es opcional. La ficha del estudiante empieza privada. Compartir explica expresamente que alias, foto, biografía, intereses y sitio web pueden verse sin sesión; correo, nombre de cuenta, compras, progreso, objetivo y notas permanecen privados. Ocultar la ficha no elimina los mensajes enviados. Perfil y certificado se comparten por separado. La foto de un estudiante privado puede aparecer a participantes autorizados de sus conversaciones; no se sirve a visitantes arbitrarios.

Cambiar de espacio exige autenticar la otra cuenta. Se explica que la sesión cambia también en las demás pestañas. Antes de guardar, los formularios consultan la identidad y actualizan la protección de envío. Si la sesión expiró o la cuenta cambió, conservan el texto y la selección de archivo en la página y muestran cómo volver a autenticar. El servidor comprueba el identificador de cuenta y los permisos; la protección no depende del botón visible.

El alumno puede guardar recursos y referencias publicados desde su ficha y encontrarlos en Mi aprendizaje. Guardar contenido gratuito o la ficha de un recurso de pago no compra ni concede acceso. El guardado conserva revisión, título y procedencia; una publicación retirada sin derechos adquiridos aparece no disponible. Un recurso adquirido mantiene acceso a su revisión histórica. Quitar el guardado no elimina la compra.

El estudio del creador reúne preguntas sin respuesta, revisiones con cambios y reportes pendientes del contenido propio. Ofrece un recorrido inicial entre borrador, comprobación/revisión y oferta tras publicación. Aprobación del creador, publicación editorial y aprobación comercial continúan siendo decisiones diferentes.

## Fotografías y privacidad

Se aceptan JPG, PNG y WebP estáticos, hasta 3 MB, mínimo 64 píxeles por lado y máximo 16 megapíxeles. Se valida el contenido real, no solo extensión o tipo declarado. Pillow aplica orientación, reconstruye los píxeles sin EXIF/GPS/comentarios, recorta con posición y acercamiento elegidos y genera WebP de 384 × 384 con nombre aleatorio. El archivo original no se publica.

La carpeta de almacenamiento es privada. La ruta de fotografía comprueba propietario, ficha pública o participación autorizada en cada solicitud. Responde sin caché y con `nosniff`; al sustituir o eliminar la foto, la URL anterior deja de funcionar. Una eliminación física aplazada por un lector de Windows no revierte el cambio confirmado. El mantenimiento retira archivos generados sin referencia y con antigüedad suficiente. No se puede borrar una copia que alguien ya descargó; la retirada controla el acceso posterior desde el servicio.

Fuentes de diseño: [OWASP, carga de archivos](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) y [Pillow, tratamiento de imágenes](https://pillow.readthedocs.io/en/stable/reference/Image.html). La implementación utiliza Pillow 12.3.0 declarado en las dependencias.

## Acceso y ciclo de cuenta

Acceso permite confirmar correo, cambiar contraseña, cambiar correo con contraseña actual y confirmación desde ambos buzones, consultar/cerrar sesiones, exportar datos propios y desactivar la cuenta. El cambio conserva el identificador y sus relaciones históricas. El nuevo correo solo sustituye al anterior cuando se completan ambas confirmaciones y se vuelve a comprobar su disponibilidad dentro del tipo de cuenta.

Los enlaces tienen propósito, cuenta, estado y vencimiento de 30 minutos. No se reutilizan después de su consumo o de un cambio incompatible de cuenta. Las solicitudes de recuperación se limitan al tipo correspondiente y excluyen cuentas administrativamente inactivas. La contraseña de una cuenta nunca modifica la otra. Los cambios sensibles utilizan escritura selectiva y vuelven a comprobar el estado después de reservar la operación; una petición de contraseña antigua no reactiva una cuenta recién desactivada.

El cambio de contraseña conserva la sesión propia y revoca las otras; cambiar correo revoca las sesiones de esa cuenta. La huella de autenticación incluye contraseña, correo, tipo y revisión de sesión. La actualización modifica esa huella, por lo que sesiones anteriores pueden requerir un nuevo acceso. El inventario de sesiones comienza con la actividad de esta implementación; no reconstruye navegadores históricos ni guarda IP o agente de usuario completo.

Desactivar exige contraseña y aceptación explícita. Oculta ficha y certificados compartidos, retira fotografía y cierra sesiones, conservando compras, progreso, publicaciones y decisiones. Reactivar exige enlace al buzón y contraseña nueva, preserva la identidad y no vuelve a compartir ficha/certificados ni restituye una foto eliminada. No revierte una desactivación administrativa ni aprueba un perfil de creador.

La exportación exige contraseña y devuelve información de la cuenta concreta. Excluye contraseñas, hashes, tokens, claves de sesión y datos de la identidad del otro espacio. Es un resumen del alcance documentado, no una exportación universal de todas las tablas.

Los límites temporales de acceso consideran propósito, correo/tipo y origen; los contadores almacenan claves HMAC. Registro, login, recuperación y solicitudes de correo tienen controles propios. No equivalen a un segundo factor, protección de red o prueba de carga. [Django, invalidación de sesiones](https://docs.djangoproject.com/en/5.2/topics/auth/default/#session-invalidation-on-password-change), [OWASP, autenticación](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).

## Solicitud y atención del creador

Pendientes y solicitudes con cambios pueden gestionar cuenta y consultar el siguiente paso. Una visita de lectura a herramientas aún bloqueadas vuelve a la solicitud; los envíos no autorizados siguen rechazados. Las decisiones tienen motivo cuando corresponde, responsable, fecha, revisión y aviso interno único. Una edición obsoleta no sobrescribe la revisión concurrente. El historial registra sucesos nuevos; no se inventaron decisiones anteriores.

Un creador suspendido puede entrar al área restringida para consultar el motivo, gestionar su acceso y solicitar revisión. No puede crear, editar ni publicar contenido. Ayuda conserva solicitudes propias y respuestas administrativas con permisos e historial. Enviar una apelación no levanta la suspensión automáticamente. Las cuentas inactivas no obtienen este acceso.

## Avisos y correo

La bandeja distingue servicio, preguntas y comunidad; permite filtrar pendientes y marcar como leídos los propios. Las preferencias afectan avisos nuevos de preguntas/comunidad. Decisiones de cuenta, revisión y moderación se conservan. Los títulos de preguntas y respuestas incorporan contexto del curso. No se configuraron correos generales para toda la actividad educativa.

El correo de acceso utiliza una cola persistente: solicitud, caducidad, intentos y resultado. Un fallo de transporte permite reintentar sin confirmar ficticiamente el envío. Los mensajes caducados o incompatibles con el estado se cancelan y el mantenimiento vacía cuerpos expirados. SMTP aceptado no demuestra entrega en bandeja ni lectura; una respuesta perdida del transporte puede producir un reenvío, por lo que no se promete envío exactamente una vez.

`DJANGO_EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL` y `DEFAULT_FROM_EMAIL` permiten configurar el proveedor. `manage.py deliver_account_mail --watch --interval 30` procesa reintentos; `manage.py prune_account_data` limpia fotos sin referencias y datos temporales vencidos. Deben instalarse como procesos/tareas supervisados antes de operación pública. No se ejecutó el trabajador contra buzones reales desde esta entrega ni se añadieron credenciales de un proveedor.

Con `DEBUG=False`, las fichas públicas, aprobación de creador y compra requieren correo confirmado. La confirmación comprueba control del buzón, no identidad legal o competencia docente. Los controles de despliegue avisan de una configuración incompleta. El entorno local mantiene su recorrido anterior; estos detalles permanecen en documentación y no se añaden como banners a la interfaz.

## Verificación realizada

La suite completa pasó 310 pruebas Django en 163,907 segundos. Después del ajuste para reservar la escritura antes de leer una confirmación simultánea se repitieron las 39 pruebas de servicio y guardados: pasaron en 1,868 segundos. El aviso deliberado de fallo de correo pertenece al escenario que simula una avería y comprueba el reintento. Ruff pasó, las migraciones no presentan cambios pendientes y los dos archivos JavaScript modificados pasaron la comprobación sintáctica.

Pasaron cinco controles con conexiones SQLite independientes: comercio, evaluaciones, certificados/preguntas, comunidad y cuentas. El nuevo control verifica confirmación única, revisión concurrente sin sobrescritura, rechazo de contraseña obsoleta tras desactivación y aislamiento de identidades con el mismo correo. Está incorporado en `scripts/check-platform.ps1`. No son mediciones de capacidad para tráfico público.

La migración principal tuvo respaldo en `.local/backups/accounts-before-20261013T045714Z.sqlite3`. Se compararon por huella todos los valores de 540 filas anteriores en 61 tablas y no hubo diferencias. Se excluyeron sesiones y registro operativo de migraciones. Las seis migraciones pendientes se aplicaron, sin cargar cuentas de ejemplo; otras migraciones del bloque ya estaban aplicadas por trabajo concurrente. El respaldo contiene datos privados y no se copia a la documentación pública.

Se recorrieron en Chrome las cuentas sintéticas de estudiante y creador, fotografía ya cargada, edición/guardado de alias, panel y solicitud del creador, suspensión con acceso a Ayuda y cambio de identidad entre pestañas con borrador conservado. Se revisaron apariencia clara/oscura y móvil, sin desbordamiento horizontal del documento. La captura móvil solicitó 390 × 844; con el zoom existente el navegador midió 300 píxeles CSS de ancho. Las imágenes de prueba son figuras abstractas, no personas reales.

La extensión de Chrome rechazó la selección automatizada de archivo porque no tiene permiso para URLs de archivos. No se cambió ese permiso. La carga, reemplazo, retirada, recorte, formatos inválidos, metadatos y privacidad se comprobaron por HTTP y servicios; no se acredita la selección completa de un archivo mediante ese navegador. La página muestra correctamente fotos servidas por la ruta protegida. No hubo sesiones externas, prueba integral con lector de pantalla, compra nueva contra ZEUS ni ensayo de SMTP real.

Pruebas, migración y huellas del código de esta entrega: [evidencias](../../strategy/evidencias/2026-10-12-entrega-cuentas.json), [suite completa](evidence/cuentas-pruebas-completas-2026-10-12.txt), [regresión posterior](evidence/cuentas-pruebas-finales-2026-10-12.txt).

## Próximos pasos

Configurar y verificar correo real, supervisar trabajador y mantenimiento, definir atención de solicitudes y ejecutar las tareas con estudiantes y creadores de [validación](../../strategy/16-validacion-con-usuarios.md). La revisión técnica no acredita comprensión de privacidad, mejora educativa, demanda ni disponibilidad operativa del equipo. Segundo factor administrativo, solución marcada en preguntas y apelaciones de moderación comunitaria conservan alcance pendiente propio.

El servidor de revisión temporal quedó detenido y sus pestañas se cerraron. La política automática de ejecución rechazó la eliminación de `.local/accounts-preview-mjh453li`, incluso con la ruta absoluta comprobada; no proporcionó otro motivo específico. La carpeta conserva únicamente los datos sintéticos de esa revisión y está excluida de Git. No se intentó eliminarla mediante otro mecanismo tras el rechazo.


## Registro del commit de cuentas

El 12 de octubre de 2026 se registró `71a19a4eee6a165ddc2ce89c7a2d2b63307cd916` en main, con 112 archivos. Se separaron catorce archivos compartidos sin modificar su contenido de trabajo. El commit incluye cuentas, fotos, perfiles necesarios, identidad pública, navegación contextual, avisos, guardados y sus pruebas. Las mejoras independientes de lectura, evaluaciones, comunidad en lecciones, catálogo y apariencia general permanecen como cambios locales.

Las nuevas migraciones de avisos y guardados del commit dependen del esquema ya versionado. Los archivos de trabajo conservan sus dependencias respecto de las otras entregas locales. Se conservaron las operaciones de esquema y la base principal no se modificó durante la preparación de commits. Este ajuste permite comprobar el commit por separado y mantiene la composición del trabajo en curso.

Una copia exacta del índice pasó 271 pruebas en 205,271 segundos, Ruff, consistencia de migraciones y los cinco controles de concurrencia. Después del commit se compararon sus 112 archivos con la copia probada y coincidieron sus objetos Git. La verificación anterior de 310 pruebas corresponde al conjunto de cambios locales, que incluye entregas independientes; las capturas corresponden a ese conjunto. No se presenta esa apariencia conjunta como una captura exclusiva del commit.

[Pruebas de la versión registrada](evidence/cuentas-commit-pruebas-2026-10-12.txt), [commit, árbol y alcance](../../strategy/evidencias/2026-10-12-commit-cuentas.json).


## Consolidación del trabajo pendiente

A petición del usuario se registraron posteriormente los 110 archivos pendientes del espacio principal en el commit `3045e7abd95a86d87c34396500dbc610161ed9b0` de main. Incluye las mejoras de catálogo, lectura, continuidad, comunidad en lecciones, evaluaciones, apariencia y documentación que habían quedado fuera de 71a19a4. Los registros anteriores conservan el alcance de sus verificaciones; el registro conjunto pasó revisión estática, comprobación de migraciones y formato sin repetir las pruebas ya ejecutadas. El espacio principal quedó sin cambios pendientes. La documentación restante se consolida en business/teorica; no hubo push ni despliegue.
