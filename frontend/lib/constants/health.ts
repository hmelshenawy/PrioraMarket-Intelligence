import { healthPollingInterval as DEFAULT } from "@/lib/config/env"

// Backend health polling interval (ms). Independent from search/listing queries.
export const HEALTH_POLLING_INTERVAL = DEFAULT

export const HEALTH_STATUSES = {
  checking: "checking",
  available: "available",
  unavailable: "unavailable",
  degraded: "degraded",
} as const