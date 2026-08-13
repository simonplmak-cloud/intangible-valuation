import { getSurrealClient } from "@/lib/surreal/client";
import type { BusinessStage, StageDefaults, Benchmark } from "./types";

const FALLBACK_DEFAULTS: Record<BusinessStage, StageDefaults> = {
  startup: {
    businessStage: "startup",
    discountRate: { median: 0.25, low: 0.18, high: 0.35 },
    royaltyRate: { median: 0.06, low: 0.03, high: 0.10 },
    usefulLife: { median: 5, low: 3, high: 10 },
    growthRate: { median: 0.50, low: 0.20, high: 1.00 },
  },
  growth: {
    businessStage: "growth",
    discountRate: { median: 0.15, low: 0.10, high: 0.20 },
    royaltyRate: { median: 0.05, low: 0.02, high: 0.08 },
    usefulLife: { median: 10, low: 5, high: 15 },
    growthRate: { median: 0.20, low: 0.10, high: 0.40 },
  },
  mature: {
    businessStage: "mature",
    discountRate: { median: 0.08, low: 0.06, high: 0.12 },
    royaltyRate: { median: 0.04, low: 0.02, high: 0.07 },
    usefulLife: { median: 15, low: 7, high: 25 },
    growthRate: { median: 0.03, low: 0.02, high: 0.05 },
  },
};

function buildDefaults(stage: BusinessStage, benchmarks: Benchmark[]): StageDefaults {
  const base = FALLBACK_DEFAULTS[stage];

  const catDefaults = (
    category: string,
    metric: string,
    key: keyof StageDefaults
  ) => {
    const match = benchmarks.find(
      (b) =>
        b.category === category &&
        b.business_stage === stage &&
        b.metric_name === metric
    );
    if (match) {
      (base[key] as { median: number; low: number; high: number }) = {
        median: match.value,
        low: match.p25 ?? match.value * 0.7,
        high: match.p75 ?? match.value * 1.3,
      };
    }
  };

  catDefaults("discount_rate", "median_wacc", "discountRate");
  catDefaults("royalty_rate", "median_royalty_rate", "royaltyRate");
  catDefaults("useful_life", "median_useful_life", "usefulLife");
  catDefaults("growth_rate", "median_revenue_growth", "growthRate");

  return base;
}

export async function getStageDefaults(
  stage: BusinessStage,
  assetType?: string,
  industry?: string
): Promise<StageDefaults> {
  try {
    const db = await getSurrealClient();
    const conditions: string[] = [`business_stage = "${stage}"`];
    if (assetType) conditions.push(`(asset_type = "${assetType}" OR asset_type = "all")`);
    if (industry) conditions.push(`(industry = "${industry}" OR industry = "all")`);
    else conditions.push(`industry = "all"`);

    const query = `SELECT * FROM benchmarks WHERE ${conditions.join(" AND ")}`;
    const result = await db.query(query);
    const benchmarks = (result as unknown[]) as Benchmark[];

    if (benchmarks && benchmarks.length > 0) {
      return buildDefaults(stage, benchmarks);
    }
  } catch {
    // DB not available — use fallback
  }

  return FALLBACK_DEFAULTS[stage];
}

export function getFallbackDefaults(stage: BusinessStage): StageDefaults {
  return FALLBACK_DEFAULTS[stage];
}
