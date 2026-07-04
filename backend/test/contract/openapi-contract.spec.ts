import { readFileSync } from 'node:fs';
import { join } from 'node:path';

describe('OpenAPI contract', () => {
  const openapi = readFileSync(join(__dirname, '../../../specs/003-backend-search-api/contracts/openapi.yaml'), 'utf8');

  it('documents every implemented v1 endpoint', () => {
    for (const path of ['/health:', '/listings:', '/listings/filters:', '/listings/{id}:', '/stats:']) {
      expect(openapi).toContain(path);
    }
  });

  it('documents stable response schemas used by controllers', () => {
    for (const schema of [
      'HealthResponse:',
      'SearchListingsResponse:',
      'ListingDetailResponse:',
      'FilterMetadataResponse:',
      'InventoryStatsResponse:',
      'ApiErrorResponse:'
    ]) {
      expect(openapi).toContain(schema);
    }
  });
});
