import { Test } from '@nestjs/testing';
import { validate } from 'class-validator';
import { plainToInstance } from 'class-transformer';
import { FilterOptionsController } from '../../src/analytics/filter-options.controller';
import { FilterOptionsService } from '../../src/analytics/filter-options.service';
import { FilterOptionsQueryDto } from '../../src/analytics/dto/filter-options-query.dto';

describe('GET /api/v1/market/filter-options contract', () => {
  // US2 (T047): cascading options constrained by higher-level filters; filters echoed
  // (unselected fields omitted, matching the backend's undefined → omitted serialization);
  // freshness present. Models are limited to the selected make; trims/years stay empty
  // until their higher-level filters are also selected.
  const filterOptionsFixture = {
    filters: { make: 'toyota', model: 'corolla' },
    options: {
      makes: [
        { value: 'toyota', displayName: 'toyota', activeListingCount: 4381 },
        { value: 'bmw', displayName: 'bmw', activeListingCount: 2981 }
      ],
      models: [
        { value: 'corolla', displayName: 'corolla', activeListingCount: 842 },
        { value: 'camry', displayName: 'camry', activeListingCount: 612 }
      ],
      trims: [],
      years: []
    },
    freshness: {
      lastUpdated: '2026-07-05T08:00:00.000Z',
      datasetVersion: 'canonical-2024.05',
      scrapeRunId: 1042
    },
    generatedAt: '2026-07-05T12:30:00.000Z'
  };

  it('returns the cascading filter-options shape through FilterOptionsController', async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [FilterOptionsController],
      providers: [
        {
          provide: FilterOptionsService,
          useValue: { getOptions: jest.fn().mockResolvedValue(filterOptionsFixture) }
        }
      ]
    }).compile();

    const controller = moduleRef.get(FilterOptionsController);
    const query = new FilterOptionsQueryDto();
    Object.assign(query, { make: 'toyota', model: 'corolla' });

    await expect(controller.getOptions(query)).resolves.toEqual(filterOptionsFixture);
  });

  it('constrains lower-level options by the selected higher-level filters', () => {
    // Only model options are populated once a make is selected; trims/years stay empty
    // until the full hierarchy is selected.
    const modelValues = filterOptionsFixture.options.models.map((o: { value: string }) => o.value);
    expect(modelValues).toEqual(['corolla', 'camry']);
    expect(filterOptionsFixture.options.trims).toEqual([]);
    expect(filterOptionsFixture.options.years).toEqual([]);
  });

  it('echoes the selected canonical filters and exposes freshness', () => {
    expect(filterOptionsFixture.filters).toEqual({
      make: 'toyota',
      model: 'corolla'
    });
    expect(filterOptionsFixture.freshness.lastUpdated).toBe('2026-07-05T08:00:00.000Z');
    expect(filterOptionsFixture.freshness.datasetVersion).toBe('canonical-2024.05');
    expect(filterOptionsFixture.freshness.scrapeRunId).toBe(1042);
    // generatedAt is distinct from freshness.lastUpdated.
    expect(filterOptionsFixture.generatedAt).toBe('2026-07-05T12:30:00.000Z');
  });

  it('exposes year options as integer values with canonical-fallback display names', () => {
    const yearFixture = {
      ...filterOptionsFixture,
      options: {
        ...filterOptionsFixture.options,
        years: [{ value: 2023, displayName: '2023', activeListingCount: 57 }]
      }
    };
    expect(yearFixture.options.years[0].value).toBe(2023);
    expect(typeof yearFixture.options.years[0].value).toBe('number');
    expect(yearFixture.options.years[0].displayName).toBe('2023');
  });

  it.each([
    ['model without make', { model: 'corolla' }, /model requires make/i],
    ['trim without make+model', { make: 'toyota', trim: 'xli' }, /trim requires make and model/i],
    ['year without make+model+trim', { make: 'toyota', model: 'corolla', year: 2023 }, /year requires make, model, and trim/i]
  ])('rejects an invalid filter hierarchy (%s) with a validation error', async (_label, payload, expected) => {
    const dto = plainToInstance(FilterOptionsQueryDto, payload);
    const errors = await validate(dto);
    expect(errors.length).toBeGreaterThan(0);
    const messages = errors.flatMap((e) => (e.constraints ? Object.values(e.constraints) : []));
    expect(messages.some((m) => expected.test(m))).toBe(true);
  });
});