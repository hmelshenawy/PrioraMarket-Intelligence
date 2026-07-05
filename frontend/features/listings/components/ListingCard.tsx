"use client"

import Link from "next/link"
import { ExternalLink } from "lucide-react"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Tag } from "@/components/ui/Tag"
import { cn } from "@/components/ui/cn"
import { captureScroll } from "@/lib/routing/scrollRestore"
import { ListingImage } from "./ListingImage"
import type { ListingCardModel } from "../types"

export interface ListingCardProps {
  item: ListingCardModel
  className?: string
}

// ListingCard — display-ready card linking to the listing detail route.
// Captures scroll position on click so the back journey restores the user's
// place in the results. Uses sibling anchors to keep the internal detail link
// and external marketplace link valid, keyboard-accessible HTML.
export function ListingCard({ item, className }: ListingCardProps) {
  return (
    <Card
      as="article"
      className={cn(
        "group relative h-full transition hover:border-accent focus-within:border-accent",
        className,
      )}
    >
      <Link
        href={item.href}
        onClick={captureScroll}
        className="absolute inset-0 z-10 rounded-card focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        <span className="sr-only">View details for {item.title}</span>
      </Link>
      <ListingImage title={item.title} photosCount={item.photosCount} />
      <div className="flex flex-col gap-2 p-4">
        <div className="flex items-start justify-between gap-2">
          <span className="text-lg font-semibold text-text">{item.priceLabel}</span>
          {item.conditionLabel !== "—" && (
            <Badge variant="neutral" className="capitalize">
              {item.conditionLabel}
            </Badge>
          )}
        </div>
        <h3 className="line-clamp-2 text-sm font-medium text-text">{item.title}</h3>
        {item.subtitle && <p className="text-xs text-muted">{item.subtitle}</p>}
        <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted">
          <Tag>{item.yearLabel}</Tag>
          <Tag>{item.kmLabel}</Tag>
          {item.sellerTypeLabel !== "—" && <Tag className="capitalize">{item.sellerTypeLabel}</Tag>}
        </div>
        <p className="text-xs text-muted">{item.locationLabel}</p>
        <div className="mt-2 flex items-center justify-between border-t border-border pt-2 text-[11px] text-muted">
          <span>First seen {item.firstSeenLabel}</span>
          <span>Updated {item.lastSeenLabel}</span>
        </div>
        {item.externalUrl && (
          <a
            href={item.externalUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="relative z-20 mt-1 inline-flex items-center gap-1 text-xs text-accent hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            <ExternalLink aria-hidden className="h-3 w-3" />
            View on marketplace
          </a>
        )}
      </div>
    </Card>
  )
}
