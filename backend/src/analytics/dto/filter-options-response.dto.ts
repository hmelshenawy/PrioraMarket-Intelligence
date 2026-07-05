import { MarketFilterSelection } from '../domain/applied-market-filters.domain';
import { FilterOption } from '../domain/filter-option.domain';
import { Freshness } from '../domain/freshness.domain';

export interface FilterOptionsGroupDto {
  makes: FilterOption[];
  models: FilterOption[];
  trims: FilterOption[];
  years: FilterOption[];
}

/**
 * Response payload for GET /market/filters. Each option group is populated based on
 * the currently-applied selection; groups outside the active hierarchy are empty.
 */
export class FilterOptionsResponseDto {
  filters!: MarketFilterSelection;
  options!: FilterOptionsGroupDto;
  freshness!: Freshness;
  generatedAt!: string;
}