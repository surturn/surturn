<!--
  Before publishing, replace:
    YOUR-LINKEDIN, YOUR-EMAIL (two places), YOUR-PORTFOLIO-URL
  Optional: point each project card at its repo instead of its route notes.
  Assets are regenerated from build.py (python3 build.py), so edit copy there rather than in the SVGs.
  Images use absolute raw URLs because GitHub does not reliably resolve relative paths inside <picture> srcset.
-->

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/header-dark.svg">
  <img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/header-light.svg" alt="Sydney Kamau. Systems engineer and founder of Invonics Technologies, Nairobi, Kenya. A transit map links his products through Invonics." width="100%">
</picture>

<p align="center">
  <a href="https://www.linkedin.com/in/sydney-kamau-991b362a2/"><img src="https://img.shields.io/badge/LinkedIn-Sydney_Kamau-1C8F82?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <a href="mailto:sydneykamau2005@gmail.com"><img src="https://img.shields.io/badge/Email-Get_in_touch-D08912?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>
  <a href="https://invonicstechnologies.com"><img src="https://img.shields.io/badge/Portfolio-FORGE-13223A?style=flat-square" alt="Portfolio"></a>
  <a href="https://github.com/surturn?tab=repositories"><img src="https://img.shields.io/badge/Repositories-Browse-4C9530?style=flat-square&logo=github&logoColor=white" alt="Repositories"></a>
</p>

## About

I build software that has to survive real conditions: patchy signal, expensive data, shared phones, and users who will never read a manual. Most of my work sits where backend architecture meets a concrete local problem, like tracking school assets, diagnosing crop disease over WhatsApp, or bringing informal traders into tax compliance.

I founded **Invonics Technologies**, a bootstrapped Nairobi software studio with a four-person founding team, shipping across edtech, fintech, agritech, and events. I'm also on industrial attachment at **Eclectics International**, a banking software vendor serving 260+ financial institutions across Africa, while studying Computer Science at **Multimedia University of Kenya**.

Every project I lead starts with a PRD, an architecture document, and a milestone plan before the first commit. I would rather explain why a system is shaped the way it is than how fast I typed it.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/now-dark.svg">
  <img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/now-light.svg" alt="Now running: AssetFlow Schools in beta across several schools; FarmAssist building the WhatsApp diagnosis channel; digital twin RAG pipeline in progress; an n8n and AI re-engagement prototype for a streaming client; open to backend engineering internships." width="100%">
</picture>

## Selected work

Each card opens its route notes below: the one design decision that matters most, and a diagram of how the pieces connect.

<p align="center">
<a href="#route-assetflow"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/assetflow-dark.svg"><img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/assetflow-light.svg" alt="AssetFlow Schools: QR asset tracking SaaS for Kenyan secondary schools, in beta" width="49%"></picture></a>
<a href="#route-eventify"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/eventify-dark.svg"><img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/eventify-light.svg" alt="Eventify: Fraud-hardened ticketing platform, in production with a partner" width="49%"></picture></a>
</p>
<p align="center">
<a href="#route-farmassist"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/farmassist-dark.svg"><img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/farmassist-light.svg" alt="FarmAssist: WhatsApp-first crop disease diagnosis for smallholder farmers" width="49%"></picture></a>
<a href="#route-risiti"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/risiti-dark.svg"><img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/risiti-light.svg" alt="Risiti: Offline-capable eTIMS compliance rail for informal B2B trade" width="49%"></picture></a>
</p>
<p align="center">
<a href="#route-lucklotter"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/lucklotter-dark.svg"><img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/lucklotter-light.svg" alt="LuckLotter: Rules-based customer retention system for a banking software vendor" width="49%"></picture></a>
<a href="#route-retail"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/retail-dark.svg"><img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/cards/retail-light.svg" alt="Retail analytics: Privacy-first edge video analytics for retail" width="49%"></picture></a>
</p>

### Route notes

<a name="route-assetflow"></a>
<details>
<summary><b>AssetFlow Schools</b>: How it's built</summary>

Every request is scoped to a single school tenant, and slow work runs in Celery so a scan at the storeroom door never waits on it.

```mermaid
flowchart LR
  A["Staff scans a QR tag"] --> B["React web app"]
  B --> C["Django API<br/>tenant-scoped"]
  C --> D[("PostgreSQL")]
  C --> E["Celery workers"]
  E <--> F[("Redis")]
  C --> G["Cloudflare R2<br/>files and images"]
  C -.-> H["Sentry + Grafana Loki"]
```

</details>

<a name="route-eventify"></a>
<details>
<summary><b>Eventify</b>: The hard part: offline gates</summary>

Two gate scanners that lose signal can each admit the same ticket. Scan logs are reconciled when devices reconnect so duplicates surface instead of slipping through.

