import { describe, it, expect } from "vitest";
import { CATALOG_SLUGS } from "@/lib/valuation/catalog";
import {
  getMethodCitations,
  citationCoverage,
  SOURCE_REGISTRY,
} from "@/lib/valuation/citations";

describe("Method citations (AC-1, AC-2, AC-E1)", () => {
  it("covers all 68 methods with at least one real citation (AC-1)", () => {
    const uncovered = citationCoverage();
    expect(uncovered).toEqual([]);
  });

  it("returns a textbook citation plus standards for a sample income method (AC-2)", () => {
    const citations = getMethodCitations("relief-from-royalty");
    const kinds = citations.map((c) => c.kind);
    expect(kinds).toContain("textbook");
    expect(kinds).toContain("standard");
    expect(citations.some((c) => c.id === "ias-38" || c.id === "ifrs-13" || c.id === "ivs-2025")).toBe(true);
  });

  it("returns an empty array for an unknown method (AC-E1)", () => {
    expect(getMethodCitations("does-not-exist")).toEqual([]);
  });

  it("resolves every citation id referenced by the registry to a real source", () => {
    for (const slug of CATALOG_SLUGS) {
      for (const c of getMethodCitations(slug)) {
        if (c.kind !== "textbook") {
          expect(SOURCE_REGISTRY[c.id]).toBeDefined();
        }
      }
    }
  });
});
