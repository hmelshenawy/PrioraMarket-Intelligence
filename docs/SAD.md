# PrioraMarket Intelligence — System Analysis & Design

## Version

0.1

## Status

Draft

## Product

PrioraMarket Intelligence

## 1. Purpose

PrioraMarket Intelligence is an automotive market intelligence platform that collects marketplace vehicle listings, stores them as structured historical data, enables market search and analytics, and prepares the foundation for AI-assisted insights and machine learning price prediction.

The platform is not a marketplace, CRM, DMS, ERP, or inventory system.

## 2. Architecture Goals

The system must:

* Collect Dubai used and new car listings.
* Store listings in PostgreSQL/Supabase.
* Deduplicate listings by marketplace UUID.
* Preserve historical snapshots.
* Track listing lifecycle and missing listings.
* Provide backend APIs for search and analytics.
* Support future ML price prediction.
* Support future AI assistant responses based on backend APIs.
* Remain marketplace-agnostic for future sources.

## 3. High-Level Architecture

```text
External Marketplace
        |
        v
Data Ingestion Service
        |
        v
Normalizer + Validator
        |
        v
PostgreSQL / Supabase
        |
        +--------------------+
        |                    |
        v                    v
Market API             Analytics Service
        |                    |
        v                    v
Web Frontend           AI Assistant
                             |
                             v
                     ML Prediction Service
```

## 4. Bounded Contexts

### 4.1 Data Ingestion

Responsible for collecting raw marketplace data.

Responsibilities:

* Execute scrape runs.
* Fetch listings from configured marketplace sources.
* Store scrape run metadata.
* Preserve raw JSON payloads.
* Handle retries and partial failures.
* Pass data to normalization.

Out of scope:

* Analytics.
* User-facing search.
* ML training.

### 4.2 Marketplace Listings

Responsible for current listing state and listing lifecycle.

Responsibilities:

* Maintain latest listing record.
* Deduplicate by source + UUID.
* Update newest listing data.
* Preserve historical snapshots.
* Track active/inactive status.
* Track missing count.

### 4.3 Search

Responsible for user-facing listing search.

Responsibilities:

* Filter listings by make, model, year, price, mileage, condition, city, specs, transmission, body type.
* Return paginated results.
* Sort by price, mileage, year, or added date.
* Return data freshness metadata.

### 4.4 Analytics

Responsible for deterministic market calculations.

Responsibilities:

* Average price.
* Median price.
* Min/max price.
* Listing count.
* Average mileage.
* Dealer/private distribution.
* Price ranges.
* Market summaries.

Analytics are authoritative. AI may explain analytics but must not replace them.

### 4.5 Price Prediction

Responsible for ML-based listing price estimation.

Responsibilities:

* Train price prediction models.
* Version datasets and models.
* Serve predicted price, price range, and confidence.
* Record model version used for each prediction.

Initial features:

* Make
* Model
* Year
* Mileage
* Fuel
* Transmission
* Trim
* Body type
* Regional specs

Future features:

* Seller type
* Location
* Photos count
* Days listed

### 4.6 AI Assistant

Responsible for natural language interaction.

Responsibilities:

* Understand user questions.
* Call backend APIs.
* Summarize analytics results.
* Explain predictions.
* Refuse unsupported answers when data is insufficient.

AI must never query external marketplaces directly.

### 4.7 Administration

Responsible for operational controls.

Responsibilities:

* Trigger scrape runs.
* View scrape history.
* View ingestion errors.
* Manage marketplace source configuration.
* Monitor data freshness.

## 5. Core Data Entities

### 5.1 MarketplaceSource

Represents an external marketplace provider.

Fields:

* id
* name
* code
* country
* is_active
* created_at
* updated_at

Example:

* code: `dubizzle`
* name: `Dubizzle`

### 5.2 ScrapeRun

Represents one ingestion execution.

Fields:

* id
* source_id
* condition
* city
* status
* started_at
* finished_at
* total_fetched
* total_inserted
* total_updated
* total_failed
* error_message
* created_at

Statuses:

* PENDING
* RUNNING
* COMPLETED
* FAILED
* PARTIAL_FAILED

### 5.3 Listing

Represents the latest known state of a marketplace listing.

Fields:

