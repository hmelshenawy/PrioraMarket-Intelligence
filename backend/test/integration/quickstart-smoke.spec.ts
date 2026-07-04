import { INestApplication, NotFoundException, ValidationPipe } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import * as request from 'supertest';
import { HttpExceptionFilter } from '../../src/common/filters/http-exception.filter';
import { HealthController } from '../../src/health/health.controller';
import { SearchController } from '../../src/search/search.controller';
import { SearchService } from '../../src/search/search.service';
import { StatsController } from '../../src/search/stats.controller';
import { StatsService } from '../../src/search/stats.service';

describe('quickstart smoke checks', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [HealthController, SearchController, StatsController],
      providers: [
        {
          provide: SearchService,
          useValue: {
            search: jest.fn().mockResolvedValue({ data: [], meta: { page: 1, limit: 20, total: 0, totalPages: 0 } }),
            findDetail: jest.fn((id: string) => (id === '1' ? Promise.resolve({ id: '1' }) : Promise.reject(new NotFoundException('Listing not found')))),
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
    app.useGlobalFilters(new HttpExceptionFilter());
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('matches documented quickstart endpoints and error behavior', async () => {
    await request(app.getHttpServer()).get('/api/v1/health').expect(200).expect({ status: 'ok' });
    await request(app.getHttpServer()).get('/api/v1/listings').expect(200).expect(({ body }) => {
      expect(body).toEqual({ data: [], meta: { page: 1, limit: 20, total: 0, totalPages: 0 } });
    });
    await request(app.getHttpServer()).get('/api/v1/listings?sort=relevance').expect(200);
    await request(app.getHttpServer()).get('/api/v1/listings?sort=unknown').expect(400).expect(({ body }) => {
      expect(body).toEqual(expect.objectContaining({ statusCode: 400, message: expect.any(Array) }));
    });
    await request(app.getHttpServer()).get('/api/v1/listings/1').expect(200).expect({ id: '1' });
    await request(app.getHttpServer()).get('/api/v1/listings/999').expect(404);
    await request(app.getHttpServer()).get('/api/v1/listings/filters').expect(200);
    await request(app.getHttpServer()).get('/api/v1/stats').expect(200);
  });
});
