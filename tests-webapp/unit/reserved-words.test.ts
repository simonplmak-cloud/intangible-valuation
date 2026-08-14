import { describe, it, expect } from "vitest";
import { assertNotReserved, assertSchemaNoReservedWords } from "@/lib/db/reserved-words";

describe("Reserved-word denylist (lesson: `function` field broke SurrealQL)", () => {
  it("rejects a reserved word field name", () => {
    expect(() => assertNotReserved("function", "field")).toThrow(/Reserved word/);
  });

  it("allows a normal field name", () => {
    expect(() => assertNotReserved("result_value", "field")).not.toThrow();
  });

  it("is case-insensitive", () => {
    expect(() => assertNotReserved("SELECT", "field")).toThrow(/Reserved word/);
  });

  it("rejects reserved words in schema SQL", () => {
    expect(() =>
      assertSchemaNoReservedWords("DEFINE FIELD function ON t TYPE string;", "001.surql")
    ).toThrow(/Reserved word 'function'/);
  });

  it("passes clean schema SQL", () => {
    expect(() =>
      assertSchemaNoReservedWords("DEFINE FIELD result_value ON valuations TYPE number;", "001.surql")
    ).not.toThrow();
  });
});
