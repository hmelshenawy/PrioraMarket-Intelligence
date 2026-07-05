import { MarketFilterSelection } from './applied-market-filters.domain';

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

/**
 * Build the MarketScope for a selection. The level is the deepest selected filter;
 * the label is the canonical fallback (raw canonical values joined by a space).
 * Per the spec edge case, the canonical fallback is used WITHOUT transforming or
 * normalizing the values — catalog display names are introduced in US3 (T065).
 */
export function buildMarketScope(selection: MarketFilterSelection): MarketScope {
  const { make, model, trim, year } = selection;
  if (make && model && trim && year !== undefined) {
    return { level: 'year', label: `${make} ${model} ${trim} ${year}`, canonical: { make, model, trim, year } };
  }
  if (make && model && trim) {
    return { level: 'trim', label: `${make} ${model} ${trim}`, canonical: { make, model, trim } };
  }
  if (make && model) {
    return { level: 'model', label: `${make} ${model}`, canonical: { make, model } };
  }
  if (make) {
    return { level: 'make', label: make, canonical: { make } };
  }
  return { level: 'overall', label: 'Overall UAE Used Cars', canonical: {} };
}