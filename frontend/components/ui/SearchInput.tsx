"use client"

import { forwardRef, useEffect, useRef, useState } from "react"
import { Search, X } from "lucide-react"
import { cn } from "./cn"
import { SEARCH_DEBOUNCE_MS } from "@/lib/constants/debounce"

export interface SearchInputProps {
  initialValue?: string
  placeholder?: string
  ariaLabel?: string
  onDebouncedChange: (value: string) => void
  debounceMs?: number
  className?: string
}

// SearchInput — client component with immediate visible input and debounced URL/API update.
export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(function SearchInput(
  { initialValue = "", placeholder = "Search listings…", ariaLabel = "Search listings", onDebouncedChange, debounceMs = SEARCH_DEBOUNCE_MS, className },
  ref,
) {
  const [value, setValue] = useState(initialValue)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Re-seed from URL when the initial value changes (e.g., browser Back/Forward).
  useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  useEffect(() => {
    return () => {
      if (timer.current) clearTimeout(timer.current)
    }
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const next = e.target.value
    setValue(next)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => onDebouncedChange(next.trim()), debounceMs)
  }

  const handleClear = () => {
    setValue("")
    if (timer.current) clearTimeout(timer.current)
    onDebouncedChange("")
  }

  return (
    <div className={cn("relative flex items-center", className)}>
      <Search aria-hidden className="pointer-events-none absolute left-3 h-4 w-4 text-muted" />
      <input
        ref={ref}
        type="search"
        role="searchbox"
        aria-label={ariaLabel}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className={cn(
          "h-10 w-full rounded-control border border-border bg-elevated pl-9 pr-9 text-sm text-text",
          "placeholder:text-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus",
        )}
      />
      {value && (
        <button
          type="button"
          aria-label="Clear search"
          onClick={handleClear}
          className="absolute right-2 inline-flex h-6 w-6 items-center justify-center rounded-control text-muted hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
        >
          <X aria-hidden className="h-4 w-4" />
        </button>
      )}
    </div>
  )
})