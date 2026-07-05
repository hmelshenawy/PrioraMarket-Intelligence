"use client"

import { forwardRef } from "react"
import { cn } from "./cn"

export interface SelectOption {
  value: string
  label: string
}

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, "onChange"> {
  label?: string
  options: SelectOption[]
  placeholder?: string
  onValueChange?: (value: string) => void
}

// Select — client filter control. Native select for accessibility + keyboard support.
export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, options, placeholder, value, onValueChange, id, className, disabled, ...props },
  ref,
) {
  const selectId = id ?? props.name
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={selectId} className="text-sm font-medium text-text">
          {label}
        </label>
      )}
      <select
        ref={ref}
        id={selectId}
        value={value ?? ""}
        disabled={disabled}
        onChange={(e) => onValueChange?.(e.target.value)}
        className={cn(
          "h-10 rounded-control border border-border bg-elevated px-3 text-sm text-text",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus disabled:opacity-50",
          className,
        )}
        {...props}
      >
        {placeholder != null && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  )
})