import { EMPTY_VALUE } from "./emptyValue"

// Locale-aware number grouping for counts and metrics.
export function formatNumber(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return EMPTY_VALUE
  return new Intl.NumberFormat("en-AE").format(value)
}