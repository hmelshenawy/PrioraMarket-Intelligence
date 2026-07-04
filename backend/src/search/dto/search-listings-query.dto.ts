import { Transform, Type } from 'class-transformer';
import { IsIn, IsInt, IsNumber, IsOptional, IsString, Max, Min } from 'class-validator';
import { ListingSort } from '../domain/search-query.domain';

const sortValues: ListingSort[] = ['relevance', 'newest', 'price_asc', 'price_desc', 'year_asc', 'year_desc', 'km_asc', 'km_desc'];

function emptyToUndefined(value: unknown): unknown {
  return typeof value === 'string' && value.trim() === '' ? undefined : value;
}

export class SearchListingsQueryDto {
  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  q?: string;

  @IsOptional()
  @IsIn(['used', 'new'])
  @Transform(({ value }) => emptyToUndefined(value))
  condition?: 'used' | 'new';

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  make?: string;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  model?: string;

  @IsOptional()
  @IsInt()
  @Min(0)
  @Type(() => Number)
  yearFrom?: number;

  @IsOptional()
  @IsInt()
  @Min(0)
  @Type(() => Number)
  yearTo?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Type(() => Number)
  priceMin?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Type(() => Number)
  priceMax?: number;

  @IsOptional()
  @IsInt()
  @Min(0)
  @Type(() => Number)
  kmMin?: number;

  @IsOptional()
  @IsInt()
  @Min(0)
  @Type(() => Number)
  kmMax?: number;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  location?: string;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  sellerType?: string;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Type(() => Number)
  page = 1;

  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(100)
  @Type(() => Number)
  limit = 20;

  @IsOptional()
  @IsIn(sortValues)
  sort: ListingSort = 'newest';
}
