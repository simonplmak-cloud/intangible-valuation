import Link from "next/link";
import { ArrowRight, TrendingUp } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden gradient-primary text-white">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(255,255,255,0.1),transparent_70%)]" />
      <div className="container-page relative py-24 md:py-32">
        <div className="max-w-3xl">
          <p className="text-primary-200 text-sm font-medium mb-4 tracking-wide uppercase">
            Powered by Ascent Partners
          </p>
          <h1 className="text-display-lg md:text-display-xl mb-6 text-balance">
            The Authority on Intangible Asset Valuation
          </h1>
          <p className="text-lg md:text-xl text-primary-100 mb-8 max-w-2xl text-balance">
            68 textbook-verified valuation methods. Step-by-step proofs. MCP gateway for AI agents.
            The most transparent, auditable valuation platform on the internet.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/calculator"
              className="inline-flex items-center justify-center gap-2 bg-white text-primary-600 px-6 py-3 rounded-xl text-sm font-semibold hover:bg-primary-50 transition-colors"
            >
              Try the Calculator <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/docs"
              className="inline-flex items-center justify-center gap-2 border border-white/30 text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-white/10 transition-colors"
            >
              Browse Methods
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
