import { NextRequest, NextResponse } from "next/server";
import { getSurrealClient } from "@/lib/surreal/client";
import { getFallbackDefaults } from "@/lib/valuation/defaults";
import type { BusinessStage } from "@/lib/valuation/types";
import type { Benchmark } from "@/lib/valuation/types";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const category = searchParams.get("category") || undefined;
  const businessStage = searchParams.get("business_stage") as BusinessStage | undefined;
  const assetType = searchParams.get("asset_type") || undefined;
  const industry = searchParams.get("industry") || undefined;

  try {
    const db = await getSurrealClient();
    const conditions: string[] = [];
    if (category) conditions.push(`category = "${category}"`);
    if (businessStage) conditions.push(`business_stage = "${businessStage}"`);
    if (assetType) conditions.push(`(asset_type = "${assetType}" OR asset_type = "all")`);
    if (industry) conditions.push(`(industry = "${industry}" OR industry = "all")`);

    const whereClause = conditions.length > 0 ? ` WHERE ${conditions.join(" AND ")}` : "";
    const [benchmarks] = await db.query<[Benchmark[]]>(
      `SELECT * FROM benchmarks${whereClause} ORDER BY category, business_stage, asset_type`
    );

    return NextResponse.json({
      benchmarks: benchmarks ?? [],
      count: benchmarks?.length ?? 0,
    });
  } catch {
    // DB unavailable — return fallback for common queries
    if (businessStage && (businessStage === "startup" || businessStage === "growth" || businessStage === "mature")) {
      const defaults = getFallbackDefaults(businessStage);
      return NextResponse.json({
        benchmarks: [
          {
            category: "discount_rate",
            business_stage: businessStage,
            metric_name: "median_wacc",
            value: defaults.discountRate.median,
            p25: defaults.discountRate.low,
            p75: defaults.discountRate.high,
            source: "Damodaran 2025 (fallback)",
          },
          {
            category: "royalty_rate",
            business_stage: businessStage,
            metric_name: "median_royalty_rate",
            value: defaults.royaltyRate.median,
            p25: defaults.royaltyRate.low,
            p75: defaults.royaltyRate.high,
            source: "RoyaltySource 2024 (fallback)",
          },
        ] as Benchmark[],
        count: 2,
      });
    }

    return NextResponse.json({ benchmarks: [], count: 0 });
  }
}
