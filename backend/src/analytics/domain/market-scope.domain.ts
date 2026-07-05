export type MarketScopeLevel = 'overall' | 'make' | 'model' | 'trim' | 'year';

export interface MarketScopeCanonical {
  make?: string;
  model?: string;
  trim?: string;
  year?: number | null;
}

export interface MarketScope {
  level: MarketScopeLevel;
  label: string;
  canonical: MarketScopeCanonical;
}