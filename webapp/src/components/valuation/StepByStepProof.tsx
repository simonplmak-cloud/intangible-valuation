"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Copy, Check } from "lucide-react";
import type { ValuationResult } from "@/lib/valuation/types";

interface StepByStepProofProps {
  result: ValuationResult;
}

export function StepByStepProof({ result }: StepByStepProofProps) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const text = [
      `Method: ${result.method}`,
      `Value: $${result.value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      `Formula: ${result.formula_reference}`,
      "",
      "Steps:",
      ...result.steps.map((s, i) => `  ${i + 1}. ${s}`),
      "",
      "Assumptions:",
      ...result.assumptions.map((a) => `  - ${a}`),
    ].join("\n");

    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border border-neutral-200 dark:border-neutral-800 rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-neutral-50 dark:hover:bg-neutral-900 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-neutral-900 dark:text-white">Step-by-Step Proof</span>
          <span className="text-xs text-neutral-400">{result.steps.length} steps</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleCopy();
            }}
            className="p-1.5 rounded-lg hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors"
            title="Copy as report"
          >
            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4 text-neutral-400" />}
          </button>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-neutral-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-neutral-400" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="border-t border-neutral-200 dark:border-neutral-800 p-4 space-y-4">
          <div>
            <p className="text-xs font-semibold text-neutral-400 uppercase mb-2">Formula Reference</p>
            <p className="text-sm font-mono text-neutral-700 dark:text-neutral-300">
              {result.formula_reference}
            </p>
          </div>

          <div>
            <p className="text-xs font-semibold text-neutral-400 uppercase mb-2">Calculation Breakdown</p>
            <ol className="space-y-2">
              {result.steps.map((step, i) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="text-neutral-400 font-mono min-w-[1.5rem]">{i + 1}.</span>
                  <span className="text-neutral-700 dark:text-neutral-300">{step}</span>
                </li>
              ))}
            </ol>
          </div>

          {result.assumptions.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-neutral-400 uppercase mb-2">Assumptions</p>
              <ul className="space-y-1">
                {result.assumptions.map((a, i) => (
                  <li key={i} className="flex gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                    <span className="text-primary-400">-</span>
                    {a}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.pv_before_tab !== undefined && (
            <div className="flex gap-4 text-sm">
              <div>
                <span className="text-neutral-400">PV before TAB:</span>{" "}
                <span className="font-mono text-neutral-700 dark:text-neutral-300">
                  ${result.pv_before_tab.toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-neutral-400">TAB Factor:</span>{" "}
                <span className="font-mono text-neutral-700 dark:text-neutral-300">
                  {result.tab_factor?.toFixed(4)}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
