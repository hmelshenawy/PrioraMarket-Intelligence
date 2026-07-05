# Feature Specification: Canonical Data Model & Vehicle Reference Catalog

**Feature Branch**: `003-backend-search-api`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Canonical Data Model & Vehicle Reference Catalog for canonical operational categorical values, normalized listing values, preserved raw marketplace payloads, reference catalog synchronization, safe backfill, and future generation classification readiness."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persist Canonical Operational Data (Priority: P1)

As a PrioraMarket ingestion operator, I need every normalized listing to store stable canonical values for supported categorical operational fields so that search, filtering, grouping, future classification, and reporting do not depend on inconsistent marketplace names or display labels.

**Why this priority**: Canonical listing values are the foundation for all downstream read-only behavior, presentation independence, and future market intelligence.

**Independent Test**: Can be fully tested by processing representative marketplace categorical values and verifying that normalized listing categorical values are deterministic canonical keys while the original marketplace payload remains unchanged.

**Acceptance Scenarios**:

1. **Given** marketplace make values `Mercedes Benz`, `Mercedes-Benz`, and `Mercedes`, **When** listings are normalized, **Then** the listing make value is stored as `mercedesbenz` for all catalog-supported aliases and deterministic variants.
2. **Given** marketplace model values `C Class` and `C-Class`, **When** listings are normalized, **Then** the listing model value is stored as `cclass` for both inputs.
3. **Given** marketplace values `Land Rover` and `7 Series`, **When** listings are normalized, **Then** the listing values are stored as `landrover` and `7series` respectively.
4. **Given** supported marketplace categorical fields such as trim, fuel type, transmission, body type, seller type, vehicle condition, specs, or color, **When** listings are normalized, **Then** those fields use deterministic canonical values where applicable while numeric values and free-text fields remain unchanged.
5. **Given** an unknown marketplace categorical value, **When** no catalog alias exists, **Then** the value is canonicalized deterministically without fuzzy matching, guessing, or correction.

---

### User Story 2 - Maintain Reference Catalog as Source of Truth (Priority: P1)

As a data steward, I need the Vehicle Reference Catalog to define canonical keys, display values, generation details, market-specific metadata, aliases, and confidence so that all marketplace-independent vehicle identity decisions come from one managed reference catalog.

**Why this priority**: A single source of truth prevents backend, presentation, ingestion, and analytics logic from each inventing their own vehicle naming or display rules.

**Independent Test**: Can be fully tested by reviewing catalog entries and confirming that canonical keys, display names, aliases, generation metadata, and confidence are present and can represent multiple markets.

**Acceptance Scenarios**:

1. **Given** a Vehicle Reference Catalog entry, **When** the entry is reviewed, **Then** it contains market, make key, make display, model key, model display, generation, body code, year range, facelift year range, aliases, and confidence.
2. **Given** a listing with canonical make and model keys, **When** presentation values are needed, **Then** display names come from the Vehicle Reference Catalog rather than formatting or reconstructing canonical keys.
3. **Given** operational logic for search, filtering, grouping, analytics preparation, or future classification, **When** it references vehicle identity, **Then** it uses canonical keys instead of display values.
4. **Given** presentation layers need vehicle labels, **When** they display canonical values such as `mercedesbenz` or `cclass`, **Then** they show catalog display values such as `Mercedes-Benz` or `C-Class` from the Vehicle Reference Catalog.

---

### User Story 3 - Synchronize Catalog from Reference Files (Priority: P2)

As a data steward, I need CSV reference files to safely synchronize the Vehicle Reference Catalog so that catalog updates are repeatable, reviewable, and consistent across environments.

**Why this priority**: The catalog must be easy to extend with additional brands, models, markets, generations, and aliases without introducing marketplace-specific backend logic.

**Independent Test**: Can be fully tested by applying the same reference file set multiple times and confirming the catalog result is identical each time.

**Acceptance Scenarios**:

