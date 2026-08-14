import type { ProviderAdapter, DataPoint, DataSeries } from "./types";

/**
 * EODHD (eodhd.com) — end-of-day prices, fundamentals, macro.
 * Requires `EODHD_API_KEY` (stored in the `valuation_report` repo per the
 * vision constraint, injected as an env var — never hardcoded here).
 * Subscription data is NOT redistributable.
 */
export const eodhdAdapter: ProviderAdapter = {
  id: "eodhd",
  provenance: () => ({
    provider: "eodhd",
    url: "https://eodhd.com/",
    license: "EODHD subscription — see EODHD terms; not for redistribution",
    redistributable: false,
  }),
  async fetch(series: DataSeries, opts?: { signal?: AbortSignal }): Promise<DataPoint[]> {
    const apiKey = process.env.EODHD_API_KEY;
    if (!apiKey) {
      throw new Error("EODHD_API_KEY not configured");
    }

    const path = series.kind === "macro"
      ? "macro-indicator"
      : "eod";

    const url =
      series.kind === "macro"
        ? `https://eodhd.com/api/${path}/${encodeURIComponent(series.symbol)}?api_token=${apiKey}&fmt=json`
        : `https://eodhd.com/api/${path}/${encodeURIComponent(series.symbol)}?api_token=${apiKey}&fmt=json&period=d`;

    const res = await fetch(url, { signal: opts?.signal });
    if (!res.ok) throw new Error(`EODHD fetch failed: ${res.status}`);
    const rows = (await res.json()) as Array<{ date: string; [key: string]: unknown }>;

    return rows
      .map((row) => {
        const field = series.field ?? "close";
        const raw = row[field];
        const value = typeof raw === "number" ? raw : Number(raw);
        return { date: row.date, value };
      })
      .filter((p) => Number.isFinite(p.value));
  },
};
