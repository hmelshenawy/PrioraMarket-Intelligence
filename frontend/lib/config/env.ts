import { z } from "zod"

// Trust boundary: validate frontend environment at load time.
// No secrets are required for Feature 004.
const envSchema = z.object({
  // Required: base URL for the Feature 003 Backend Search API (no trailing slash).
  NEXT_PUBLIC_API_BASE_URL: z
    .string()
    .url("NEXT_PUBLIC_API_BASE_URL must be a valid URL")
    .refine((v) => !v.endsWith("/"), "NEXT_PUBLIC_API_BASE_URL must not end with a slash"),

  // Optional: public site URL for canonical/OG/sitemap.
  NEXT_PUBLIC_SITE_URL: z.string().url().optional(),

  // Optional: robots indexing toggle.
  NEXT_PUBLIC_ALLOW_INDEXING: z
    .string()
    .optional()
    .transform((v) => (v == null ? true : v === "true")),

  // Optional: health polling interval (ms).
  NEXT_PUBLIC_HEALTH_POLLING_INTERVAL: z
    .string()
    .optional()
    .transform((v) => (v == null ? undefined : Number(v)))
    .pipe(z.number().int().positive().optional()),
})

export type Env = z.infer<typeof envSchema>

function loadEnv(): Env {
  // Safe local default only for documented local development.
  const rawBase = process.env.NEXT_PUBLIC_API_BASE_URL
  const isDev = process.env.NODE_ENV !== "production"

  const raw = {
    NEXT_PUBLIC_API_BASE_URL: rawBase ?? (isDev ? "http://localhost:3000" : undefined),
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
    NEXT_PUBLIC_ALLOW_INDEXING: process.env.NEXT_PUBLIC_ALLOW_INDEXING,
    NEXT_PUBLIC_HEALTH_POLLING_INTERVAL: process.env.NEXT_PUBLIC_HEALTH_POLLING_INTERVAL,
  }

  const parsed = envSchema.safeParse(raw)
  if (!parsed.success) {
    const issues = parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ")
    throw new Error(`Invalid frontend environment configuration: ${issues}`)
  }
  return parsed.data
}

export const env = loadEnv()

export const apiBaseUrl = env.NEXT_PUBLIC_API_BASE_URL
export const siteUrl = env.NEXT_PUBLIC_SITE_URL
export const allowIndexing = env.NEXT_PUBLIC_ALLOW_INDEXING
export const healthPollingInterval = env.NEXT_PUBLIC_HEALTH_POLLING_INTERVAL ?? 30_000