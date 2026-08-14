"use client";

import { cn } from "@/lib/utils/cn";
import type { BusinessStage } from "@/lib/valuation/types";

const stages: { value: BusinessStage; label: string; description: string }[] = [
  { value: "startup", label: "Startup", description: "Pre-revenue, early-stage" },
  { value: "growth", label: "Growth", description: "Scaling, revenue+" },
  { value: "mature", label: "Mature", description: "Established, stable" },
];

interface StageSelectorProps {
  value: BusinessStage;
  onChange: (stage: BusinessStage) => void;
}

export function StageSelector({ value, onChange }: StageSelectorProps) {
  return (
    <div className="flex gap-2 bg-neutral-100 dark:bg-neutral-800 p-1 rounded-xl">
      {stages.map((stage) => (
        <button
          key={stage.value}
          onClick={() => onChange(stage.value)}
          className={cn(
            "flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
            value === stage.value
              ? "bg-white dark:bg-neutral-900 text-primary-600 dark:text-primary-400 shadow-card"
              : "text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300"
          )}
          title={stage.description}
        >
          {stage.label}
        </button>
      ))}
    </div>
  );
}
