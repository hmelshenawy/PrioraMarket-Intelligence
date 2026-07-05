import { EMPTY_VALUE } from "./emptyValue"

// AED currency formatting. Null/undefined → empty placeholder.
// Never fabricates values for missing prices.
export function formatAed(value: number | null | undefined, opts: { compact?: boolean } = {}): string {
  if (value == null || !Number.isFinite(value)) return EMPTY_VALUE
  if (opts.compact && value >= 1000) {
    const formatter = new Intl.NumberFormat("en-AE", {
      notation: "compact",
      maximumFractionDigits: 1,
    })
    return `AED ${formatter.format(value)}`
  }
  const formatter = new Intl.NumberFormat("en-AE", { maximumFractionDigits: 0 })
  return `AED ${formatter.format(value)}`
}