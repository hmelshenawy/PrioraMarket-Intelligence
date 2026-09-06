import { Inject, Injectable, NotFoundException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { IFilterMetadataCache } from './cache/filter-metadata-cache.interface';
import { FILTER_METADATA_CACHE } from './cache/filter-metadata-cache.token';
import { ListingSearchCriteria } from './domain/search-query.domain';
import { FilterMetadataResponseMapper } from './mappers/filter-metadata-response.mapper';
import { ListingResponseMapper } from './mappers/listing-response.mapper';
import { ListingReadRepositoryInterface } from './listing-read.repository.interface';
import { ISearchQueryBuilder } from './search-query-builder.interface';
import { LISTING_READ_REPOSITORY, SEARCH_QUERY_BUILDER } from './search.tokens';

@Injectable()
export class SearchService {
  constructor(
    @Inject(LISTING_READ_REPOSITORY) private readonly listingReadRepository: ListingReadRepositoryInterface,
    @Inject(SEARCH_QUERY_BUILDER) private readonly queryBuilder: ISearchQueryBuilder,
    @Inject(FILTER_METADATA_CACHE) private readonly filterMetadataCache: IFilterMetadataCache,
    private readonly config: ConfigService,
    private readonly listingMapper: ListingResponseMapper,
    private readonly filterMetadataMapper: FilterMetadataResponseMapper
  ) {}

  async search(criteria: ListingSearchCriteria) {
    const normalizedCriteria = criteria.sort === 'relevance' && !criteria.q ? { ...criteria, sort: 'newest' as const } : criteria;
    const query = this.queryBuilder.buildListingSearchQuery(normalizedCriteria);
    const result = await this.listingReadRepository.search(query);

    return this.listingMapper.toSearchResponse(result.rows, normalizedCriteria.page, normalizedCriteria.limit, result.total);
  }

  async findDetail(id: string) {
    const query = this.queryBuilder.buildListingDetailQuery(id);
    if(!query){
      throw new NotFoundException("qoury notfound !!")
    }
    console.log(query)
    const detail = await this.listingReadRepository.findDetail(query);
    console.log("details1!", detail)
    if (!detail) {
      throw new NotFoundException('Listing not found');
    }

    return this.listingMapper.toDetail(detail);
  }

  async getFilterMetadata() {
    const cached = this.filterMetadataCache.get();
    if (cached) {
      return this.filterMetadataMapper.toResponse(cached);
    }

    const query = this.queryBuilder.buildFilterMetadataQuery();
    const metadata = await this.listingReadRepository.getFilterMetadata(query);
    this.filterMetadataCache.set(metadata);

    return this.filterMetadataMapper.toResponse(metadata);
  }
}
