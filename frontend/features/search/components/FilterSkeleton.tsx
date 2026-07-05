import { Skeleton } from "@/components/ui/Skeleton"

// FilterSkeleton — placeholder for the filter sidebar while metadata loads.
// Mirrors the control stack dimensions.
export function FilterSkeleton() {
  return (
    <div className="flex flex-col gap-4" aria-hidden>
      {Array.from({ length: 4 }, (_, i) => (
        <div key={i} className="flex flex-col gap-1">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-10 w-full" />
        </div>
      ))}
      <Skeleton className="h-px w-full" />
      {Array.from({ length: 3 }, (_, i) => (
        <div key={i} className="flex flex-col gap-1">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-10 w-full" />
        </div>
      ))}
    </div>
  )
}