import { cn } from "./cn"
import { Button, type ButtonProps } from "./Button"
import { AlertCircle } from "lucide-react"

export interface ErrorStateProps {
  title?: string
  message?: string
  retryLabel?: string
  onRetry?: () => void
  retryProps?: ButtonProps
  className?: string
}

// ErrorState — recoverable failure state with retry path. Never exposes stack traces.
export function ErrorState({
  title = "Something went wrong",
  message = "We couldn't load this content. Please try again.",
  retryLabel = "Try again",
  onRetry,
  retryProps,
  className,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className={cn("flex flex-col items-center justify-center gap-3 rounded-card border border-danger/30 bg-surface px-6 py-12 text-center", className)}
    >
      <AlertCircle aria-hidden className="h-8 w-8 text-danger" />
      <h2 className="text-lg font-semibold text-text">{title}</h2>
      <p className="max-w-md text-sm text-muted">{message}</p>
      {onRetry && (
        <Button type="button" onClick={onRetry} variant="secondary" {...retryProps}>
          {retryLabel}
        </Button>
      )}
    </div>
  )
}