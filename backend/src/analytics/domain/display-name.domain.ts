import { MarketScopeLevel } from './market-scope.domain';

/**
 * Display-name resolution policy (spec edge case 83): when a catalog display
 * name exists, use it; otherwise fall back to the canonical value WITHOUT
 * transforming or normalizing it. This is the single rule applied at every
 * consumption site (filter options + scope label).
 *
 * @param catalogDisplay raw catalog display name, or null/empty when absent
 * @param canonicalValue  the canonical value, returned unchanged on fallback
 */
export function displayOrCanonical(catalogDisplay: string | null | undefined, canonicalValue: string | number): string {
  return catalogDisplay && catalogDisplay.length > 0 ? catalogDisplay : String(canonicalValue);
}

/**
 * Resolved display names for a market scope. Trim and year always carry the
 * canonical fallback (the catalog exposes no trim/year display column); make
 * and model carry the catalog display name when available, canonical fallback
 * otherwise. Year is the string form of the integer.
 */
export interface ScopeDisplayNames {
  make?: string;
  model?: string;
  trim?: string;
  year?: string;
}

/**
 * Build the human-readable scope label from resolved display names. Pure —
 * no DB access, no normalization. Joins the display names available at the
 * scope's level with a single space. The overall level has no selection and
 * renders the fixed overall label.
 */
export function buildScopeDisplayLabel(level: MarketScopeLevel, names: ScopeDisplayNames): string {
  switch (level) {
    case 'year':
      return `${names.make ?? ''} ${names.model ?? ''} ${names.trim ?? ''} ${names.year ?? ''}`.trim();
    case 'trim':
      return `${names.make ?? ''} ${names.model ?? ''} ${names.trim ?? ''}`.trim();
    case 'model':
      return `${names.make ?? ''} ${names.model ?? ''}`.trim();
    case 'make':
      return `${names.make ?? ''}`.trim();
    case 'overall':
    default:
      return 'Overall UAE Used Cars';
  }
}