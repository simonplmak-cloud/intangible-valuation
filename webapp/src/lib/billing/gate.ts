import { getSurrealClient } from "@/lib/surreal/client";

export interface PlanRow {
  id: string;
  name: string;
  price_monthly_cents: number;
  stripe_price_id?: string | null;
  features: string[];
  quota_saved_valuations: number;
}

export interface SubscriptionRow {
  id: string;
  user_id: string;
  plan_id: string;
  status: string;
  stripe_customer_id: string;
  stripe_subscription_id?: string | null;
  current_period_end?: string | null;
}

const FREE_QUOTA = 5;

export async function getPlanByUser(userId: string): Promise<PlanRow> {
  const db = await getSurrealClient();
  const [subs] = await db.query<[SubscriptionRow[]]>(
    "SELECT * FROM subscriptions WHERE user_id = $uid",
    { uid: userId }
  );
  const sub = subs?.[0];

  if (sub && sub.plan_id && sub.status === "active") {
    const [plans] = await db.query<[PlanRow[]]>("SELECT * FROM plans WHERE id = $pid", {
      pid: sub.plan_id,
    });
    if (plans?.[0]) return plans[0];
  }

  return {
    id: "plans:free",
    name: "Free",
    price_monthly_cents: 0,
    stripe_price_id: null,
    features: [],
    quota_saved_valuations: FREE_QUOTA,
  };
}

export async function hasFeature(userId: string, feature: string): Promise<boolean> {
  const plan = await getPlanByUser(userId);
  return plan.features.includes(feature);
}

export async function getQuota(userId: string): Promise<{ limit: number; used: number }> {
  const plan = await getPlanByUser(userId);
  const limit = plan.quota_saved_valuations;

  if (limit < 0) return { limit: -1, used: 0 };

  const db = await getSurrealClient();
  const [rows] = await db.query<[{ count: number }[]]>(
    "SELECT count() AS count FROM valuations WHERE user_id = $uid GROUP ALL",
    { uid: userId }
  );
  const used = rows?.[0]?.count ?? 0;
  return { limit, used };
}

export async function canSaveValuation(userId: string): Promise<boolean> {
  const { limit, used } = await getQuota(userId);
  if (limit < 0) return true;
  return used < limit;
}
