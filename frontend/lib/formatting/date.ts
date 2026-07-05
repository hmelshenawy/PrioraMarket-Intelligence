import { EMPTY_VALUE } from "./emptyValue"

// Absolute date formatting for first seen / last seen / last updated.
export function formatDate(value: string | null | undefined): string {
  if (!value) return EMPTY_VALUE
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return EMPTY_VALUE
  return new Intl.DateTimeFormat("en-AE", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date)
}

// Date + time formatting for detailed timestamps.
export function formatDateTime(value: string | null | undefined): string {
  if (!value) return EMPTY_VALUE
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return EMPTY_VALUE
  return new Intl.DateTimeFormat("en-AE", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date)
}