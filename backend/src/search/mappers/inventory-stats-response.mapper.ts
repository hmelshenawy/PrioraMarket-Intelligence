import { Injectable } from '@nestjs/common';
import { InventoryStatsDomain } from '../domain/listing-stats.domain';
import { InventoryStatsResponseDto } from '../dto/inventory-stats-response.dto';

@Injectable()
export class InventoryStatsResponseMapper {
  toResponse(stats: InventoryStatsDomain): InventoryStatsResponseDto {
    return { ...stats };
  }
}
