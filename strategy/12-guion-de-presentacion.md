# Presentation script / Guion de presentación

Study guide for Demo Day at CUBO+ (10-minute live demo, started from the terminal). Part A is in English and Part B in Spanish, with the same content, so either of us can present in the language the jury prefers. Speaker A is Caleb (Dev and Business); Speaker B is the partner. Swap parts if it suits you better, but both of us must be able to answer any question: the rubric says everyone must understand the whole project.

Guía de estudio para el Demo Day de CUBO+ (demostración en vivo de 10 minutos, iniciada desde la terminal). La parte A está en inglés y la parte B en español, con el mismo contenido. Hablante A es Caleb (Dev y Business); hablante B es el compañero.

---

# Part A — English

## 1. What the jury will evaluate

The CUBO+ evaluation document names five pillars. Keep them in mind; each section of the script answers one of them.

| Pillar | Where we answer it |
|---|---|
| Transparency and evolution (daily commits) | 94 commits since October 1, a daily log in `src/docs/operacion-y-bitacora.md` and the Google Doc with edit history |
| Technical execution (clean, organized code) | Django apps with one responsibility each, a single access rule, 629 automated tests |
| Real collaboration | Business research and technical specs in `strategy/`, the working build in `src/` |
| Documentation | Report, technical README with architecture diagram, user manual for students, educators and admin |
| Value proposition for the Bitcoin ecosystem in El Salvador | Lightning makes small payments, tips, refunds and "pay the difference" practical |

The original challenge ("Micropayments for Content") asks for: free and locked content, server-side protection, simulated invoices with Pending / Paid / Expired / Failed states, automatic unlock, persistent access, an admin view, funnel analytics, responsive UI and documentation. All of that is implemented.

## 2. The script (10 minutes)

### 0:00 – 1:00 · Opening and problem (Speaker B)

> "Good morning. We are BTC.EDU. Our project started with one question: how can someone buy exactly the educational content they need, without paying for a full course or a monthly subscription?
>
> Think of a student who only needs to understand one topic for tomorrow's exam, or someone at work who needs to automate one report. Today most platforms sell the whole course or a subscription. The unit they sell doesn't match the need."

### 1:00 – 2:00 · The idea and who it is for (Speaker B)

> "BTC.EDU is a learning platform where you can buy a single lesson, a chapter, or the full course, and pay with sats over Lightning. You can read free content and a sample before you pay, and after you pay you keep access to the version you bought.
>
> Our first audience is students, working people and self-learners in El Salvador who need to apply something concrete. The catalog covers six technology categories: Bitcoin and Lightning, software development, data and AI, cybersecurity, infrastructure and cloud, and digital design. Bitcoin is the payment method; the content goes beyond Bitcoin."

### 2:00 – 3:00 · Research and business model (Speaker B)

> "We compared subscription, advertising, freemium and micropayments, and reviewed Udemy, Domestika, Coursera Plus, Gumroad, Patreon, Teachable and Thinkific. Individual purchases already exist, so we don't claim to invent them. What we combine is: small units that each have a clear result, practice, payment in sats, and access that stays tied to the version you bought.
>
> Why Lightning? Card fees have a fixed part. With Patreon's published card fees, a 1-dollar purchase loses about 43 cents. Lightning makes very small payments viable, and also tips, refunds and partial payments.
>
> We show that the models can live together. Each category has a paid course, a freemium course with three free lessons, and a course included in a 30-day membership of 5,000 sats. Lessons cost 1.5 times their share of the course, so the full course is the better deal. All prices are test values; we have not validated them with buyers yet."

### 3:00 – 7:30 · Live demo (Speaker A drives, Speaker B narrates)

Prepare everything before going on stage (see checklist in section 3). Steps:

1. **Terminal (15 s).** Show `./dev.ps1` already running: Django on port 8000 and LNbits with FakeWallet on port 5000.
   > "Everything runs locally: Django, and LNbits connected to a test wallet. No real funds."
2. **Catalog (30 s).** Home → Courses → a category. Point at free, freemium and paid labels and the price in sats. Switch ES/EN once.
3. **Locked lesson (30 s).** Open a paid lesson as a logged-in student. Show the sample, objectives and requirements, and that the protected text is not there.
   > "The server decides access. The protected text is never sent to the browser, so you can't unlock it with the developer tools."
