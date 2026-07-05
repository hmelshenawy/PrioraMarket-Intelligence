import { Module } from '@nestjs/common';
import { PrismaModule } from '../db/prisma.module';

/**
 * Analytics module — owns the Market Snapshot Dashboard read surface.
 *
 * Phase 1 scaffolding: repository implementations, services, and controllers are
 * wired in subsequent phases. PrismaModule is @Global but imported here to mirror
 * the SearchModule convention and make the read dependency explicit.
 */
@Module({
  imports: [PrismaModule],
  controllers: [],
  providers: []
})
export class AnalyticsModule {}