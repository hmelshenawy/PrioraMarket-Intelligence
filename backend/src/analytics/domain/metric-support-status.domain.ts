export type MetricSupportState = 'supported' | 'unsupported' | 'unavailable' | 'partial';

export interface MetricSupportStatus {
  status: MetricSupportState;
  dataAvailable: boolean;
  reason?: string;
}

export const SUPPORTED: MetricSupportStatus = { status: 'supported', dataAvailable: true };

export function unsupported(reason: string): MetricSupportStatus {
  return { status: 'unsupported', dataAvailable: false, reason };
}

export function unavailable(reason: string): MetricSupportStatus {
  return { status: 'unavailable', dataAvailable: false, reason };
}

export function partial(reason: string): MetricSupportStatus {
  return { status: 'partial', dataAvailable: true, reason };
}