4. **Buy (60 s).** Buy now on one lesson → Prepare payment → QR invoice with a 15-minute expiry. Show the pending state.
   > "This is a real Lightning invoice from LNbits. The page checks its status silently."
5. **Pay and unlock (45 s).** Pay with the FakeWallet button. The lesson opens on its own. Reload the page or log out and back in: access persists.
6. **Pay the difference (30 s).** Go back to the course offer: the full course price now subtracts what was already paid.
   > "You can start with one lesson and later complete the course paying only what's missing."
7. **My learning (20 s).** Show progress and the next step.
8. **Admin and metrics (40 s).** `/administracion/estadisticas/`: conversion to invoice, payment completion, opening after purchase, return to library, repeat purchase. Then `/admin/` → Invoices.
   > "Every indicator shows its period and denominator. If there is no data, it says so."
9. **(Optional, 20 s)** Mention the phone test:
   > "On November 3 we also paid 3,600 sats from the ZEUS wallet on a phone, on a regtest network with Polar, and the course unlocked."

If something fails live, don't debug on stage: switch to the screenshots in `src/docs/evidence` and keep talking.

### 7:30 – 8:30 · How it works inside (Speaker A)

> "The project is Django 5.2 with SQLite for this stage, split into apps: accounts, content, creators, commerce, learning and media.
>
> Three rules keep it trustworthy. First, the server calculates and signs the price; the browser never sets it. Second, when a payment arrives, `settle` checks the payment hash, the amount in millisats, the expiry and the order. If all match, it creates the purchase, the access rights and the enrollment in one transaction. If not, it stores the evidence as an incident and grants nothing. Third, publishing freezes a version: if an educator edits a course later, what you bought doesn't change.
>
> A paid confirmation repeated twice never creates two purchases. A background process, `reconcile_payments`, checks pending invoices even if nobody has the page open. We have 629 automated tests plus concurrency checks."

### 8:30 – 9:30 · Sustainability and honest limits (Speaker B)

> "Running a minimal pilot would cost about 16 dollars a month in infrastructure, and about 42 with email and video, without the Lightning node or people's time. At 80,000 dollars per bitcoin, that's about 11 memberships or 46 average courses per month if the content is ours. With a 20% commission on other educators, it would be around 230 courses. Our proposal is 80% for the educator and 20% for the platform, paid weekly over Lightning; it's a hypothesis and the MVP doesn't calculate payouts yet.
>
> We want to be clear about what we have and haven't proven. We proved the technical flow: publish, pay, unlock, keep access. We have not yet run interviews or usability sessions, prices are not validated, and no real money has moved. The interview scripts and tasks are ready; that's the next step."

### 9:30 – 10:00 · Close (Speaker A or B)

> "BTC.EDU shows that Lightning can change the unit of purchase in education: you pay for the lesson you need, in sats, and keep it. Next we will test it with students and educators in El Salvador. Thank you; we're happy to take questions."

## 3. Demo checklist

The day before:

- [ ] Run `./dev.ps1` from the repository root and confirm Django (8000) and LNbits (5000) start.
- [ ] Confirm `src/.local/commerce.env` uses FakeWallet (the stable option). Use regtest only if Docker and Polar are already running.
- [ ] Create and log in with three accounts in separate browser profiles: student, approved educator, admin.
- [ ] Choose the exact lesson and course you'll buy, and make sure the student hasn't bought them yet. Have a second unbought lesson in case you need to repeat.
- [ ] Rehearse with a timer at least twice. The demo must fit in 4 min 30 s.
- [ ] Have screenshots ready as a fallback, plus the GitHub link and the Google Doc open in tabs.
- [ ] Turn off notifications, increase browser zoom, close unrelated tabs.
- [ ] Submit by November 8: the strategic PDF and a `.txt` with the public GitHub link.

## 4. Key numbers