1. **Given** a valid CSV reference file containing catalog rows, **When** synchronization is performed, **Then** the Vehicle Reference Catalog reflects those rows without duplicating existing entries.
2. **Given** the same reference file is synchronized repeatedly, **When** no source data has changed, **Then** the catalog remains unchanged after the first successful synchronization.
3. **Given** reference file rows for additional marketplaces, **When** synchronization is performed, **Then** catalog entries remain distinguishable by market while preserving shared canonical make and model identity.
4. **Given** a catalog value differs between the CSV reference files and the synchronized database copy, **When** authoritative ownership is evaluated, **Then** the CSV reference files are treated as the source of truth.

---

### User Story 4 - Backfill Existing Listings Safely (Priority: P2)

As a platform operator, I need existing listings to be backfilled to canonical values in a repeatable, idempotent, safe-to-rerun, non-destructive way so that current data becomes compatible with the new foundation without altering original payloads, identifiers, or historical records.

**Why this priority**: Existing marketplace data must participate in canonical search and analytics without losing auditability or historical continuity.

**Independent Test**: Can be fully tested by running backfill multiple times on a representative existing listing set and verifying canonical values remain consistent while raw payloads, listing identifiers, and historical metadata are preserved.

**Acceptance Scenarios**:

1. **Given** existing listings with inconsistent marketplace make and model values, **When** backfill is performed, **Then** their normalized listing values are populated with canonical keys.
2. **Given** existing raw listing payloads, **When** backfill is performed, **Then** every raw payload remains byte-for-byte unchanged.
3. **Given** existing listing identifiers and historical records, **When** backfill is performed, **Then** identifiers and history remain preserved.
4. **Given** the same backfill is rerun without source changes, **When** backfill completes, **Then** normalized listing values remain consistent and no duplicate, conflicting, or destructive changes are introduced.

### Edge Cases

