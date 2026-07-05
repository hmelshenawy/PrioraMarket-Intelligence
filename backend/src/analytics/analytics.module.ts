import { Module } from '@nestjs/common';
import { PrismaModule } from '../db/prisma.module';
import { MarketSnapshotController } from './market-snapshot.controller';
import { MarketSnapshotService } from './market-snapshot.service';
import { SnapshotAggregationService } from './aggregation/market-snapshot.aggregator';
import { MarketSnapshotResponseMapper } from './mappers/market-snapshot-response.mapper';
import { PrismaSnapshotReadRepository } from './snapshot-read.repository';
import { FilterOptionsController } from './filter-options.controller';
import { FilterOptionsService } from './filter-options.service';
import { FilterOptionsResponseMapper } from './mappers/filter-options-response.mapper';
import { PrismaFilterReadRepository } from './filter-read.repository';
import { PrismaCatalogReadRepository } from './catalog-read.repository';
import { SNAPSHOT_READ_REPOSITORY, FILTER_READ_REPOSITORY, CATALOG_READ_REPOSITORY } from './analytics.tokens';

/**
 * Analytics module — owns the Market Snapshot Dashboard read surface.
 * Repositories are bound by Symbol tokens; services and mappers are class-DI;
 * controllers are thin. PrismaModule is @Global but imported here to make the read
 * dependency explicit. Read-only: no listing/raw_listing/catalog/lifecycle/price-history
 * mutations are exposed by any provider in this module.
 */
@Module({
  imports: [PrismaModule],
  controllers: [MarketSnapshotController, FilterOptionsController],
  providers: [
    MarketSnapshotService,
    SnapshotAggregationService,
    MarketSnapshotResponseMapper,
    { provide: SNAPSHOT_READ_REPOSITORY, useClass: PrismaSnapshotReadRepository },
    FilterOptionsService,
    FilterOptionsResponseMapper,
    { provide: FILTER_READ_REPOSITORY, useClass: PrismaFilterReadRepository },
    // US3: catalog display-name resolution (read-only catalog access).
    { provide: CATALOG_READ_REPOSITORY, useClass: PrismaCatalogReadRepository }
  ]
})
export class AnalyticsModule {}