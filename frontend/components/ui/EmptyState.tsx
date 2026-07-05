import Link from "next/link"
import { cn } from "./cn"
import { Button, type ButtonProps } from "./Button"

export interface EmptyStateProps {
  title: string
  description?: string
  illustration?: React.ReactNode
  actionLabel?: string
  onAction?: () => void
  actionHref?: string
  actionProps?: ButtonProps
  className?: string
}

// EmptyState — friendly non-data state with explanation and optional action.
// Use `actionHref` for navigation (server-compatible) or `onAction` for client callbacks.
export function EmptyState({
  title,
  description,
  illustration,
  actionLabel,
  onAction,
  actionHref,
  actionProps,
  className,
}: EmptyStateProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn("flex flex-col items-center justify-center gap-3 rounded-card border border-border bg-surface px-6 py-12 text-center", className)}
    >
      {illustration && <div aria-hidden className="text-muted">{illustration}</div>}
      <h2 className="text-lg font-semibold text-text">{title}</h2>
      {description && <p className="max-w-md text-sm text-muted">{description}</p>}
      {actionLabel && onAction && (
        <Button type="button" onClick={onAction} variant="secondary" {...actionProps}>
          {actionLabel}
        </Button>
      )}
      {actionLabel && actionHref && !onAction && (
        <Link
          href={actionHref}
          className={cn(
            "inline-flex h-10 items-center justify-center rounded-control border border-border bg-elevated px-4 text-sm font-medium text-text hover:bg-surface",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus",
          )}
          {...(actionProps as Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, "href">)}
        >
          {actionLabel}
        </Link>
      )}
    </div>
  )
}