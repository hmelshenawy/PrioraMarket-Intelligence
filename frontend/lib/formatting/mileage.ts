import { EMPTY_VALUE } from "./emptyValue"

// Mileage formatting in kilometers with grouping and unit label.
export function formatKm(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return EMPTY_VALUE
  const formatter = new Intl.NumberFormat("en-AE", { maximumFractionDigits: 0 })
  return `${formatter.format(value)} km`
}