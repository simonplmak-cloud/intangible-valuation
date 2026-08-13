import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { getSurrealClient, closeSurrealClient } from "@/lib/surreal/client";
import { validateCitation, type Citation } from "./citation";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_FILE = join(__dirname, "..", "..", "data", "benchmarks.json");

interface BenchmarkRecord {
  category: string;
  business_stage: string;
  asset_type: string;
  industry: string;
  metric_name: string;
  value: number;
  unit: string;
  p25?: number;
  p75?: number;
  citation: Citation;
}

function recordKey(record: BenchmarkRecord): string {
  return [record.category, record.business_stage, record.asset_type, record.industry, record.metric_name]
    .join("_")
    .replace(/[^a-zA-Z0-9_]/g, "_");
}

async function importBenchmarks(): Promise<void> {
  const raw = readFileSync(DATA_FILE, "utf-8");
  const records: BenchmarkRecord[] = JSON.parse(raw);

  const db = await getSurrealClient();
  let imported = 0;
  let rejected = 0;

  for (const record of records) {
    const errors = validateCitation(record.citation);
    if (errors.length > 0) {
      rejected++;
      console.error(
        `  REJECTED: ${record.metric_name} (${record.category}/${record.business_stage}) — missing ${errors
          .map((e) => e.field)
          .join(", ")}`
      );
      continue;
    }

    await db.merge(`benchmarks:${recordKey(record)}`, {
      category: record.category,
      business_stage: record.business_stage,
      asset_type: record.asset_type,
      industry: record.industry,
      metric_name: record.metric_name,
      value: record.value,
      unit: record.unit,
      p25: record.p25 ?? null,
      p75: record.p75 ?? null,
      source: record.citation.source,
      source_url: record.citation.url ?? record.citation.doi ?? null,
      author: record.citation.author,
      date: record.citation.date,
      ref: record.citation.ref,
      last_updated: new Date().toISOString(),
    });
    imported++;
  }

  console.log(`\nBenchmark import complete: ${imported} imported, ${rejected} rejected.\n`);
  if (rejected > 0) {
    process.exit(1);
  }
}

importBenchmarks()
  .catch((error) => {
    console.error("\nBenchmark import failed:", error);
    process.exit(1);
  })
  .finally(() => closeSurrealClient());
