# Specification Quality Checklist: Database Persistence Foundation

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-04
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) beyond constraints mandated by the feature description
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders (operator-facing journeys)
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details beyond mandated constraints)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded (explicit Out of Scope section)
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification beyond mandated constraints

## Approved Architecture Change Coverage (DatasetVersion removal)

- [x] `DatasetVersion`, `DatasetVersionRun`, `datasetKey`, and Dataset grouping removed as active concepts (FR-014, FR-015, NFR-012, Out of Scope, Key Entities)
- [x] `IngestionRun` is the primary replay and lineage unit; replay by run name or run id (FR-030, US3, SC-003)
- [x] `ScrapeRun` renamed to `IngestionRun` throughout; `scrapeRunId` → `ingestionRunId`
- [x] IngestionRun has a unique readable run name: `run_<marketplace>_<condition>_<make>_<yyyyMMdd>_<HHmmss>` UTC + disambiguator (FR-011, FR-011a, assumptions, edge cases)
- [x] RawListings selected directly by `ingestionRunId`; no dataset mapping table (FR-015, FR-032)
- [x] Replay CLI: `replay --run <run-name-or-id> --normalization-version <version>` (FR-030, US3, FR-070)
- [x] Schema entities limited to MarketplaceSource, IngestionRun, RawListing, Listing, ListingSnapshot (US5, SC-005, Key Entities)
- [x] PersistenceService owns dedup, newest-wins, meaningful-change via `canonicalHash`, snapshot decision, transaction orchestration, replay run resolution — no dataset mapping (FR-005, NFR-003, NFR-009)
- [x] ADR requirement updated: IngestionRun as unit + deferral of DatasetVersion + run naming + persistence strategy/transactions (FR-071, FR-072, US6, SC-009)
- [x] Acceptance & success criteria updated (US1, US3, US5, US6, SC-001, SC-003, SC-004, SC-005, SC-007, SC-009)
- [x] Explicit Out of Scope section listing DatasetVersion, Dataset grouping, ReplayRun, scheduling, Search API, Analytics, AI, ML, Auth, Admin UI, Public API

## Previously Approved Corrections Preserved

- [x] Pipeline → PersistenceService → StorageAdapter → backend
- [x] No business rules inside adapters
- [x] `canonicalHash` (not `currentSnapshotHash`)
- [x] ListingSnapshot stores `canonicalPayload` only, not duplicated field columns
- [x] `Listing.normalizationVersion` lineage
- [x] No listing disappearance inference
- [x] `ReplayRun` out of scope
- [x] `MarketplaceSource` as reference/seeded data
- [x] Atomic per-listing persistence transactions (FR-054/055/056, NFR-010, SC-010)
- [x] Feature 001 artifacts remain frozen

## Implementation-Neutrality Coverage (revision pass)

- [x] No references to Prisma (or any specific ORM/query builder/library) as a required technology (FR-001, FR-002, FR-060, NFR-003, SC-007, R-002, Assumptions, Dependencies, Pipeline Model)
- [x] PostgreSQL/Supabase required as the production relational database; a relational persistence implementation required behind the StorageAdapter
- [x] Ingestion pipeline and PersistenceService MUST remain independent of any specific ORM, query builder, or database library (FR-060, NFR-003)
- [x] Technology selection (Prisma or any alternative) deferred to the implementation plan, not the specification (FR-002, Assumptions, Dependencies)

## Canonical Hash Future-Proofing Coverage (revision pass)

- [x] Canonical hash defined as deterministically generated from the complete canonical listing state (FR-023, Assumptions)
- [x] Deterministic, order-independent where applicable, any meaningful change produces a different canonical hash (FR-023)
- [x] Hardcoded example field lists (price/mileage/title/location) removed from FRs, Assumptions, Risks, Success Criteria, Edge Cases
- [x] Exact list of canonical fields participating in the hash is an implementation detail determined during planning (FR-023, Assumptions)
- [x] "canonical snapshot hash" wording normalized to "canonical hash" throughout

## Notes

- PostgreSQL/Supabase is the production relational database target. The choice of ORM, query builder, or database library is an implementation decision for the implementation plan, not this specification; the ingestion pipeline and PersistenceService remain independent of that choice.
- The canonical hash is defined by behavior (deterministic, complete canonical state, order-independent, change-sensitive), not by a hardcoded field list. The exact participating fields are determined during planning.
- The exact run-name slug rules and collision disambiguator are bounded to planning + an ADR (FR-011a/FR-071).
- Listing lifecycle / disappearance management and DatasetVersion/Dataset grouping are intentionally deferred to future features.
- Items marked complete pass validation. The spec is ready for `/speckit-clarify` or `/speckit-plan`.