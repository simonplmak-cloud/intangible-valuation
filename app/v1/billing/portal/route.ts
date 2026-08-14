import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth/config";
import { getStripe } from "@/lib/billing/stripe";
import { getSurrealClient } from "@/lib/surreal/client";
import type { SubscriptionRow } from "@/lib/billing/gate";

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

  const db = await getSurrealClient();
  const [subs] = await db.query<[SubscriptionRow[]]>(
    "SELECT * FROM subscriptions WHERE user_id = $uid",
    { uid: userId }
  );
  const sub = subs?.[0];
  if (!sub?.stripe_customer_id) {
    return NextResponse.json({ error: "NOT_FOUND", message: "No subscription found" }, { status: 404 });
  }

  const origin = request.nextUrl.origin;
  const portal = await stripe.billingPortal.sessions.create({
    customer: sub.stripe_customer_id,
    return_url: `${origin}/dashboard`,
  });

  return NextResponse.json({ url: portal.url });
}
