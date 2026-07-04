import { ConfigModule } from '@nestjs/config';
import { Test } from '@nestjs/testing';
import configuration from '../../src/config/configuration';
import { validate } from '../../src/config/validation';
import { FILTER_METADATA_CACHE } from '../../src/search/cache/filter-metadata-cache.token';
import { InMemoryFilterMetadataCache } from '../../src/search/cache/in-memory-filter-metadata.cache';
import { PrismaListingReadRepository } from '../../src/search/listing-read.repository';
import { SearchQueryBuilder } from '../../src/search/search-query.builder';
import { SearchModule } from '../../src/search/search.module';
import { LISTING_READ_REPOSITORY, SEARCH_QUERY_BUILDER } from '../../src/search/search.tokens';

describe('SearchModule DI', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = {
      ...originalEnv,
      DATABASE_URL: 'postgresql://user:password@localhost:5432/test',
      PORT: '3000',
      NODE_ENV: 'test',
      LOG_LEVEL: 'info',
      FILTER_METADATA_CACHE_TTL_SECONDS: '60'
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('registers abstraction tokens to concrete providers', async () => {
    const moduleRef = await Test.createTestingModule({
      imports: [
        ConfigModule.forRoot({ isGlobal: true, load: [configuration], validate }),
        SearchModule
      ]
    }).compile();

    expect(moduleRef.get(LISTING_READ_REPOSITORY)).toBeInstanceOf(PrismaListingReadRepository);
    expect(moduleRef.get(SEARCH_QUERY_BUILDER)).toBeInstanceOf(SearchQueryBuilder);
    expect(moduleRef.get(FILTER_METADATA_CACHE)).toBeInstanceOf(InMemoryFilterMetadataCache);
  });
});
