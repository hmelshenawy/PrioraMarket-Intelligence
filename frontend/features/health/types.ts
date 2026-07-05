import type { StatusState } from "@/components/ui/StatusIndicator"

// Backend DTO: { status: "ok" }. Request failure → unavailable.
export interface HealthResponseDto {
  status: "ok"
}

// Frontend-safe UI model.
export interface BackendAvailability {
  state: StatusState
  lastCheckedAt: string | null
}