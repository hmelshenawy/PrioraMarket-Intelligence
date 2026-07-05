import { MarketFilterSelection } from './domain/applied-market-filters.domain';
import { FilterOption } from './domain/filter-option.domain';
import { Freshness } from './domain/freshness.domain';

/**
 * Read-only data access for the filter-options endpoint. Returns canonical option
 * values with display names and optional active-listing counts. Data access only —
 * no hierarchy resolution, no formatting.
 */
export interface FilterReadRepositoryInterface {
  listMakes(): Promise<FilterOption[]>;
  listModels(make: string): Promise<FilterOption[]>;
  listTrims(make: string, model: string): Promise<FilterOption[]>;
  listYears(make: string, model: string, trim: string): Promise<FilterOption[]>;
  getFreshness(filters: MarketFilterSelection): Promise<Freshness>;
}