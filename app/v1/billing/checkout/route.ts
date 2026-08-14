import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth/config";
import { getStripe } from "@/lib/billing/stripe";
import { getSurrealClient } from "@/lib/surreal/client";
import type { PlanRow, SubscriptionRow } from "@/lib/billing/gate";

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session?.user?.email) {
    return NextResponse.json({ error: "UNAUTHORIZED", message: "Authentication required" }, { status: 401 });
  }
  const userId = (session.user as { id?: string }).id ?? session.user.email;

  const stripe = getStripe();
  if (!stripe) {
    return NextResponse.json({ error: "BILLING_UNAVAILABLE", message: "Billing is not configured" }, { status: 503 });
  }

  const body = await request.json().catch(() => ({}));
  const planId = typeof body.plan_id === "string" ? body.plan_id : "";
  if (!planId) {
    return NextResponse.json({ error: "VALIDATION_ERROR", message: "plan_id is required" }, { status: 400 });
  }

  const db = await getSurrealClient();
  const [plans] = await db.query<[PlanRow[]]>("SELECT * FROM plans WHERE id = $pid", { pid: planId });
  const plan = plans?.[0];
  if (!plan?.stripe_price_id) {
    return NextResponse.json({ error: "VALIDATION_ERROR", message: "Unknown or non-billable plan" }, { status: 400 });
  }

  const [subs] = await db.query<[SubscriptionRow[]]>(
    "SELECT * FROM subscriptions WHERE user_id = $uid",
    { uid: userId }
  );
  let customerId = subs?.[0]?.stripe_customer_id;

  if (!customerId) {
    const customer = await stripe.customers.create({
      email: session.user.email,
      metadata: { user_id: userId },
    });
    customerId = customer.id;
  }

  const origin = request.nextUrl.origin;
  const checkout = await stripe.checkout.sessions.create({
    mode: "subscription",
    line_items: [{ price: plan.stripe_price_id, quantity: 1 }],
    customer: customerId,
    success_url: `${origin}/dashboard?checkout=success`,
    cancel_url: `${origin}/calculator?checkout=cancelled`,
    metadata: { user_id: userId, plan_id: planId },
    subscription_data: { metadata: { user_id: userId, plan_id: planId } },
  });

  return NextResponse.json({ url: checkout.url });
}
