-- yoyo-migration
-- depends: 202607050001_vehicle_reference_catalog

-- Best-effort rollback: the run-tracking structures are recreated, but
-- historical run/source references cannot be recovered, so the columns
-- come back nullable.

CREATE TABLE IF NOT EXISTS marketplace_source (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    base_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ingestion_run (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    marketplace_source_id BIGINT NULL REFERENCES marketplace_source(id) ON DELETE RESTRICT,
    marketplace TEXT NOT NULL,
    condition TEXT NOT NULL,
    make TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NULL,
    pages_scraped INTEGER NOT NULL DEFAULT 0,
    listings_extracted INTEGER NOT NULL DEFAULT 0,
    listings_skipped INTEGER NOT NULL DEFAULT 0,
    failures_count INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER NULL,
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    report_json JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS listing_snapshot (
    id BIGSERIAL PRIMARY KEY,
    listing_id BIGINT NOT NULL REFERENCES listing(id) ON DELETE CASCADE,
    ingestion_run_id BIGINT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT,
    raw_listing_id BIGINT NULL REFERENCES raw_listing(id) ON DELETE SET NULL,
    snapshot_hash TEXT NOT NULL,
    canonical_payload JSONB NOT NULL,
    changed_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    captured_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE raw_listing ADD COLUMN IF NOT EXISTS marketplace_source_id BIGINT NULL REFERENCES marketplace_source(id) ON DELETE RESTRICT;
ALTER TABLE raw_listing ADD COLUMN IF NOT EXISTS ingestion_run_id BIGINT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT;

ALTER TABLE listing ADD COLUMN IF NOT EXISTS marketplace_source_id BIGINT NULL REFERENCES marketplace_source(id) ON DELETE RESTRICT;
ALTER TABLE listing ADD COLUMN IF NOT EXISTS first_seen_run_id BIGINT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT;
ALTER TABLE listing ADD COLUMN IF NOT EXISTS last_seen_run_id BIGINT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT;