-- yoyo-migration
-- depends: 202607050001_vehicle_reference_catalog

-- Ingestion-run tracking is no longer part of the flow: the CLI runs
-- once, saves listings over a single connection, and exits. Listings
-- keep their own history via first_seen_at / last_seen_at and the raw
-- payload history in raw_listing. The marketplace identity stays in the
-- existing `source` text column, so the marketplace_source foreign key
-- is dropped with the run tables.

DROP TABLE IF EXISTS listing_snapshot;

ALTER TABLE raw_listing DROP COLUMN IF EXISTS ingestion_run_id;
ALTER TABLE raw_listing DROP COLUMN IF EXISTS marketplace_source_id;

ALTER TABLE listing DROP COLUMN IF EXISTS marketplace_source_id;
ALTER TABLE listing DROP COLUMN IF EXISTS first_seen_run_id;
ALTER TABLE listing DROP COLUMN IF EXISTS last_seen_run_id;

DROP TABLE IF EXISTS ingestion_run;
DROP TABLE IF EXISTS marketplace_source;