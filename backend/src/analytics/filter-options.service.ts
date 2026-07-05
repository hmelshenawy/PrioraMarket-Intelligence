import { Inject, Injectable } from '@nestjs/common';
import { MarketFilterSelection } from './domain/applied-market-filters.domain';
import { FilterOptionsResponseMapper, FilterOptionsResult } from './mappers/filter-options-response.mapper';
import { FilterReadRepositoryInterface } from './filter-read.repository.interface';
import { FILTER_READ_REPOSITORY } from './analytics.tokens';
import { FilterOptionsQueryDto } from './dto/filter-options-query.dto';

/**
 * FilterOptionsService — application orchestration for the cascading filter-options
 * endpoint. Builds the selection from the query DTO, fans out read-only repository
 * calls (only the levels allowed by the current hierarchy), populates `freshness`
 * from the scoped active listings, sets generatedAt, and delegates to the mapper.
 * No business calculations, no DB access, no formatting.
 */
@Injectable()
export class FilterOptionsService {
  constructor(
    @Inject(FILTER_READ_REPOSITORY) private readonly repository: FilterReadRepositoryInterface,
    private readonly mapper: FilterOptionsResponseMapper
  ) {}

  async getOptions(query: FilterOptionsQueryDto) {
    const selection: MarketFilterSelection = {
      make: query.make,
      model: query.model,
      trim: query.trim,
      year: query.year
    };

    const [makes, models, trims, years, freshness] = await Promise.all([
      this.repository.listMakes(),
      selection.make ? this.repository.listModels(selection.make) : Promise.resolve([]),
      selection.make && selection.model ? this.repository.listTrims(selection.make, selection.model) : Promise.resolve([]),
      selection.make && selection.model && selection.trim
        ? this.repository.listYears(selection.make, selection.model, selection.trim)
        : Promise.resolve([]),
      this.repository.getFreshness(selection)
    ]);

    const result: FilterOptionsResult = {
      filters: selection,
      options: { makes, models, trims, years },
      freshness,
      generatedAt: new Date().toISOString()
    };

    return this.mapper.toResponse(result);
  }
}