| Topic | Number |
|---|---|
| Catalog | 25 courses, 252 lessons, 6 categories; 5 tutorials and 5 resources per category; 6 learning paths with 15% discount |
| Prices (test values) | Lessons 50–450 sats, courses 120–3,600 sats, membership 5,000 sats / 30 days |
| Invoice | Expires in 15 minutes; states pending, paid, expired, failed; late payment = incident, no access |
| Refunds | 8 days, paid by Lightning to an invoice the student provides; admin answers within 15 days |
| Tips | 10 to 100,000 sats |
| Tests | 629 automated tests (Nov 6), Ruff, migration checks, 5 concurrency checks |
| Commits | 94 since October 1 |
| Real wallet test | 3,600 sats from ZEUS on regtest, Nov 3 |
| Costs | USD 15.88/month pilot, USD 41.88/month initial operation (no node, no people) |
| Revenue split (proposal) | 80% educator / 20% platform, weekly Lightning payouts after 15 days |
| Stack | Django 5.2, SQLite, HTMX, LNbits v1.6.2, FakeWallet or LND regtest in Polar |

## 5. Likely questions and answers

### Business and product

**Why would anyone pay for a lesson when YouTube and ChatGPT are free?**
They might not, and we need to test that. Our bet is on structure and trust: a unit with a stated result, requirements, practice with solution, a sample before buying, and access that doesn't disappear. We still have free content and samples, and we link free external videos with credit. Interviews will compare our units with the free alternatives people already use.

**Have you talked to users? What evidence of demand do you have?**
Not yet, and we don't claim demand. We prepared interview guides (6–10 students, 3–5 creators), usability tasks and pricing questions (Van Westendorp and Gabor-Granger). What we can show today is technical evidence.

**How did you choose the prices?**
They are editorial test values. A lesson costs 1.5× its proportional share so the full course is cheaper than buying all lessons separately. Real prices will come from validation and the cost scenarios.

**Why not just a subscription?**
A subscription only makes sense if you consume often. We implemented the membership too, to show it coexists with individual purchases. The question we want to answer with users is which one they prefer for which need.

**How do creators earn money?**
Proposal: 80% educator, 20% platform, weekly payouts over Lightning after 15 days (the refund window plus margin). Today the MVP records sales and tips per educator but doesn't pay out yet. Tips already go through Lightning invoices.

**Who creates the content? Is it yours?**
The 25 courses are original BTC.EDU texts based on primary documentation (Python, MDN, SQLite, OWASP, Bitcoin Core, etc.). External videos are embedded with credit and always free; we don't resell other people's courses. No course has had specialist review yet.

**How is this different from Udemy or Gumroad?**
Udemy sells full courses; Gumroad sells files without the learning part. We combine units smaller than a course, practice and progress, payment in sats, crediting what you already paid, and version-based access. We still have to prove that this combination is worth it to users.

**What's the business recommendation?**
Run a small local validation first (zero infrastructure cost), then a reduced public pilot with invited educators and low real payments. Current prices are good to demonstrate micropayments but would not sustain paid staff without volume we haven't seen yet.

### Bitcoin and Lightning

**Why Bitcoin, after the 2025 reform made it voluntary to accept in El Salvador?**
We don't depend on mandatory acceptance. We use Lightning because it makes very small payments, tips and refunds practical with low fees, which is exactly what micropayments need. We don't assume people prefer Bitcoin; we'll test whether sats are understood.

**Did you use real bitcoin?**
No. The challenge asks for a simulated environment. We use LNbits with FakeWallet, and a regtest network with Polar. We also paid from ZEUS on a phone on regtest. Same invoice format and flow as mainnet, no real funds.

**What happens if the user pays after the invoice expires?**
The system records it as an incident with its evidence and does not grant access automatically. Admin reviews it. We don't ask the user to pay again.

**What if the page is closed while paying?**
`reconcile_payments` checks pending invoices in the background. When the user returns, the content is already unlocked. If the status is uncertain, the page offers "Update payment status" before paying again.

**What about price volatility?**
Prices are in sats. We show prices only in sats; a fiat equivalent is something we might test if users don't understand sats.

**How would you go to mainnet?**
Replace FakeWallet with a funded LND node with inbound liquidity (or a provider), deploy with HTTPS, and run reconciliation as a supervised service. LNbits already abstracts the wallet, so the app code stays the same.

### Technical

**How do you prevent someone from unlocking content from the browser?**
The rule lives in `content/access.py` and is applied on the server for HTML, JSON and files. Protected text is never sent to the browser unless access is granted. Files are served only after the same check.

