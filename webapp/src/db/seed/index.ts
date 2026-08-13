import { getSurrealClient, closeSurrealClient } from "@/lib/surreal/client";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

const SEED_FILES = ["method_catalog.surql", "benchmarks.surql"];

async function seed(): Promise<void> {
  console.log("\nSeeding database...\n");

  const db = await getSurrealClient();

  for (const file of SEED_FILES) {
    const path = join(__dirname, file);
    if (!existsSync(path)) {
      console.log(`  SKIP: ${file} (not found)`);
      continue;
    }

    const sql = readFileSync(path, "utf-8");
    const statements = sql
      .split(";")
      .map((s) => s.trim())
      .filter((s) => s.length > 0 && !s.startsWith("--"));

    for (const statement of statements) {
      try {
        await db.query(statement);
      } catch (error) {
        console.error(`  FAILED in ${file}: ${statement.slice(0, 80)}...`);
        throw error;
      }
    }

    console.log(`  OK: ${file}`);
  }

  console.log("\nSeed complete.\n");
}

seed()
  .catch((error) => {
    console.error("\nSeed failed:", error);
    process.exit(1);
  })
  .finally(() => closeSurrealClient());
