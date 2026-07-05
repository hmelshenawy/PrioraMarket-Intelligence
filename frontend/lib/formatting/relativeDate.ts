import { EMPTY_VALUE } from "./emptyValue"

// Friendly recency labels while preserving access to absolute dates in tooltips/details.
export function formatRelativeDate(value: string | null | undefined): string {
  if (!value) return EMPTY_VALUE
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return EMPTY_VALUE

  const now = Date.now()
  const diffMs = now - date.getTime()
  const sec = Math.round(diffMs / 1000)
  const min = Math.round(sec / 60)
  const hr = Math.round(min / 60)
  const day = Math.round(hr / 24)

  if (sec < 60) return "just now"
  if (min < 60) return `${min} min ago`
  if (hr < 24) return `${hr} hr ago`
  if (day < 30) return `${day} day${day === 1 ? "" : "s"} ago`
  const month = Math.round(day / 30)
  if (month < 12) return `${month} month${month === 1 ? "" : "s"} ago`
  const year = Math.round(day / 365)
  return `${year} year${year === 1 ? "" : "s"} ago`
}