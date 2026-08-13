import { Surreal } from "surrealdb";

let _client: Surreal | null = null;
let _connectionPromise: Promise<Surreal> | null = null;

function getConfig(): { url: string; namespace: string; database: string; user: string; password: string } {
  const url = process.env.SURREALDB_URL;
  const namespace = process.env.SURREALDB_NS || "intangible_valuation";
  const database = process.env.SURREALDB_DB || (process.env.NODE_ENV === "production" ? "production" : "development");
  const user = process.env.SURREALDB_USER || "root";
  const password = process.env.SURREALDB_PASS || "root";

  if (!url) {
    throw new Error("SURREALDB_URL environment variable is required");
  }

  return { url, namespace, database, user, password };
}

export async function getSurrealClient(): Promise<Surreal> {
  if (_client) return _client;

  if (_connectionPromise) return _connectionPromise;

  _connectionPromise = (async () => {
    const { url, namespace, database, user, password } = getConfig();
    const db = new Surreal();

    try {
      await db.connect(url, {
        namespace,
        database,
        auth: { username: user, password },
      });

      await db.use({ namespace, database });

      _client = db;
      return db;
    } catch (error) {
      _connectionPromise = null;
      throw new Error(`Failed to connect to SurrealDB at ${url}: ${error instanceof Error ? error.message : String(error)}`);
    }
  })();

  return _connectionPromise;
}

export async function healthCheck(): Promise<{ status: string; namespace: string; database: string; latency_ms: number }> {
  const start = Date.now();
  try {
    const db = await getSurrealClient();
    await db.query("RETURN true");
    const latency = Date.now() - start;
    const { namespace, database } = getConfig();
    return { status: "ok", namespace, database, latency_ms: latency };
  } catch (error) {
    const latency = Date.now() - start;
    return { status: "error", namespace: getConfig().namespace, database: getConfig().database, latency_ms: latency };
  }
}

export async function closeSurrealClient(): Promise<void> {
  if (_client) {
    await _client.close();
    _client = null;
    _connectionPromise = null;
  }
}

export async function query<T extends unknown[] = unknown[]>(surrealql: string, params?: Record<string, unknown>): Promise<T> {
  const db = await getSurrealClient();
  const result = await db.query<T>(surrealql, params);
  return result as unknown as T;
}

export async function queryOne<T = unknown>(surrealql: string, params?: Record<string, unknown>): Promise<T | null> {
  const results = await query(surrealql, params);
  const arr = results as unknown[];
  return (arr?.[0] as T | undefined) ?? null;
}

export type SurrealRecord<T = Record<string, unknown>> = T & { id: string };
