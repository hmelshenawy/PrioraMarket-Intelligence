import { cn } from "./cn"

export type SkeletonProps = React.HTMLAttributes<HTMLDivElement>

// Skeleton — placeholder block using skeleton token with a shimmer animation.
export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn("animate-pulse rounded-control bg-skeleton", className)}
      aria-hidden
      {...props}
    />
  )
}