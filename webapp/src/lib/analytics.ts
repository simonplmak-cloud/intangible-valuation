import { track } from "@vercel/analytics";

export type AnalyticsEvent =
  | "landing"
  | "calculation"
  | "checkout_started"
  | "checkout_completed"
  | "signup";

export function trackEvent(name: AnalyticsEvent, properties?: Record<string, unknown>): void {
  track(name, properties);
}
