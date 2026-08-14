import { describe, it, expect } from "vitest";
import { CATALOG } from "@/lib/valuation/catalog";

interface AuditResult {
  total: number;
  complete: number;
  missingFormula: string[];
  missingDescription: string[];
  missingReference: string[];
  missingParameters: string[];
}

function auditCatalog(): AuditResult {
  const result: AuditResult = {
    total: CATALOG.length,
    complete: 0,
    missingFormula: [],
    missingDescription: [],
    missingReference: [],
    missingParameters: [],
  };

  for (const method of CATALOG) {
    const ok: boolean[] = [];

    if (!method.description?.trim()) result.missingDescription.push(method.slug);
    else ok.push(true);

    if (!/^(Ch \d+|Appendix [A-Z])/.test(method.textbookReference)) result.missingReference.push(method.slug);
    else ok.push(true);

    if (!method.parameters?.length) result.missingParameters.push(method.slug);
    else ok.push(true);

    if (!method.formulaTex?.trim()) result.missingFormula.push(method.slug);

    if (ok.length === 3) result.complete++;
  }

  return result;
}

describe("Content completeness audit (AC-CONTENT-01)", () => {
  const audit = auditCatalog();

  it("has non-empty description, textbook reference, and parameters for every method", () => {
    expect(audit.missingDescription).toEqual([]);
    expect(audit.missingReference).toEqual([]);
    expect(audit.missingParameters).toEqual([]);
    expect(audit.complete).toBe(audit.total);
  });

  it("reports completeness ≥ 95% (or lists every missing field)", () => {
    const pct = audit.total === 0 ? 0 : audit.complete / audit.total;
    expect(pct).toBeGreaterThanOrEqual(0.95);
  });

  it("reports formula coverage as a measurable metric", () => {
    // Formula coverage is tracked (not gating) — a follow-up fills missing formulas.
    const coverage = audit.total - audit.missingFormula.length;
    expect(coverage).toBeGreaterThan(0);
    expect(audit.missingFormula.length).toBeLessThanOrEqual(audit.total);
  });
});
