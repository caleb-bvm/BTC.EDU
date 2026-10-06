# Investigación de plataformas y necesidades

La comparación funcional conserva la consulta del 1 de octubre de 2026. El 5 de octubre se amplió con [modelos, tarifas, muestras y costos](13-monetizacion-precios-y-muestras.md), y [guiones/pruebas](16-validacion-con-usuarios.md). La ausencia de comparación de precios correspondía a la consulta inicial. No se usaron cuentas externas ni se realizaron entrevistas. Las necesidades siguen siendo propuestas por validar.

## Ampliación

Las fuentes documentan coexistencia de compras y membresías, freemium y muestras por módulo. No permiten presentar la compra individual como una modalidad inexistente en el mercado. La recomendación provisional mantiene gratuito + compras individuales, validando utilidad y claridad.

Los costos distinguen suscripción del creador, precio al alumno, comisión, procesamiento y video. Un cargo fijo pesa sobre compras pequeñas; el acceso permanente requiere estimar consumo posterior y archivos históricos. No se eligió proveedor ni se fijaron precios de mercado.

Los instrumentos no producen resultados hasta ejecutarse. Fuentes comerciales y metodológicas con fecha en 13 y 16; síntesis integrada en el [documento principal](19-recomendacion-y-entrega-final.md).

## Plataformas de referencia

| Referencia | Comportamiento documentado | Aplicación propuesta |
|---|---|---|
| Udemy | Panel del instructor con organización del contenido, preparación para publicar y gestión del curso [S1] | Editor de cursos, orden de capítulos y revisión antes de publicar |
| Teachable | Finalización de lecciones, seguimiento de video y cuestionarios con nota mínima e intentos [S2] | Progreso guardado y evaluaciones configurables |
| Thinkific | Membresías que agrupan productos educativos y beneficios como comunidad [S3] | Planes con alcance y duración definidos, además de compras individuales |
| Patreon | Membresías y compras únicas de videos y otros productos [S4] | Ofrecer compra individual aunque exista una membresía |
| Udemy | Subtítulos de video mediante archivos VTT [S5] | Soportar subtítulos cargados por el creador |
| Udemy | Panel de preguntas y respuestas para instructores [S6] | Bandeja de preguntas asociadas a cursos y lecciones |
| Thinkific | Comunidades con publicaciones, comentarios y moderadores [S7, S8] | Espacios por curso o creador, con reportes y moderación |
| Teachable | Informes de lecciones completadas, videos y resultados de cuestionarios [S9] | Métricas educativas por curso y creador |
| Thinkific | Certificado disponible después de completar el curso [S10] | Certificado condicionado a requisitos de finalización |
| Patreon | Cancelar la membresía puede conservar acceso hasta terminar el periodo pagado [S11] | Separar cancelación de renovación de vencimiento del acceso |

No copiamos todas las reglas comerciales de esas plataformas. Por ejemplo, el precio de una compra de curso después de adquirir capítulos necesita una decisión propia. Las fuentes no establecen nuestra política de descuentos ni nuestros precios.

## Lado del alumno o comprador

| Momento | Necesidad propuesta | Cómo la atenderemos | Evidencia y validación pendiente |
|---|---|---|---|
| Elegir | Entender qué aprenderá, requisitos y qué incluye el precio | Objetivos, temario, muestra, formato y lista de extras | Organización del curso [S1]; probar si puede explicar lo incluido |
| Comprar | Elegir curso, capítulo, video o material sin obligación de suscribirse | Ofertas independientes, precio y acceso visible | Compras únicas y membresías coexisten [S4]; validar preferencias |
| Estudiar | Retomar una lección y un video | Continuar aprendiendo, última posición y lecciones completadas | Seguimiento educativo [S2, S9]; probar cambio de dispositivo |
| Acceder | Usar video con subtítulos y controles accesibles | VTT, teclado, velocidad y diseño móvil | Subtítulos [S5]; realizar pruebas de accesibilidad |
| Practicar | Saber qué comprende y qué necesita repasar | Cuestionarios, resultado, explicación y reglas de reintento | Evaluaciones [S2]; validar utilidad de preguntas |
| Preguntar | Resolver dudas en el contexto correcto | Preguntas por lección y respuestas del creador | Panel de preguntas [S6]; validar carga de soporte |
| Finalizar | Obtener evidencia de haber terminado | Certificado verificable según requisitos | Finalización [S10]; validar interés, sin prometer acreditación |
| Participar | Conversar con otros alumnos sin perder el contexto | Comunidad por curso o creador, búsqueda y reportes | Comunidad y moderadores [S7, S8]; validar participación |
| Administrar acceso | Entender lo comprado y cuándo vence una membresía | Biblioteca, historial, fecha de vigencia y cancelar renovación | Periodo pagado [S11]; probar comprensión de cancelación |
| Volver | Recuperar cuenta y ver novedades relevantes | Recuperación de contraseña y notificaciones internas | Propuesta propia; probar recuperación y evitar avisos excesivos |