- Marketplace values containing leading or trailing whitespace are trimmed before canonical keys are produced.
- Marketplace values containing spaces, hyphens, underscores, punctuation, or mixed capitalization produce the same canonical key when their remaining characters match.
- Canonicalization removes formatting differences but preserves semantic letters and numbers, so values such as `C200`, `E53 AMG`, `GLC300 Coupe`, and `7 Series` become `c200`, `e53amg`, `glc300coupe`, and `7series`.
- Alias values such as `Mercedes`, `VW`, and `Chevy` map to explicit canonical keys only when present on matching Vehicle Reference Catalog records.
- Unknown aliases are not rejected; they are canonicalized by deterministic rules, reported for operational monitoring, and remain available for later catalog improvement.
- Raw marketplace payloads remain unchanged even when normalized listing values are corrected or backfilled.
- Catalog synchronization is repeatable and does not duplicate entries when the same source rows are applied more than once.
- Backfill is repeatable and safe to rerun without creating inconsistent normalized data.
- The foundation prepares normalized listings and catalog metadata for future generation classification, but this feature does not classify listings into generations.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST store canonical values in normalized listing records for supported categorical operational fields, including make, model, trim, fuel type, transmission, body type, seller type, vehicle condition, specs, and color.
- **FR-002**: The system MUST leave numeric values and free-text fields unchanged except for existing normalization unrelated to categorical canonicalization.
- **FR-003**: The system MUST preserve the original marketplace payload in raw listing records without modification during ingestion, normalization, catalog synchronization, or backfill.
- **FR-004**: The system MUST canonicalize supported categorical values by trimming whitespace, lowercasing, and removing spaces, hyphens, underscores, and punctuation.
- **FR-005**: Canonicalization MUST remove formatting differences only and MUST preserve semantic letters and numbers that carry business meaning, including examples such as `C200` to `c200`, `E53 AMG` to `e53amg`, `GLC300 Coupe` to `glc300coupe`, and `7 Series` to `7series`.
- **FR-006**: The system MUST apply canonicalization deterministically with no fuzzy matching, automatic correction, artificial intelligence matching, guessing, OCR, VIN decoding, or valuation logic.
- **FR-007**: The Vehicle Reference Catalog MUST own alias resolution through aliases stored on catalog records for values that canonicalization alone cannot resolve, including aliases such as `Mercedes` to `mercedesbenz`, `VW` to `volkswagen`, and `Chevy` to `chevrolet`.
- **FR-008**: The system MUST canonicalize unknown values using the standard deterministic rules when no catalog-owned alias exists.
- **FR-009**: Unknown marketplace values encountered during ingestion, including unknown makes, models, trims, and fuel types, MUST be exposed through operational normalization statistics for catalog improvement without blocking ingestion.
- **FR-010**: Normalized listing records MUST retain the canonicalization or normalization rule version used when they were processed to support deterministic replay, safe future rule changes, repeatable backfills, debugging, and operational traceability.
- **FR-011**: The Vehicle Reference Catalog, represented by `vehicle_reference_catalog` when referring to the database object, MUST serve as the single source of truth for canonical vehicle identity, display names, vehicle generations, and market-specific vehicle metadata.
- **FR-012**: Canonical keys MUST be stable identifiers and MUST NOT be renamed or changed once introduced; display values may evolve over time without changing canonical identity.
- **FR-013**: Canonical keys such as `mercedesbenz` and `cclass` MUST remain stable to avoid breaking analytics, search, filters, URLs, caches, integrations, and future APIs.
- **FR-014**: All systems that need vehicle naming, display, generation metadata, or market-specific vehicle metadata MUST consume the Vehicle Reference Catalog rather than implementing independent naming logic.
- **FR-015**: Each Vehicle Reference Catalog entry MUST include market, make key, make display, model key, model display, generation, body code, start year, end year, facelift start year, facelift end year, aliases, and confidence.
- **FR-016**: Display values MUST be used only for presentation and MUST come from the Vehicle Reference Catalog.
- **FR-017**: Operational systems for search, filtering, grouping, analytics preparation, and future classification MUST use canonical keys rather than display values.
- **FR-018**: Presentation consumers MUST use display values from the Vehicle Reference Catalog and MUST NOT reconstruct names from canonical keys.
- **FR-019**: Display values such as `Mercedes-Benz` and `C-Class` MUST be available to presentation consumers for canonical values such as `mercedesbenz` and `cclass`.
- **FR-020**: All ingestion flows MUST normalize and canonicalize extracted marketplace values before persisting normalized listing records.
- **FR-021**: The foundation flow MUST follow the business sequence: raw marketplace payload, extraction, normalization, canonicalization, listing persistence, Vehicle Reference Catalog synchronization, ready for future classification.
- **FR-022**: The system MUST provide a catalog synchronization capability where CSV reference files are the source used to update the Vehicle Reference Catalog.
- **FR-023**: CSV reference files MUST be treated as the source of truth, and the database catalog MUST be treated as a synchronized copy rather than the authoritative source.
- **FR-024**: Manual database editing of catalog values MUST be discouraged and MUST NOT be considered authoritative when it conflicts with CSV reference files.
- **FR-025**: Catalog synchronization MUST be idempotent so applying unchanged CSV reference files repeatedly produces the same catalog state.
- **FR-026**: Synchronized catalog records MUST provide lightweight provenance indicating when they were last synchronized from the CSV source through synchronization metadata or an equivalent traceability mechanism.
- **FR-027**: Existing listing records MUST be backfillable to canonical values while preserving raw data, listing identifiers, and listing history.
- **FR-028**: Backfill MUST be repeatable, idempotent, safe to rerun, and non-destructive.
- **FR-029**: Rerunning backfill MUST NOT create inconsistent normalized values, duplicate history, or conflicting listing state.
- **FR-030**: Backend read behavior MUST continue to function without requiring marketplace-specific naming logic.
- **FR-031**: Marketplace-specific naming differences MUST be handled before normalized listing data is consumed by backend or presentation experiences.
- **FR-032**: Future market analytics, vehicle valuation, comparable vehicle analysis, price prediction, AI classification, generation classification, OCR, VIN decoding, and automatic fuzzy corrections MUST remain outside this feature scope.

### Key Entities *(include if feature involves data)*

