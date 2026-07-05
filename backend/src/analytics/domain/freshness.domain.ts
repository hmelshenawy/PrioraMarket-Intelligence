/**
 * Data-recency metadata exposed on every analytical response (Constitution Data Freshness).
 * Distinct from `generatedAt`, which records when the snapshot was generated.
 *
 * `scrapeRunId` is exposed as a JSON-safe number; the repository/mapper converts the
 * underlying `BigInt` listing run id to a number for transport.
 */
export interface Freshness {
  lastUpdated: string | null;
  datasetVersion: string | null;
  scrapeRunId: number | null;
}

export const UNKNOWN_FRESHNESS: Freshness = {
  lastUpdated: null,
  datasetVersion: null,
  scrapeRunId: null
};