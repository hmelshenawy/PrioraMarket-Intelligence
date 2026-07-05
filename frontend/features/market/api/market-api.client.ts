import { getApiClient } from "@/lib/api/client"
import { marketSnapshotSchema } from "../schemas/market-snapshot.schema"
import { filterOptionsSchema } from "../schemas/filter-options.schema"
import type { FilterOptionsDto, MarketSnapshotDto, MarketSnapshotRequest } from "../types"

// Build query params, omitting empty/undefined values so the backend never receives
// empty-string filters (the global ValidationPipe would reject them anyway).
function buildParams(req: MarketSnapshotRequest): Record<string, string | number> {
  const params: Record<string, string | number> = {}
  if (req.make) params.make = req.make
  if (req.model) params.model = req.model
  if (req.trim) params.trim = req.trim
  if (req.year != null) params.year = req.year
  if (req.periodDays != null) params.periodDays = req.periodDays
  return params
}

// GET /api/v1/market/snapshot — raw response passthrough after zod validation.
export async function fetchMarketSnapshot(req: MarketSnapshotRequest = {}): Promise<MarketSnapshotDto> {
  const client = getApiClient()
  const { data } = await client.get<unknown>("/market/snapshot", { params: buildParams(req) })
  return marketSnapshotSchema.parse(data) as MarketSnapshotDto
}

// GET /api/v1/market/filter-options — raw response passthrough after zod validation.
// (Used from US2 onward; shipped with the market API client for a single import surface.)
export async function fetchFilterOptions(req: MarketSnapshotRequest = {}): Promise<FilterOptionsDto> {
  const client = getApiClient()
  const { data } = await client.get<unknown>("/market/filter-options", { params: buildParams(req) })
  return filterOptionsSchema.parse(data) as FilterOptionsDto
}