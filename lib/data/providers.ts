import { eodhdAdapter } from "./eodhd";
import { fredAdapter } from "./fred";
import { stooqAdapter } from "./stooq";
import type {
  DataSeries,
  DataSourceSnapshot,
  FetchOptions,
  ProviderAdapter,
  ProviderId,
} from "./types";

export const PROVIDERS: Record<ProviderId, ProviderAdapter> = {
  eodhd: eodhdAdapter,
  fred: fredAdapter,
  stooq: stooqAdapter,
};

export function cacheKey(series: DataSeries): string {
  return [series.provider, series.symbol, series.field ?? ""].join("|");
}

const snapshotCache = new Map<string, DataSourceSnapshot>();

export async function fetchSeries(
  series: DataSeries,
  opts?: FetchOptions
): Promise<DataSourceSnapshot> {
  const adapter = PROVIDERS[series.provider];
  if (!adapter) {
    throw new Error(`Unknown data provider: ${series.provider}`);
  }

  const key = cacheKey(series);
  const cached = snapshotCache.get(key);
  if (cached) return cached;

  const points = await adapter.fetch(series, opts);
  const snapshot: DataSourceSnapshot = {
    series,
    points,
    asOf: new Date().toISOString(),
    provenance: adapter.provenance(),
  };
  snapshotCache.set(key, snapshot);
  return snapshot;
}

export function clearSnapshotCache(): void {
  snapshotCache.clear();
}
