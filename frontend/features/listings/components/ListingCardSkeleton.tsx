import { Card } from "@/components/ui/Card"
import { Skeleton } from "@/components/ui/Skeleton"
import { cn } from "@/components/ui/cn"

export interface ListingCardSkeletonProps {
  className?: string
}

// ListingCardSkeleton — placeholder preserving ListingCard dimensions for
// loading states. Same aspect ratio + content block heights as the real card.
export function ListingCardSkeleton({ className }: ListingCardSkeletonProps) {
  return (
    <Card className={cn("overflow-hidden", className)}>
      <Skeleton className="aspect-video w-full rounded-none" aria-hidden />
      <div className="flex flex-col gap-2 p-4">
        <Skeleton className="h-6 w-28" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-3 w-2/3" />
        <div className="mt-1 flex gap-2">
          <Skeleton className="h-5 w-12" />
          <Skeleton className="h-5 w-16" />
        </div>
        <Skeleton className="h-3 w-1/3" />
        <Skeleton className="mt-2 h-3 w-full" />
      </div>
    </Card>
  )
}