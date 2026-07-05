ALTER TABLE vehicle_generation_catalog
    DROP CONSTRAINT IF EXISTS uq_vehicle_generation_catalog_market_identity;

DROP INDEX IF EXISTS idx_vehicle_generation_catalog_market_make_model;
DROP INDEX IF EXISTS idx_vehicle_generation_catalog_market_make_model_years;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_vehicle_generation_catalog_identity'
          AND conrelid = 'public.vehicle_generation_catalog'::regclass
    ) THEN
        ALTER TABLE vehicle_generation_catalog
            ADD CONSTRAINT uq_vehicle_generation_catalog_identity
            UNIQUE (make, model, generation, body_code);
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_make_model
    ON vehicle_generation_catalog(make, model);

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_make_model_years
    ON vehicle_generation_catalog(make, model, start_year, end_year);

ALTER TABLE vehicle_generation_catalog
    DROP COLUMN IF EXISTS market;
