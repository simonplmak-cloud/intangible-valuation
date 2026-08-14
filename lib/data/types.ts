export type ProviderId = "eodhd" | "fred" | "stooq";

export type SeriesKind = "price" | "fundamental" | "macro" | "fx";

export interface DataSeries {
  provider: ProviderId;
  symbol: string;
  kind: SeriesKind;
  field?: string;
}

export interface DataPoint {
  date: string;
  value: number;
}

export interface Provenance {
  provider: ProviderId;
  url: string;
  license: string;
  redistributable: boolean;
}

export interface DataSourceSnapshot {
  series: DataSeries;
  points: DataPoint[];
  asOf: string;
  provenance: Provenance;
}

export interface FetchOptions {
  signal?: AbortSignal;
}

export interface ProviderAdapter {
  id: ProviderId;
  provenance: () => Provenance;
  fetch: (series: DataSeries, opts?: FetchOptions) => Promise<DataPoint[]>;
}
