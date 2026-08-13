import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { MethodCalculator } from "./MethodCalculator";
import { CATALOG_SLUGS } from "@/lib/valuation/catalog";

export function generateStaticParams() {
  return CATALOG_SLUGS.map((method) => ({ method }));
}

export default async function MethodCalculatorPage({ params }: { params: Promise<{ method: string }> }) {
  const { method } = await params;

  return (
    <div>
      <Breadcrumb
        items={[
          { label: "Home", href: "/" },
          { label: "Calculator", href: "/calculator" },
          { label: method.replace(/-/g, " ") },
        ]}
      />
      <div className="container-narrow py-8">
        <MethodCalculator slug={method} />
      </div>
    </div>
  );
}
