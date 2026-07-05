import { ImageIcon } from "lucide-react"
import { Badge } from "@/components/ui/Badge"
import { cn } from "@/components/ui/cn"

export interface ListingImageProps {
  title: string
  photosCount?: number | null
  className?: string
}

// ListingImage — fixed-aspect media area for a listing card.
// Feature 003 exposes photosCount but no addressable image URLs, so this
// component always renders a placeholder. photosCount is metadata only.
export function ListingImage({ title, photosCount, className }: ListingImageProps) {
  return (
    <div
      // className={cn(
      //   "relative flex aspect-video items-center justify-center overflow-hidden rounded-t-card bg-surface",
      //   className,
      // )}
    >
      {/* <div className="flex flex-col items-center gap-1 text-muted" aria-hidden>
        <ImageIcon className="h-8 w-8" />
      </div> */}
      <span className="sr-only">No photo available for {title}</span>
      {photosCount != null && photosCount > 0 && (
        <Badge variant="neutral" className="absolute right-2 top-2">
          {photosCount} photo{photosCount === 1 ? "" : "s"}
        </Badge>
      )}
    </div>
  )
}
