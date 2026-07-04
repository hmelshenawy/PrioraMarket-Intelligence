import { FilterMetadataResponseMapper } from '../../../src/search/mappers/filter-metadata-response.mapper';

describe('FilterMetadataResponseMapper golden responses', () => {
  it('maps filter metadata domain data to stable DTO output', () => {
    const metadata = { makes: ['Toyota'], models: { Toyota: ['Camry'] }, price: { min: 10000, max: 120000 }, year: { min: 2010, max: 2026 }, km: { min: 0, max: 300000 }, conditions: ['used'], sellerTypes: ['dealer'] };
    expect(new FilterMetadataResponseMapper().toResponse(metadata)).toEqual(metadata);
  });
});
