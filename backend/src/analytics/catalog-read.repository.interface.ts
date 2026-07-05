/**
 * Read-only data access for the Vehicle Reference Catalog. Resolves catalog
 * display names (make_display, model_display) for canonical make/model keys.
 *
 * Read-only: never mutates catalog data. Returns the raw catalog display string
 * or `null` when no catalog row exists for a canonical key — the caller applies
 * the canonical-fallback policy. No normalization of the returned values.
 *
 * Trim and year display names are NOT resolved here: the catalog has no trim
 * display column, and year display is the integer itself. Those use canonical
 * fallback at the consumption site (spec edge case 83).
 */
export interface CatalogReadRepositoryInterface {
  /** Single canonical make → catalog make_display, or null when absent. */
  findMakeDisplay(make: string): Promise<string | null>;
  /** Single canonical (make, model) → catalog model_display, or null when absent. */
  findModelDisplay(make: string, model: string): Promise<string | null>;
  /**
   * Batch canonical makes → map keyed by lowercased canonical make to catalog
   * make_display (or null). Used by the filter-options repository to populate
   * make option display names in one query.
   */
  findMakeDisplays(makes: string[]): Promise<Map<string, string | null>>;
  /**
   * Batch canonical models under one make → map keyed by lowercased canonical
   * model to catalog model_display (or null).
   */
  findModelDisplays(make: string, models: string[]): Promise<Map<string, string | null>>;
}