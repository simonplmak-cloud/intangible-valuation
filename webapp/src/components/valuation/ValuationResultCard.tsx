import type { ValuationResult } from "@/lib/valuation/types";
import { StepByStepProof } from "./StepByStepProof";
import { ExportButton } from "./ExportButton";

interface ValuationResultCardProps {
  result: ValuationResult;
  isLoading?: boolean;
  error?: string;
}

export function ValuationResultCard({ result, isLoading, error }: ValuationResultCardProps) {
  if (isLoading) {
    return (
      <div className="card-elevated p-6 animate-pulse">
        <div className="h-6 w-32 bg-neutral-200 dark:bg-neutral-700 rounded mb-4" />
        <div className="h-12 w-48 bg-primary-100 dark:bg-primary-900 rounded mb-3" />
        <div className="h-4 w-64 bg-neutral-100 dark:bg-neutral-800 rounded" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card-elevated p-6 border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-950">
        <p className="text-sm font-semibold text-red-600 dark:text-red-400 mb-1">Calculation Error</p>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="card-elevated p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-xs font-semibold text-primary-500 uppercase tracking-wide mb-1">
              {result.metadata?.category || result.method}
            </p>
            <h3 className="text-lg font-serif font-semibold text-neutral-900 dark:text-white">
              {result.method}
            </h3>
          </div>
          <ExportButton result={result} />
        </div>

        <div className="mb-4">
          <p className="text-xs text-neutral-400 mb-1">Valuation Result</p>
          <p className="text-3xl font-bold font-mono text-primary-600 dark:text-primary-400">
            ${result.value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        {result.metadata?.textbook_chapter && (
          <p className="text-xs text-neutral-400">
            Source: {result.metadata.textbook_chapter}
          </p>
        )}
      </div>

      <StepByStepProof result={result} />
    </div>
  );
}
