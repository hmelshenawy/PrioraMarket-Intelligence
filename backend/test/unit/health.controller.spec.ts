import { HealthController } from '../../src/health/health.controller';

describe('HealthController', () => {
  it('does not require database access to report health', () => {
    const controller = new HealthController();

    expect(controller.health()).toEqual({ status: 'ok' });
  });
});
