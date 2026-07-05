export interface SnapshotPeriod {
  days: number;
  label: string;
}

export function buildSnapshotPeriod(days: number): SnapshotPeriod {
  return { days, label: `Last ${days} days` };
}