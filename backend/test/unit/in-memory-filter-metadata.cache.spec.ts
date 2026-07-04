import { ConfigService } from '@nestjs/config';
import { InMemoryFilterMetadataCache } from '../../src/search/cache/in-memory-filter-metadata.cache';

describe('InMemoryFilterMetadataCache', () => {
  it('stores and clears metadata without persistence writes', () => {
    const cache = new InMemoryFilterMetadataCache({ get: jest.fn().mockReturnValue(60) } as unknown as ConfigService);
    const metadata = { makes: [], models: {}, price: { min: null, max: null }, year: { min: null, max: null }, km: { min: null, max: null }, conditions: [], sellerTypes: [] };
    cache.set(metadata);
    expect(cache.get()).toEqual(metadata);
    cache.clear();
    expect(cache.get()).toBeNull();
  });
});
