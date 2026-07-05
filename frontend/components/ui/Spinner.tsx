import { cn } from "./cn"

export interface SpinnerProps {
  size?: "sm" | "md" | "lg"
  label?: string
  className?: string
}

// Spinner — accessible loading indicator with required aria-label.
export function Spinner({ size = "md", label = "Loading", className }: SpinnerProps) {
  const sizeClass = size === "sm" ? "h-4 w-4" : size === "lg" ? "h-8 w-8" : "h-6 w-6"
  return (
    <span
      role="status"
      aria-live="polite"
      className={cn("inline-flex items-center gap-2 text-muted", className)}
    >
      <svg
        className={cn("animate-spin", sizeClass)}
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden
      >
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      <span className="sr-only">{label}</span>
    </span>
  )
}