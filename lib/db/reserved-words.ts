// SurrealDB reserved words — a field/table name in this list breaks the
// SurrealQL parser (a field named `function` failed in the sibling repo).
// Every schema field/table name is validated against this list before migration.

export const RESERVED_WORDS = [
  "function", "return", "table", "field", "index", "event", "select", "update", "delete", "create",
  "if", "then", "else", "end", "type", "value", "none", "null", "true", "false", "and", "or", "not",
  "in", "out", "set", "let", "from", "where", "group", "order", "limit", "start", "on", "as",
];

export function assertNotReserved(name: string, context: string): void {
  if (RESERVED_WORDS.includes(name.toLowerCase())) {
    throw new Error(`Reserved word '${name}' used as ${context}`);
  }
}

export function assertSchemaNoReservedWords(surql: string, file: string): void {
  const fieldMatches = surql.matchAll(/DEFINE (FIELD|TABLE)\s+([A-Za-z_][A-Za-z0-9_]*)/g);
  for (const match of fieldMatches) {
    const name = match[2];
    if (RESERVED_WORDS.includes(name.toLowerCase())) {
      throw new Error(`Reserved word '${name}' used in ${file} (DEFINE ${match[1].toUpperCase()})`);
    }
  }
}
