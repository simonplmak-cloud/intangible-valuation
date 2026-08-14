import { describe, it, expect } from "vitest";
import { buildSystemPrompt } from "@/lib/ai/prompts";

describe("AI advisor system prompt (grounded — never computes)", () => {
  it("forbids the advisor from computing numbers itself", () => {
    const p = buildSystemPrompt();
    expect(p).toContain("NEVER compute numbers yourself");
  });

  it("injects the full method catalog with citations", () => {
    const p = buildSystemPrompt();
    expect(p).toMatch(/Available methods \(68 total\)/);
    expect(p).toContain("slug:");
    expect(p).toMatch(/Ch \d+/);
  });

  it("mandates textbook citations for every recommendation", () => {
    const p = buildSystemPrompt();
    expect(p).toContain("cite its textbook chapter/section");
  });

  it("tells the user to run the calculator rather than ask for a number", () => {
    const p = buildSystemPrompt();
    expect(p).toContain("run it in the calculator");
  });
});
