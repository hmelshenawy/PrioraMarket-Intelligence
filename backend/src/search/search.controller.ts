import { Controller, Get, Param, Query } from '@nestjs/common';
import { SearchListingsQueryDto } from './dto/search-listings-query.dto';
import { SearchService } from './search.service';

@Controller('listings')
export class SearchController {
  constructor(private readonly searchService: SearchService) {}

  @Get()
  search(@Query() query: SearchListingsQueryDto) {
    return this.searchService.search(query);
  }

  @Get('filters')
  filters() {
    return this.searchService.getFilterMetadata();
  }

  @Get(':id')
  detail(@Param('id') id: string) {
    return this.searchService.findDetail(id);
  }
}
