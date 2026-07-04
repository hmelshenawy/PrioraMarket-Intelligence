# Feature Specification: Backend Search API

**Feature Branch**: `003-backend-search-api`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Implement Feature 003 — Backend Search API for PrioraMarket Intelligence. Create a strictly read-only backend search and read interface over existing vehicle listings, including health, listing search, listing detail, filter metadata, and optional inventory stats capabilities."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search Current Vehicle Listings (Priority: P1)

As a product experience or future UI consumer, I need to retrieve paginated vehicle listings using common marketplace filters so that users can discover relevant cars from the existing PrioraMarket inventory.

**Why this priority**: Search is the core user value of this feature and enables all downstream listing discovery experiences.

**Independent Test**: Can be fully tested by requesting listings with and without filters and confirming the returned results, pagination metadata, validation behavior, and ordering match the requested criteria.

**Acceptance Scenarios**:

1. **Given** current vehicle listing data exists, **When** a consumer requests listings without query criteria, **Then** the system returns the first page using page 1, limit 20, and pagination metadata.
2. **Given** current vehicle listing data exists, **When** a consumer searches by free text, make, model, year range, price range, mileage range, condition, location, seller type, page, limit, and supported sort order, **Then** the system returns only matching listings in the requested order with accurate metadata.
3. **Given** a consumer provides free text and requests relevance sorting, **When** the search is requested, **Then** the system orders matching listings by text relevance before applying stable tie-breaking.
4. **Given** a consumer requests relevance sorting without free text, **When** the search is requested, **Then** the system falls back to newest sorting and returns a valid response.
5. **Given** a consumer submits an unsupported sort option, unknown condition, invalid number, or a limit above the maximum allowed value, **When** the search is requested, **Then** the system rejects the request with a clear client error and does not return misleading results.

---

### User Story 2 - Read Listing Details (Priority: P2)

As a product experience or future UI consumer, I need to retrieve one vehicle listing by identifier so that a user can inspect complete canonical details and lineage information before comparing or acting on the listing.

**Why this priority**: Listing detail is required after discovery and provides the canonical data needed for a complete marketplace intelligence experience.

**Independent Test**: Can be fully tested by requesting a known listing identifier and confirming all expected detail and lineage fields are present, then requesting an unknown identifier and confirming a not-found response.

**Acceptance Scenarios**:

1. **Given** a listing exists, **When** a consumer requests that listing by identifier, **Then** the system returns the listing's latest canonical vehicle, seller, location, source, timing, and lineage fields.
2. **Given** no listing exists for an identifier, **When** a consumer requests that listing, **Then** the system returns a not-found response.

---

### User Story 3 - Discover Available Filters (Priority: P3)

As a product experience or future UI consumer, I need available filter metadata based on current listings so that search controls can show meaningful make, model, price, year, mileage, condition, and seller type options.

**Why this priority**: Filter metadata improves usability and prevents users from selecting filters that cannot produce results.

**Independent Test**: Can be fully tested by requesting filter metadata and confirming the response contains distinct available values and numeric ranges derived from current listing data.

**Acceptance Scenarios**:

1. **Given** current vehicle listing data exists, **When** a consumer requests filter metadata, **Then** the system returns available makes, models grouped by make, price range, year range, mileage range, conditions, and seller types.
2. **Given** recently computed filter metadata is available, **When** a consumer requests filter metadata, **Then** the system returns cached metadata within the short freshness window instead of recomputing expensive distinct and range values on every request.
3. **Given** current listings contain missing or partial values, **When** filter metadata is requested, **Then** the system excludes empty categorical values while still returning a stable response shape.

---

### User Story 4 - Verify Service Availability (Priority: P4)

As an operator or integrating client, I need a simple availability check so that deployments and consumers can confirm the read service is reachable.

**Why this priority**: A health check supports safe deployment and integration but does not provide direct listing discovery value.

**Independent Test**: Can be fully tested by requesting the health check and confirming it returns an OK status.

**Acceptance Scenarios**:

1. **Given** the service is running, **When** a consumer requests the health check, **Then** the system returns a response indicating status is ok.

---

### User Story 5 - View Inventory Stats (Priority: P5)

As a product experience or operator, I need high-level inventory statistics at `GET /api/v1/stats` so that dashboards and monitoring views can summarize the current marketplace inventory without scanning raw listing records client-side.

**Why this priority**: Stats are useful for reporting and future dashboards, but they are optional and lower priority than search, detail, filters, and health.

**Independent Test**: Can be fully tested by requesting inventory stats and confirming the response contains total listing counts, condition counts, make and model counts, price summary values, and the latest update time.

**Acceptance Scenarios**:

1. **Given** current vehicle listing data exists, **When** a consumer requests inventory stats, **Then** the system returns high-level read-only totals, price summaries, and latest update time.
2. **Given** current listing data is empty, **When** a consumer requests inventory stats, **Then** the system returns zero counts and consistent null or empty summary values without failing.

### Edge Cases

- Empty or omitted search filters are ignored and do not restrict results.
- Page defaults to 1 when omitted; limit defaults to 20 when omitted.
- Limit values above 100 are rejected as client errors.
- Non-numeric values for year, price, mileage, page, or limit are rejected as client errors.
- Unsupported sort values are rejected as client errors.
- Relevance sorting is valid when free-text search is provided.
- Relevance sorting without free-text search falls back to newest sorting so consumers receive a predictable default ordering.
- Conditions outside `used` and `new` are rejected as client errors.
- Searches with no matching listings return an empty data list with accurate pagination metadata.
- Detail requests for unknown listing identifiers return not found.
- Missing optional listing attributes are represented as consistent null or empty values without failing the whole response.
- Filter metadata requests use short-lived cached values when available and safely refresh after ingestion updates.
- The feature never creates, updates, deletes, or otherwise mutates listing or ingestion data.
- The feature does not add scraping, ingestion, replay, normalization, or database mutation capabilities.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a health check that returns an OK status when the read service is reachable.
- **FR-002**: System MUST provide a paginated listing search over current vehicle listing records.
- **FR-003**: System MUST default listing search to page 1 and limit 20 when pagination values are omitted.
- **FR-004**: System MUST reject listing search requests with limit values greater than 100.
- **FR-005**: System MUST support free-text listing search across vehicle title or name, make, model, and trim.
- **FR-006**: System MUST support filtering listings by condition, make, model, year range, price range, mileage range, location, and seller type.
- **FR-007**: System MUST ignore omitted or empty filters rather than treating them as restrictive criteria.
- **FR-008**: System MUST reject invalid numeric filters for year, price, mileage, page, and limit with a clear client error.
- **FR-009**: System MUST reject unsupported condition values with a clear client error.
- **FR-010**: System MUST support sorting listings by relevance, newest, price ascending, price descending, year ascending, year descending, mileage ascending, and mileage descending.
- **FR-011**: System MUST use relevance sorting when free-text search is provided and relevance is requested.
- **FR-012**: System MUST fall back from relevance sorting to newest sorting when relevance is requested without free-text search.
- **FR-013**: System MUST reject unsupported sort values with a clear client error.
- **FR-014**: Search requests MUST follow the interaction boundary Controller to Search Service to Search Query Builder to Listing Repository to Database.
- **FR-015**: Controllers MUST NOT access database clients, database models, or persistence tools directly.
- **FR-016**: Listing data access MUST be isolated behind a repository abstraction so future search engines can replace the backing search implementation without changing controller contracts.
- **FR-017**: Search query construction MUST be isolated inside a Search Query Builder to keep Search Service focused on business logic and to simplify future expansion as additional filters are introduced.
- **FR-018**: Search Service MUST be responsible only for request orchestration, validation coordination, business rules, pagination logic, and calling the repository.
- **FR-019**: Search Query Builder MUST be responsible only for translating validated search criteria into persistence-specific query objects, building filters, building sorting, building free-text search conditions, and composing pagination.
- **FR-020**: Search Query Builder MUST remain independent of HTTP concerns.
- **FR-021**: Listing Repository MUST only execute queries produced by the Search Query Builder and return domain data; it MUST NOT contain search decision logic.
- **FR-022**: System MUST return explicit stable API response DTOs and MUST NOT expose raw database models.
- **FR-023**: System MUST define stable API response DTOs for listing search result, listing detail, pagination metadata, filter metadata, health response, and inventory stats response.
- **FR-024**: Stable response contracts MUST represent missing optional values consistently as null, empty arrays, or empty objects according to each field type.
- **FR-025**: Listing search responses MUST include a data list and metadata containing page, limit, total matching listings, and total pages.
- **FR-026**: Each listing search result MUST include identifier, external identifier, title, make, model, trim, year, price in AED, mileage, condition, location, seller type, source URL, photo count, first seen time, and last seen time when available.
- **FR-027**: System MUST provide listing detail retrieval by listing identifier.
- **FR-028**: Listing detail responses MUST include the latest canonical vehicle attributes, seller attributes, source marketplace, source URL, photo count, first and last seen run identifiers, first and last seen timestamps, and canonical hash when available.
- **FR-029**: System MUST return a not-found response when listing detail is requested for an unknown identifier.
- **FR-030**: System MUST provide filter metadata derived from current listings, including makes, models grouped by make, price range, year range, mileage range, conditions, and seller types.
- **FR-031**: Filter metadata responses MUST preserve a stable shape even when current listing data is empty or partially populated.
- **FR-032**: Filter metadata MUST use short time-to-live caching between 30 and 60 seconds to avoid expensive distinct and range calculations on every request.
- **FR-033**: Filter metadata cache refresh MUST be safe after ingestion updates and MUST NOT require writing to listing or ingestion records.
- **FR-034**: System SHOULD provide optional high-level inventory stats at `GET /api/v1/stats` containing total listings, used listings, new listings, total makes, total models, average price in AED, minimum price in AED, maximum price in AED, and latest listing update time.
- **FR-035**: Search planning MUST include indexes or equivalent query optimization for condition, make, model, year, price, mileage, seller type, location, last seen timestamp, first seen timestamp when used for newest sorting, and free-text search fields.
- **FR-036**: System MUST read from the existing listing data source and MUST NOT duplicate ingestion, scraping, normalization, replay, or persistence responsibilities.
- **FR-037**: System MUST NOT provide scraping, ingestion, replay, normalization, database mutation endpoints, or any capability that creates, updates, deletes, or mutates listing records or related ingestion records.
- **FR-038**: System MUST return clean structured responses suitable for future user interfaces and third-party consumers.

