import type { ProviderAdapter, DataPoint, DataSeries } from "./types";

/**
 * FRED (Federal Reserve Economic Data) — St. Louis Fed.
 * Public CSV graph endpoint requires no API key; the JSON API is used when
 * `FRED_API_KEY` is present. U.S. government data — no redistribution restriction.
 */
export const fredAdapter: ProviderAdapter = {
  id: "fred",
  provenance: () => ({
    provider: "fred",
    url: "https://fred.stlouisfed.org/",
    license: "U.S. federal government data — public domain (attribution requested)",
    redistributable: true,
  }),
  async fetch(series: DataSeries, opts?: { signal?: AbortSignal }): Promise<DataPoint[]> {
    const apiKey = process.env.FRED_API_KEY;

    if (apiKey) {
      const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${encodeURIComponent(
        series.symbol
      )}&api_key=${apiKey}&file_type=json`;
      const res = await fetch(url, { signal: opts?.signal });
      if (!res.ok) throw new Error(`FRED fetch failed: ${res.status}`);
      const json = (await res.json()) as {
        observations?: { date: string; value: string }[];
      };
      return (json.observations ?? [])
        .filter((o) => o.value !== ".")
        .map((o) => ({ date: o.date, value: Number(o.value) }));
    }

    const csvUrl = `https://fred.stlouisfed.org/graph/fredgraph.csv?id=${encodeURIComponent(series.symbol)}`;
    const res = await fetch(csvUrl, { signal: opts?.signal });
    if (!res.ok) throw new Error(`FRED CSV fetch failed: ${res.status}`);
    const text = await res.text();
    return parseCsv(text);
  },
};

function parseCsv(text: string): DataPoint[] {
  const lines = text.trim().split(/\r?\n/);
  const points: DataPoint[] = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    const [date, value] = line.split(",");
    if (!date || value === undefined || value === ".") continue;
    const n = Number(value);
    if (!Number.isFinite(n)) continue;
    points.push({ date, value: n });
  }
  return points;
}
