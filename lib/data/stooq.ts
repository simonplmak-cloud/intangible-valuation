import type { ProviderAdapter, DataPoint, DataSeries } from "./types";

/**
 * Stooq — free end-of-day CSV download, no API key required.
 * Redistribution is restricted; use for computation and internal snapshots only.
 */
export const stooqAdapter: ProviderAdapter = {
  id: "stooq",
  provenance: () => ({
    provider: "stooq",
    url: "https://stooq.com/",
    license: "Free EOD quotes — see Stooq terms; not for redistribution",
    redistributable: false,
  }),
  async fetch(series: DataSeries, opts?: { signal?: AbortSignal }): Promise<DataPoint[]> {
    const url = `https://stooq.com/q/d/l/?s=${encodeURIComponent(series.symbol)}&i=d`;
    const res = await fetch(url, { signal: opts?.signal });
    if (!res.ok) throw new Error(`Stooq fetch failed: ${res.status}`);
    const text = await res.text();
    return parseStooqCsv(text);
  },
};

function parseStooqCsv(text: string): DataPoint[] {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const header = lines[0].split(",");
  const closeIndex = header.indexOf("Close");
  if (closeIndex === -1) return [];

  const points: DataPoint[] = [];
  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(",");
    const date = cols[0];
    const value = Number(cols[closeIndex]);
    if (!date || !Number.isFinite(value)) continue;
    points.push({ date, value });
  }
  return points.reverse();
}
