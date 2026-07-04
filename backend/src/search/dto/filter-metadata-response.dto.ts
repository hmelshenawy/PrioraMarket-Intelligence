export class NumericRangeResponseDto {
  min!: number | null;
  max!: number | null;
}

export class FilterMetadataResponseDto {
  makes!: string[];
  models!: Record<string, string[]>;
  price!: NumericRangeResponseDto;
  year!: NumericRangeResponseDto;
  km!: NumericRangeResponseDto;
  conditions!: string[];
  sellerTypes!: string[];
}
