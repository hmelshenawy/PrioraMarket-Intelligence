import {
  EMPTY_VALUE,
  formatAed,
  formatDate,
  formatKm,
  formatRelativeDate,
} from "@/lib/formatting"
import { EMPTY_LABELS } from "@/lib/constants/emptyValue"
import type { ListingDetailDto, ListingDetailModel, SpecRow } from "../types"

function validUrl(url: string | null): string | null {
  if (!url) return null
  try {
    const parsed = new URL(url)
    return parsed.protocol === "http:" || parsed.protocol === "https:" ? url : null
  } catch {
    return null
  }
}

const row = (label: string, value: string | null | undefined): SpecRow | null =>
  value == null || value === "" ? null : { label, value: String(value) }

// Map the detail DTO to the display-ready detail model, grouping fields into
// gallery/summary/specifications/seller-source and surfacing unknown specs keys
// as additional specifications. Centralizes all null handling and formatting.
export function mapListingDetail(dto: ListingDetailDto): ListingDetailModel {
  const title =
    dto.title?.trim() ||
    [dto.year, dto.make, dto.model].filter(Boolean).join(" ") ||
    "Untitled listing"

  const specifications: SpecRow[] = [
    row("Body type", dto.bodyType),
    row("Fuel", dto.fuel),
    row("Transmission", dto.transmission),
    row("Color", dto.color),
  ].filter((r): r is SpecRow => r !== null)

  // Unknown specs keys are displayed as additional specifications, safely.
  // Keys are humanized: camelCase split into words, then title-cased.
  const humanize = (k: string) =>
    k
      .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
      .replace(/\b\w/g, (c) => c.toUpperCase())
  const additionalSpecs: SpecRow[] = dto.specs
    ? Object.entries(dto.specs)
        .map(([k, v]) => row(humanize(k), v == null ? null : String(v)))
        .filter((r): r is SpecRow => r !== null)
    : []

  return {
    id: dto.id,
    title,
    href: `/listings/${encodeURIComponent(dto.id)}`,
    gallery: {
      photosCount: dto.photosCount,
    },
    summary: {
      priceLabel: dto.priceAed != null ? formatAed(dto.priceAed) : EMPTY_LABELS.price,
      yearLabel: dto.year != null ? String(dto.year) : EMPTY_VALUE,
      kmLabel: dto.km != null ? formatKm(dto.km) : EMPTY_LABELS.mileage,
      conditionLabel: dto.condition ?? EMPTY_VALUE,
      locationLabel: dto.location ?? EMPTY_LABELS.location,
      sellerTypeLabel: dto.sellerType ?? EMPTY_VALUE,
      firstSeenLabel: dto.firstSeenAt ? formatRelativeDate(dto.firstSeenAt) : EMPTY_VALUE,
      lastSeenLabel: dto.lastSeenAt ? formatDate(dto.lastSeenAt) : EMPTY_VALUE,
    },
    sellerSource: {
      sellerLabel: dto.seller ?? EMPTY_VALUE,
      marketplaceLabel: dto.marketplace ?? EMPTY_VALUE,
      neighbourhoodLabel: dto.neighbourhood ?? EMPTY_VALUE,
      isVerified: dto.isVerified,
      isAgent: dto.isAgent,
    },
    specifications,
    additionalSpecs,
    marketplaceAction: {
      url: validUrl(dto.url),
    },
  }
}
