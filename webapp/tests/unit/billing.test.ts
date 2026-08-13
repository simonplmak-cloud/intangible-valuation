import { describe, it, expect } from "vitest";
import { validateCitation, hasValidCitation, type Citation } from "@/lib/etl/citation";

const COMPLETE: Citation = {
  source: "Damodaran Online — Cost of Capital by Industry",
  author: "Aswath Damodaran (NYU Stern)",
  date: "2025",
  url: "https://pages.stern.nyu.edu/~adamodar/",
  ref: "Cost of Capital by Industry Sector",
};

describe("Citation chain validation (AC-DATA-01)", () => {
  it("accepts a complete citation chain", () => {
    expect(validateCitation(COMPLETE)).toEqual([]);
    expect(hasValidCitation(COMPLETE)).toBe(true);
  });

  it("rejects a missing citation", () => {
    expect(validateCitation(null).length).toBeGreaterThan(0);
    expect(hasValidCitation(undefined)).toBe(false);
  });

  it("rejects when url and doi are both missing", () => {
    const { url, ...rest } = COMPLETE;
    const errors = validateCitation(rest);
    expect(errors.some((e) => e.field === "url")).toBe(true);
  });

  it("accepts a doi in place of url", () => {
    const { url, ...rest } = COMPLETE;
    expect(validateCitation({ ...rest, doi: "10.1000/example" })).toEqual([]);
  });

  it("rejects an empty source", () => {
    const errors = validateCitation({ ...COMPLETE, source: "  " });
    expect(errors.some((e) => e.field === "source")).toBe(true);
  });

  it("rejects a missing specific reference", () => {
    const { ref, ...rest } = COMPLETE;
    expect(validateCitation(rest).some((e) => e.field === "ref")).toBe(true);
  });
});
