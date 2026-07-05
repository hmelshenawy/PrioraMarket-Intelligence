export interface FilterOption {
  /** Canonical string value, or integer for year options. */
  value: string | number;
  /** Catalog display name when available, canonical fallback otherwise. */
  displayName: string;
  activeListingCount?: number | null;
}