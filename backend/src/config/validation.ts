type Env = Record<string, string | undefined>;

const allowedNodeEnvs = new Set(['development', 'test', 'production']);
const allowedLogLevels = new Set(['debug', 'info', 'warn', 'error']);

function parsePositiveInt(value: string | undefined, name: string): number {
  if (!value) {
    throw new Error(`${name} is required`);
  }

  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error(`${name} must be a positive integer`);
  }

  return parsed;
}

export function validate(config: Env): Env {
  if (!config.DATABASE_URL) {
    throw new Error('DATABASE_URL is required');
  }

  const port = parsePositiveInt(config.PORT ?? '3000', 'PORT');
  const ttl = parsePositiveInt(config.FILTER_METADATA_CACHE_TTL_SECONDS ?? '60', 'FILTER_METADATA_CACHE_TTL_SECONDS');
  const nodeEnv = config.NODE_ENV ?? 'development';
  const logLevel = config.LOG_LEVEL ?? 'info';

  if (!allowedNodeEnvs.has(nodeEnv)) {
    throw new Error('NODE_ENV must be development, test, or production');
  }

  if (!allowedLogLevels.has(logLevel)) {
    throw new Error('LOG_LEVEL must be debug, info, warn, or error');
  }

  return {
    ...config,
    PORT: String(port),
    NODE_ENV: nodeEnv,
    LOG_LEVEL: logLevel,
    FILTER_METADATA_CACHE_TTL_SECONDS: String(ttl)
  };
}