**How do you prevent double charging or double access?**
The server signs the quote, reuses the same invoice if a response is lost, and `settle` is idempotent: a repeated confirmation finds the existing purchase. We test this with concurrency checks.

**Why SQLite? Will it scale?**
It's enough for local development and a small pilot. The stages plan includes moving to a database with more concurrency if usage requires it. Django makes that change mostly a configuration step.

**How do you test?**
`check-platform.ps1` runs 629 Django tests, Ruff, `manage.py check`, migration consistency and concurrency checks. Before each migration we back up the database.

**Did you use AI to build this?**
Answer honestly. Say how you used it (writing and reviewing code, research, documentation) and that you reviewed, tested and can explain every part. Be ready to explain any module they point at.

**What are certificates worth? What is OpenTimestamps?**
A certificate proves completion under the published rules, not an official degree. Each one has a SHA-256 fingerprint anyone can recompute. Optionally, OpenTimestamps anchors that fingerprint in a Bitcoin block to prove the date; it's off by default and not tested against real calendars yet.

### Team and process

**The rule was 4 members (2 Dev + 2 Non-Dev). Why are you two?**
Answer with the real situation. Caleb covered Business and Dev since October 7; the team size was a point to clarify with CUBO+. Show that both roles' deliverables exist: `strategy/` and `src/`.

**Was the work done daily?**
Yes: 94 commits from October 1, and a daily log with dates and evidence. Point them to the GitHub history and the Google Doc edit history.

**What would you do with one more month?**
Run the interviews and usability sessions, define educator payouts, legal review of refunds, deploy a pilot with HTTPS, email and a funded node, and get specialists to review the courses.

**What's the biggest risk?**
Demand. We built the product before validating that people will pay for units. That's why the next stage is validation, not more features.

## 6. Other suggestions

- **Decide who answers what.** Business questions go to the partner first, technical ones to Caleb, but both should know the short answer to everything above.
- **Don't oversell.** The jury's rule is "Don't trust, verify". Saying "implemented and tested, not yet validated with users" builds more credibility than claiming demand.
- **Have a fallback.** A 2-minute screen recording of the full purchase flow saves the demo if the network or LNbits fails.
- **Quick slides.** Three or four slides (problem, model, architecture, numbers) help the opening and the close; the rest is live.
- **Know the files.** Be ready to open `content/access.py`, `commerce/services.py` and the README diagram if someone asks to see code.

---

# Parte B — Español

## 1. Qué evaluará el jurado

El documento de evaluación de CUBO+ tiene cinco pilares. Cada parte del guion responde a uno.

| Pilar | Dónde lo respondemos |
|---|---|
| Transparencia y evolución (commits diarios) | 94 commits desde el 1 de octubre, bitácora diaria en `src/docs/operacion-y-bitacora.md` y el Google Doc con historial |
| Ejecución técnica (código limpio y ordenado) | Aplicaciones Django con una responsabilidad cada una, una regla única de acceso, 629 pruebas automatizadas |
| Colaboración real | Investigación y especificaciones en `strategy/`, la aplicación funcionando en `src/` |
| Documentación | Informe, README técnico con diagrama de arquitectura, manual para estudiantes, educadores y administración |
| Propuesta de valor para el ecosistema Bitcoin en El Salvador | Lightning hace viables pagos pequeños, propinas, reembolsos y «pagar solo la diferencia» |

El reto original («Micropayments for Content») pide: contenido gratuito y bloqueado, protección en el servidor, facturas simuladas con estados Pendiente / Pagada / Vencida / Fallida, desbloqueo automático, acceso persistente, vista de administración, analítica del embudo, interfaz adaptable y documentación. Todo está implementado.

## 2. El guion (10 minutos)

### 0:00 – 1:00 · Apertura y problema (Hablante B)

> «Buenos días. Somos BTC.EDU. El proyecto empezó con una pregunta: ¿cómo puede alguien comprar exactamente el contenido educativo que necesita, sin pagar un curso completo ni una suscripción mensual?
>
> Piensen en un estudiante que solo necesita entender un tema para el examen de mañana, o en alguien que en su trabajo necesita automatizar un reporte. Hoy la mayoría de plataformas venden el curso entero o una suscripción. Lo que venden no coincide con lo que la persona necesita.»