## Lado del creador

| Necesidad propuesta | Cómo la atenderemos | Evidencia y validación pendiente |
|---|---|---|
| Presentarse | Perfil con descripción, temas y cursos publicados | Perfil de instructor y publicación [S1]; validar información necesaria |
| Preparar contenido | Borradores, capítulos ordenados, carga de video, texto, archivos y subtítulos | Organización [S1] y VTT [S5]; observar a un creador usando el editor |
| Revisar antes de publicar | Vista como alumno, lista de faltantes, envío a revisión y motivos de rechazo | Preparación de publicación [S1]; definir controles propios |
| Vender con claridad | Definir qué es gratis, qué se compra y qué incluye una membresía | Combinación de formas de venta [S3, S4]; revisar ofertas ambiguas |
| Evaluar | Crear preguntas, nota mínima, intentos y requisitos de certificado | Evaluaciones [S2, S10]; medir tiempo de preparación |
| Acompañar | Bandeja de preguntas, comentarios y notificaciones internas | Preguntas [S6]; validar disponibilidad para responder |
| Mejorar cursos | Ver avance, abandono, resultados y preguntas frecuentes | Informes [S9]; evitar confundir aperturas con aprendizaje |
| Administrar comunidad | Moderar sus espacios, reportar problemas y delegar según permiso | Moderadores [S8]; validar responsabilidades |
| Entender resultados comerciales | Facturas, compras y volumen simulado de sus ofertas | Propuesta propia apoyada en venta [S4]; sin presentar saldo ficticio como ingreso |
| Actualizar sin perjudicar compras | Versiones publicadas y conservación de lo comprado | Propuesta propia; probar cambios de temario y contenidos |

Un creador puede también ser alumno. El acceso al panel de creador no concede permisos sobre cursos de otros creadores. Solo verá datos educativos y comerciales de sus contenidos; no contraseñas ni claves de pago.

## Lo que falta comprobar con personas

Entrevistar alumnos sobre su última compra o curso real, cómo retoman, cuándo compran solo un video, dificultades al pagar, utilidad de evaluaciones y certificados y preferencia entre membresía y compra individual. Entrevistar creadores sobre publicación actual, estructura de materiales, respuesta a preguntas, derechos de contenido, actualización y métricas utilizadas.

Probar tareas en un prototipo: distinguir gratuito y comprado; comprar un video; entender extras del curso; retomar en otro dispositivo; consultar una duda; completar evaluación; cancelar membresía sin perder compras. Con creadores: preparar un curso, añadir material, configurar oferta, enviar a revisión y responder una pregunta. Registrar hallazgos reales y cambios derivados; no inventar resultados.

## Fuentes oficiales

- S1: [Udemy — panel de gestión de cursos](https://support.udemy.com/hc/en-us/articles/230048607-How-to-Navigate-the-Course-Management-Dashboard)
- S2: [Teachable — requisitos de finalización](https://support.teachable.com/en/articles/11682463-course-compliance)
- S3: [Thinkific — crear una membresía](https://support.thinkific.com/hc/en-us/articles/360052568634-Create-a-Membership)
- S4: [Patreon — membresías y compras únicas](https://support.patreon.com/hc/en-us/articles/16263061573645-Get-started-on-Patreon)
- S5: [Udemy — subtítulos para videos](https://support.udemy.com/hc/en-us/articles/229605428-Adding-Captions-to-Your-Videos)
- S6: [Udemy — panel de preguntas y respuestas](https://support.udemy.com/hc/en-us/articles/229606328-Instructor-Q-A-Dashboard)
- S7: [Thinkific — comunidades](https://support.thinkific.com/hc/en-us/articles/7265849758999-Get-Started-with-Thinkific-Communities)
- S8: [Thinkific — moderador de comunidad](https://support.thinkific.com/hc/en-us/articles/7897629454871-Community-Moderator-Role)
- S9: [Teachable — informes educativos](https://support.teachable.com/en/articles/11682570-course-reporting-tools)
- S10: [Thinkific — probar certificados](https://support.thinkific.com/hc/en-us/articles/360060666253-How-can-I-create-a-test-certificate)
- S11: [Patreon — cancelar membresía](https://support.patreon.com/hc/en-gb/articles/360005502572-Cancelling-a-paid-membership)
