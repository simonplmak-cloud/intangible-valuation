/**
 * TASK-011: Vercel Python Cold Start Spike
 *
 * Measures cold start latency for Vercel Python functions.
 * Run after deployment: `pnpm tsx tests/spikes/vercel-coldstart.ts`
 *
 * Usage:
 *   1. Deploy to Vercel
 *   2. Set DEPLOY_URL env var to your Vercel deployment URL
 *   3. Run this spike script
 *
 * Expected output:
 *   P50 cold start: ~300ms
 *   P95 cold start: ~800ms
 *   If P95 > 2000ms: migrate hot-path formulas to TypeScript
 */

const DEPLOY_URL = process.env.DEPLOY_URL || "https://intangiable-valuation.vercel.app";
const ENDPOINTS = ["present-value", "capm", "wacc", "relief-from-royalty"];
const ITERATIONS = 10;

interface TimingResult {
  endpoint: string;
  durations: number[];
  p50: number;
  p95: number;
  p99: number;
  avg: number;
  min: number;
  max: number;
  coldStarts: number;
}

async function timeRequest(url: string, body: Record<string, unknown>): Promise<{ duration: number; coldStart: boolean }> {
  const start = performance.now();
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const duration = performance.now() - start;
  const coldStart = res.headers.get("x-vercel-is-cold-start") === "1" || duration > 500;
  return { duration, coldStart };
}

function percentile(sorted: number[], p: number): number {
  const index = Math.ceil((p / 100) * sorted.length) - 1;
  return sorted[Math.max(0, index)];
}

async function main() {
  console.log(`\nVercel Python Cold Start Spike\n`);
  console.log(`Deployment URL: ${DEPLOY_URL}`);
  console.log(`Endpoints: ${ENDPOINTS.join(", ")}`);
  console.log(`Iterations per endpoint: ${ITERATIONS}\n`);

  const results: TimingResult[] = [];

  for (const endpoint of ENDPOINTS) {
    const url = `${DEPLOY_URL}/api/valuation/${endpoint}`;
    const body = endpoint === "relief-from-royalty"
      ? { revenue_projections: [1000000, 1100000], royalty_rate: 0.05, discount_rate: 0.15, tax_rate: 0.21, useful_life: 10 }
      : endpoint === "wacc"
        ? { equity_value: 1000000, debt_value: 200000, cost_of_equity: 0.12, cost_of_debt: 0.05, tax_rate: 0.21 }
        : { future_value: 100000, discount_rate: 0.10, periods: 5 };

    const durations: number[] = [];
    let coldStarts = 0;

    for (let i = 0; i < ITERATIONS; i++) {
      const { duration, coldStart } = await timeRequest(url, body);
      durations.push(duration);
      if (coldStart) coldStarts++;
      process.stdout.write(`  ${endpoint} [${i + 1}/${ITERATIONS}]: ${Math.round(duration)}ms${coldStart ? " (cold)" : ""}\r`);
    }

    const sorted = [...durations].sort((a, b) => a - b);
    const result: TimingResult = {
      endpoint,
      durations,
      p50: percentile(sorted, 50),
      p95: percentile(sorted, 95),
      p99: percentile(sorted, 99),
      avg: durations.reduce((a, b) => a + b, 0) / durations.length,
      min: sorted[0],
      max: sorted[sorted.length - 1],
      coldStarts,
    };

    results.push(result);
    console.log(`\n  P50: ${Math.round(result.p50)}ms | P95: ${Math.round(result.p95)}ms | P99: ${Math.round(result.p99)}ms | Avg: ${Math.round(result.avg)}ms | Cold starts: ${result.coldStarts}/${ITERATIONS}\n`);
  }

  // Decision gate
  const worstP95 = Math.max(...results.map((r) => r.p95));
  console.log(`\n=== Decision ===`);
  console.log(`Worst P95: ${Math.round(worstP95)}ms`);

  if (worstP95 > 2000) {
    console.log(`RESULT: P95 > 2s — migrate hot-path formulas to TypeScript`);
    console.log(`Recommended: migrate present_value, future_value, capm, wacc to TS functions`);
  } else if (worstP95 > 1000) {
    console.log(`RESULT: P95 > 1s — acceptable for complex methods, pre-warm simple ones`);
  } else {
    console.log(`RESULT: P95 < 1s — Python functions are viable for all 68 methods`);
  }
}

main().catch(console.error);
