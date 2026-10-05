# Cuentas independientes — 3 de octubre de 2026

El usuario confirmó cuentas independientes de creador y estudiante. Sustituye la propuesta anterior de una cuenta compartida con roles. Se conserva un sistema técnico de autenticación, con identidades diferentes y sin reutilizar datos de un perfil en el otro.

## Comportamiento

| Espacio | Registro | Entrada | Perfil | Recuperación |
|---|---|---|---|---|
| Estudiante | `/cuenta/registro/` | `/cuenta/entrar/` | `/cuenta/perfil/` | `/cuenta/recuperar/` |
| Creador | `/crear/registro/` | `/crear/entrar/` | `/crear/solicitud/` | `/crear/recuperar/` |
| Administración | Alta administrativa | `/admin/login/` | Administración | Gestionada por administración |

Cada registro crea otra fila de usuario y otro hash de contraseña. Es posible usar el mismo correo en espacios distintos; unicidad sin distinguir mayúsculas dentro de cada espacio. La autenticación usa correo + tipo de cuenta + contraseña y solo consulta la identidad del acceso elegido. Los formularios no aceptan el tipo de cuenta, permisos administrativos ni aprobación desde datos enviados por el usuario.

El creador nuevo entra a preparar su perfil y solicitud. Tener cuenta no concede aprobación. Pendientes y solicitudes con observaciones vuelven al perfil; aprobados llegan al estudio. Inactivos y suspendidos no pueden entrar como creadores. Una sesión de estudiante no habilita el estudio ni permite crear un perfil docente en esa identidad; una cuenta de creador no abre Mi aprendizaje o el perfil de estudiante.

El estudio tiene encabezado, menú y cierre de sesión propios. Cursos del catálogo, tutoriales, recursos y Mi aprendizaje no forman parte de su navegación de trabajo. Los enlaces hacia la academia o acceso de estudiantes son salidas explícitas. Para creadores se convierte en la entrada pública a registro/login, sin depender de la sesión de aprendizaje.

Los destinos de login se limitan al espacio correspondiente y rechazan enlaces externos. Cambiar de acceso autentica otra identidad y reemplaza la sesión de ese navegador. No hay dos sesiones simultáneas en una misma cookie del sitio; para usarlas simultáneamente, emplear navegadores o perfiles de navegador distintos. Cerrar sesión desde el endpoint de un espacio no termina una sesión de otro tipo. Las cuentas permanecen independientes aunque la persona elija la misma contraseña.

## Recuperación

Solicitud y correo separados por tipo de cuenta. Aunque el correo coincida, la recuperación de creador solo genera un enlace para esa identidad. Los enlaces incluyen el identificador de usuario y token de Django; vencen conforme a la configuración de Django y dejan de servir después de cambiar la contraseña. Un token de creador no se acepta en confirmación de estudiante.

La respuesta de solicitud no distingue correo inexistente. No se cambia la aprobación o suspensión al recuperar acceso. En desarrollo se usa el backend de correo local existente; antes de ofrecerlo públicamente es necesario configurar SMTP y verificar entrega real. No se enviaron correos reales en este bloque.

## Migración y conservación

`accounts.0002_remove_user_unique_email_case_insensitive_and_more` agrega tipo de cuenta, reemplaza unicidad global de correo por unicidad dentro del espacio y clasifica identidades anteriores: creadores con perfil/contenido propio no administrativos → creador; staff/superuser → administración; restantes → estudiante. Se preservan IDs, hashes, perfiles y vínculos a contenidos. Un administrador anterior con contenido conserva sus referencias y opera por administración; si también quiere un estudio de creador, debe tener su cuenta independiente y resolver explícitamente la propiedad del contenido.

La base real se respaldó mediante la API de SQLite antes de migrar. Cantidades antes/después de usuarios, cursos, capítulos, lecciones, videos, materiales, perfiles y envíos iguales: todas cero. No se añadieron cuentas reales ni ejemplos. Después de permitir correos iguales en distintos espacios, restaurar un esquema anterior requiere restaurar su respaldo o una migración específica; no revertir automáticamente a unicidad global sobre esas identidades.

## Verificación y límites

96 pruebas Django pasan: las 77 anteriores y 19 de cuentas/separación. Incluyen mismas direcciones con identidades distintas, credenciales cruzadas rechazadas, destinos de login, solicitudes pendientes/suspensión, permisos, CSRF, registro sin privilegios, edición independiente de perfil, recuperación por espacio, token cruzado/reutilizado, administración, cierre por espacio y preservación de datos de una base histórica. Migraciones consistentes y revisión estática pasan.

Django emite `auth.W004` porque el correo ya no es globalmente único. Es una advertencia esperada: el backend `AccountBackend` sustituye al backend estándar y consulta la combinación correo/tipo; los casos de duplicidad y autenticación por espacio están probados. No se silenció la advertencia.

Navegador: portada de creadores, login, registro, recuperación y estudio con navegación propia; revisión en escritorio/móvil de las pantallas inspeccionadas, sin desbordamiento global. [Login escritorio](evidence/login-creador-escritorio.jpg), [login móvil](evidence/login-creador-movil.jpg). Registro/contraseñas y entrega de correos se probaron con pruebas de integración; no se crearon credenciales mediante navegador ni se hizo una auditoría WCAG.

La vista temporal usa cookies propias para no interferir con el servidor de desarrollo real. `/para-creadores/` ya no inicia sesión automáticamente. La entrada rápida con `?vista=creador` o `?vista=revisor` existe solo en el script de demostración y únicamente cuando se pide explícitamente; las demás visitas permiten probar login/logout normales. Las cuentas iniciales de ejemplo no tienen contraseña utilizable.

Compras, progreso, evaluaciones, comunidad y membresías siguen pendientes. Verificación de correo al registrarse, límites de intentos/abuso y MFA quedan como trabajo de operación antes de abrir el sitio al público. Al cierre del 3 de octubre no hubo despliegue, commit ni push.

Actualización del 4 de octubre: implementación guardada en el commit `8792c98`, junto al estudio por sus dependencias de acceso. Se repitió la verificación completa: 96 pruebas, migraciones consistentes y revisión estática pasan. Documentación y capturas se guardan en un commit separado. No hubo despliegue ni push.
