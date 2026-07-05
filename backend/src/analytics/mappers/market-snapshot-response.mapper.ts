import { Injectable } from '@nestjs/common';
import { MarketSnapshot } from '../domain/market-snapshot.domain';
import { MarketSnapshotResponseDto } from '../dto/market-snapshot-response.dto';

/**
 * Maps the MarketSnapshot domain aggregate to the response DTO (raw values only).
 * Phase 2 skeleton — field mapping is complete; extended in Phase 3 once the
 * aggregation service produces the domain object.
 */
@Injectable()
export class MarketSnapshotResponseMapper {
  toResponse(snapshot: MarketSnapshot): MarketSnapshotResponseDto {
    return {
      scope: snapshot.scope,
      filters: snapshot.filters,
      period: snapshot.period,
      metrics: snapshot.metrics,
      supportStatuses: snapshot.supportStatuses,
      freshness: snapshot.freshness,
      generatedAt: snapshot.generatedAt
    };
  }
}