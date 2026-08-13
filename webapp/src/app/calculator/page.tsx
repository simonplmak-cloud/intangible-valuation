import { Calculator, TrendingUp, BarChart3, Building2, Brain, ArrowRight } from "lucide-react";
import Link from "next/link";

const categories = [
  {
    label: "Core Methods",
    icon: Calculator,
    href: "/calculator?category=core",
    description: "Time value of money, discount rates, and statistical foundations",
    methods: ["Present Value", "Future Value", "CAPM", "WACC", "Build-Up Rate"],
  },
  {
    label: "Valuation Approaches",
    icon: TrendingUp,
    href: "/calculator?category=approaches",
    description: "Cost, market, and income approaches to valuation",
    methods: ["Cost Approach", "Market Approach", "Income Approach"],
  },
  {
    label: "Income Methods",
    icon: BarChart3,
    href: "/calculator?category=income_methods",
    description: "Advanced income-based valuation techniques",
    methods: ["Relief from Royalty", "MPEEM", "Incremental Cash Flow"],
  },
  {
    label: "Asset Types",
    icon: Building2,
    href: "/calculator?category=asset_types",
    description: "IP, brand, technology, customer, and human capital valuation",
    methods: ["Patent Valuation", "Brand Valuation", "Technology Valuation"],
  },
  {
    label: "Advanced Topics",
    icon: Brain,
    href: "/calculator?category=advanced",
    description: "Goodwill, PPA, impairment, litigation, Monte Carlo",
    methods: ["Goodwill Calculation", "PPA Waterfall", "Monte Carlo Simulation"],
  },
];

export default function CalculatorPage() {
  return (
    <div className="container-page py-12">
      <div className="max-w-3xl mx-auto text-center mb-12">
        <h1 className="text-display-sm text-primary-500 mb-4">Valuation Calculator</h1>
        <p className="text-lg text-neutral-500 text-balance">
          Choose from 68 textbook-verified valuation methods. Every calculation shows the formula,
          step-by-step proof, and source citation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((cat) => (
          <Link
            key={cat.href}
            href={cat.href}
            className="card p-6 hover:shadow-elevation hover:border-primary-200 dark:hover:border-primary-800 transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-primary-50 dark:bg-primary-950 flex items-center justify-center mb-4 group-hover:bg-primary-100 dark:group-hover:bg-primary-900 transition-colors">
              <cat.icon className="w-5 h-5 text-primary-500" />
            </div>
            <h3 className="font-serif font-semibold text-neutral-900 dark:text-white mb-2">{cat.label}</h3>
            <p className="text-sm text-neutral-500 mb-3">{cat.description}</p>
            <ul className="space-y-1 mb-4">
              {cat.methods.map((m) => (
                <li key={m} className="text-xs text-neutral-400 font-mono">
                  {m}
                </li>
              ))}
            </ul>
            <span className="inline-flex items-center gap-1 text-sm font-medium text-primary-500 group-hover:text-primary-600">
              Browse methods <ArrowRight className="w-3.5 h-3.5" />
            </span>
          </Link>
        ))}
      </div>

      <div className="mt-12 card p-8 text-center">
        <p className="text-sm text-neutral-500 mb-4">
          Looking for the full catalog? Browse all 68 methods with search and filtering.
        </p>
        <Link
          href="/calculator/all"
          className="inline-flex items-center justify-center rounded-lg bg-primary-500 text-white px-6 py-3 text-sm font-semibold hover:bg-primary-600 transition-colors"
        >
          View All Methods
        </Link>
      </div>
    </div>
  );
}
