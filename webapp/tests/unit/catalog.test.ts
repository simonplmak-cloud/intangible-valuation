import { describe, it, expect } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { CATALOG, CATALOG_SLUGS, getCatalogMethod } from "@/lib/valuation/catalog";

describe("Valuation method catalog", () => {
  it("declares all 68 methods", () => {
    expect(CATALOG.length).toBe(68);
    expect(CATALOG_SLUGS.length).toBe(68);
  });

  it("has no duplicate slugs", () => {
    expect(new Set(CATALOG_SLUGS).size).toBe(CATALOG_SLUGS.length);
  });

  it("uses kebab-case slugs only", () => {
    for (const slug of CATALOG_SLUGS) {
      expect(slug).toMatch(/^[a-z0-9-]+$/);
      expect(slug).not.toContain("_");
    }
  });

  it("declares an mcpTool in snake_case for every method", () => {
    for (const method of CATALOG) {
      expect(method.mcpTool).toMatch(/^[a-z0-9_]+$/);
      expect(method.mcpTool).not.toContain("-");
    }
  });

  it("keeps the slug ↔ mcpTool naming invariant (traceability)", () => {
    for (const method of CATALOG) {
      expect(method.mcpTool.replace(/_/g, "-")).toBe(method.slug);
    }
  });

  it("declares a non-empty parameters schema for every method", () => {
    for (const method of CATALOG) {
      expect(method.parameters.length).toBeGreaterThan(0);
      for (const p of method.parameters) {
        expect(p.name).toMatch(/^[a-z0-9_]+$/);
        expect(p.type).toBeTruthy();
      }
    }
  });

  it("declares a pythonFunction and textbookReference for every method", () => {
    for (const method of CATALOG) {
      expect(method.pythonFunction).toMatch(/^intangible_valuation\.[a-z0-9_.]+$/);
      expect(method.textbookReference).toMatch(/^(Ch \d+|Appendix [A-Z])/);
    }
  });

  it("resolves every slug via getCatalogMethod", () => {
    for (const slug of CATALOG_SLUGS) {
      expect(getCatalogMethod(slug)).toBeDefined();
    }
  });
});

describe("Catalog source-of-truth parity", () => {
  const routeFile = readFileSync(
    join(process.cwd(), "src", "app", "v1", "valuation", "route.ts"),
    "utf-8"
  );

  it("route.ts imports the shared catalog (no inline duplicate)", () => {
    expect(routeFile).toContain('import { CATALOG } from "@/lib/valuation/catalog"');
    expect(routeFile).not.toContain("slug: \"present-value\"");
  });
});
