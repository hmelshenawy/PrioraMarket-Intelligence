import { cn } from "./cn"

export type BadgeVariant = "neutral" | "success" | "warning" | "danger" | "accent"

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

const variants: Record<BadgeVariant, string> = {
  neutral: "bg-surface text-muted border-border",
  success: "bg-surface text-success border-success/30",
  warning: "bg-surface text-warning border-warning/30",
  danger: "bg-surface text-danger border-danger/30",
  accent: "bg-surface text-accent border-accent/30",
}

// Badge — small status/metadata chip.
export function Badge({ variant = "neutral", className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-pill border px-2 py-0.5 text-xs font-medium",
        variants[variant],
        className,
      )}
      {...props}
    />
  )
}