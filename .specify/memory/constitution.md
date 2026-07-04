<!--
=== Sync Impact Report ===
Version change: 1.0.0 → 1.1.0
Rationale: MINOR bump — one new core principle added (Analytics Before AI)
plus materially expanded guidance in ML explainability, AI governance, and
data freshness. No existing principle was removed or redefined in a
backward-incompatible way. Renumbering of principles IX–XV → X–XVI is a
consequence of the insertion and is reflected throughout the document.

Modified principles:
  - III. Domain-Driven Architecture — the bounded-context addition rule was
    relaxed from "new bounded contexts require a constitution amendment" to
    "architecture review + SAD update + documentation update". The
    constitution is no longer amended solely because a new bounded context
    is introduced; it remains stable while the architecture evolves.
  - Machine Learning as a Product Feature (was IX, now X) — added a
    mandatory explainability requirement: feature importance, per-prediction
    feature contribution, and model-appropriate explainability techniques.
    Users must understand WHY a prediction was produced, not only the price.

Added principles:
  - IX. Analytics Before AI — new core principle, inserted after
    "VIII. AI Assists, Never Invents" and before Machine Learning as a
    Product Feature. Establishes analytics as first-class citizens, AI as a
    consumer of analytics (never a replacement), and deterministic
    analytical queries as the authoritative source for business insights.

Added subsections:
  - AI & Machine Learning Governance → "Deterministic Backend Over
    Free-Form Reasoning": the AI must prefer deterministic backend services
    over free-form reasoning and retrieve information via backend APIs /
    analytics services rather than inferring or generating answers
    directly. LLMs are interpreters of platform intelligence, not
    independent sources of truth.
  - Data Engineering Principles → "Data Freshness": every analytical
    response must expose last_updated, dataset_version, and scrape_run_id;
    analytics must never appear real-time when generated from historical
    snapshots.

Renumbering (insertion-driven; no semantic change to existing rules):
  - IX  Machine Learning as a Product Feature  → X
  - X   Data Quality Before Intelligence        → XI
  - XI  Scalability by Design                   → XII
  - XII Backend-Centric Business Logic          → XIII
  - XIII Modularity                             → XIV
  - XIV Security by Default                     → XV
  - XV  Simplicity Over Complexity              → XVI

Cross-references updated:
  - AI & ML Governance intro: "Principles VIII and IX" → "VIII, IX, and X".
  - Data Engineering Principles intro: "Principles VI, VII, and X" → "VI, VII, and XI".
  - Definition of Done: "Security controls (Principle XIV)" → "(Principle XV)".

Removed sections: None.

