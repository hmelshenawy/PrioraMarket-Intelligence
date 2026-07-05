import { Injectable } from '@nestjs/common';
import { MarketFilterSelection } from '../domain/applied-market-filters.domain';
import { FilterOption } from '../domain/filter-option.domain';
import { Freshness } from '../domain/freshness.domain';
import { FilterOptionsResponseDto } from '../dto/filter-options-response.dto';

/** Domain result assembled by the filter-options service before mapping. */
export interface FilterOptionsResult {
  filters: MarketFilterSelection;
  options: {
    makes: FilterOption[];
    models: FilterOption[];
    trims: FilterOption[];
    years: FilterOption[];
  };
  freshness: Freshness;
  generatedAt: string;
}

/**
 * Maps the filter-options domain result to the response DTO (raw values only).
 * Phase 2 skeleton — field mapping is complete; extended in Phase 4 once the
 * filter-options service is implemented.
 */
@Injectable()
export class FilterOptionsResponseMapper {
  toResponse(result: FilterOptionsResult): FilterOptionsResponseDto {
    return {
      filters: result.filters,
      options: result.options,
      freshness: result.freshness,
      generatedAt: result.generatedAt
    };
  }
}