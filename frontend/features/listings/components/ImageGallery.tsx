import { ImageIcon } from "lucide-react"
import { Badge } from "@/components/ui/Badge"
import { cn } from "@/components/ui/cn"

export interface ImageGalleryProps {
  title: string
  photosCount?: number | null
}

// ImageGallery — large media area for the detail page. Feature 003 does not
// expose image URLs, so it always renders an accessible placeholder that does
// not imply a real photo. photosCount is metadata only.
export function ImageGallery({ title, photosCount }: ImageGalleryProps) {
  return (
    <div
      className={cn(
        "relative flex aspect-video items-center justify-center overflow-hidden rounded-card border border-border bg-surface",
      )}
    >
      <div className="flex flex-col items-center gap-2 text-muted" aria-hidden>
        <ImageIcon className="h-12 w-12" />
        <span className="text-xs">No photo available</span>
      </div>
      <span className="sr-only">No photo available for {title}</span>
      {photosCount != null && photosCount > 0 && (
        <Badge variant="neutral" className="absolute right-3 top-3">
          {photosCount} photo{photosCount === 1 ? "" : "s"}
        </Badge>
      )}
    </div>
  )
}
