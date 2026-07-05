import type { Metadata } from "next"
import { siteUrl, allowIndexing } from "@/lib/config/env"

const site = siteUrl ?? "https://prioramarket.example"

// Default app metadata: title, description, favicon, OpenGraph defaults.
export const defaultMetadata: Metadata = {
  metadataBase: new URL(site),
  title: {
    default: "PrioraMarket — Vehicle Market Intelligence",
    template: "%s · PrioraMarket",
  },
  description:
    "Browse, search, and inspect current vehicle listings across marketplaces with PrioraMarket.",
  applicationName: "PrioraMarket",
  openGraph: {
    type: "website",
    siteName: "PrioraMarket",
    title: "PrioraMarket — Vehicle Market Intelligence",
    description:
      "Browse, search, and inspect current vehicle listings across marketplaces with PrioraMarket.",
  },
  robots: allowIndexing
    ? { index: true, follow: true }
    : { index: false, follow: false },
}

// Home page metadata.
export const homeMetadata: Metadata = {
  title: "Search Vehicles",
  description: "Search current vehicle listings and view market overview metrics.",
  alternates: { canonical: "/" },
}

// Listing detail metadata with safe fallbacks for missing identity fields.
export function listingMetadata(input: {
  make?: string | null
  model?: string | null
  year?: number | null
  id: string
}): Metadata {
  const parts = [input.year, input.make, input.model].filter((v) => v != null && v !== "")
  const title = parts.length
    ? `${parts.join(" ")}`
    : "Vehicle Listing"
  return {
    title,
    description: `View details for ${title}.`,
    alternates: { canonical: `/listings/${input.id}` },
  }
}