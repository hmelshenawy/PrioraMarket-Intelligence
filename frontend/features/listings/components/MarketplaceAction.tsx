"use client"

import { ExternalLink, Unlink } from "lucide-react"
import { Button } from "@/components/ui/Button"

export interface MarketplaceActionProps {
  url: string | null
  title?: string
}

// MarketplaceAction — opens the original marketplace listing in a new browser
// context. Hidden when no valid URL exists (validated by the mapper); never
// renders a broken or unsafe link.
export function MarketplaceAction({ url, title = "listing" }: MarketplaceActionProps) {
  if (!url) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted" role="status">
        <Unlink aria-hidden className="h-4 w-4" />
        <span>No marketplace link available for this {title}.</span>
      </div>
    )
  }
  return (
    <Button
      type="button"
      variant="secondary"
      onClick={() => window.open(url, "_blank", "noopener,noreferrer")}
      className="w-full sm:w-auto"
    >
      <ExternalLink aria-hidden className="h-4 w-4" />
      View on marketplace
    </Button>
  )
}