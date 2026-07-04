import { Inject, Injectable } from '@nestjs/common';
import { InventoryStatsResponseMapper } from './mappers/inventory-stats-response.mapper';
import { ListingReadRepositoryInterface } from './listing-read.repository.interface';
import { ISearchQueryBuilder } from './search-query-builder.interface';
import { LISTING_READ_REPOSITORY, SEARCH_QUERY_BUILDER } from './search.tokens';

@Injectable()
export class StatsService {
  constructor(
    @Inject(LISTING_READ_REPOSITORY) private readonly listingReadRepository: ListingReadRepositoryInterface,
    @Inject(SEARCH_QUERY_BUILDER) private readonly queryBuilder: ISearchQueryBuilder,
    private readonly mapper: InventoryStatsResponseMapper
  ) {}

  async getInventoryStats() {
    const query = this.queryBuilder.buildInventoryStatsQuery();
    const stats = await this.listingReadRepository.getInventoryStats(query);
    return this.mapper.toResponse(stats);
  }
}
