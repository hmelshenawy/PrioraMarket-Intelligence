import configuration from '../../src/config/configuration';
import { validate } from '../../src/config/validation';

describe('configuration', () => {
  it('validates required environment values', () => {
    const env = validate({
      DATABASE_URL: 'postgresql://user:password@localhost:5432/test',
      PORT: '3000',
      NODE_ENV: 'test',
      LOG_LEVEL: 'info',
      FILTER_METADATA_CACHE_TTL_SECONDS: '60'
    });

    expect(env.DATABASE_URL).toBe('postgresql://user:password@localhost:5432/test');
    expect(env.PORT).toBe('3000');
    expect(env.NODE_ENV).toBe('test');
    expect(env.LOG_LEVEL).toBe('info');
    expect(env.FILTER_METADATA_CACHE_TTL_SECONDS).toBe('60');
  });

  it('exposes typed application configuration', () => {
    const originalEnv = process.env;
    process.env = {
      ...originalEnv,
      DATABASE_URL: 'postgresql://user:password@localhost:5432/test',
      PORT: '3001',
      NODE_ENV: 'test',
      LOG_LEVEL: 'debug',
      FILTER_METADATA_CACHE_TTL_SECONDS: '30'
    };

    expect(configuration()).toMatchObject({
      databaseUrl: 'postgresql://user:password@localhost:5432/test',
      port: 3001,
      nodeEnv: 'test',
      logLevel: 'debug',
      filterMetadataCacheTtlSeconds: 30
    });

    process.env = originalEnv;
  });
});
