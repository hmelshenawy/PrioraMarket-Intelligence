-- yoyo-migration
-- depends: 202607040002_seed_marketplace_source

CREATE TABLE IF NOT EXISTS vehicle_generation_catalog (
    id BIGSERIAL PRIMARY KEY,
    slug TEXT NOT NULL,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    generation TEXT NOT NULL,
    body_code TEXT NULL,
    marketing_name TEXT NULL,
    start_year INTEGER NOT NULL,
    end_year INTEGER NULL,
    facelift_start_year INTEGER NULL,
    facelift_end_year INTEGER NULL,
    aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence TEXT NOT NULL DEFAULT 'manual',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_vehicle_generation_catalog_slug UNIQUE (slug),
    CONSTRAINT uq_vehicle_generation_catalog_identity UNIQUE (make, model, generation, body_code)
);

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_make_model
    ON vehicle_generation_catalog(make, model);

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_make_model_years
    ON vehicle_generation_catalog(make, model, start_year, end_year);
