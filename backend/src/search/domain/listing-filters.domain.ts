export interface NumericRangeDomain {
  min: number | null;
  max: number | null;
}

export interface FilterMetadataDomain {
  makes: string[];
  models: Record<string, string[]>;
  price: NumericRangeDomain;
  year: NumericRangeDomain;
  km: NumericRangeDomain;
  conditions: string[];
  sellerTypes: string[];
}
