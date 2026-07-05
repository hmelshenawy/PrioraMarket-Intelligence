import { cn } from "./cn"

export type TagProps = React.HTMLAttributes<HTMLSpanElement>

// Tag — compact label for categorical metadata (e.g., condition, seller type).
export function Tag({ className, ...props }: TagProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-control border border-border bg-surface px-2 py-0.5 text-xs text-text",
        className,
      )}
      {...props}
    />
  )
}