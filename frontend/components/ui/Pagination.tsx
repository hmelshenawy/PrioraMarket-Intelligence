"use client"

import { cn } from "./cn"

export interface PaginationProps {
  page: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
}

// Pagination — keyboard-accessible paged navigation using backend meta.
// Out-of-bounds pages are normalized by the caller before rendering.
export function Pagination({ page, totalPages, onPageChange, className }: PaginationProps) {
  if (totalPages <= 1) return null
  const pages = computePageWindow(page, totalPages)

  const go = (p: number) => {
    const next = Math.min(Math.max(1, p), totalPages)
    if (next !== page) onPageChange(next)
  }

  return (
    <nav aria-label="Pagination" className={cn("flex items-center gap-1", className)}>
      <PaginationButton onClick={() => go(page - 1)} disabled={page <= 1} aria-label="Previous page">
        ‹
      </PaginationButton>
      {pages.map((p, idx) =>
        p === "…" ? (
          <span key={`ellipsis-${idx}`} className="px-2 text-muted" aria-hidden>
            …
          </span>
        ) : (
          <PaginationButton
            key={p}
            onClick={() => go(p)}
            aria-current={p === page ? "page" : undefined}
            aria-label={`Page ${p}`}
            active={p === page}
          >
            {p}
          </PaginationButton>
        ),
      )}
      <PaginationButton onClick={() => go(page + 1)} disabled={page >= totalPages} aria-label="Next page">
        ›
      </PaginationButton>
    </nav>
  )
}

function PaginationButton({
  children,
  onClick,
  disabled,
  active,
  "aria-current": ariaCurrent,
  "aria-label": ariaLabel,
}: {
  children: React.ReactNode
  onClick: () => void
  disabled?: boolean
  active?: boolean
  "aria-current"?: "page"
  "aria-label"?: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-current={ariaCurrent}
      aria-label={ariaLabel}
      className={cn(
        "inline-flex h-9 min-w-9 items-center justify-center rounded-control border border-border px-2 text-sm",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus disabled:opacity-50",
        active ? "bg-accent text-accent-foreground" : "bg-elevated text-text hover:bg-surface",
      )}
    >
      {children}
    </button>
  )
}

function computePageWindow(page: number, total: number): (number | "…")[] {
  const window = 1
  const pages: (number | "…")[] = []
  const push = (p: number | "…") => pages.push(p)
  push(1)
  if (page - window > 2) push("…")
  for (let p = Math.max(2, page - window); p <= Math.min(total - 1, page + window); p++) push(p)
  if (page + window < total - 1) push("…")
  if (total > 1) push(total)
  return pages
}