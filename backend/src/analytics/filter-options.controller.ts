import { Controller, Get, Query } from '@nestjs/common';
import { FilterOptionsService } from './filter-options.service';
import { FilterOptionsQueryDto } from './dto/filter-options-query.dto';

/**
 * FilterOptionsController — thin HTTP adapter for GET /api/v1/market/filter-options.
 * Validates the query DTO and delegates to the service. No business logic.
 */
@Controller('market/filter-options')
export class FilterOptionsController {
  constructor(private readonly service: FilterOptionsService) {}

  @Get()
  getOptions(@Query() query: FilterOptionsQueryDto) {
    return this.service.getOptions(query);
  }
}