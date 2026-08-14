import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function CTASection() {
  return (
    <section className="gradient-primary-subtle dark:gradient-dark py-20">
      <div className="container-page text-center">
        <h2 className="text-display-sm text-neutral-900 dark:text-white mb-4">
          Ready to Value with Confidence?
        </h2>
        <p className="text-neutral-500 dark:text-neutral-400 max-w-xl mx-auto mb-8">
          Join the financial professionals who trust our platform for transparent, traceable,
          and textbook-verified intangible asset valuations.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <Link
            href="/calculator"
            className="inline-flex items-center justify-center gap-2 bg-primary-500 text-white px-8 py-4 rounded-xl text-sm font-semibold hover:bg-primary-600 transition-colors shadow-lg shadow-primary-500/25"
          >
            Start Free <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/docs"
            className="inline-flex items-center justify-center gap-2 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-white border border-neutral-300 dark:border-neutral-700 px-8 py-4 rounded-xl text-sm font-semibold hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
          >
            View Documentation
          </Link>
        </div>
      </div>
    </section>
  );
}
