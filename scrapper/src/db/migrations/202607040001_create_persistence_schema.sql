-- yoyo-migration
-- depends:

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
    marketplace_source_id BIGINT NOT NULL REFERENCES marketplace_source(id) ON DELETE RESTRICT,
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

CREATE INDEX IF NOT EXISTS idx_ingestion_run_marketplace_source_id ON ingestion_run(marketplace_source_id);
CREATE INDEX IF NOT EXISTS idx_ingestion_run_scope ON ingestion_run(marketplace, condition, make);

CREATE TABLE IF NOT EXISTS raw_listing (
    id BIGSERIAL PRIMARY KEY,
    marketplace_source_id BIGINT NOT NULL REFERENCES marketplace_source(id) ON DELETE RESTRICT,
    ingestion_run_id BIGINT NOT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT,
    source TEXT NOT NULL,
    uuid TEXT NOT NULL,
    raw_payload JSONB NOT NULL,
    raw_hash TEXT NOT NULL,
    adapter_version TEXT NOT NULL,
    marketplace_schema_version TEXT NULL,
    marketplace_payload_version TEXT NULL,
    extracted_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_raw_listing_ingestion_run_id ON raw_listing(ingestion_run_id);
CREATE INDEX IF NOT EXISTS idx_raw_listing_source_uuid ON raw_listing(source, uuid);
CREATE INDEX IF NOT EXISTS idx_raw_listing_raw_hash ON raw_listing(raw_hash);

CREATE TABLE IF NOT EXISTS listing (
    id BIGSERIAL PRIMARY KEY,
    marketplace_source_id BIGINT NOT NULL REFERENCES marketplace_source(id) ON DELETE RESTRICT,
    source TEXT NOT NULL,
    uuid TEXT NOT NULL,
    title TEXT NULL,
    make TEXT NULL,
    model TEXT NULL,
    trim TEXT NULL,
    year INTEGER NULL,
    price NUMERIC(14, 2) NULL,
    mileage INTEGER NULL,
    condition TEXT NULL,
    location TEXT NULL,
    seller_type TEXT NULL,
    url TEXT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    first_seen_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    first_seen_run_id BIGINT NOT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT,
    last_seen_run_id BIGINT NOT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT,
    current_raw_listing_id BIGINT NULL REFERENCES raw_listing(id) ON DELETE SET NULL,
    canonical_hash TEXT NOT NULL,
    normalization_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, uuid)
);

CREATE INDEX IF NOT EXISTS idx_listing_marketplace_source_id ON listing(marketplace_source_id);
CREATE INDEX IF NOT EXISTS idx_listing_canonical_hash ON listing(canonical_hash);
CREATE INDEX IF NOT EXISTS idx_listing_last_seen_run_id ON listing(last_seen_run_id);

CREATE TABLE IF NOT EXISTS listing_snapshot (
    id BIGSERIAL PRIMARY KEY,
    listing_id BIGINT NOT NULL REFERENCES listing(id) ON DELETE CASCADE,
    ingestion_run_id BIGINT NOT NULL REFERENCES ingestion_run(id) ON DELETE RESTRICT,
    raw_listing_id BIGINT NULL REFERENCES raw_listing(id) ON DELETE SET NULL,
    snapshot_hash TEXT NOT NULL,
    canonical_payload JSONB NOT NULL,
    changed_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    captured_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_listing_snapshot_listing_id ON listing_snapshot(listing_id);
CREATE INDEX IF NOT EXISTS idx_listing_snapshot_listing_captured ON listing_snapshot(listing_id, captured_at);
CREATE INDEX IF NOT EXISTS idx_listing_snapshot_ingestion_run_id ON listing_snapshot(ingestion_run_id);


