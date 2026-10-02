# Decisiones, configuración y seguridad

Python 3.12.14, Django 5.2.17 LTS y uv 0.12.21 verificados localmente. `uv.lock` fija dependencias y setup usa `sync --locked`. Django aporta sesiones, CSRF, administración, ORM y plantillas en una aplicación modular. HTMX 2.0.8 actualiza el bloque del catálogo. Bootstrap 5.3.8 aporta retícula, botones y formularios; site.css define el diseño propio. Distribuciones locales en static/vendor, sin consultas a CDN durante las visitas; se conservan sus avisos de licencia.

## Configuración actual: SQLite

Decisión vigente del usuario, 1 de octubre de 2026: SQLite para esta etapa local. Archivo `src/.local/platform.sqlite3`, timeout de espera de escritura de 20 segundos. No requiere servidor ni credenciales. Se retiraron mysqlclient, variables MYSQL y comprobaciones MySQL de los scripts. No se usa PostgreSQL.

Las variables activas de la plataforma son DJANGO_DEBUG, DJANGO_SECRET_KEY y DJANGO_ALLOWED_HOSTS. Setup conserva `.env` y la base existente; aplica migraciones sin cargar contenidos. La base y los respaldos permanecen ignorados en Git. LNbits sigue separado, con FakeWallet y sus propios datos.

SQLite permite comprobar persistencia, restricciones y recorridos locales. Sus escrituras se serializan y select_for_update no ofrece bloqueo de filas equivalente a un servidor relacional. El timeout no garantiza escalabilidad ni resuelve carreras de compra. La concurrencia comercial sigue pendiente porque no hay comercio implementado; diseñar y probar explícitamente esos escenarios antes de ampliar el uso.

## Seguridad actual y límites

Usuario por correo con migración inicial anterior a admin; manager normaliza correos al crear cuentas y restricción Lower(email) evita duplicados por mayúsculas. Hash y validadores de contraseñas Django. Espacio privado exige sesión; admin exige staff. LoginView rechaza redirecciones externas. Logout solo POST con CSRF.

CSRF, validación de hosts, escape HTML, cookies de sesión HttpOnly, protección contra frames y detección de tipos habilitados. No hay ruta pública MEDIA ni archivos de pago. Health consulta la base y devuelve solo ok/unavailable. Recuperación de contraseña, registro, límites de intentos de login y roles de creador todavía no existen.

Servidor ligado a 127.0.0.1; DEBUG true solo para revisar localmente. Check de despliegue local informó cinco avisos: DEBUG, HTTPS, cookies Secure de sesión y CSRF, y HSTS sin configurar. Fuera de DEBUG se activan redirección HTTPS y cookies Secure. Antes de publicación definir/probar certificado, proxy, HSTS, correo, rate limiting, copias de seguridad y observabilidad. Runserver y esta configuración local no son una entrega de producción.

## Contratos implementados

| Método y ruta | Resultado |
|---|---|
| GET / | Portada pública |
| GET /explorar/?tipo=todos,cursos,videos,materiales | Catálogo vacío; valor inválido vuelve a todos |
| GET /explorar/ con HX-Request: true | Fragmento HTML de filtros y catálogo |
| GET /para-creadores/ | Información; herramientas pendientes |
| GET, POST /cuenta/entrar/ | Login por correo; POST exige CSRF |
| POST /cuenta/salir/ | Logout con CSRF; GET devuelve 405 |
| GET /mi-espacio/ | Privado; visitante redirigido a login |
| /admin/ | Administración de cuentas, exige staff |
| GET /health/ | JSON 200 status ok; fallo de base 503 status unavailable |

No hay API de cursos, compras o facturas. Los contratos en diseno-plataforma.md siguen siendo propuestas.

## Evolución real del 1 de octubre

Se completó instalación, migración de cuentas, interfaz y pruebas. Durante preparación se aplicó admin antes de existir accounts. Se verificó ausencia de cuentas, grupos, registros admin y sesiones; se conservó la base vacía anterior en `.local/platform-before-account-migration.sqlite3` y se migró una nueva base correctamente. Los datos de LNbits se preservaron. No se inventó ni reescribió historial GitHub.
