-- yoyo-migration
-- depends: 202607050001_vehicle_reference_catalog

DROP INDEX IF EXISTS idx_listing_canonical_categoricals;
DROP INDEX IF EXISTS idx_listing_make_model;

ALTER TABLE listing
    DROP COLUMN IF EXISTS canonicalization_version,
    DROP COLUMN IF EXISTS vehicle_condition,
    DROP COLUMN IF EXISTS color,
    DROP COLUMN IF EXISTS specs,
    DROP COLUMN IF EXISTS regional_spec,
    DROP COLUMN IF EXISTS body_type,
    DROP COLUMN IF EXISTS transmission,
    DROP COLUMN IF EXISTS fuel_type;

DROP INDEX IF EXISTS idx_vehicle_reference_catalog_aliases_gin;
DROP INDEX IF EXISTS idx_vehicle_reference_catalog_market_make_model_years;
DROP INDEX IF EXISTS idx_vehicle_reference_catalog_market_make_model;
DROP TABLE IF EXISTS vehicle_reference_catalog;
