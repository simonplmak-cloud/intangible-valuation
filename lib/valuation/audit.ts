import { getSurrealClient } from "@/lib/surreal/client";
import { ulid } from "ulid";

export type AuditAction = "created" | "exported" | "shared" | "deleted";

export interface LogAuditInput {
  userId: string;
  valuationId: string;
  action: AuditAction;
  ipAddress?: string;
  userAgent?: string;
  metadata?: Record<string, unknown>;
}

export async function logAuditTrail(input: LogAuditInput): Promise<{ id: string }> {
  const db = await getSurrealClient();
  const id = `audit_trail:${ulid()}`;
  const inId = `users:${input.userId}`;
  const outId = input.valuationId.startsWith("valuations:") ? input.valuationId : `valuations:${input.valuationId}`;

  await db.query(
    `RELATE $in->audit_trail->$out SET
      id = $id,
      action = $action,
      ip_address = $ip,
      user_agent = $ua,
      created_at = $ts,
      metadata = $meta`,
    {
      id,
      in: inId,
      out: outId,
      action: input.action,
      ip: input.ipAddress ?? null,
      ua: input.userAgent ?? null,
      ts: new Date().toISOString(),
      meta: input.metadata ?? null,
    }
  );

  return { id };
}

export async function getAuditTrail(
  valuationId: string,
  options?: { page?: number; limit?: number }
): Promise<{ entries: unknown[]; total: number }> {
  const db = await getSurrealClient();
  const limit = options?.limit ?? 20;

  const countResult = await db.query("SELECT count() FROM audit_trail WHERE out = $vid GROUP ALL", { vid: valuationId });
  const countRows = countResult as unknown[];
  const countItem = countRows?.[0] as { count: number } | undefined;
  const total = countItem?.count ?? 0;

  const dataResult = await db.query(
    "SELECT *, in.* as user FROM audit_trail WHERE out = $vid ORDER BY created_at DESC LIMIT $limit",
    { vid: valuationId, limit }
  );
  const entries = (dataResult as unknown[]) ?? [];

  return { entries, total };
}

export async function getUserAuditTrail(
  userId: string,
  options?: { page?: number; limit?: number }
): Promise<{ entries: unknown[]; total: number }> {
  const db = await getSurrealClient();
  const limit = options?.limit ?? 20;

  const countResult = await db.query("SELECT count() FROM audit_trail WHERE in = $uid GROUP ALL", { uid: `users:${userId}` });
  const countRows = countResult as unknown[];
  const countItem = countRows?.[0] as { count: number } | undefined;
  const total = countItem?.count ?? 0;

  const dataResult = await db.query(
    "SELECT *, out.* as valuation FROM audit_trail WHERE in = $uid ORDER BY created_at DESC LIMIT $limit",
    { uid: `users:${userId}`, limit }
  );
  const entries = (dataResult as unknown[]) ?? [];

  return { entries, total };
}
