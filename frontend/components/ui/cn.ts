// Tiny class-name combiner (no external dependency). Filters falsy values.
export type ClassValue = string | number | null | false | undefined

export function cn(...classes: ClassValue[]): string {
  return classes.filter(Boolean).join(" ")
}