### 1:00 – 2:00 · La idea y para quién es (Hablante B)

> «BTC.EDU es una plataforma de aprendizaje donde puedes comprar una lección, un capítulo o el curso completo, y pagar en sats por Lightning. Puedes leer contenido gratuito y una muestra antes de pagar, y después de pagar conservas el acceso a la versión que compraste.
>
> Nuestro público inicial son estudiantes, personas que trabajan y autodidactas en El Salvador que necesitan aplicar algo concreto. El catálogo cubre seis categorías: Bitcoin y Lightning, desarrollo de software, datos e IA, ciberseguridad, infraestructura y nube, y diseño digital. Bitcoin es la forma de pago; el contenido va más allá de Bitcoin.»

### 2:00 – 3:00 · Investigación y modelo de negocio (Hablante B)

> «Comparamos suscripción, publicidad, freemium y micropagos, y revisamos Udemy, Domestika, Coursera Plus, Gumroad, Patreon, Teachable y Thinkific. La compra individual ya existe, así que no decimos haberla inventado. Lo que combinamos es: unidades pequeñas con un resultado claro, práctica, pago en sats y acceso ligado a la versión comprada.
>
> ¿Por qué Lightning? Las comisiones de tarjeta tienen una parte fija. Con las tarifas publicadas de Patreon, una compra de 1 dólar pierde unos 43 centavos. Lightning hace viables los pagos muy pequeños, y también propinas, reembolsos y pagos parciales.
>
> Mostramos que los modelos conviven. Cada categoría tiene un curso de pago, uno freemium con tres lecciones gratis y uno incluido en una membresía de 5 000 sats por 30 días. Cada lección cuesta 1,5 veces su parte del curso, así que el curso completo conviene más. Todos los precios son de prueba; todavía no los validamos con compradores.»

### 3:00 – 7:30 · Demostración en vivo (Hablante A maneja, Hablante B narra)

Preparar todo antes de subir (ver lista en la sección 3). Pasos:

1. **Terminal (15 s).** Mostrar `./dev.ps1` ya en marcha: Django en el puerto 8000 y LNbits con FakeWallet en el 5000.
   > «Todo corre en local: Django y LNbits conectado a una wallet de prueba. Sin fondos reales.»
2. **Catálogo (30 s).** Inicio → Cursos → una categoría. Señalar las etiquetas gratuito, freemium y de pago y el precio en sats. Cambiar una vez ES/EN.
3. **Lección bloqueada (30 s).** Abrir una lección de pago con la cuenta de estudiante. Mostrar la muestra, objetivos y requisitos, y que el texto protegido no aparece.
   > «El servidor decide el acceso. El texto protegido nunca llega al navegador; no se puede desbloquear con las herramientas de desarrollador.»
4. **Comprar (60 s).** Comprar ahora en una lección → Preparar pago → factura con QR que vence en 15 minutos. Mostrar el estado pendiente.
   > «Es una factura Lightning real generada por LNbits. La página consulta su estado en silencio.»
5. **Pagar y desbloquear (45 s).** Pagar con el botón de FakeWallet. La lección se abre sola. Recargar o cerrar sesión y volver a entrar: el acceso se conserva.
6. **Pagar la diferencia (30 s).** Volver a la oferta del curso: el precio del curso completo ya descuenta lo pagado.
   > «Puedes empezar con una lección y después completar el curso pagando solo lo que falta.»
7. **Mi aprendizaje (20 s).** Mostrar el avance y el siguiente paso.
8. **Administración y métricas (40 s).** `/administracion/estadisticas/`: conversión a factura, finalización del pago, apertura después de comprar, regreso a la biblioteca y compra repetida. Después `/admin/` → Invoices.
   > «Cada indicador muestra su periodo y su denominador. Si no hay datos, lo dice.»
9. **(Opcional, 20 s)** Mencionar la prueba con teléfono:
   > «El 3 de noviembre también pagamos 3 600 sats desde la wallet ZEUS en un teléfono, en una red regtest con Polar, y el curso se desbloqueó.»

Si algo falla en vivo, no depurar en el escenario: pasar a las capturas de `src/docs/evidence` y seguir hablando.

