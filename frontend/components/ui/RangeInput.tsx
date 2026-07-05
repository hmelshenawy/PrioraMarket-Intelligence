"use client"

import { forwardRef } from "react"
import { cn } from "./cn"

export interface RangeInputProps {
  label: string
  name: string
  minPlaceholder?: string
  maxPlaceholder?: string
  min?: number | string
  max?: number | string
  onMinChange?: (value: string) => void
  onMaxChange?: (value: string) => void
  className?: string
}

// RangeInput — pair of min/max numeric inputs for price/year/km ranges.
// Min > max is corrected before URL update by the caller.
export const RangeInput = forwardRef<HTMLDivElement, RangeInputProps>(function RangeInput(
  { label, name, minPlaceholder = "Min", maxPlaceholder = "Max", min, max, onMinChange, onMaxChange, className },
  ref,
) {
  return (
    <div ref={ref} className={cn("flex flex-col gap-1", className)}>
      <span className="text-sm font-medium text-text">{label}</span>
      <div className="flex items-center gap-2">
        <input
          type="number"
          inputMode="numeric"
          aria-label={`${label} minimum`}
          name={`${name}Min`}
          value={min ?? ""}
          placeholder={minPlaceholder}
          onChange={(e) => onMinChange?.(e.target.value)}
          className="h-10 w-full rounded-control border border-border bg-elevated px-2 text-sm text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        />
        <span className="text-muted">–</span>
        <input
          type="number"
          inputMode="numeric"
          aria-label={`${label} maximum`}
          name={`${name}Max`}
          value={max ?? ""}
          placeholder={maxPlaceholder}
          onChange={(e) => onMaxChange?.(e.target.value)}
          className="h-10 w-full rounded-control border border-border bg-elevated px-2 text-sm text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        />
      </div>
    </div>
  )
})