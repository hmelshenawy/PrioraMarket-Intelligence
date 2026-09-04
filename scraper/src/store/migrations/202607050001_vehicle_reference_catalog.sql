-- yoyo-migration
-- depends: 202607040005_vehicle_generation_catalog_canonical_keys

CREATE TABLE IF NOT EXISTS vehicle_reference_catalog (
    id BIGSERIAL PRIMARY KEY,
    market TEXT NOT NULL DEFAULT 'global',
    make_key TEXT NOT NULL,
    make_display TEXT NOT NULL,
    model_key TEXT NOT NULL,
    model_display TEXT NOT NULL,
    generation TEXT,
    body_code TEXT,
    start_year INTEGER,
    end_year INTEGER,
    facelift_start_year INTEGER,
    facelift_end_year INTEGER,
    aliases JSONB NOT NULL DEFAULT '{}'::jsonb,
    confidence TEXT NOT NULL DEFAULT 'manual',
    source_file TEXT,
    source_row_hash TEXT,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_vehicle_reference_catalog_market_identity
        UNIQUE (market, make_key, model_key, generation, body_code)
);

INSERT INTO vehicle_reference_catalog (
    market,
    make_key,
    make_display,
    model_key,
    model_display,
    generation,
    body_code,
    start_year,
    end_year,
    facelift_start_year,
    facelift_end_year,
    aliases,
    confidence,
    created_at,
    updated_at
)
SELECT
    market,
    make_key,
    initcap(replace(make_key, '-', ' ')) AS make_display,
    model_key,
    initcap(replace(model_key, '-', ' ')) AS model_display,
    generation,
    body_code,
    start_year,
    end_year,
    facelift_start_year,
    facelift_end_year,
    CASE
        WHEN jsonb_typeof(aliases) = 'object' THEN aliases
        ELSE jsonb_build_object('legacy', aliases)
    END AS aliases,
    confidence,
    created_at,
    updated_at
FROM vehicle_generation_catalog
ON CONFLICT (market, make_key, model_key, generation, body_code) DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_vehicle_reference_catalog_market_make_model
    ON vehicle_reference_catalog(market, make_key, model_key);

CREATE INDEX IF NOT EXISTS idx_vehicle_reference_catalog_market_make_model_years
    ON vehicle_reference_catalog(market, make_key, model_key, start_year, end_year);

CREATE INDEX IF NOT EXISTS idx_vehicle_reference_catalog_aliases_gin
    ON vehicle_reference_catalog USING GIN (aliases);

ALTER TABLE listing
    ADD COLUMN IF NOT EXISTS fuel_type TEXT,
    ADD COLUMN IF NOT EXISTS transmission TEXT,
    ADD COLUMN IF NOT EXISTS body_type TEXT,
    ADD COLUMN IF NOT EXISTS regional_spec TEXT,
    ADD COLUMN IF NOT EXISTS specs TEXT,
    ADD COLUMN IF NOT EXISTS color TEXT,
    ADD COLUMN IF NOT EXISTS vehicle_condition TEXT,
    ADD COLUMN IF NOT EXISTS canonicalization_version TEXT;

UPDATE listing
SET canonicalization_version = normalization_version
WHERE canonicalization_version IS NULL;

CREATE INDEX IF NOT EXISTS idx_listing_make_model
    ON listing(make, model);

CREATE INDEX IF NOT EXISTS idx_listing_canonical_categoricals
    ON listing(make, model, trim, fuel_type, transmission, body_type, seller_type, condition);