### 7:30 – 8:30 · Cómo funciona por dentro (Hablante A)

> «El proyecto usa Django 5.2 con SQLite en esta etapa, dividido en aplicaciones: accounts, content, creators, commerce, learning y media.
>
> Tres reglas lo hacen confiable. Primero, el servidor calcula y firma el precio; el navegador nunca lo fija. Segundo, cuando llega un pago, `settle` compara el hash, el importe en milisats, el vencimiento y el pedido. Si todo coincide, crea la compra, los derechos de acceso y la inscripción en una sola transacción. Si no, guarda la evidencia como incidencia y no concede nada. Tercero, publicar congela una versión: si el educador edita el curso después, lo que compraste no cambia.
>
> Una confirmación repetida nunca crea dos compras. Un proceso en segundo plano, `reconcile_payments`, revisa las facturas pendientes aunque nadie tenga la página abierta. Tenemos 629 pruebas automatizadas más controles de concurrencia.»

### 8:30 – 9:30 · Sostenibilidad y límites (Hablante B)

> «Un piloto mínimo costaría unos 16 dólares al mes en infraestructura, y unos 42 con correo y video, sin contar el nodo Lightning ni el tiempo de las personas. Con el bitcoin a 80 000 dólares, son unas 11 membresías o 46 cursos de precio medio al mes si el contenido es nuestro. Con una comisión del 20 % sobre otros educadores, serían unos 230 cursos. Proponemos 80 % para el educador y 20 % para la plataforma, con pagos semanales por Lightning; es una hipótesis y el MVP todavía no calcula liquidaciones.
>
> Queremos ser claros con lo que hemos demostrado y lo que no. Demostramos el flujo técnico: publicar, pagar, desbloquear y conservar el acceso. Todavía no hicimos entrevistas ni sesiones de usabilidad, los precios no están validados y no se ha movido dinero real. Los guiones y tareas están listos; ese es el siguiente paso.»

### 9:30 – 10:00 · Cierre (Hablante A o B)

> «BTC.EDU muestra que Lightning puede cambiar la unidad de compra en la educación: pagas la lección que necesitas, en sats, y la conservas. Lo siguiente es probarlo con estudiantes y educadores en El Salvador. Gracias; con gusto respondemos sus preguntas.»

## 3. Lista para la demostración

El día anterior:

- [ ] Ejecutar `./dev.ps1` desde la raíz del repositorio y confirmar que arrancan Django (8000) y LNbits (5000).
- [ ] Confirmar que `src/.local/commerce.env` usa FakeWallet (la opción estable). Usar regtest solo si Docker y Polar ya están abiertos.
- [ ] Crear y abrir tres cuentas en perfiles de navegador distintos: estudiante, educador aprobado y administración.
- [ ] Elegir la lección y el curso exactos que se comprarán y comprobar que el estudiante no los tiene. Tener otra lección sin comprar por si hay que repetir.
- [ ] Ensayar con cronómetro al menos dos veces. La demostración debe caber en 4 min 30 s.
- [ ] Tener capturas de respaldo, y el enlace de GitHub y el Google Doc abiertos en pestañas.
- [ ] Desactivar notificaciones, aumentar el zoom del navegador y cerrar pestañas ajenas.
- [ ] Entregar a más tardar el 8 de noviembre: el PDF estratégico y un `.txt` con el enlace público de GitHub.

## 4. Cifras clave

| Tema | Cifra |
|---|---|
| Catálogo | 26 cursos, 264 lecciones, 6 categorías; 5 tutoriales y 5 recursos por categoría; 8 rutas con 15 % de descuento |
| Precios (de prueba) | Lecciones de 50 a 450 sats, cursos de 120 a 3 600 sats, membresía de 5 000 sats por 30 días |
| Factura | Vence en 15 minutos; estados pendiente, pagada, vencida, fallida; pago tardío = incidencia, sin acceso |
| Reembolsos | 8 días, pagados por Lightning a una factura del estudiante; administración responde en 15 días |
| Propinas | De 10 a 100 000 sats |
| Pruebas | 629 pruebas automatizadas (6 de noviembre), Ruff, migraciones, 5 controles de concurrencia |
| Commits | 94 desde el 1 de octubre |
| Prueba con wallet | 3 600 sats desde ZEUS en regtest, 3 de noviembre |
| Costos | USD 15.88 al mes el piloto, USD 41.88 al mes la operación inicial (sin nodo ni personas) |
| Reparto (propuesta) | 80 % educador / 20 % plataforma, pagos semanales por Lightning después de 15 días |
| Tecnología | Django 5.2, SQLite, HTMX, LNbits v1.6.2, FakeWallet o LND regtest en Polar |

