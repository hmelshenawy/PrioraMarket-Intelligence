import { cn } from "./cn"

export type StatusState = "checking" | "available" | "unavailable" | "degraded"

export interface StatusIndicatorProps {
  state: StatusState
  label?: string
  className?: string
}

const stateConfig: Record<StatusState, { dot: string; text: string; defaultLabel: string }> = {
  checking: { dot: "bg-muted", text: "text-muted", defaultLabel: "Checking backend…" },
  available: { dot: "bg-success", text: "text-success", defaultLabel: "Backend available" },
  unavailable: { dot: "bg-danger", text: "text-danger", defaultLabel: "Backend unavailable" },
  degraded: { dot: "bg-warning", text: "text-warning", defaultLabel: "Backend degraded" },
}

// StatusIndicator — accessible backend-availability signal in navigation.
// Color is never the only indicator: a text label always accompanies the dot.
export function StatusIndicator({ state, label, className }: StatusIndicatorProps) {
  const cfg = stateConfig[state]
  return (
    <span
      role="status"
      aria-live="polite"
      aria-label={label ?? cfg.defaultLabel}
      className={cn("inline-flex items-center gap-2 text-xs", cfg.text, className)}
    >
      <span aria-hidden className={cn("h-2 w-2 rounded-full", cfg.dot)} />
      <span className="hidden sm:inline">{label ?? cfg.defaultLabel}</span>
    </span>
  )
}