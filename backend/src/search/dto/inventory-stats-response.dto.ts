export class InventoryStatsResponseDto {
  totalListings!: number;
  usedListings!: number;
  newListings!: number;
  totalMakes!: number;
  totalModels!: number;
  averagePriceAed!: number | null;
  minPriceAed!: number | null;
  maxPriceAed!: number | null;
  lastUpdatedAt!: string | null;
}