- **Raw Listing**: Original marketplace payload captured from a source marketplace. It remains immutable for this feature and is the audit source for what the marketplace provided.
- **Listing**: Normalized operational listing record used by read and presentation experiences. It stores canonical categorical operational keys rather than marketplace display names for supported categorical fields.
- **Vehicle Reference Catalog**: Canonical vehicle reference database that defines canonical make and model keys, presentation display values, market context, generation metadata, aliases owned by catalog records, and confidence. It is referred to as `vehicle_reference_catalog` when discussing the database object.
- **Reference File Set**: Curated CSV catalog source files used by data stewards as the authoritative source for synchronizing the Vehicle Reference Catalog.
- **Canonical Categorical Field**: A supported operational listing field whose values are normalized to deterministic canonical keys, such as make, model, trim, fuel type, transmission, body type, seller type, vehicle condition, specs, or color.
- **Canonicalization Version**: Identifier for the canonicalization or normalization rule set used to process a normalized listing, retained for replayability, backfill consistency, debugging, and operational traceability.
- **Normalization Statistics**: Operational reporting output that exposes unknown marketplace values and normalization outcomes so data stewards can improve the Vehicle Reference Catalog without blocking ingestion.

### Architectural Note

The Vehicle Reference Catalog intentionally combines canonical identity, display names, aliases, and generation metadata at this stage of PrioraMarket. This is a deliberate simplification to keep the foundation lightweight. If catalog complexity grows significantly in the future, the catalog may be normalized into dedicated reference tables without changing the canonical data model established by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All supported canonical categorical values on newly ingested listings are stored as canonical keys instead of marketplace display values, while unknown values continue through deterministic canonicalization without blocking ingestion.
- **SC-002**: Raw listing payloads remain unchanged after ingestion, normalization, synchronization, and backfill activities.
- **SC-003**: The provided examples canonicalize exactly as specified while preserving semantic information: `Mercedes Benz`, `Mercedes-Benz`, and `Mercedes` to `mercedesbenz`; `C Class` and `C-Class` to `cclass`; `Land Rover` to `landrover`; `C200` to `c200`; `E53 AMG` to `e53amg`; `GLC300 Coupe` to `glc300coupe`; and `7 Series` to `7series`.
- **SC-004**: Applying the same CSV catalog reference file set three consecutive times produces the same Vehicle Reference Catalog contents after the first successful application.
- **SC-005**: A representative backfill of existing listings preserves listing identifiers, raw payloads, and history while populating canonical categorical values where source values exist; rerunning it produces no inconsistent data.
- **SC-006**: All catalog-backed vehicle identity display names available to presentation consumers are sourced from Vehicle Reference Catalog display values, not reconstructed from canonical keys.
- **SC-007**: Search, filtering, and grouping test cases produce identical results for equivalent marketplace spellings that map to the same canonical key.
- **SC-008**: Listings normalized through this feature contain the canonical keys and catalog-aligned metadata needed for a future generation classification feature, without performing generation classification in this feature.
- **SC-009**: Catalog synchronization results are traceable by confirming when synchronized catalog records were last synchronized from the CSV source.
- **SC-010**: Normalized listings can be traced to the canonicalization rule version used when they were processed.
- **SC-011**: Ingestion exposes operational normalization statistics for unknown supported categorical values without blocking listing persistence.

## Assumptions

- The existing raw listing concept already contains enough marketplace payload data to preserve original categorical values without adding or changing raw payload content.
- Existing listing records contain or can access enough source categorical values to perform deterministic backfill.
- CSV reference files are curated by trusted data stewards before synchronization and are treated as authoritative once accepted.
- Canonical keys are stable identifiers for operational use and are not renamed after introduction; display names may change for presentation without changing canonical identity.
- Canonicalization rules may evolve over time, but each normalized listing remains traceable to the rule version used at processing time.
- Market is part of the catalog identity so the same canonical make and model can be represented across multiple marketplaces without backend marketplace-specific logic.
- Confidence describes the trust level of catalog metadata and alias coverage, not an AI-derived match score.
- Vehicle generation data can be present in the Vehicle Reference Catalog, but assigning listings to generations is a separate future feature.
- Future market analytics will consume this canonical foundation but will be specified separately.
