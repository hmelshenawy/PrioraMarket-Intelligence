import type { BackendAvailability, HealthResponseDto } from "../types"

// Map DTO + request outcome into a frontend-safe availability model.
// Success → available; failure/timeout/invalid → unavailable.
export function mapHealth(dto: HealthResponseDto | null, ok: boolean): BackendAvailability {
  return {
    state: ok && dto?.status === "ok" ? "available" : "unavailable",
    lastCheckedAt: new Date().toISOString(),
  }
}