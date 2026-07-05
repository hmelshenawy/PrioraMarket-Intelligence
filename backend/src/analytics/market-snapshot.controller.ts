import { Controller, Get, Query } from '@nestjs/common';
import { MarketSnapshotQueryDto } from './dto/market-snapshot-query.dto';
import { MarketSnapshotService } from './market-snapshot.service';

/**
 * MarketSnapshotController — thin HTTP adapter. Validation runs via the global
 * ValidationPipe (transform/whitelist/forbidNonWhitelisted) before reaching here.
 * No business logic; returns the response DTO produced by the service.
 */
@Controller('market/snapshot')
export class MarketSnapshotController {
  constructor(private readonly service: MarketSnapshotService) {}

  @Get()
  getSnapshot(@Query() query: MarketSnapshotQueryDto) {
    return this.service.getSnapshot(query);
  }
}