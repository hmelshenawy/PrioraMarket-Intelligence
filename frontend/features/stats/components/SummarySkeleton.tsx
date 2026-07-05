import { Skeleton } from "@/components/ui/Skeleton"

// SummarySkeleton — placeholder for the Market Overview section while stats load.
// aria-hidden so assistive tech announces a pending region rather than reading blocks.
export function SummarySkeleton() {
  return (
    <div aria-hidden className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      {Array.from({ length: 6 }, (_, i) => (
        <div key={i} className="flex flex-col gap-2 rounded-card border border-border bg-elevated p-4">
          <Skeleton className="h-3 w-20" />
          <Skeleton className="h-7 w-16" />
        </div>
      ))}
    </div>
  )
}