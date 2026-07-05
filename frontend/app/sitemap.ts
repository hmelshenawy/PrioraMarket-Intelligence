import type { MetadataRoute } from "next"
import { siteUrl } from "@/lib/config/env"

// sitemap.xml — extensible for future dynamic listing strategies; no backend dependency.
export default function sitemap(): MetadataRoute.Sitemap {
  const site = siteUrl ?? "https://prioramarket.example"
  const now = new Date().toISOString()
  return [
    { url: `${site}/`, lastModified: now, changeFrequency: "daily", priority: 1 },
    { url: `${site}/listings`, lastModified: now, changeFrequency: "daily", priority: 0.6 },
  ]
}