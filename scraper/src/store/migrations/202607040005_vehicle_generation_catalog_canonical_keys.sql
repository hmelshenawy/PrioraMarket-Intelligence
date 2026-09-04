-- yoyo-migration
-- depends: 202607040004_vehicle_generation_catalog_market

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
          AND column_name = 'make'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vehicle_generation_catalog'
          AND column_name = 'make_key'
    ) THEN
        ALTER TABLE vehicle_generation_catalog RENAME COLUMN make TO make_key;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vehicle_generation_catalog'
          AND column_name = 'model'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'vehicle_generation_catalog'
          AND column_name = 'model_key'
    ) THEN
        ALTER TABLE vehicle_generation_catalog RENAME COLUMN model TO model_key;
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
            UNIQUE (market, make_key, model_key, generation, body_code);
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_market_make_model
    ON vehicle_generation_catalog(market, make_key, model_key);

CREATE INDEX IF NOT EXISTS idx_vehicle_generation_catalog_market_make_model_years
    ON vehicle_generation_catalog(market, make_key, model_key, start_year, end_year);
