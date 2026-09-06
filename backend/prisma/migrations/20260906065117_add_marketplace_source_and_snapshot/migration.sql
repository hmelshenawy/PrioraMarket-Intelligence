-- AlterTable
ALTER TABLE "listing" ADD COLUMN     "last_seen_run_id" BIGINT,
ADD COLUMN     "marketplace_source_id" BIGINT;

-- CreateTable
CREATE TABLE "marketplace_source" (
    "id" BIGSERIAL NOT NULL,
    "slug" TEXT NOT NULL,
    "name" TEXT,
    "base_url" TEXT,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "marketplace_source_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "listing_snapshot" (
    "id" BIGSERIAL NOT NULL,
    "listing_id" BIGINT NOT NULL,
    "captured_at" TIMESTAMPTZ(6) NOT NULL,
    "canonical_payload" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "listing_snapshot_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "marketplace_source_slug_key" ON "marketplace_source"("slug");

-- CreateIndex
CREATE INDEX "idx_listing_snapshot_listing_captured" ON "listing_snapshot"("listing_id", "captured_at");

-- AddForeignKey
ALTER TABLE "listing" ADD CONSTRAINT "listing_marketplace_source_id_fkey" FOREIGN KEY ("marketplace_source_id") REFERENCES "marketplace_source"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "listing_snapshot" ADD CONSTRAINT "listing_snapshot_listing_id_fkey" FOREIGN KEY ("listing_id") REFERENCES "listing"("id") ON DELETE CASCADE ON UPDATE CASCADE;
