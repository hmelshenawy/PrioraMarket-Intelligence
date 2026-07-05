// Market presentation formatting. Reuses the shared formatting helpers for AED and
// numbers; adds percentage and "As of" rendering. Presentation only — no recalculation.
//
// `freshness` (lastUpdated/datasetVersion/scrapeRunId) is raw metadata and MUST NOT be
// rendered as a real-time market reading. The user-facing recency cue is "As of
// <generatedAt>" via formatAsOf below.

import { formatDateTime, formatNumber } from "@/lib/formatting"

export { formatAed, formatNumber } from "@/lib/formatting"

// Percentage with a fixed fractional precision. Null/invalid → placeholder.
export function formatPercent(value: number | null | undefined, fractionDigits = 1): string {
  if (value == null || !Number.isFinite(value)) return "—"
  return `${value.toFixed(fractionDigits)}%`
}

// "As of <generatedAt>" — the user-facing recency cue. Sourced from generatedAt, never
// from freshness.lastUpdated.
export function formatAsOf(generatedAt: string | null | undefined): string {
  if (!generatedAt) return "—"
  const date = new Date(generatedAt)
  if (Number.isNaN(date.getTime())) return "—"
  return `As of ${formatDateTime(generatedAt)}`
}

// Compact AED for large counts (e.g., 4,381 → "AED 4,381"); used for non-price integers.
export function formatCount(value: number | null | undefined): string {
  return formatNumber(value)
}