* id
* source_id
* external_uuid
* external_id
* condition
* city
* country
* make
* model
* trim
* year
* price_aed
* mileage_km
* fuel
* transmission
* body_type
* regional_specs
* color
* seller_type
* seller_name
* is_verified
* is_agent
* neighborhood
* location_text
* url
* photos_count
* source_added_at
* first_seen_at
* last_seen_at
* missing_count
* status
* raw_json
* created_at
* updated_at

Unique constraint:

```text
source_id + external_uuid
```

Statuses:

* ACTIVE
* MISSING
* INACTIVE

### 5.4 ListingSnapshot

Immutable point-in-time listing observation.

Fields:

* id
* listing_id
* scrape_run_id
* observed_at
* price_aed
* mileage_km
* make
* model
* trim
* year
* condition
* city
* seller_type
* location_text
* raw_json
* created_at

Rules:

* Snapshots are append-only.
* Snapshots must not be updated after creation.

### 5.5 PricePrediction

Represents one model prediction result.

Fields:

* id
* listing_id nullable
* input_payload
* predicted_price_aed
* range_low_aed
* range_high_aed
* confidence_score
* model_version
* dataset_version
* created_at

### 5.6 ModelVersion

Represents a trained ML model.

Fields:

* id
* name
* version
* dataset_version
* feature_set
* metrics
* artifact_path
* status
* trained_at
* promoted_at

Statuses:

* TRAINED
* EVALUATED
* PROMOTED
* ARCHIVED

## 6. Listing Lifecycle Rules

### 6.1 Deduplication

Listings are deduplicated by:

```text
source_id + external_uuid
```

If a listing appears again:

* update `listings`
* insert `listing_snapshots`
* set `last_seen_at`
* reset `missing_count` to 0
* set status to ACTIVE

### 6.2 Newest Data Wins

The `listings` table stores the latest known listing state.

Older states remain available through `listing_snapshots`.

### 6.3 Missing Listings

After each scrape run:

* If a previously active listing is not found, increment `missing_count`.
* If `missing_count = 1`, set status to MISSING.
* If `missing_count >= 2`, set status to INACTIVE.
* If the listing appears again, reset `missing_count` to 0 and set status to ACTIVE.

The system must not label missing listings as sold.

## 7. Data Freshness Rules

Every search, analytics, AI, and prediction response must expose freshness metadata where applicable:

* last_updated
* scrape_run_id
* dataset_version, if applicable
* model_version, if applicable

The UI must show the latest data collection date.

## 8. API Architecture

All APIs use:

```text
/api/v1
```

Initial APIs:

### 8.1 Listings Search

```text
GET /api/v1/listings/search
```

Query parameters:

* make
* model
* year
* condition
* city
* min_price
* max_price
* min_mileage
* max_mileage
* fuel
* transmission
* body_type
* regional_specs
* seller_type
* page
* limit
* sort

Returns:

* listings
* pagination
* freshness metadata

### 8.2 Market Summary

```text
GET /api/v1/market/summary
```

Returns:

* average price
* median price
* minimum price
* maximum price
* listing count
* average mileage
* price range
* dealer/private split
* freshness metadata

### 8.3 Prediction

```text
POST /api/v1/predictions/price
```

Input:

* make
* model
* year
* mileage
* fuel
* transmission
* trim
* body_type
* regional_specs

Returns:

* predicted price
* price range
* confidence score
* model version
* dataset version

### 8.4 Scrape Runs

```text
GET /api/v1/admin/scrape-runs
POST /api/v1/admin/scrape-runs
```

Used by administrators to monitor or trigger ingestion.

## 9. Backend Architecture

Backend stack:

* NestJS
* TypeScript
* Prisma
* PostgreSQL/Supabase

Layer rules:

* Controller: HTTP only.
* Service: business logic.
* Repository: database access.
* DTO: validated request/response contracts.

Suggested modules:

```text
src/modules/
  ingestion/
  listings/
  search/
  analytics/
  predictions/
  ai-assistant/
  admin/
  common/
  config/
```

## 10. Data Ingestion Design

The ingestion flow:

```text
Start ScrapeRun
      |
Fetch marketplace pages
      |
Extract raw listings
      |
Normalize fields
      |
Validate data
      |
Upsert Listing
      |
Insert ListingSnapshot
      |
Update missing listings
      |
Complete ScrapeRun
```

Rules:

