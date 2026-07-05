"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchHealth } from "../api/health.api"
import { mapHealth } from "../mappers/healthMapper"
import { queryKeys } from "@/lib/query/keys"
import { HEALTH_POLLING_INTERVAL } from "@/lib/constants/health"
import type { StatusState } from "@/components/ui/StatusIndicator"

// useBackendHealth — periodic, independent availability polling for the top nav.
// Never blocks search/stats/listings.
export function useBackendHealth(): {
  state: StatusState
  label: string
  lastCheckedAt: string | null
} {
  const query = useQuery({
    queryKey: queryKeys.health.status(),
    queryFn: async () => {
      try {
        const dto = await fetchHealth()
        return mapHealth(dto, true)
      } catch {
        return mapHealth(null, false)
      }
    },
    refetchInterval: HEALTH_POLLING_INTERVAL,
    staleTime: HEALTH_POLLING_INTERVAL,
    retry: 1,
  })

  const state: StatusState = query.isLoading ? "checking" : query.data?.state ?? "checking"
  const labelMap: Record<StatusState, string> = {
    checking: "Checking backend…",
    available: "Backend available",
    unavailable: "Backend unavailable",
    degraded: "Backend degraded",
  }
  return { state, label: labelMap[state], lastCheckedAt: query.data?.lastCheckedAt ?? null }
}