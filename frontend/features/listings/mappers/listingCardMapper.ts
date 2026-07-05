import {
  EMPTY_VALUE,
  formatAed,
  formatDate,
  formatKm,
  formatRelativeDate,
} from "@/lib/formatting"
import { EMPTY_LABELS } from "@/lib/constants/emptyValue"
import type { ListingCardModel, ListingSearchResultDto } from "../types"

// A URL is only exposed when it is a usable http(s) link; otherwise treated as absent.
function validUrl(url: string | null): string | null {
  if (!url) return null
  try {
    const parsed = new URL(url)
    return parsed.protocol === "http:" || parsed.protocol === "https:" ? url : null
  } catch {
    return null
  }
}

// Map one listing DTO to a display-ready card model, centralizing null handling
// and formatting so card components never duplicate this logic or handle nulls.
export function mapListingCard(dto: ListingSearchResultDto): ListingCardModel {
  const title =
    dto.title?.trim() ||
    [dto.year, dto.make, dto.model].filter(Boolean).join(" ") ||
    "Untitled listing"
  const subtitle = [dto.make, dto.model, dto.trim].filter(Boolean).join(" ")

  return {
    id: dto.id,
    title,
    subtitle,
    priceLabel: dto.priceAed != null ? formatAed(dto.priceAed) : EMPTY_LABELS.price,
    kmLabel: dto.km != null ? formatKm(dto.km) : EMPTY_LABELS.mileage,
    yearLabel: dto.year != null ? String(dto.year) : EMPTY_VALUE,
    conditionLabel: dto.condition ?? EMPTY_VALUE,
    locationLabel: dto.location ?? EMPTY_LABELS.location,
    sellerTypeLabel: dto.sellerType ?? EMPTY_VALUE,
    href: `/listings/${encodeURIComponent(dto.id)}`,
    externalUrl: validUrl(dto.url),
    photosCount: dto.photosCount,
    firstSeenLabel: dto.firstSeenAt ? formatRelativeDate(dto.firstSeenAt) : EMPTY_VALUE,
    lastSeenLabel: dto.lastSeenAt ? formatDate(dto.lastSeenAt) : EMPTY_VALUE,
  }
}