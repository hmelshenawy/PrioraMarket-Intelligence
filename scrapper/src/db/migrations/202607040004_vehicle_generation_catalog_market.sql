-- yoyo-migration
-- depends: 202607040003_create_vehicle_generation_catalog

ALTER TABLE vehicle_generation_catalog
    ADD COLUMN IF NOT EXISTS market TEXT NOT NULL DEFAULT 'global';

ALTER TABLE vehicle_generation_catalog
    DROP CONSTRAINT IF EXISTS uq_vehicle_generation_catalog_identity;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_vehicle_generation_catalog_market_identity'
          AND conrelid = 'public.vehicle_generation_catalog'::regclass
    ) THEN
        ALTER TABLE vehicle_generation_catalog
            ADD CONSTRAINT uq_vehicle_generation_catalog_market_identity
            UNIQUE (market, make, model, generation, body_code);
    END IF;
END
$$;

DROP INDEX IF EXISTS idx_vehicle_generation_catalog_make_model;
DROP INDEX IF EXISTS idx_vehicle_generation_catalog_make_model_years;

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_market_make_model
    ON vehicle_generation_catalog(market, make, model);

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_market_make_model_years
    ON vehicle_generation_catalog(market, make, model, start_year, end_year);
