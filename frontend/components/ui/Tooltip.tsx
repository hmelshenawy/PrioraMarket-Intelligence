"use client"

import { useId, useState } from "react"
import { cn } from "./cn"

export interface TooltipProps {
  content: React.ReactNode
  children: React.ReactNode
  className?: string
}

// Tooltip — supplemental info shown on focus/hover. Never used for critical-only content.
export function Tooltip({ content, children, className }: TooltipProps) {
  const [open, setOpen] = useState(false)
  const id = useId()
  return (
    <span
      className="relative inline-flex"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <span aria-describedby={open ? id : undefined} tabIndex={0}>
        {children}
      </span>
      {open && (
        <span
          id={id}
          role="tooltip"
          className={cn(
            "absolute bottom-full left-1/2 z-tooltip mb-2 -translate-x-1/2 whitespace-nowrap rounded-control bg-elevated px-2 py-1 text-xs text-text shadow-dropdown border border-border",
            className,
          )}
        >
          {content}
        </span>
      )}
    </span>
  )
}