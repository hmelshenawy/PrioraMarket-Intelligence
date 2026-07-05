/**
 * Transport shape for Data Freshness metadata (Constitution-mandated on every
 * analytical response). Mirrors the domain `Freshness` type; kept as a distinct
 * DTO class so the controller never returns domain objects directly.
 */
export class FreshnessDto {
  lastUpdated: string | null;
  datasetVersion: string | null;
  scrapeRunId: number | null;
}