<div align="center">

# BTC.EDU

**Aprende pagando solo lo que necesitas, en sats.**

Plataforma educativa con micropagos Lightning: cursos, lecciones, tutoriales y recursos que se compran por unidad, por curso o en paquete, con acceso concedido en el servidor al confirmarse el pago.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Lightning](https://img.shields.io/badge/Lightning-Network-792EE5?logo=lightning&logoColor=white)](https://lightning.network/)
[![LNbits](https://img.shields.io/badge/LNbits-1.6.2-FF1EE6)](https://lnbits.com/)
[![Polar](https://img.shields.io/badge/Polar-regtest-F7931A?logo=bitcoin&logoColor=white)](https://lightningpolar.com/)
[![ZEUS](https://img.shields.io/badge/ZEUS-wallet-0B0B0B)](https://zeusln.com/)
<br>
[![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Ruff](https://img.shields.io/badge/lint-Ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![uv](https://img.shields.io/badge/uv-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![Pruebas](https://img.shields.io/badge/pruebas-597-2EA44F)](src/README.md#comprobaciones)
[![Idiomas](https://img.shields.io/badge/idiomas-ES%20%7C%20EN-FF6A00)](src/README.md#lógica-principal)
[![CUBO+](https://img.shields.io/badge/CUBO%2B-El%20Salvador-0047AB)](docs/)

🇸🇻 [Español](#qué-es) · 🇺🇸 [English](#in-english)

<img src="src/docs/evidence/compra-zeus-regtest-2026-11-03.webp" alt="Compra confirmada en BTC.EDU después de pagar desde ZEUS" width="820">

<sub>Curso de 3 600 sats pagado desde ZEUS en un teléfono, a través de Polar y LNbits en regtest.</sub>

</div>

---

## Qué es

BTC.EDU nace de una pregunta: ¿cómo puede alguien comprar solo el contenido educativo que necesita, sin pagar un curso completo ni mantener una suscripción? Los educadores publican cursos, tutoriales y recursos con precio en sats; los estudiantes pagan una factura Lightning y el contenido queda en su biblioteca de forma permanente.

Es el proyecto del reto *Micropayments for Content* de CUBO+, en El Salvador.

| | |
|---|---|
| 📚 **Catálogo** | 25 cursos y 252 lecciones en seis categorías, 30 tutoriales, 30 recursos y 6 rutas de aprendizaje |
| ⚡ **Pagos** | Facturas Lightning por curso, lección, carrito o paquete; membresía, cupones, regalos, propinas y reembolsos |
| 🔒 **Acceso** | Una sola regla en el servidor decide qué se ve; el navegador nunca fija precios ni desbloquea contenido |
| 🎓 **Aprendizaje** | Progreso, evaluaciones, prácticas con entrega, certificados con huella SHA-256 y sello OpenTimestamps |
| 🧑‍🏫 **Educadores** | Estudio con borradores, revisión antes de publicar, versiones congeladas, ventas y métricas |
| 💬 **Comunidad** | Conversaciones por curso y lección, preguntas privadas, avisos y moderación |
| 🌐 **Idiomas** | Interfaz en español e inglés (`/en/`), modo claro y oscuro, instalable como aplicación |

## Cómo funciona un pago

```mermaid
sequenceDiagram
    actor E as Estudiante
    participant B as BTC.EDU
    participant L as LNbits
    participant W as ZEUS / wallet
    E->>B: Elige curso, lección o carrito
    B->>B: Calcula y firma el precio
    B->>L: Crea la factura
    L-->>B: lnbc… / lnbcrt…
    B-->>E: Muestra el QR
    W->>L: Paga la factura
    B->>L: Consulta el estado (en silencio)
    L-->>B: Pagada
    B->>B: settle: valida hash, importe, plazo y pedido
    B-->>E: Compra confirmada y contenido en Mi aprendizaje
```

Si algo no coincide, el pago queda como incidencia para administración y no concede acceso. Una confirmación repetida no duplica compras.

## Inicio rápido

Requiere Windows con PowerShell. Desde la raíz del repositorio:

```powershell
./dev.ps1
```

El script descarga `uv`, Python 3.12, las dependencias y LNbits dentro de `src/.local`, aplica migraciones e inicia LNbits y Django en `http://127.0.0.1:8000/`. La conexión del comercio, la carga del catálogo y el modo regtest con Polar y ZEUS están en la [guía técnica](src/README.md#instalación-y-arranque).

## Estructura del repositorio

```text
.
├── dev.ps1 · dev-platform.ps1   arranque completo o solo plataforma
├── src/                          código Django, scripts, traducciones y documentación técnica
├── strategy/                     investigación, requisitos y decisiones, numerados en orden de lectura
└── docs/                         documentos originales del reto CUBO+
```

## Documentación

| | Documento | Para qué |
|---|---|---|
| 📘 | [Informe](strategy/01-informe.md) | Idea, investigación, objetivos, desarrollo, logros y manual de uso |
| 🗂️ | [Índice de strategy](strategy/README.md) | Requisitos, investigación, producto, arquitectura, catálogo y validación |
| 🛠️ | [Guía técnica](src/README.md) | Instalación, arquitectura, lógica de compra y comprobaciones |
| 📓 | [Operación y bitácora](src/docs/operacion-y-bitacora.md) | Operación local, decisiones, pendientes e historial por día |

## Estado y límites

Funciona en local con LNbits sobre FakeWallet o sobre una red regtest de Polar: **no mueve fondos reales**. No tiene todavía despliegue público con HTTPS, correo con entrega comprobada ni liquidación automática a educadores. La propuesta, los precios y la utilidad educativa aún no se han validado con participantes; las pruebas técnicas no equivalen a esa validación.

---

## In English

**BTC.EDU** is a learning platform with Lightning micropayments. Educators publish courses, lessons, tutorials and resources priced in sats; students pay a Lightning invoice for a single lesson, a full course or a bundle, and the server grants permanent access once the payment is confirmed. It includes progress tracking, assessments, certificates with SHA-256 fingerprints, community threads, memberships, coupons, gifts, tips and refunds, with the interface in Spanish and English (`/en/`).

Built with Django 5.2 and LNbits, tested locally against FakeWallet and a Polar regtest network paid from ZEUS. No real funds are moved. Created for the *Micropayments for Content* challenge at CUBO+, El Salvador. Run `./dev.ps1` from the repository root and see the [technical guide](src/README.md) for details; the project documentation is in Spanish.
