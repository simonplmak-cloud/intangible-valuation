import { track } from "@vercel/analytics";

export type AnalyticsEvent =
  | "landing"
  | "calculation"
  | "checkout_started"
  | "checkout_completed"
  | "signup";

export type AnalyticsProperties = Record<string, string | number | boolean | null>;

export function trackEvent(name: AnalyticsEvent, properties?: AnalyticsProperties): void {
  track(name, properties);
}
