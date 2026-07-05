import { cn } from "./cn"

export type AlertVariant = "info" | "success" | "warning" | "danger"

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant
  title?: string
}

const variants: Record<AlertVariant, string> = {
  info: "border-accent/30 text-text",
  success: "border-success/30 text-text",
  warning: "border-warning/30 text-text",
  danger: "border-danger/30 text-text",
}

// Alert — inline notification with semantic tone.
export function Alert({ variant = "info", title, className, children, ...props }: AlertProps) {
  return (
    <div
      role="alert"
      className={cn("rounded-control border bg-surface px-4 py-3 text-sm", variants[variant], className)}
      {...props}
    >
      {title && <p className="font-semibold">{title}</p>}
      {children && <div className={cn("text-sm text-muted", title && "mt-1")}>{children}</div>}
    </div>
  )
}