* Ingestion must be idempotent.
* Raw JSON must be preserved.
* Failed records must be logged.
* Partial failure must not destroy successful records.
* Marketplace-specific logic must stay inside adapters.

## 11. ML Architecture

ML should be implemented as a separate Python service or pipeline.

Responsibilities:

* Dataset creation.
* EDA.
* Data cleaning.
* Feature engineering.
* Model training.
* Model evaluation.
* Model artifact storage.
* Prediction serving.

Initial model target:

* Listing price prediction.
* Price range.
* Confidence score.

The first model should not be promoted until EDA and data quality checks are completed.

## 12. AI Architecture

AI assistant flow:

```text
User Question
      |
Intent Detection
      |
Backend API Call
      |
Structured Result
      |
AI Summary
      |
User Response
```

Rules:

* AI calls backend APIs.
* AI does not directly query the database.
* AI does not call Dubizzle.
* AI does not invent prices or statistics.
* If data is insufficient, AI must say so.

## 13. Frontend Architecture

Initial frontend scope:

* Search page.
* Listing results.
* Market summary card.
* Data freshness indicator.
* Later: prediction form.
* Later: AI question box.

Frontend responsibilities:

* Render UI.
* Collect filters.
* Call backend APIs.
* Display results.

Frontend must not calculate market analytics.

## 14. Security

MVP may start with admin-only access.

Required controls:

* Environment-based secrets.
* No API keys in source code.
* Input validation.
* Rate limiting.
* Admin protection for ingestion APIs.
* Structured error handling.
* Safe logging.

## 15. Non-Functional Requirements

### Performance

Search and summary APIs should respond within acceptable interactive latency for MVP.

Target:

* Search: under 1 second for indexed filters.
* Summary: under 2 seconds for common queries.

### Reliability

* Scrape runs must be resumable or safely retryable.
* Partial failures must be recorded.
* Database writes must be transactional where needed.

### Maintainability

* No hardcoded filesystem paths.
* No hardcoded secrets.
* Marketplace-specific code isolated.
* Small modules and clear responsibilities.

### Scalability

Architecture must support:

* More marketplaces.
* More cities.
* More countries.
* More vehicle categories.
* More analytics.
* More ML models.

## 16. Key Architectural Decisions

### ADR-001: Database as Source of Truth

Decision:

The internal PostgreSQL/Supabase database is the source of truth after ingestion.

Reason:

Search, analytics, AI, and ML require stable historical data.

### ADR-002: Listing as Primary Entity

Decision:

The primary entity is Listing, not Vehicle.

Reason:

VIN is not available, so true vehicle identity cannot be guaranteed.

### ADR-003: UUID-Based Deduplication

Decision:

Deduplicate by marketplace UUID.

Reason:

Price, mileage, URL, and seller details may change.

### ADR-004: Current + Snapshots

Decision:

Use `listings` for latest state and `listing_snapshots` for history.

Reason:

This supports analytics, price history, and ML datasets.

### ADR-005: Missing Twice Before Inactive

Decision:

A listing becomes inactive only after two consecutive missed scrape runs.

Reason:

One missing scrape may be caused by source inconsistency or partial failure.

### ADR-006: Backend APIs Before AI

Decision:

AI must call backend APIs instead of querying database directly.

Reason:

Backend APIs preserve business rules, validation, permissions, and consistency.

### ADR-007: ML as Separate Pipeline

Decision:

ML training and experimentation should live in a Python pipeline/service.

Reason:

Data science tooling is stronger in Python and should remain independent from NestJS backend logic.

## 17. Open Questions

* Will the first deployment use Supabase hosted database or self-hosted PostgreSQL?
* Will ingestion run from backend, separate worker, or scheduled Python job?
* What authentication model is needed for MVP?
* What exact data quality checks are mandatory before analytics?
* What ML model family will be tested first?
* Should analytics be computed on demand or pre-aggregated later?

## 18. Initial Implementation Sequence

1. Refactor scraper into ingestion modules.
2. Create Prisma schema.
3. Create ingestion tables.
4. Implement CSV-to-database or scraper-to-database ingestion.
5. Implement dedupe and snapshots.
6. Implement missing listing lifecycle.
7. Build `GET /api/v1/listings/search`.
8. Build `GET /api/v1/market/summary`.
9. Build simple frontend search page.
10. Start EDA notebook/pipeline.
11. Prepare first ML training dataset.
12. Build prediction API after model validation.
