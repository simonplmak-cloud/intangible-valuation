import { NextRequest, NextResponse } from "next/server";
import type Stripe from "stripe";
import { ulid } from "ulid";
import { getStripe } from "@/lib/billing/stripe";
import { getSurrealClient } from "@/lib/surreal/client";

export async function POST(request: NextRequest) {
  const stripe = getStripe();
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!stripe || !webhookSecret) {
    return NextResponse.json({ error: "BILLING_UNAVAILABLE", message: "Billing is not configured" }, { status: 503 });
  }

  const signature = request.headers.get("stripe-signature");
  if (!signature) {
    return NextResponse.json({ error: "INVALID_SIGNATURE" }, { status: 400 });
  }

  const body = await request.text();
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch {
    return NextResponse.json({ error: "INVALID_SIGNATURE" }, { status: 400 });
  }

  const db = await getSurrealClient();

  // Idempotency: a duplicate event must not double-apply (AC-BILL-02).
  const [existing] = await db.query<[unknown[]]>(
    "SELECT * FROM webhook_events WHERE stripe_event_id = $eid",
    { eid: event.id }
  );
  if (existing && existing.length > 0) {
    return NextResponse.json({ received: true });
  }

  await db.create(`webhook_events:${ulid()}`, {
    stripe_event_id: event.id,
    type: event.type,
    payload: { object_id: (event.data.object as { id?: string }).id ?? null },
    processed_at: new Date().toISOString(),
  });

  switch (event.type) {
    case "checkout.session.completed": {
      const session = event.data.object as Stripe.Checkout.Session;
      const userId = session.subscription_data?.metadata?.user_id ?? session.metadata?.user_id ?? "";
      const planId = session.subscription_data?.metadata?.plan_id ?? session.metadata?.plan_id ?? "plans:pro";
      const customerId = typeof session.customer === "string" ? session.customer : "";
      if (userId && customerId) {
        await db.merge(`subscriptions:${userId}`, {
          user_id: userId,
          plan_id: planId,
          status: "active",
          stripe_customer_id: customerId,
          stripe_subscription_id: typeof session.subscription === "string" ? session.subscription : null,
          updated_at: new Date().toISOString(),
        });
      }
      break;
    }
    case "customer.subscription.updated": {
      const sub = event.data.object as Stripe.Subscription;
      const userId = sub.metadata?.user_id ?? "";
      if (userId) {
        await db.merge(`subscriptions:${userId}`, {
          status: sub.status,
          stripe_subscription_id: sub.id,
          current_period_end: sub.current_period_end
            ? new Date(sub.current_period_end * 1000).toISOString()
            : null,
          updated_at: new Date().toISOString(),
        });
      }
      break;
    }
    case "customer.subscription.deleted": {
      const sub = event.data.object as Stripe.Subscription;
      const userId = sub.metadata?.user_id ?? "";
      if (userId) {
        await db.merge(`subscriptions:${userId}`, {
          status: "canceled",
          updated_at: new Date().toISOString(),
        });
      }
      break;
    }
    case "invoice.payment_failed": {
      const invoice = event.data.object as Stripe.Invoice;
      const userId = invoice.metadata?.user_id ?? "";
      if (userId) {
        await db.merge(`subscriptions:${userId}`, {
          status: "past_due",
          updated_at: new Date().toISOString(),
        });
      }
      break;
    }
    default:
      break;
  }

  return NextResponse.json({ received: true });
}
