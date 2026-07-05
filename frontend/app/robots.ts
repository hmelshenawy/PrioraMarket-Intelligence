import type { MetadataRoute } from "next"
import { allowIndexing, siteUrl } from "@/lib/config/env"

// robots.txt — environment-driven indexing toggle.
export default function robots(): MetadataRoute.Robots {
  const site = siteUrl ?? "https://prioramarket.example"
  return {
    rules: {
      userAgent: "*",
      allow: allowIndexing ? "/" : undefined,
      disallow: allowIndexing ? undefined : "/",
    },
    sitemap: `${site}/sitemap.xml`,
    host: site,
  }
}