```mermaid
flowchart LR
  S1["Gate scanner A<br/>offline"] --> L1["Local scan log"]
  S2["Gate scanner B<br/>offline"] --> L2["Local scan log"]
  L1 --> R["Reconcile on reconnect"]
  L2 --> R
  R --> C{"Same ticket<br/>scanned twice?"}
  C -->|no| OK["Admission confirmed"]
  C -->|yes| F["Flagged for review"]
```

</details>

<a name="route-farmassist"></a>
<details>
<summary><b>FarmAssist</b>: How a leaf photo becomes a diagnosis</summary>

WhatsApp retries webhooks, so every inbound message passes an idempotency check before it touches the queue. Diagnosis runs in a worker, never inside the webhook.

```mermaid
flowchart LR
  F["Farmer sends a leaf photo<br/>on WhatsApp"] --> W["Cloud API webhook"]
  W --> I{"Seen this<br/>message before?"}
  I -->|yes| X["Ignored"]
  I -->|no| R["Intent router"]
  R --> Q["BullMQ queue"]
  Q --> V["Diagnosis worker"]
  V --> O["OpenAI Vision"]
  V -.->|planned| Y["Local YOLO11s-cls"]
  V --> P[("PostgreSQL via Prisma")]
  V -.->|in progress| Rp["Reply to farmer"]
```

</details>

<a name="route-risiti"></a>
<details>
<summary><b>Risiti</b>: Offline first, compliant later</summary>

Informal traders sell where signal is unreliable. Sales are captured on the device first and synced to eTIMS when a connection returns, so compliance never blocks a sale.

```mermaid
flowchart LR
  T["Trader records a sale<br/>no signal needed"] --> Q["On-device queue"]
  Q -->|connection returns| S["Spring Boot service"]
  S <--> K["KRA eTIMS"]
  S --> RC["Compliant receipt"]
```

</details>

<a name="route-lucklotter"></a>
<details>
<summary><b>LuckLotter</b>: Why rules, not a model</summary>

Deliberately rules-based. A bank team can see exactly why a customer was flagged, which is worth more to them than a model nobody can explain.

```mermaid
flowchart LR
  T[("Transaction history")] --> B["Per-customer<br/>cadence baseline"]
  B --> D{"Current gap vs<br/>usual rhythm"}
  D -->|within rhythm| N["No action"]
  D -->|drifting| F["Retention flag"]
  F --> UI["Angular dashboard"]
```

</details>

<a name="route-retail"></a>
<details>
<summary><b>Retail analytics</b>: Privacy by architecture</summary>

Detection runs on an edge device in the shop. Only counts and events leave the premises, so there is no footage in the cloud to leak.

```mermaid
flowchart LR
  C["In-store camera"] --> E["Edge device<br/>YOLO11n"]
  E -->|counts and events only| D["Analytics dashboard"]
  E -.->|stays on device| N["Raw footage"]
```

</details>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/stack-dark.svg">
  <img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/stack-light.svg" alt="Tech stack. Languages: Kotlin, Java, Python, TypeScript, JavaScript, PHP. Backend: Spring Boot, Django, Express, Celery, BullMQ. Frontend and mobile: React, Angular, Jetpack Compose, Tailwind, Framer Motion, Three.js. Data: PostgreSQL, Redis, Prisma, Firebase. Infrastructure: Docker Compose, Cloudflare R2, Sentry, Grafana Loki. AI and automation: OpenAI API, RAG, YOLO, n8n, WhatsApp Cloud API." width="100%">
</picture>

## How I build

- **Document before code.** PRD, architecture, and milestones first, so every decision has a reason on record.
- **Design for the network we actually have.** Offline-first, idempotent, and light on data wherever the user is on a phone in the field.
- **Boring infrastructure, interesting products.** Docker Compose on a VPS, Postgres, Redis, a queue. Fewer moving parts, fewer 3am surprises.
- **Observe from day one.** Structured logs and error tracking ship with v1, not after the first outage.
- **Kill bad ideas early.** A feature cut in week one is cheaper than a rewrite in month six.

## Activity

<p align="center">
  <img src="https://raw.githubusercontent.com/surturn/surturn/HEAD/assets/metrics.svg" alt="Top languages and contribution calendar" width="480">
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/surturn/surturn/output/snake-dark.svg">
  <img src="https://raw.githubusercontent.com/surturn/surturn/output/snake-light.svg" alt="Contribution graph being eaten by a snake" width="100%">
</picture>

<br>

<p align="center">
  Off the keyboard: football, and FIFA matches I only ever lose to input lag.<br><br>
  <b>Open to backend engineering internships and collaborations on software for African markets.</b><br>
  <a href="mailto:YOUR-EMAIL">Get in touch</a>
</p>
