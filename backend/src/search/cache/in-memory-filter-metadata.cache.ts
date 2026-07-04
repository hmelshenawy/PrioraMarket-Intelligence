import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { FilterMetadataDomain } from '../domain/listing-filters.domain';
import { IFilterMetadataCache } from './filter-metadata-cache.interface';

@Injectable()
export class InMemoryFilterMetadataCache implements IFilterMetadataCache {
  private value: FilterMetadataDomain | null = null;
  private expiresAt = 0;

  constructor(private readonly config: ConfigService) {}

  get(): FilterMetadataDomain | null {
    if (!this.value || Date.now() >= this.expiresAt) {
      this.clear();
      return null;
    }

    return this.value;
  }

  set(value: FilterMetadataDomain): void {
    const ttlSeconds = this.config.get<number>('filterMetadataCacheTtlSeconds', 60);
    this.value = value;
    this.expiresAt = Date.now() + ttlSeconds * 1000;
  }

  clear(): void {
    this.value = null;
    this.expiresAt = 0;
  }
}
