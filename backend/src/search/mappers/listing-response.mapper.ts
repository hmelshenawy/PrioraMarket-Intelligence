import { Injectable } from '@nestjs/common';
import { ListingDetailDomain, ListingDomain } from '../domain/listing.domain';
import { ListingDetailResponseDto } from '../dto/listing-detail-response.dto';
import { ListingSearchResultResponseDto, SearchListingsResponseDto } from '../dto/listing-search-result-response.dto';
import { PaginationMetaResponseDto } from '../dto/pagination-meta-response.dto';

@Injectable()
export class ListingResponseMapper {
  toSearchResult(listing: ListingDomain): ListingSearchResultResponseDto {
    return { ...listing };
  }

  toPaginationMeta(page: number, limit: number, total: number): PaginationMetaResponseDto {
    return {
      page,
      limit,
      total,
      totalPages: total === 0 ? 0 : Math.ceil(total / limit)
    };
  }

  toSearchResponse(rows: ListingDomain[], page: number, limit: number, total: number): SearchListingsResponseDto {
    return {
      data: rows.map((row) => this.toSearchResult(row)),
      meta: this.toPaginationMeta(page, limit, total)
    };
  }

  toDetail(detail: ListingDetailDomain): ListingDetailResponseDto {
    return { ...detail };
  }
}
