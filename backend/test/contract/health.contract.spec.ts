import { HealthController } from '../../src/health/health.controller';

describe('GET /api/v1/health contract', () => {
  it('returns status ok response shape', () => {
    expect(new HealthController().health()).toEqual({ status: 'ok' });
  });
});
