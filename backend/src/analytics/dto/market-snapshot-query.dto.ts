import { Transform, Type } from 'class-transformer';
import { IsInt, IsOptional, IsString, Max, Min, Validate } from 'class-validator';
import {
  DEFAULT_PERIOD_DAYS,
  MAX_PERIOD_DAYS,
  MIN_PERIOD_DAYS
} from '../domain/applied-market-filters.domain';
import { MarketFilterHierarchyConstraint } from './market-filter-hierarchy.validator';

function emptyToUndefined(value: unknown): unknown {
  return typeof value === 'string' && value.trim() === '' ? undefined : value;
}

export class MarketSnapshotQueryDto {
  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  make?: string;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  model?: string;

  @IsOptional()
  @IsString()
  @Transform(({ value }) => emptyToUndefined(value))
  trim?: string;

  @IsOptional()
  @IsInt()
  @Min(1900)
  @Max(2100)
  @Type(() => Number)
  year?: number;

  /**
   * Always present (default 7), so the cross-field hierarchy constraint placed
   * here runs for every request and inspects the whole object.
   */
  @IsOptional()
  @IsInt()
  @Min(MIN_PERIOD_DAYS)
  @Max(MAX_PERIOD_DAYS)
  @Type(() => Number)
  @Validate(MarketFilterHierarchyConstraint)
  periodDays = DEFAULT_PERIOD_DAYS;
}