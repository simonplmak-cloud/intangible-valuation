import { test, expect, type APIRequestContext } from "@playwright/test";
import { appendFileSync, writeFileSync } from "node:fs";
import { CATALOG } from "../../lib/valuation/catalog";
import type { MethodDefinition, MethodParameter } from "../../lib/valuation/types";

const BASE = process.env.PLAYWRIGHT_BASE_URL ?? "https://intangible-valuation.ascent-partners.com";
const LOG = process.env.TEST_LOG ?? `/tmp/test${process.pid}.log`;

let buf: string[] = [];
function log(msg: string) {
  buf.push(msg);
}
function flush() {
  appendFileSync(LOG, buf.join("\n") + "\n");
  buf = [];
}

function valueFor(param: MethodParameter, v: number): unknown {
  const n = param.name.toLowerCase();
  if (param.type === "number[]") {
    const sets = [
      [1000000, 1100000, 1200000, 1300000, 1400000],
      [500000, 600000, 700000],
      [2000000, 2100000, 2200000, 2300000],
      [750000, 800000, 850000, 900000, 950000],
      [1500000, 1600000, 1700000],
    ];
    return sets[v % sets.length];
  }
  if (param.type === "integer") {
    if (n.includes("life") || n.includes("period") || n.includes("year") || n.includes("term")) {
      return [5, 7, 10, 3, 15][v];
    }
    if (n.includes("count") || n.includes("size") || n.includes("base") || n.includes("user")) {
      return [1000, 5000, 10000, 20000, 50000][v];
    }
    return [5, 10, 3, 8, 12][v];
  }
  if (param.type === "boolean") return [true, false, true, false, true][v];
  if (param.type === "string") return ["technology", "saas", "pharma", "all", "retail"][v];
  if (param.type === "json") return {};
  const rateish =
    n.includes("rate") || n.includes("premium") || n.includes("margin") || n.includes("probability") ||
    n.includes("volatility") || n.includes("index") || n.includes("score") || n.includes("strength") ||
    n.includes("loyalty") || n.includes("reach") || n.includes("stability") || n.includes("share") ||
    n.includes("retention") || n.includes("churn") || n.includes("factor") || n.includes("attrition") ||
    n.includes("secrecy") || n.includes("enforcement") || n.includes("completion");
  if (rateish) return [0.1, 0.15, 0.2, 0.08, 0.12][v];
  if (n.includes("beta")) return [1.2, 1.5, 0.8, 1.0, 1.4][v];
  return [1000000, 500000, 2000000, 750000, 1500000][v];
}

function genCases(m: MethodDefinition): Record<string, unknown>[] {
  const cases: Record<string, unknown>[] = [];
  for (let v = 0; v < 5; v++) {
    const inputs: Record<string, unknown> = {};
    for (const p of m.parameters) {
      if (!p.required && v === 0) continue;
      inputs[p.name] = valueFor(p, v);
    }
    cases.push(inputs);
  }
  return cases;
}

async function getLinks(request: APIRequestContext, url: string): Promise<string[]> {
  const res = await request.get(url);
  if (!res.ok()) return [];
  const html = await res.text();
  const hrefs = [...html.matchAll(/href="([^"]+)"/g)].map((m) => m[1]);
  const internal = hrefs
    .filter((h) => h.startsWith("/") && !h.startsWith("/_next") && !h.startsWith("/api"))
    .map((h) => h.split("#")[0])
    .filter((h) => h.length > 1);
  return [...new Set(internal)];
}

test.describe("Full-site regression", () => {
  test("all links resolve (no 404/500)", async ({ request }) => {
    writeFileSync(LOG, `# Full-site regression — ${new Date().toISOString()}\nBASE=${BASE}\n`);
    const roots = ["/", "/calculator", "/pricing", "/terms", "/privacy", "/mcp", "/skills", "/about", "/ai-advisor"];
    const seen = new Set<string>();
    const queue = [...roots, ...CATALOG.map((m) => `/calculator/${m.slug}`)];
    const broken: string[] = [];
    while (queue.length) {
      const path = queue.shift()!;
      if (seen.has(path)) continue;
      seen.add(path);
      const res = await request.get(`${BASE}${path}`);
      const ok = res.status() < 400;
      log(`${ok ? "OK" : "BROKEN"} ${res.status()} ${path}`);
      if (!ok) broken.push(`${res.status()} ${path}`);
    }
    flush();
    expect(broken).toEqual([]);
  });

  test("all 68 methods calculate — 5 cases each (no 500)", async ({ request }) => {
    let ok = 0, validation = 0, crash = 0;
    for (const m of CATALOG) {
      const cases = genCases(m);
      for (let i = 0; i < cases.length; i++) {
        const res = await request.post(`${BASE}/v1/valuation/${m.slug}`, { data: cases[i] });
        const status = res.status();
        if (status === 200) {
          const body = await res.json();
          const hasValue = typeof body?.value === "number";
          log(`  CALC ${m.slug} case${i} -> 200 value=${hasValue ? body.value : "MISSING"}`);
          if (hasValue) ok++; else crash++;
        } else if (status === 400) {
          log(`  CALC ${m.slug} case${i} -> 400 (validation)`);
          validation++;
        } else {
          log(`  CALC ${m.slug} case${i} -> ${status} (UNEXPECTED)`);
          crash++;
        }
      }
    }
    log(`SUMMARY: ok=${ok} validation=${validation} crash=${crash} total=${CATALOG.length * 5}`);
    flush();
    expect(crash).toBe(0);
  });

  test("core methods produce correct textbook values (5 cases each)", async ({ request }) => {
    // Known-good formulas verified against textbook values.
    const pv = async (fv: number, r: number, n: number) => {
      const res = await request.post(`${BASE}/v1/valuation/present-value`, { data: { future_value: fv, discount_rate: r, periods: n } });
      return (await res.json()).value as number;
    };
    const cases: [number, number, number][] = [
      [100000, 0.1, 5], [500000, 0.08, 10], [1000000, 0.12, 3], [250000, 0.15, 7], [10000, 0.05, 20],
    ];
    for (const [fv, r, n] of cases) {
      const got = await pv(fv, r, n);
      const exp = fv / Math.pow(1 + r, n);
      log(`  PV fv=${fv} r=${r} n=${n} -> ${got} (expect ${exp.toFixed(2)})`);
      expect(Math.abs(got - exp)).toBeLessThan(1);
    }

    const fv = async (pv0: number, r: number, n: number) => {
      const res = await request.post(`${BASE}/v1/valuation/future-value`, { data: { present_value: pv0, discount_rate: r, periods: n } });
      return (await res.json()).value as number;
    };
    for (const [p0, r, n] of cases) {
      const got = await fv(p0, r, n);
      const exp = p0 * Math.pow(1 + r, n);
      expect(Math.abs(got - exp)).toBeLessThan(1);
    }
    flush();
  });
});
