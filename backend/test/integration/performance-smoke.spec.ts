import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import * as request from 'supertest';
import { HealthController } from '../../src/health/health.controller';
import { SearchController } from '../../src/search/search.controller';
import { SearchService } from '../../src/search/search.service';
import { StatsController } from '../../src/search/stats.controller';
import { StatsService } from '../../src/search/stats.service';

describe('performance smoke', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [HealthController, SearchController, StatsController],
      providers: [
        {
          provide: SearchService,
          useValue: {
            search: jest.fn().mockResolvedValue({ data: [], meta: { page: 1, limit: 20, total: 0, totalPages: 0 } }),
            findDetail: jest.fn().mockResolvedValue({ id: '1' }),
            getFilterMetadata: jest.fn().mockResolvedValue({
              makes: [],
              models: {},
              price: { min: null, max: null },
              year: { min: null, max: null },
              km: { min: null, max: null },
              conditions: [],
              sellerTypes: []
            })
          }
        },
        {
          provide: StatsService,
          useValue: {
            getInventoryStats: jest.fn().mockResolvedValue({
              totalListings: 0,
              usedListings: 0,
              newListings: 0,
              totalMakes: 0,
              totalModels: 0,
              averagePriceAed: null,
              minPriceAed: null,
              maxPriceAed: null,
              lastUpdatedAt: null
            })
          }
        }
      ]
    }).compile();
    app = moduleRef.createNestApplication();
    app.setGlobalPrefix('api/v1');
    app.useGlobalPipes(new ValidationPipe({ transform: true, whitelist: true, forbidNonWhitelisted: true }));
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('meets smoke latency targets without database work', async () => {
    await expectFast('/api/v1/health', 50, app);
    await expectFast('/api/v1/listings', 300, app);
    await expectFast('/api/v1/listings/1', 100, app);
    await expectFast('/api/v1/listings/filters', 100, app);
  });
});

async function expectFast(path: string, maxMs: number, app: INestApplication) {
  await request(app.getHttpServer()).get(path).expect(200);
  const start = performance.now();
  await request(app.getHttpServer()).get(path).expect(200);
  expect(performance.now() - start).toBeLessThan(maxMs);
}
