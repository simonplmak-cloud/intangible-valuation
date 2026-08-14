"use client";

import { HelpCircle } from "lucide-react";
import type { MethodParameter } from "@/lib/valuation/types";

interface ParameterGuideProps {
  parameters: MethodParameter[];
  stageDefaults?: {
    businessStage: string;
    discountRate: { median: number; low: number; high: number };
    royaltyRate: { median: number; low: number; high: number };
    usefulLife: { median: number; low: number; high: number };
    growthRate: { median: number; low: number; high: number };
  };
}

export function ParameterGuide({ parameters, stageDefaults }: ParameterGuideProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-neutral-900 dark:text-white">Parameter Guide</h3>

      <div className="space-y-3">
        {parameters.map((param) => (
          <div key={param.name} className="flex items-start gap-2">
            <HelpCircle className="w-4 h-4 text-neutral-400 mt-0.5 shrink-0" />
            <div>
              <div className="flex items-center gap-2">
                <code className="text-xs font-mono bg-neutral-100 dark:bg-neutral-800 px-1.5 py-0.5 rounded">
                  {param.name}
                </code>
                <span className="text-xs text-neutral-400">
                  {param.type}
                  {param.required ? " • required" : " • optional"}
                </span>
              </div>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">{param.description}</p>
              {param.minimum !== undefined && param.maximum !== undefined && (
                <p className="text-xs text-neutral-400 mt-0.5">
                  Range: {param.minimum} — {param.maximum}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {stageDefaults && <StageDefaultsDisplay defaults={stageDefaults} />}
    </div>
  );
}

function StageDefaultsDisplay({
  defaults,
}: {
  defaults: NonNullable<ParameterGuideProps["stageDefaults"]>;
}) {
  return (
    <div className="mt-4 p-4 rounded-lg bg-primary-50 dark:bg-primary-950 border border-primary-100 dark:border-primary-900">
      <p className="text-xs font-semibold text-primary-700 dark:text-primary-300 mb-2">
        Stage-Specific Defaults ({defaults.businessStage})
      </p>
      <div className="grid grid-cols-2 gap-2 text-xs text-primary-600 dark:text-primary-400">
        <div>
          <span className="font-medium">Discount Rate:</span>{" "}
          {defaults.discountRate.low * 100}% — {defaults.discountRate.high * 100}%
        </div>
        <div>
          <span className="font-medium">Royalty Rate:</span> {defaults.royaltyRate.low * 100}% —{" "}
          {defaults.royaltyRate.high * 100}%
        </div>
        <div>
          <span className="font-medium">Useful Life:</span> {defaults.usefulLife.low} —{" "}
          {defaults.usefulLife.high} years
        </div>
        <div>
          <span className="font-medium">Growth Rate:</span> {defaults.growthRate.low * 100}% —{" "}
          {defaults.growthRate.high * 100}%
        </div>
      </div>
    </div>
  );
}
