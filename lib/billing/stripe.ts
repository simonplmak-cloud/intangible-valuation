import Stripe from "stripe";

let _stripe: Stripe | null = null;

/**
 * Lazily construct the Stripe client from the environment. Returns null when
 * STRIPE_SECRET_KEY is not configured so callers can degrade gracefully
 * (AC-ERR-01 — billing unavailable must not crash the free tier).
 */
export function getStripe(): Stripe | null {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) return null;
  if (!_stripe) {
    _stripe = new Stripe(key);
  }
  return _stripe;
}
