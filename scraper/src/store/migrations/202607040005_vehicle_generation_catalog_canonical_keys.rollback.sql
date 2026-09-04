ALTER TABLE vehicle_generation_catalog
    DROP CONSTRAINT IF EXISTS uq_vehicle_generation_catalog_market_identity;

DROP INDEX IF EXISTS idx_vehicle_generation_catalog_market_make_model;
DROP INDEX IF EXISTS idx_vehicle_generation_catalog_market_make_model_years;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vehicle_generation_catalog'
          AND column_name = 'make_key'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vehicle_generation_catalog'
          AND column_name = 'make'
    ) THEN
        ALTER TABLE vehicle_generation_catalog RENAME COLUMN make_key TO make;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vehicle_generation_catalog'
          AND column_name = 'model_key'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vehicle_generation_catalog'
          AND column_name = 'model'
    ) THEN
        ALTER TABLE vehicle_generation_catalog RENAME COLUMN model_key TO model;
    END IF;
END
$$;

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

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_market_make_model
    ON vehicle_generation_catalog(market, make, model);

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_market_make_model_years
    ON vehicle_generation_catalog(market, make, model, start_year, end_year);
