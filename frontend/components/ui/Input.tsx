import { forwardRef } from "react"
import { cn } from "./cn"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  hint?: string
}

// Input — labeled text entry. Server-compatible (no client-only behavior).
export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, hint, id, className, ...props },
  ref,
) {
  const inputId = id ?? props.name
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-text">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        className={cn(
          "h-10 rounded-control border border-border bg-elevated px-3 text-sm text-text",
          "placeholder:text-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus",
          "disabled:opacity-50",
          className,
        )}
        {...props}
      />
      {hint && <span className="text-xs text-muted">{hint}</span>}
    </div>
  )
})