### Key Entities *(include if feature involves data)*

- **Listing**: A current vehicle listing available for search and detail views. Key attributes include identifiers, source reference, title, make, model, trim, year, price, mileage, condition, location, seller type, URL, photo count, and first or last seen timestamps.
- **Listing Detail**: The complete current representation of one listing, including canonical vehicle attributes, seller and marketplace context, verification and agent indicators, neighbourhood, source URL, lineage run identifiers, timestamps, and canonical hash.
- **Filter Metadata**: Distinct categorical values and numeric ranges derived from current listings to power user-facing search controls.
- **Pagination Metadata**: Page, limit, total matching records, and total pages returned with listing search results.
- **Health Response**: A stable status response used by operators and clients to verify service availability.
- **Inventory Stats**: Optional high-level current inventory summary, including listing counts, condition counts, make and model counts, price summary values, and latest update time.
- **Ingestion Lineage**: Read-only provenance information showing where and when a listing was first and last observed.
- **Listing Repository**: A replaceable read-only data access boundary for listing search, listing detail, filter metadata, and stats queries.
- **Search Service**: The application boundary that validates search behavior and coordinates listing read operations through the repository.
- **Search Query Builder**: A dedicated architectural boundary that translates validated search criteria into persistence-specific query objects, including filters, sorting, free-text conditions, and pagination, while remaining independent of HTTP concerns and repository execution.
- **Response DTO**: A stable API response contract that maps internal listing data into consumer-safe fields and consistent null, empty array, or empty object values.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of listing searches over the expected current inventory return a complete response in under 300 milliseconds under normal operating conditions when planned indexes or equivalent optimizations are available.
- **SC-002**: Consumers can retrieve the first page of listings without specifying any query values and receive page 1, limit 20, total, and total pages in 100% of valid requests.
- **SC-003**: 100% of invalid numeric, condition, limit, and sort inputs are rejected with client errors instead of returning incorrect search results.
- **SC-004**: 100% of successful listing detail responses include the required canonical and lineage fields, with unavailable optional values represented consistently.
- **SC-005**: 100% of unknown listing detail requests return a not-found response.
- **SC-006**: 95% of listing detail requests for existing listings return a complete response in under 100 milliseconds under normal operating conditions.
- **SC-007**: Filter metadata reflects current listing data with distinct categorical values and min/max ranges in 100% of successful metadata requests.
- **SC-008**: 95% of filter metadata requests served from cache return in under 100 milliseconds under normal operating conditions.
- **SC-009**: 95% of health checks return in under 50 milliseconds under normal operating conditions.
- **SC-010**: 100% of successful responses conform to stable API response DTOs and never expose raw database records.
- **SC-011**: No listing or ingestion records are created, changed, or deleted by any read capability in this feature.

## Assumptions

- Consumers are trusted internal or future product clients for this feature; authentication and authorization are outside the scope of this feature unless introduced by a later feature.
- Current listing data already exists from completed ingestion and persistence features.
- Search and metadata operate on the latest current listing state; historical snapshot exploration is outside the scope of this feature except for lineage fields needed in listing detail.
- Missing optional marketplace attributes may occur and should not prevent otherwise valid listings from being returned.
- Response field names and shapes are intended to be stable contracts for the future user interface.
- Relevance sorting without free-text search falls back to newest sorting rather than rejecting the request.
- Filter metadata cache freshness of 30 to 60 seconds is acceptable for the future user interface and remains safe because ingestion updates are handled outside this read-only feature.
- The number of supported search filters is expected to grow over time, so query construction remains isolated from service orchestration to preserve maintainability.
