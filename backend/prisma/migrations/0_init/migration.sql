-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateTable
CREATE TABLE "raw_listing" (
    "id" BIGSERIAL NOT NULL,
    "source" TEXT NOT NULL,
    "uuid" TEXT NOT NULL,
    "raw_payload" JSONB NOT NULL,
    "raw_hash" TEXT NOT NULL,
    "adapter_version" TEXT NOT NULL,
    "marketplace_schema_version" TEXT,
    "marketplace_payload_version" TEXT,
    "extracted_at" TIMESTAMPTZ(6) NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "raw_listing_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "listing" (
    "id" BIGSERIAL NOT NULL,
    "source" TEXT NOT NULL,
    "uuid" TEXT NOT NULL,
    "title" TEXT,
    "make" TEXT,
    "model" TEXT,
    "trim" TEXT,
    "year" INTEGER,
    "price" DECIMAL(14,2),
    "mileage" INTEGER,
    "condition" TEXT,
    "location" TEXT,
    "seller_type" TEXT,
    "url" TEXT,
    "status" TEXT NOT NULL DEFAULT 'ACTIVE',
    "first_seen_at" TIMESTAMPTZ(6) NOT NULL,
    "last_seen_at" TIMESTAMPTZ(6) NOT NULL,
    "current_raw_listing_id" BIGINT,
    "canonical_hash" TEXT NOT NULL,
    "normalization_version" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fuel_type" TEXT,
    "transmission" TEXT,
    "body_type" TEXT,
    "regional_spec" TEXT,
    "specs" TEXT,
    "color" TEXT,
    "vehicle_condition" TEXT,
    "canonicalization_version" TEXT,

    CONSTRAINT "listing_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_yoyo_log" (
    "id" VARCHAR(36) NOT NULL,
    "migration_hash" VARCHAR(64),
    "migration_id" VARCHAR(255),
    "operation" VARCHAR(10),
    "username" VARCHAR(255),
    "hostname" VARCHAR(255),
    "comment" VARCHAR(255),
    "created_at_utc" TIMESTAMP(6),

    CONSTRAINT "_yoyo_log_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_yoyo_migration" (
    "migration_hash" VARCHAR(64) NOT NULL,
    "migration_id" VARCHAR(255),
    "applied_at_utc" TIMESTAMP(6),

    CONSTRAINT "_yoyo_migration_pkey" PRIMARY KEY ("migration_hash")
);

-- CreateTable
CREATE TABLE "_yoyo_version" (
    "version" INTEGER NOT NULL,
    "installed_at_utc" TIMESTAMP(6),

    CONSTRAINT "_yoyo_version_pkey" PRIMARY KEY ("version")
);

-- CreateTable
CREATE TABLE "vehicle_reference_catalog" (
    "id" BIGSERIAL NOT NULL,
    "market" TEXT NOT NULL DEFAULT 'global',
    "make_key" TEXT NOT NULL,
    "make_display" TEXT NOT NULL,
    "model_key" TEXT NOT NULL,
    "model_display" TEXT NOT NULL,
    "generation" TEXT,
    "body_code" TEXT,
    "start_year" INTEGER,
    "end_year" INTEGER,
    "facelift_start_year" INTEGER,
    "facelift_end_year" INTEGER,
    "aliases" JSONB NOT NULL DEFAULT '{}',
    "confidence" TEXT NOT NULL DEFAULT 'manual',
    "source_file" TEXT,
    "source_row_hash" TEXT,
    "last_synced_at" TIMESTAMPTZ(6),
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "vehicle_reference_catalog_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "yoyo_lock" (
    "locked" INTEGER NOT NULL DEFAULT 1,
    "ctime" TIMESTAMP(6),
    "pid" INTEGER NOT NULL,

    CONSTRAINT "yoyo_lock_pkey" PRIMARY KEY ("locked")
);

-- CreateTable
CREATE TABLE "vehicle_generation_catalog" (
    "id" BIGSERIAL NOT NULL,
    "slug" TEXT NOT NULL,
    "make_key" TEXT NOT NULL,
    "model_key" TEXT NOT NULL,
    "generation" TEXT NOT NULL,
    "body_code" TEXT,
    "marketing_name" TEXT,
    "start_year" INTEGER NOT NULL,
    "end_year" INTEGER,
    "facelift_start_year" INTEGER,
    "facelift_end_year" INTEGER,
    "aliases" JSONB NOT NULL DEFAULT '[]',
    "confidence" TEXT NOT NULL DEFAULT 'manual',
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "market" TEXT NOT NULL DEFAULT 'global',

    CONSTRAINT "vehicle_generation_catalog_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "idx_raw_listing_raw_hash" ON "raw_listing"("raw_hash");

-- CreateIndex
CREATE INDEX "idx_raw_listing_source_uuid" ON "raw_listing"("source", "uuid");

-- CreateIndex
CREATE INDEX "idx_listing_canonical_hash" ON "listing"("canonical_hash");

-- CreateIndex
CREATE INDEX "idx_listing_canonical_categoricals" ON "listing"("make", "model", "trim", "fuel_type", "transmission", "body_type", "seller_type", "condition");

-- CreateIndex
CREATE INDEX "idx_listing_make_model" ON "listing"("make", "model");

-- CreateIndex
CREATE UNIQUE INDEX "listing_source_uuid_key" ON "listing"("source", "uuid");

-- CreateIndex
CREATE INDEX "idx_vehicle_reference_catalog_market_make_model" ON "vehicle_reference_catalog"("market", "make_key", "model_key");

-- CreateIndex
CREATE INDEX "idx_vehicle_reference_catalog_market_make_model_years" ON "vehicle_reference_catalog"("market", "make_key", "model_key", "start_year", "end_year");

-- CreateIndex
CREATE INDEX "idx_vehicle_reference_catalog_aliases_gin" ON "vehicle_reference_catalog" USING GIN ("aliases");

-- CreateIndex
CREATE UNIQUE INDEX "uq_vehicle_reference_catalog_market_identity" ON "vehicle_reference_catalog"("market", "make_key", "model_key", "generation", "body_code");

-- CreateIndex
CREATE UNIQUE INDEX "uq_vehicle_generation_catalog_slug" ON "vehicle_generation_catalog"("slug");

-- CreateIndex
CREATE INDEX "idx_vehicle_generation_catalog_market_make_model" ON "vehicle_generation_catalog"("market", "make_key", "model_key");

-- CreateIndex
CREATE INDEX "idx_vehicle_generation_catalog_market_make_model_years" ON "vehicle_generation_catalog"("market", "make_key", "model_key", "start_year", "end_year");

-- CreateIndex
CREATE UNIQUE INDEX "uq_vehicle_generation_catalog_market_identity" ON "vehicle_generation_catalog"("market", "make_key", "model_key", "generation", "body_code");

-- AddForeignKey
ALTER TABLE "listing" ADD CONSTRAINT "listing_current_raw_listing_id_fkey" FOREIGN KEY ("current_raw_listing_id") REFERENCES "raw_listing"("id") ON DELETE SET NULL ON UPDATE NO ACTION;

