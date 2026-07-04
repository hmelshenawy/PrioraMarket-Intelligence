export default () => ({
  databaseUrl: process.env.DATABASE_URL,
  port: Number(process.env.PORT ?? 3000),
  nodeEnv: process.env.NODE_ENV ?? 'development',
  logLevel: process.env.LOG_LEVEL ?? 'info',
  filterMetadataCacheTtlSeconds: Number(process.env.FILTER_METADATA_CACHE_TTL_SECONDS ?? 60)
});
