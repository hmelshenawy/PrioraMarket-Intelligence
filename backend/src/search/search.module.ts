import { Module } from '@nestjs/common';
import { PrismaModule } from '../db/prisma.module';
import { FILTER_METADATA_CACHE } from './cache/filter-metadata-cache.token';
import { InMemoryFilterMetadataCache } from './cache/in-memory-filter-metadata.cache';
import { PrismaListingReadRepository } from './listing-read.repository';
import { FilterMetadataResponseMapper } from './mappers/filter-metadata-response.mapper';
import { InventoryStatsResponseMapper } from './mappers/inventory-stats-response.mapper';
import { ListingResponseMapper } from './mappers/listing-response.mapper';
import { SearchController } from './search.controller';
import { SearchQueryBuilder } from './search-query.builder';
import { SearchService } from './search.service';
import { LISTING_READ_REPOSITORY, SEARCH_QUERY_BUILDER } from './search.tokens';
import { StatsController } from './stats.controller';
import { StatsService } from './stats.service';

@Module({
  imports: [PrismaModule],
  controllers: [SearchController, StatsController],
  providers: [
    SearchService,
    StatsService,
    ListingResponseMapper,
    FilterMetadataResponseMapper,
    InventoryStatsResponseMapper,
    { provide: LISTING_READ_REPOSITORY, useClass: PrismaListingReadRepository },
    { provide: SEARCH_QUERY_BUILDER, useClass: SearchQueryBuilder },
    { provide: FILTER_METADATA_CACHE, useClass: InMemoryFilterMetadataCache }
  ],
  exports: [SearchService, StatsService]
})
export class SearchModule {}