## 5. Preguntas probables y respuestas

### Negocio y producto

**¿Por qué alguien pagaría una lección si YouTube y ChatGPT son gratis?**
Quizá no lo haga, y eso hay que probarlo. Apostamos por estructura y confianza: una unidad con resultado declarado, requisitos, práctica con solución, muestra antes de comprar y acceso que no desaparece. Mantenemos contenido gratuito y muestras, y enlazamos videos externos gratuitos con crédito. Las entrevistas compararán nuestras unidades con las alternativas gratuitas que la gente ya usa.

**¿Hablaron con usuarios? ¿Qué evidencia de demanda tienen?**
Todavía no, y no afirmamos que haya demanda. Preparamos guiones de entrevista (6 a 10 estudiantes, 3 a 5 creadores), tareas de usabilidad y preguntas de precio (Van Westendorp y Gabor-Granger). Lo que mostramos hoy es evidencia técnica.

**¿Cómo eligieron los precios?**
Son valores editoriales de prueba. Una lección cuesta 1,5 veces su parte proporcional para que el curso completo salga más barato que comprar todas las lecciones. Los precios reales saldrán de la validación y de los escenarios de costos.

**¿Por qué no solo una suscripción?**
La suscripción conviene si consumes seguido. También implementamos la membresía para mostrar que convive con la compra individual. Lo que queremos averiguar con usuarios es cuál prefieren para cada necesidad.

**¿Cómo ganan los creadores?**
Propuesta: 80 % para el educador y 20 % para la plataforma, con pagos semanales por Lightning después de 15 días (el plazo de reembolso más margen). Hoy el MVP registra ventas y propinas por educador, pero todavía no liquida. Las propinas ya se pagan con facturas Lightning.

**¿Quién crea el contenido? ¿Es suyo?**
Los 26 cursos son textos originales de BTC.EDU basados en documentación primaria (Python, MDN, SQLite, OWASP, Bitcoin Core, etc.). Los videos externos se insertan con crédito y siempre son gratuitos; no revendemos cursos de otros. Ningún curso tiene todavía revisión de especialistas.

**¿En qué se diferencian de Udemy o Gumroad?**
Udemy vende cursos completos; Gumroad vende archivos sin la parte de aprendizaje. Nosotros combinamos unidades más pequeñas que un curso, práctica y progreso, pago en sats, crédito por lo ya pagado y acceso por versión. Falta comprobar que esta combinación valga la pena para los usuarios.

**¿Cuál es la recomendación de negocio?**
Primero una validación local pequeña (sin costo de infraestructura), después un piloto público reducido con educadores invitados y pagos reales bajos. Los precios actuales sirven para demostrar micropagos, pero no sostendrían personal remunerado sin un volumen que todavía no hemos visto.

### Bitcoin y Lightning

**¿Por qué Bitcoin, si desde la reforma de 2025 aceptarlo es voluntario en El Salvador?**
No dependemos de que sea obligatorio. Usamos Lightning porque hace prácticos los pagos muy pequeños, las propinas y los reembolsos con comisiones bajas, que es justo lo que necesitan los micropagos. No suponemos que la gente prefiera Bitcoin; vamos a comprobar si entiende los sats.

**¿Usaron bitcoin real?**
No. El reto pide un entorno simulado. Usamos LNbits con FakeWallet y una red regtest con Polar. También pagamos desde ZEUS en un teléfono en regtest. Es el mismo formato de factura y el mismo flujo que en la red principal, sin fondos reales.

**¿Qué pasa si el usuario paga después de que vence la factura?**
El sistema lo registra como incidencia con su evidencia y no concede acceso automáticamente. Administración lo revisa. No le pedimos que vuelva a pagar.

