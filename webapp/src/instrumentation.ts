import * as Sentry from "@sentry/nextjs";

export function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    Sentry.init({
      dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

      tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,

      replaysSessionSampleRate: 0.1,
      replaysOnErrorSampleRate: 1.0,

      environment: process.env.NODE_ENV || "development",

      beforeSend(event) {
        // Strip financial data from error reports
        if (event.request?.data) {
          delete event.request.data;
        }
        return event;
      },
    });
  }
}

export const onRequestError = Sentry.captureRequestError;
