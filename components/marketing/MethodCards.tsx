import Link from "next/link";
import { Calculator, TrendingUp, BarChart3, Building2, Brain, ArrowRight } from "lucide-react";

const cards = [
  {
    icon: Calculator,
    title: "Core Methods",
    description: "Present value, future value, discount rates, CAPM, WACC, and statistical foundations.",
    href: "/calculator?category=core",
    color: "bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400",
  },
  {
    icon: TrendingUp,
    title: "Valuation Approaches",
    description: "Cost approach, market approach, and income approach with full methodology documentation.",
    href: "/calculator?category=approaches",
    color: "bg-green-50 text-green-600 dark:bg-green-950 dark:text-green-400",
  },
  {
    icon: BarChart3,
    title: "Income Methods",
    description: "Relief from royalty, MPEEM, incremental cash flow with TAB calculation.",
    href: "/calculator?category=income_methods",
    color: "bg-purple-50 text-purple-600 dark:bg-purple-950 dark:text-purple-400",
  },
  {
    icon: Building2,
    title: "Asset Types",
    description: "IP, brand, technology, customer relationships, and human capital valuation.",
    href: "/calculator?category=asset_types",
    color: "bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400",
  },
  {
    icon: Brain,
    title: "Advanced Topics",
    description: "Goodwill, purchase price allocation, impairment testing, Monte Carlo simulation, litigation damages.",
    href: "/calculator?category=advanced",
    color: "bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400",
  },
];

export function MethodCards() {
  return (
    <section className="container-page py-20">
      <div className="text-center mb-12">
        <h2 className="text-display-sm text-neutral-900 dark:text-white mb-4">
          Complete Valuation Toolkit
        </h2>
        <p className="text-neutral-500 max-w-2xl mx-auto">
          Every method is textbook-verified with full formula transparency, step-by-step proofs,
          and Python source code. No black boxes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="card p-6 hover:shadow-elevation hover:border-primary-200 dark:hover:border-primary-800 transition-all group"
          >
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${card.color}`}>
              <card.icon className="w-6 h-6" />
            </div>
            <h3 className="font-serif font-semibold text-lg text-neutral-900 dark:text-white mb-2">
              {card.title}
            </h3>
            <p className="text-sm text-neutral-500 mb-4">{card.description}</p>
            <span className="inline-flex items-center gap-1 text-sm font-medium text-primary-500 group-hover:text-primary-600">
              Explore <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