**¿Y si cierra la página mientras paga?**
`reconcile_payments` revisa las facturas pendientes en segundo plano. Cuando vuelve, el contenido ya está desbloqueado. Si el estado es incierto, la página ofrece «Actualizar estado del pago» antes de pagar otra vez.

**¿Y la volatilidad del precio?**
Los precios están en sats y solo se muestran en sats. Si los usuarios no entienden los sats, podríamos probar una equivalencia informativa en dólares.

**¿Cómo pasarían a la red principal?**
Cambiar FakeWallet por un nodo LND con liquidez de entrada (o un proveedor), desplegar con HTTPS y correr la conciliación como servicio supervisado. LNbits ya abstrae la wallet, así que el código de la aplicación no cambia.

### Técnicas

**¿Cómo evitan que alguien desbloquee el contenido desde el navegador?**
La regla está en `content/access.py` y se aplica en el servidor para HTML, JSON y archivos. El texto protegido nunca llega al navegador sin acceso. Los archivos se entregan solo después de la misma comprobación.

**¿Cómo evitan cobros o accesos duplicados?**
El servidor firma la cotización, recupera la misma factura si se pierde una respuesta y `settle` es idempotente: una confirmación repetida encuentra la compra existente. Lo comprobamos con controles de concurrencia.

**¿Por qué SQLite? ¿Escala?**
Alcanza para el desarrollo local y un piloto pequeño. El plan por etapas contempla pasar a una base con más concurrencia si el uso lo exige. Con Django es sobre todo un cambio de configuración.

**¿Cómo prueban?**
`check-platform.ps1` ejecuta 629 pruebas Django, Ruff, `manage.py check`, la consistencia de migraciones y los controles de concurrencia. Antes de cada migración respaldamos la base.

**¿Usaron IA para construirlo?**
Responder con honestidad. Explicar cómo la usaron (escribir y revisar código, investigar, documentar) y que revisaron, probaron y pueden explicar cada parte. Estar listos para explicar cualquier módulo que señalen.

**¿Qué valor tienen los certificados? ¿Qué es OpenTimestamps?**
El certificado acredita la finalización según las reglas publicadas; no es un título oficial. Cada uno tiene una huella SHA-256 que cualquiera puede recalcular. De forma opcional, OpenTimestamps ancla esa huella en un bloque de Bitcoin para probar la fecha; está desactivado por defecto y no se ha probado con los calendarios reales.

### Equipo y proceso

**La regla era de 4 integrantes (2 Dev + 2 Non-Dev). ¿Por qué son dos?**
Responder con la situación real. Caleb cubrió Business y Dev desde el 7 de octubre; el tamaño del equipo era un punto por aclarar con CUBO+. Mostrar que existen los entregables de ambos roles: `strategy/` y `src/`.

**¿El trabajo fue diario?**
Sí: 94 commits desde el 1 de octubre y una bitácora diaria con fechas y evidencias. Remitir al historial de GitHub y al historial del Google Doc.

**¿Qué harían con un mes más?**
Hacer las entrevistas y las sesiones de usabilidad, definir la liquidación a educadores, revisar los reembolsos con un abogado, desplegar un piloto con HTTPS, correo y un nodo con fondos, y pedir a especialistas que revisen los cursos.

**¿Cuál es el mayor riesgo?**
La demanda. Construimos el producto antes de validar que la gente pague por unidades. Por eso la siguiente etapa es validar, no añadir funciones.

## 6. Otras sugerencias

- **Repartir las preguntas.** Las de negocio las contesta primero el compañero y las técnicas Caleb, pero ambos deben saber la respuesta corta de todo lo anterior.
- **No exagerar.** La regla del jurado es «Don't trust, verify». Decir «implementado y probado, todavía no validado con usuarios» da más credibilidad que afirmar demanda.
- **Tener un respaldo.** Una grabación de pantalla de 2 minutos con la compra completa salva la demostración si fallan la red o LNbits.
- **Pocas diapositivas.** Tres o cuatro (problema, modelo, arquitectura, cifras) ayudan en la apertura y el cierre; lo demás es en vivo.
- **Conocer los archivos.** Estar listos para abrir `content/access.py`, `commerce/services.py` y el diagrama del README si piden ver código.
