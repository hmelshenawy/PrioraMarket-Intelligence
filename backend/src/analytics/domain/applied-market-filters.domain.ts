export const DEFAULT_PERIOD_DAYS = 7;
export const MIN_PERIOD_DAYS = 1;
export const MAX_PERIOD_DAYS = 90;

export interface AppliedMarketFilters {
  make?: string;
  model?: string;
  trim?: string;
  year?: number;
  periodDays: number;
}

export interface MarketFilterSelection {
  make?: string;
  model?: string;
  trim?: string;
  year?: number;
}

/**
 * Returns a human-readable hierarchy error message, or null when the selection is valid.
 * Hierarchy rules (no normalization of values, shape only):
 *   - model requires make
 *   - trim requires make and model
 *   - year requires make, model, and trim
 */
export function marketFiltersHierarchyError(selection: MarketFilterSelection): string | null {
  if (selection.model && !selection.make) {
    return 'model requires make';
  }
  if (selection.trim && (!selection.make || !selection.model)) {
    return 'trim requires make and model';
  }
  if (selection.year !== undefined && (!selection.make || !selection.model || !selection.trim)) {
    return 'year requires make, model, and trim';
  }
  return null;
}

export function toAppliedMarketFilters(selection: MarketFilterSelection, periodDays = DEFAULT_PERIOD_DAYS): AppliedMarketFilters {
  return {
    make: selection.make,
    model: selection.model,
    trim: selection.trim,
    year: selection.year,
    periodDays
  };
}