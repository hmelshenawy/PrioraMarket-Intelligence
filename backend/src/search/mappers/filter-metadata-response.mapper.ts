import { Injectable } from '@nestjs/common';
import { FilterMetadataDomain } from '../domain/listing-filters.domain';
import { FilterMetadataResponseDto } from '../dto/filter-metadata-response.dto';

@Injectable()
export class FilterMetadataResponseMapper {
  toResponse(metadata: FilterMetadataDomain): FilterMetadataResponseDto {
    return {
      makes: metadata.makes,
      models: metadata.models,
      price: metadata.price,
      year: metadata.year,
      km: metadata.km,
      conditions: metadata.conditions,
      sellerTypes: metadata.sellerTypes
    };
  }
}
