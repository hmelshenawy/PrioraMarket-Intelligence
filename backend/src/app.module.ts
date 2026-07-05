import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import configuration from './config/configuration';
import { validate } from './config/validation';
import { PrismaModule } from './db/prisma.module';
import { AnalyticsModule } from './analytics/analytics.module';
import { HealthController } from './health/health.controller';
import { SearchModule } from './search/search.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration],
      validate
    }),
    PrismaModule,
    SearchModule,
    AnalyticsModule
  ],
  controllers: [HealthController]
})
export class AppModule {}
