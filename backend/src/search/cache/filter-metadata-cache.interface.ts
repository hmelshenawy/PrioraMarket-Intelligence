import { FilterMetadataDomain } from '../domain/listing-filters.domain';

export interface IFilterMetadataCache {
  get(): FilterMetadataDomain | null;
  set(value: FilterMetadataDomain): void;
  clear(): void;
}
