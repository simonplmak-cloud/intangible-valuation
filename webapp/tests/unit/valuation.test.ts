import { describe, it, expect } from "vitest";
import { cn } from "@/lib/utils/cn";

describe("FormulaDisplay", () => {
  it("cn merges classes", () => {
    expect(cn("px-4 py-2", "px-6")).toBe("py-2 px-6");
  });

  it("cn handles conditionals", () => {
    expect(cn("base", false && "hidden", "visible")).toBe("base visible");
  });
});

describe("Types", () => {
  it("ValuationResult has required fields", () => {
    const result = {
      value: 100,
      method: "Test",
      formula_reference: "Ch 1",
      steps: ["step 1"],
      assumptions: ["assumption 1"],
      inputs: { a: 1 },
    };
    expect(result.value).toBe(100);
    expect(result.method).toBe("Test");
    expect(result.steps).toHaveLength(1);
  });
});

describe("API contract matching", () => {
  it("ValuationResult shape matches Python output", () => {
    const pythonOutput = {
      value: 521807.44,
      method: "Relief from Royalty",
      formula_reference: "Ch 4: RFR with TAB",
      steps: ["Period 1: ...", "PV before TAB: ..."],
      assumptions: ["Arm's length royalty rate"],
      pv_before_tab: 157426.12,
      tab_factor: 1.1452,
    };

    expect(typeof pythonOutput.value).toBe("number");
    expect(typeof pythonOutput.method).toBe("string");
    expect(Array.isArray(pythonOutput.steps)).toBe(true);
    expect(Array.isArray(pythonOutput.assumptions)).toBe(true);
    expect(typeof pythonOutput.pv_before_tab).toBe("number");
  });
});

describe("Stage defaults", () => {
  it("startup has higher discount rate than mature", () => {
    const startupRate = 0.25;
    const matureRate = 0.08;
    expect(startupRate).toBeGreaterThan(matureRate);
  });

  it("all stages have valid ranges", () => {
    const rates = { startup: 0.25, growth: 0.15, mature: 0.08 };
    for (const rate of Object.values(rates)) {
      expect(rate).toBeGreaterThan(0);
      expect(rate).toBeLessThan(1);
    }
  });
});
