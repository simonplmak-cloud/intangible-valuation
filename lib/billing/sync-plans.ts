import Stripe from "stripe";
import { getSurrealClient, closeSurrealClient } from "@/lib/surreal/client";

const FREE_PLAN = {
  name: "Free",
  price_monthly_cents: 0,
  features: [],
  quota_saved_valuations: 5,
};

/**
 * Sync plans from Stripe Product/Price objects into SurrealDB.
 *
 * No seeding — pricing, features, and quotas are real and single-sourced from
 * Stripe. The free tier is a product definition (not external data) and is
 * upserted as the default. Paid plans are keyed by Stripe `metadata.plan_id`.
 */
export async function syncPlans(): Promise<number> {
  const db = await getSurrealClient();

  // Default free tier (product definition, not a seeded data point)
  await db.merge("plans:free", {
    ...FREE_PLAN,
    stripe_price_id: null,
    stripe_product_id: null,
  });

  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey) {
    console.log("  SKIP paid plans: STRIPE_SECRET_KEY not set");
    return 1;
  }

  const stripe = new Stripe(secretKey);
  const prices = await stripe.prices.list({
    active: true,
    limit: 100,
    expand: ["data.product"],
  });

  let count = 1;
  for (const price of prices.data) {
    const product = price.product as Stripe.Product;
    const planId = product.metadata?.plan_id ?? product.name.toLowerCase().replace(/\s+/g, "-");
    const features = (product.metadata?.features ?? "")
      .split(",")
      .map((f) => f.trim())
      .filter(Boolean);
    const quota = parseInt(product.metadata?.quota_saved_valuations ?? "-1", 10);

    await db.merge(`plans:${planId}`, {
      name: product.name,
      price_monthly_cents: price.unit_amount ?? 0,
      stripe_price_id: price.id,
      stripe_product_id: product.id,
      features,
      quota_saved_valuations: Number.isNaN(quota) ? -1 : quota,
    });
    count++;
  }

  return count;
}

syncPlans()
  .then((count) => {
    console.log(`\nPlans synced: ${count}\n`);
    process.exit(0);
  })
  .catch((error) => {
    console.error("\nPlan sync failed:", error);
    process.exit(1);
  })
  .finally(() => closeSurrealClient());
