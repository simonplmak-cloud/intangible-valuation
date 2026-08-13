import { getSurrealClient } from "@/lib/surreal/client";
import type { ValuationResult, SavedValuation, SavedValuationDetail } from "@/lib/valuation/types";
import { ulid } from "ulid";

export interface SaveValuationInput {
  userId: string;
  method: string;
  category: string;
  assetType?: string;
  businessStage?: string;
  inputs: Record<string, unknown>;
  result: ValuationResult;
}

export async function saveValuation(input: SaveValuationInput): Promise<{ id: string }> {
  const db = await getSurrealClient();
  const id = `valuations:${ulid()}`;

  const record = {
    id,
    user_id: input.userId,
    method: input.method,
    category: input.category,
    asset_type: input.assetType ?? null,
    business_stage: input.businessStage ?? null,
    inputs: input.inputs,
    result_value: input.result.value,
    formula_reference: input.result.formula_reference,
    steps: input.result.steps,
    assumptions: input.result.assumptions,
    pv_before_tab: input.result.pv_before_tab ?? null,
    tab_factor: input.result.tab_factor ?? null,
    created_at: new Date().toISOString(),
    is_favorite: false,
  };

  await db.create(id, record);

  return { id };
}

export async function getValuationById(id: string): Promise<SavedValuationDetail | null> {
  const db = await getSurrealClient();
  const fullId = id.startsWith("valuations:") ? id : `valuations:${id}`;
  const result = await db.query("SELECT * FROM valuations WHERE id = $id", { id: fullId });
  const rows = result as unknown[];
  return (rows?.[0] as SavedValuationDetail) ?? null;
}

export async function getUserValuations(
  userId: string,
  options?: {
    page?: number;
    limit?: number;
    method?: string;
    category?: string;
    sort?: string;
    order?: "asc" | "desc";
  }
): Promise<{ valuations: SavedValuation[]; total: number }> {
  const db = await getSurrealClient();
  const page = options?.page ?? 1;
  const limit = options?.limit ?? 20;
  const sort = options?.sort ?? "created_at";
  const order = options?.order ?? "desc";
  const category = options?.category;
  const method = options?.method;

  let whereClause = `user_id = "${userId}"`;
  if (category) whereClause += ` AND category = "${category}"`;
  if (method) whereClause += ` AND method = "${method}"`;

  const countResult = await db.query(`SELECT count() FROM valuations WHERE ${whereClause} GROUP ALL`);
  const countRows = countResult as unknown[];
  const countItem = countRows?.[0] as { count: number } | undefined;
  const total = countItem?.count ?? 0;

  const dataResult = await db.query(
    `SELECT id, method, category, asset_type, business_stage, result_value, created_at, is_favorite FROM valuations WHERE ${whereClause} ORDER BY ${sort} ${order} LIMIT ${limit}`
  );
  const rows = (dataResult as unknown[]) ?? [];

  return { valuations: rows as SavedValuation[], total };
}

export async function deleteValuation(id: string): Promise<void> {
  const db = await getSurrealClient();
  const fullId = id.startsWith("valuations:") ? id : `valuations:${id}`;
  await db.delete(fullId);
}

export async function toggleFavorite(id: string, currentValue: boolean): Promise<void> {
  const db = await getSurrealClient();
  const fullId = id.startsWith("valuations:") ? id : `valuations:${id}`;
  await db.merge(fullId, { is_favorite: !currentValue });
}