Templates requiring updates:
  - .specify/templates/plan-template.md        — ✅ compatible (Constitution Check gate is generic)
  - .specify/templates/spec-template.md         — ✅ compatible (functional/requirements slots generic)
  - .specify/templates/tasks-template.md        — ✅ compatible (foundational phase already covers
                                                   schema, auth, error handling, logging, env config)
  - .specify/templates/commands/*.md            — ✅ N/A (no commands directory present)
  - AGENTS.md / docs/prd.md                     — ✅ compatible (no principle references to update)

Follow-up TODOs: None.
===
-->

# PrioraMarket Intelligence Constitution

This constitution is the supreme engineering governance document for the
PrioraMarket Intelligence platform. It binds every specification, design
artifact, implementation plan, task, and line of generated code. Where any
artifact, decision, or practice conflicts with this constitution, the
constitution prevails.

PrioraMarket Intelligence is an **Automotive Market Intelligence Platform**.
Its mission is to continuously collect, organize, analyze, and understand
automotive marketplace data in order to generate market insights, analytics,
and AI-powered price predictions. It is **not** a marketplace, a dealer
management system, an ERP, a CRM, an inventory management system, or an
accounting system.

**Data quality is the primary product asset.** Features, analytics, AI
assistants, and machine learning models derive their value from accurate,
consistent, and historical data. Every engineering decision MUST prioritize
preserving data integrity, lineage, and reproducibility over short-term
implementation convenience.

## Core Principles

### I. Documentation First

The specification artifacts — PRD, SAD, DATA_MODEL, API_SPEC, and
FRONTEND_ARCHITECTURE — are the single source of truth for the platform.

- Implementation MUST NEVER contradict approved documentation.
- Documentation MUST be updated BEFORE implementation when requirements,
  contracts, data shapes, or architecture change.
- "Code is the truth" is rejected as a governance posture: code is the
  *execution* of the truth, documentation is the *statement* of it.
- Drift between documentation and implementation is a defect and MUST be
  remediated by reconciling the documentation, not by silently accepting
  the implementation.

**Rationale**: A multi-domain platform with AI/ML components cannot be
reasoned about, audited, or safely evolved from code alone. Documentation is
the contract between domains, teams, and time.

### II. Design Before Implementation

The mandatory workflow is:

```text
PRD → SAD → Specification → Tasks → Implementation
```

- No implementation MAY begin without approved analysis and design
  artifacts for the feature in question.
- Skipping or reordering these stages is a constitution violation, even
  when the change appears trivial.
- "Spike" or exploratory work is permitted but MUST be labeled as such and
  MUST NOT be promoted to production code without passing through the
  workflow.

**Rationale**: Design errors are orders of magnitude cheaper to correct
than implementation errors. The gate exists to force intent before action.

### III. Domain-Driven Architecture

Architecture MUST be organized around business domains rather than technical
layers. The canonical bounded contexts are:

- Data Ingestion
- Marketplace Listings
- Search
- Analytics
- AI Assistant
- Price Prediction
- Administration

- Every feature belongs to **exactly one** bounded context.
- Cross-context collaboration happens via published APIs or domain events,
  never via direct access to another context's internals.
- Adding a new bounded context requires:
  - Architecture review.
  - An update to the System Analysis & Design (SAD).
  - Documentation update across affected artifacts.
- The constitution MUST NOT be amended solely because a new bounded context
  is introduced. The constitution remains stable while the architecture is
  allowed to evolve.

**Rationale**: Domain boundaries preserve autonomy, limit coupling, and keep
each context's data model coherent with its business meaning.

### IV. Clean Layered Architecture

Within each backend bounded context, responsibilities MUST be separated into:

- **Controller** — request/response handling, input validation, HTTP concerns.
- **Service** — business rules and orchestration.
- **Repository** — persistence only.
- **DTO** — data transfer shapes at the API boundary.

Non-negotiable rules:

- No business logic inside controllers.
- No database logic inside services.
- Repositories only perform persistence; they contain no business rules.
- DTOs MUST NOT leak into services or repositories as domain entities, and
  domain entities MUST NOT be returned directly from controllers.

**Rationale**: Layer discipline keeps business rules testable, replaceable,
and independent of transport and storage technology.

### V. API First

Every platform capability MUST be available through versioned REST APIs.

- Frontend, AI Assistant, CLI tools, and future mobile applications all
  consume the **same** APIs. No capability is granted to one client through
  a private channel that is unavailable to others.
- Business logic MUST NEVER exist outside backend services. Clients are
  consumers, not implementers, of business rules.
- APIs MUST be versioned (e.g., `/api/v1/...`) and version compatibility
  MUST be documented in the API_SPEC.

**Rationale**: A single API surface guarantees consistency, auditability,
and a uniform security/permissions boundary across all consumers.

### VI. Database as Source of Truth

Marketplace websites (e.g., Dubizzle) are **external data providers**, not
authoritative sources. Once data is ingested, the internal database becomes
the official source of truth.

- Queries, analytics, AI assistants, and ML models MUST use internal data.
- Live calls to external marketplaces MUST NOT serve analytical, search, or
  prediction requests; they are confined to the ingestion pipeline.
- External schema or availability changes MUST NOT break downstream
  consumers, because downstream consumers depend on the internal schema.

**Rationale**: External sources are unreliable, mutable, and uncontrolled.
Intelligence requires a stable, governed, internally-owned dataset.

### VII. Historical Data Preservation

Historical marketplace data is a core business asset. The platform MUST
preserve:

- **Listing snapshots** — immutable point-in-time captures of a listing.
- **Scrape runs** — metadata and outcomes of every ingestion execution.
- **Price history** — the full sequence of price observations per listing.
- **Listing lifecycle** — creation, modification, delisting, and removal
  events over time.

- Updates MUST NEVER destroy historical data. New observations are appended;
  prior observations are retained.
- Deletion of historical records is forbidden except under an explicit,
  documented, governance-approved retention policy.

**Rationale**: Trend, depreciation, and prediction all depend on time
series. Destroying history destroys the ability to understand the market.

### VIII. AI Assists, Never Invents

AI explanations MUST always be generated from platform analytics and stored
data.

- The AI MUST NEVER fabricate prices, statistics, or market information.
- Every AI response MUST be explainable and traceable to specific stored
  records, aggregations, or model outputs.
- AI outputs MUST cite or reference the underlying data sources that
  produced them; uncitable assertions are prohibited.
- When data is insufficient to answer, the AI MUST say so rather than
  hallucinate a plausible answer.

**Rationale**: An intelligence platform whose AI lies once is permanently
untrustworthy. Traceability is the foundation of user trust.

### IX. Analytics Before AI

Analytics are first-class citizens of the platform.

- AI consumes analytics; AI NEVER replaces analytics.
- Every AI insight MUST be reproducible using deterministic analytical
  queries.
- SQL, analytical pipelines, and statistical calculations remain the
  authoritative source for business insights.
- AI exists to explain, summarize, and communicate analytics — not to
  invent or replace them.

**Rationale**: Deterministic analytics are auditable, repeatable, and
governable; free-form AI reasoning is not. Anchoring AI to analytics keeps
the platform's intelligence verifiable and confines the AI to the role of
interpreter rather than oracle.

### X. Machine Learning as a Product Feature

Machine learning models are first-class citizens of the platform, not
experiments bolted on after delivery.

- Models MUST be **versioned**.
- Models MUST be **reproducible** from a recorded training dataset and
  configuration.
- Models MUST **record their training datasets** (dataset version, row
  count, feature set, time window).
- Models MUST **expose confidence scores** (or calibrated uncertainty) with
  every prediction.
- Models MUST NEVER silently replace previous models; promotion is an
  explicit, recorded, reversible action.
- Prediction MUST always expose uncertainty; a point estimate without a
  confidence/interval is non-compliant.
- Models MUST expose explainability whenever technically feasible. The
  platform MUST support:
  - Feature importance.
  - Feature contribution per prediction.
  - Explainability techniques appropriate for the selected model.
- The objective is that users understand WHY a prediction was produced,
  not only the predicted price.

**Rationale**: Predictions drive business decisions. Unmanaged models are
unknowable, unfixable, and untrustworthy. A price without an explanation is
a claim; a price with traceable feature contributions is intelligence.

### XI. Data Quality Before Intelligence

Analytics quality depends on data quality. Before generating analytics or
training models, the platform MUST validate:

- **Duplicates**
- **Missing values**
- **Invalid records**
- **Inconsistent values**
- **Outliers**

- Data cleaning MUST be documented: what was removed, transformed, or
  imputed, and why.
- Analytics and models MUST NOT be produced from unvalidated datasets.
- Data quality rules are themselves versioned artifacts.

**Rationale**: Intelligence built on dirty data is confidently wrong. Data
quality is the precondition for every higher-order capability.

### XII. Scalability by Design

Architecture MUST support future expansion to:

- **Multiple marketplaces** (not only Dubizzle).
- **Multiple countries.**
- **Additional vehicle categories.**
- **Additional ML models.**
- **Additional AI capabilities.**

- No implementation MAY assume Dubizzle is the only supported marketplace.
  All ingestion, storage, and analytical code MUST be marketplace-agnostic
  with marketplace-specific behavior isolated behind explicit adapters.
- Adding a marketplace, country, category, model, or AI capability MUST be
  achievable without rewriting bounded contexts.

**Rationale**: Hard-coding today's assumption blocks tomorrow's market.
Generality in the right places is a feature, not gold-plating.

### XIII. Backend-Centric Business Logic

**Frontend responsibilities** are strictly:

- Rendering
- Forms
- API communication

**Backend responsibilities** are strictly:

- Business rules
- Analytics
- Filtering
- Searching
- Permissions
- AI orchestration
- ML orchestration

- The frontend MUST NOT compute business-relevant results; it displays
  results computed by the backend.
- Filtering, sorting, and search logic MUST execute on the backend. Client-
  side filtering is a presentation convenience only and MUST not be the
  source of truth for what the user "sees" versus what exists.

**Rationale**: Business rules duplicated in the client diverge from the
server, produce inconsistent results, and bypass permissions and audit.

### XIV. Modularity

- Every feature/module MUST have a single responsibility.
- Modules communicate ONLY through public APIs (or published domain
  events). Internal data structures, private helpers, and storage layout
  are not part of a module's public surface.
- Implementation details remain private; consumers depend on contracts,
  not internals.
- A module's public API is the only stable surface; changing it is a
  versioned, documented act.

**Rationale**: Private internals + public contracts enable independent
evolution and replaceability across the platform.

### XV. Security by Default

The platform MUST enforce, from day one:

- **Authentication** — verified identity for all non-public access.
- **Authorization** — role/permission checks on every capability.
- **Rate limiting** — protection of APIs and ingestion endpoints.
- **Secure secrets management** — no secrets in code, logs, or repos.
- **Environment configuration** — environment-driven, not hard-coded.
- **Audit logging** — tamper-evident records of security-relevant actions.
- **Validation** — all inputs validated at trust boundaries.
- **Protection against malformed external data** — ingestion treats all
  external marketplace data as untrusted and validates/sanitizes it before
  persistence or processing.

**Rationale**: An intelligence platform handling commercial data and
external input is a target. Security is a precondition, not a phase.

### XVI. Simplicity Over Complexity

The platform is a **Market Intelligence Platform**. It is NOT:

- A marketplace
- A dealer management system
- An ERP
- A CRM
- An inventory management system
- An accounting system

- Every feature MUST improve market understanding. Features that do not
  advance collection, organization, analysis, or understanding of
  automotive market data are out of scope.
- When two designs satisfy a requirement, the simpler one MUST be chosen
  unless the more complex one is justified against this constitution and
  recorded in the plan's Complexity Tracking section.
- YAGNI applies: do not build for capabilities not required by an approved
  specification.

**Rationale**: Scope creep into adjacent business systems dilutes the
platform's purpose and multiplies maintenance cost without adding
intelligence value.

## Cross Cutting Requirements

These requirements apply to every bounded context, every feature, and every
layer without exception.

### Documentation Alignment

- All artifacts (PRD, SAD, DATA_MODEL, API_SPEC, FRONTEND_ARCHITECTURE,
  specs, plans, tasks) MUST remain mutually consistent.
- A change in one artifact that affects another MUST propagate to that
  artifact within the same feature cycle.
- The `/speckit-analyze` consistency check MUST pass before a feature is
  considered done.

### Coding Conventions

- A single, enforced code style per language (formatter + linter) MUST be
  configured and run in the project.
- Naming, file layout, and layering conventions derive from this
  constitution (Principles III, IV, XIII) and MUST be applied uniformly.
- No code MAY be merged with lint/format violations.

### Testing Strategy

- **Unit tests** for services and domain logic.
- **Integration tests** for repository and cross-layer behavior.
- **Contract tests** for every published API endpoint.
- **Data quality tests** asserting validation rules over ingested data.
- **Model evaluation tests** asserting that a trained model meets its
  recorded performance thresholds before promotion.
- Tests MUST fail before the implementation they guard is written
  (Red-Green), per the spec/task workflow.

### Configuration Management

- All environment-specific values (DB URLs, credentials, marketplace
  endpoints, model paths) MUST be externally configurable.
- Default configurations MUST be safe for local development and MUST NOT
  expose production secrets.

### Environment Variables

- A `.env` template (or equivalent) MUST list every required variable
  with a description and a non-secret placeholder.
- The application MUST fail fast with a clear message when a required
  variable is missing.
- Secrets MUST NEVER be committed to version control.

### Logging

- Structured logging MUST be used (machine-parseable JSON or equivalent).
- Logs MUST include: timestamp, severity, bounded context, operation, and
  a correlation/request identifier.
- Sensitive data (credentials, full marketplace HTML where it contains
  PII) MUST NOT be logged at INFO or below.

### Error Handling

- Errors are categorized into **domain errors** (business-meaningful) and
  **infrastructure errors** (transport/persistence failures).
- Controllers MUST translate errors into consistent, versioned API error
  responses; internal stack traces MUST NOT leak to clients.
- Services MUST raise domain-specific errors; they MUST NOT swallow
  exceptions silently.

### Versioning

- **API**: URI-versioned (`/api/v1/...`); breaking changes require a new
  major version with a documented deprecation path.
- **Data schema**: backward-compatible migrations by default; breaking
  migrations require a constitution-compliant migration plan.
- **ML models**: explicit `model@version` identifiers; never overwritten.
- **Constitution**: semantic versioning per Governance.

### Migration Strategy

- Every schema change MUST have a reversible migration with up and down
  paths.
- Migrations MUST be ordered, timestamped, and idempotent.
- Historical data (Principle VII) MUST be preserved across migrations;
  migrations that would destroy history are prohibited.

### API Compatibility

- Within a major API version, breaking changes are forbidden; additive
  changes are permitted.
- Removed or renamed fields, changed types, and changed semantics all
  constitute breaking changes and require a new major version.
- Deprecation MUST be documented and announced before removal.

## Development Workflow

### Analysis Gate

- Before any design or implementation, a feature MUST pass the Analysis
  Gate: the problem is understood, the affected bounded context(s) are
  identified, and the data-quality and historical-preservation
  implications are stated.
- The Analysis Gate is recorded in the feature's research artifact.

### Specification Driven Development

- Features are driven by approved specifications (`spec.md`) generated via
  the `/speckit-specify` workflow.
- No implementation task MAY be created or executed without an approved
  spec and plan.

### Feature Branches

- All work occurs on feature branches created via `/speckit-git-feature`
  (e.g., `###-feature-name`).
- Direct commits to the main branch are prohibited.
- Branches MUST be validated via `/speckit-git-validate` before merge.

### Constitution Review Gates

- **Gate 1 — Plan**: the implementation plan MUST include a Constitution
  Check verifying the design against all 15 principles; violations MUST be
  justified in Complexity Tracking or removed.
- **Gate 2 — Tasks**: tasks MUST reflect layer discipline (IV), testing
  strategy, and data-quality requirements.
- **Gate 3 — Implementation**: implementation MUST be checked against the
  constitution before merge; non-conformant code is rejected.

### Definition of Ready

A feature is **Ready** when:

- Approved PRD/SAD context exists or is produced.
- `spec.md` is approved with prioritized, independently testable user
  stories.
- Affected bounded context(s) and data-quality implications are identified.
- Constitution Check on the plan passes or violations are justified.

### Definition of Done

A feature is **Done** when:

- All acceptance scenarios pass.
- Unit, integration, contract, and applicable data-quality/model tests
  pass.
- Documentation (PRD/SAD/DATA_MODEL/API_SPEC/FRONTEND_ARCHITECTURE) is
  updated and consistent (`/speckit-analyze` passes).
- Historical data and data-lineage requirements are satisfied.
- Security controls (Principle XV) are in place.
- Code is lint/format clean and merged from a validated feature branch.
- Any constitution violations are explicitly justified and recorded.

## AI & Machine Learning Governance

This section governs every AI assistant capability and every machine
learning model on the platform. It operationalizes Principles VIII, IX,
and X.

### Deterministic Backend Over Free-Form Reasoning

- The AI MUST always prefer deterministic backend services over free-form
  reasoning.
- Whenever structured platform data exists, the AI MUST retrieve
  information through backend APIs or analytics services rather than
  attempting to infer or generate answers directly.
- LLMs are interpreters of platform intelligence, not independent sources
  of truth.

**Rationale**: Deterministic services are reproducible and governable;
free-form LLM reasoning is not. Routing the AI through backend services
keeps every answer traceable to stored data and prevents the model from
inventing facts.

### Dataset Versioning

- Every dataset MUST be versioned (`dataset@version`) and stored
  immutably; subsequent changes produce a new version, not an overwrite.
- Dataset versions MUST record: source listings, time window, filter
  rules, cleaning steps, and row counts.
- Training MUST reference a specific dataset version.

### Feature Engineering

- Feature definitions MUST be code, not notebooks, and MUST be versioned
  alongside the model that uses them.
- Feature transforms MUST be deterministic and reproducible from the
  recorded dataset version.
- Feature lineage (input columns → derived features) MUST be documented.

### Model Training

- Training runs MUST be reproducible: dataset version, feature set,
  hyperparameters, random seed, and code version all recorded.
- Training MUST be executable as a pipeline command, not a manual
  interactive session, for any model promoted to production.

### Model Evaluation

- Every model MUST pass recorded evaluation thresholds (e.g., MAPE, MAE,
  R²) on a held-out, time-aware test split before promotion.
- Evaluation results MUST be stored with the model artifact.
- A model that fails its thresholds MUST NOT be promoted.

### Model Deployment

- Promotion to production is an explicit, recorded action; it MUST NEVER
  silently replace a serving model.
- The serving model MUST be identifiable by `model@version` at request
  time, and that identifier MUST be returned with predictions.
- Rollout MAY be staged (shadow / canary), but the active version MUST
  always be unambiguous.

### Prediction Confidence

- Every prediction MUST include a confidence score or calibrated
  uncertainty interval.
- Predictions without uncertainty are non-compliant and MUST NOT be served.
- Confidence MUST be derivable from stored model metadata, not invented at
  request time.

### Experiment Tracking

- Every training run (successful or not) MUST be logged in the experiment
  tracker with inputs, parameters, metrics, and artifact references.
- Experiment records are historical artifacts (Principle VII) and MUST NOT
  be deleted.

### Model Rollback

- Any promoted model MUST be rollback-eligible to the previous version
  within a single, documented command.
- Rollback MUST NOT require retraining.
- Rollback events MUST be audit-logged.

## Data Engineering Principles

This section governs the Data Ingestion bounded context and any pipeline
that moves marketplace data into the platform. It operationalizes
Principles VI, VII, and XI.

### Incremental Ingestion

- Ingestion MUST be incremental: only new or changed listings are fetched
  per run, scoped by marketplace, category, and time window.
- Full re-ingestion is permitted only as a documented, explicitly
  triggered operation.

### Idempotent Scraping

- A scrape run re-executed with the same parameters MUST produce the same
  stored state, without duplicating records.
- Ingestion MUST be safe to retry after partial failure.

### UUID-Based Deduplication

- Listings MUST be deduplicated by stable, marketplace-independent
  identifiers (UUIDs derived from marketplace + marketplace-native id).
- Internal identifiers MUST NOT depend on ephemeral marketplace URLs or
  listing positions.

### Historical Snapshots

- Each ingestion MUST persist an immutable listing snapshot at the time of
  observation.
- Snapshots are append-only; a changed price or attribute creates a new
  snapshot, it does not overwrite the prior one.

### Data Lineage

- Every stored record MUST be traceable to its source: scrape run,
  marketplace, raw payload, ingestion timestamp, and transform version.
- Lineage metadata is mandatory, not optional.

### Raw JSON Preservation

- The raw payload received from the marketplace MUST be preserved verbatim
  (raw JSON) alongside the normalized record.
- Normalization MUST NEVER destroy the original payload; the raw form is
  the ground truth for re-processing and audit.

### Normalized Analytical Schema

- A normalized analytical schema MUST be maintained for analytics and ML,
  derived deterministically from raw payloads.
- The analytical schema is the contract between Data Ingestion and
  Analytics/Price Prediction.

### Reproducible ETL

- ETL steps MUST be code, parameterized by dataset/run identifiers, and
  re-runnable.
- Re-running an ETL step on the same inputs MUST produce the same outputs.
- ETL transformations are versioned artifacts; changing a transform
  produces a new version, not an in-place mutation.

### Data Freshness

Market intelligence depends on data freshness.

- Every analytical response produced by the platform MUST expose metadata
  including:
  - `last_updated`
  - `dataset_version`
  - `scrape_run_id`
- Users MUST always know how recent the data is.
- Analytics MUST NEVER appear real-time when they are generated from
  historical snapshots.

**Rationale**: A price trend computed from a snapshot taken days ago is not
a live market reading. Surfacing freshness metadata prevents users from
acting on stale intelligence as if it were current.

## Governance

### Supremacy

- This constitution supersedes every other engineering practice, convention,
  or precedent on the PrioraMarket Intelligence project.
- Where a spec, plan, task, or code change conflicts with this constitution,
  the constitution prevails; the conflicting artifact MUST be reconciled or
  the change rejected.
- No agent, contributor, or tool MAY waive a principle locally; waivers
  require an amendment (below).

### Amendment Process

- Amendments MUST be proposed as a written change to this document with:
  - The principle/section affected.
  - Rationale.
  - Affected artifacts (templates, specs, plans, code).
  - Migration plan for any non-conformant existing work.
- Amendments MUST pass a Constitution Review Gate before adoption.
- Adoption updates `LAST_AMENDED_DATE` and bumps `CONSTITUTION_VERSION`
  per semantic versioning.
- All dependent templates MUST be re-synced in the same change (per the
  Sync Impact Report process).

### Semantic Versioning

The constitution version follows MAJOR.MINOR.PATCH:

- **MAJOR** — backward-incompatible governance: principle removals or
  redefinitions that invalidate existing specs/plans/code.
- **MINOR** — new principle or section added, or materially expanded
  guidance that adds new obligations.
- **PATCH** — clarifications, wording, typo fixes, non-semantic refinements.

First adopted constitution is `1.0.0`.

### Compliance Review

- Every feature plan MUST include a Constitution Check.
- Every merge MUST be reviewable for constitution compliance; reviewers
  MAY block merges on constitutional grounds.
- The `/speckit-analyze` cross-artifact analysis MUST pass before Done.
- Non-compliance found post-merge MUST be tracked as a defect and
  remediated by reconciling to the constitution, not by amending the
  constitution to legitimize the drift.

**Version**: 1.1.0 | **Ratified**: 2026-07-04 | **Last Amended**: 2026-07-04