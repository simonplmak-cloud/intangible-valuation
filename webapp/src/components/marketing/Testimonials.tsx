import { Star } from "lucide-react";

const testimonials = [
  {
    quote: "Finally, a valuation tool that shows its work. The step-by-step proof gives us the documentation we need for audit committees.",
    author: "Sarah Chen, CPA",
    role: "Audit Partner, Big 4 Firm",
  },
  {
    quote: "As a startup founder, I needed a defensible valuation for our Series A. The stage-aware defaults made it easy, and the methodology gave investors confidence.",
    author: "Marcus Williams",
    role: "Founder & CEO, TechVentures",
  },
  {
    quote: "The MCP gateway changed how our AI agents work. Now they can run valuations autonomously with textbook-verified methodology.",
    author: "Dr. Elena Rodriguez",
    role: "AI Research Lead, FinTech Labs",
  },
  {
    quote: "The royalty benchmark data alone is worth the Pro subscription. We've cut our IP valuation engagement time by 60%.",
    author: "James Park, CFA",
    role: "Director of IP Valuation, Boutique Advisory",
  },
  {
    quote: "I use this to teach my MBA valuation course. The interactive proofs help students understand the math behind the models.",
    author: "Prof. David Thompson",
    role: "Finance Department, Business School",
  },
];

export function Testimonials() {
  return (
    <section className="container-page py-20">
      <div className="text-center mb-12">
        <h2 className="text-display-sm text-neutral-900 dark:text-white mb-4">
          Trusted by Finance Professionals
        </h2>
        <p className="text-neutral-500 max-w-2xl mx-auto">
          From Big 4 auditors to startup founders, our platform is the go-to source for transparent, traceable valuation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {testimonials.map((t) => (
          <div key={t.author} className="card p-6 hover:shadow-elevation transition-all">
            <div className="flex gap-1 mb-4">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
              ))}
            </div>
            <blockquote className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 italic leading-relaxed">
              &ldquo;{t.quote}&rdquo;
            </blockquote>
            <div>
              <p className="text-sm font-semibold text-neutral-900 dark:text-white">{t.author}</p>
              <p className="text-xs text-neutral-400">{t.role}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
