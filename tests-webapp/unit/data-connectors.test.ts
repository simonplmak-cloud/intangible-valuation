import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchSeries, PROVIDERS, clearSnapshotCache } from "@/lib/data/providers";
import type { DataSeries } from "@/lib/data/types";

describe("Market-data connectors (A-002)", () => {
  beforeEach(() => {
    clearSnapshotCache();
  });

  it("registers all three providers", () => {
    expect(Object.keys(PROVIDERS).sort()).toEqual(["eodhd", "fred", "stooq"]);
  });

  it("parses FRED CSV (no key) into dated points", async () => {
    const csv = "DATE,DGS10\n2024-01-01,4.0\n2024-01-02,4.1\n2024-01-03,.\n";
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, text: () => Promise.resolve(csv) } as Response));

    const series: DataSeries = { provider: "fred", symbol: "DGS10", kind: "macro" };
    const snapshot = await fetchSeries(series);

    expect(snapshot.points).toEqual([
      { date: "2024-01-01", value: 4.0 },
      { date: "2024-01-02", value: 4.1 },
    ]);
    expect(snapshot.provenance.redistributable).toBe(true);
    expect(snapshot.asOf).toBeTruthy();
  });

  it("marks EODHD as non-redistributable and errors without a key", async () => {
    delete process.env.EODHD_API_KEY;
    const series: DataSeries = { provider: "eodhd", symbol: "AAPL.US", kind: "price" };
    await expect(fetchSeries(series)).rejects.toThrow("EODHD_API_KEY");
    expect(PROVIDERS.eodhd.provenance().redistributable).toBe(false);
  });

  it("errors on unknown provider", async () => {
    const series = { provider: "unknown", symbol: "X", kind: "price" } as unknown as DataSeries;
    await expect(fetchSeries(series)).rejects.toThrow("Unknown data provider");
  });
});
