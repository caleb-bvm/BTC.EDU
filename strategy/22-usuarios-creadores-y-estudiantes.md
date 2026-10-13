# Cuentas de estudiantes y creadores

## Estado actual

El usuario autorizó implementar las mejoras e incorporar fotografías el 12 de octubre de 2026. Se conservaron las cuentas independientes y la estética del proyecto, con código en main sobre 4000ed5 y cambios locales; documentación en business/teorica. Se conservaron las ramas y los trabajos concurrentes. El código de cuentas quedó registrado posteriormente en `71a19a4eee6a165ddc2ce89c7a2d2b63307cd916`. La documentación se consolida en business/teorica; la entrega sigue local, sin push ni despliegue.

Mi cuenta reúne foto, presentación, acceso, avisos y ayuda. Estudiantes y creadores gestionan su identidad concreta; compartir correo no vincula datos ni autenticación. Cambiar de espacio reemplaza la sesión de navegador, exige credenciales del destino y detecta formularios de otra identidad antes de guardar. La revisión visual confirmó conservación del borrador tras ese cambio.

La fotografía opcional tiene posición y acercamiento de recorte, validación real de formato/tamaño, normalización a WebP y eliminación de metadatos. Se sirve desde almacenamiento privado con controles de acceso. La ficha del estudiante empieza privada y explica el alcance anónimo de compartirla. Objetivo de aprendizaje, correo, compras y notas permanecen privados. La foto puede identificar mensajes en conversaciones autorizadas sin publicar la ficha.

Acceso permite contraseña, verificación, cambio de correo confirmado desde ambos buzones, sesiones, exportación y desactivación/reactivación con conservación de la identidad y registros. Desactivar retira fotografía y compartición pública de certificados, sin borrar compras o historial. Reactivar no revierte una desactivación administrativa ni una suspensión de creador.

La solicitud del creador conserva estados, siguiente acción, motivo, responsable, fecha, revisión e historial de eventos nuevos. Cada decisión genera un aviso único. El suspendido puede autenticar un área restringida y solicitar revisión; las herramientas de creación/publicación continúan bloqueadas. Ayuda conserva solicitudes y respuestas de administración con permisos e historial.

El estudiante guarda recursos gratuitos, fichas de recursos de pago y referencias publicadas en Mi aprendizaje. Guardar no compra ni concede derechos; conserva revisión/procedencia y no elimina compras al retirarse. El creador cuenta con tareas de preguntas, cambios editoriales y reportes propios, además de la orientación de primera publicación.

Los avisos internos se filtran por servicio, preguntas, comunidad y pendientes. Las preferencias afectan actividad nueva opcional; las decisiones necesarias se mantienen. El correo de acceso tiene cola persistente, vencimiento, invalidación y reintentos. No se verificó entrega a un buzón real ni se configuró un proveedor externo.

## Trabajo y aceptación

| Entrega | Estado comprobado | Dependencia pendiente |
|---|---|---|
| US-01: gestión y privacidad | Implementada, con foto opcional, perfil privado y cambio de contraseña propio | Comprensión con participantes y auditoría completa de accesibilidad |
| US-02: solicitud y atención de creador | Historial, aviso, estados, suspensión restringida y solicitud de revisión | Responsable real de atención y tiempos de respuesta |
| US-03: continuidad entre espacios | Credenciales independientes, destinos seguros y borrador conservado al cambiar sesión | Validación de comprensión con participantes |
| US-04: correo y protección | Verificación/cambio/recuperación, tokens limitados, cola y límites de solicitudes | Proveedor y entrega real, supervisión de reintentos |
| US-05: aprendizaje y primera publicación | Guardados y bandeja del creador integrados con recorridos existentes | Calidad del contenido, acompañamiento institucional y criterios educativos completos |
| US-06: preferencias y ciclo | Preferencias, sesiones, exportación, desactivación/reactivación y conservación histórica | Procedimientos operativos y mantenimiento supervisado |

## Evidencias y límites

Pasaron 310 pruebas completas y, tras el último ajuste de confirmación concurrente, 39 pruebas relacionadas. Pasaron Ruff, comprobación de migraciones, sintaxis JavaScript y cinco controles de concurrencia con conexiones SQLite independientes. El aviso auth.W004 corresponde al correo único por tipo y al backend específico; no demuestra acceso cruzado.

La migración local tuvo respaldo y conservó todos los valores de 540 filas anteriores en 61 tablas, excluyendo sesiones y registro operativo de migraciones. No se añadieron cuentas sintéticas a la base principal. En Chrome se revisaron escritorio/móvil, fotos ya cargadas, alias guardado, panel/solicitud del creador, suspensión con ayuda y cambio de cuenta entre pestañas. La selección automatizada de archivo quedó limitada por un permiso ausente de la extensión; carga, recorte y privacidad pasaron las pruebas HTTP/de servicios. No se alteró ese permiso ni se acredita esa interacción completa en navegador.

No hubo validación educativa/comercial, entrevistas, operación pública, SMTP real, auditoría completa de accesibilidad ni un nuevo pago desde ZEUS. La cola de correo y el mantenimiento necesitan instalación supervisada. Confirmar correo acredita control del buzón; no identidad real o competencia docente. La disponibilidad de Ayuda no acredita atención humana.

[Detalle técnico y recorridos](../src/docs/cuentas-y-fotos-2026-10-12.md), [evidencias](evidencias/2026-10-12-entrega-cuentas.json), [diagnóstico histórico anterior](22-usuarios-diagnostico-2026-10-12.md), [tareas con participantes](16-validacion-con-usuarios.md).

## Próximos pasos

Verificar proveedor/remitente y entrega real de correo; supervisar reintentos y limpieza; asignar revisión y atención de solicitudes; ejecutar las tareas de privacidad, cambio de espacio y publicación con participantes. Solución marcada en preguntas, apelaciones comunitarias y segundo factor administrativo conservan su alcance propio. No se presentan como funciones entregadas.


## Versión registrada

Commit de cuentas `71a19a4eee6a165ddc2ce89c7a2d2b63307cd916` en main, registrado el 12 de octubre de 2026. Se verificó por separado una copia exacta: 271 pruebas, Ruff, migraciones y cinco controles de concurrencia. Los 112 archivos del commit coinciden con los probados. La evidencia previa de 310 pruebas y las capturas corresponden al conjunto de cambios locales; las entregas independientes permanecen en el espacio de trabajo. [Registro y alcance](evidencias/2026-10-12-commit-cuentas.json).
