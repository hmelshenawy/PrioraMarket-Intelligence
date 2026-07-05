import { Transform, Type } from 'class-transformer';
import { IsInt, IsOptional, IsString, Max, Min, Validate } from 'class-validator';
import { MarketFilterHierarchyConstraint } from './market-filter-hierarchy.validator';

function emptyToUndefined(value: unknown): unknown {
  return typeof value === 'string' && value.trim() === '' ? undefined : value;
}

export class FilterOptionsQueryDto {
  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  @Validate(MarketFilterHierarchyConstraint)
  make?: string;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  @Validate(MarketFilterHierarchyConstraint)
  model?: string;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  @Validate(MarketFilterHierarchyConstraint)
  trim?: string;

  @IsOptional()
  @IsInt()
  @Min(1900)
  @Max(2100)
  @Type(() => Number)
  @Validate(MarketFilterHierarchyConstraint)
  year?: number;
}