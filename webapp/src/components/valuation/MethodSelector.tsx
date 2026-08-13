"use client";

import { useState, useMemo } from "react";
import { Search } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import type { MethodDefinition, MethodCategory } from "@/lib/valuation/types";

const CATEGORY_LABELS: Record<MethodCategory, string> = {
  core: "Core Methods",
  approaches: "Valuation Approaches",
  income_methods: "Income Methods",
  asset_types: "Asset Types",
  advanced: "Advanced Topics",
};

interface MethodSelectorProps {
  methods: MethodDefinition[];
  selected: string | null;
  onSelect: (slug: string) => void;
}

export function MethodSelector({ methods, selected, onSelect }: MethodSelectorProps) {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<MethodCategory | "all">("all");

  const filtered = useMemo(() => {
    return methods.filter((m) => {
      const matchCategory = category === "all" || m.category === category;
      const matchSearch =
        !search ||
        m.name.toLowerCase().includes(search.toLowerCase()) ||
        m.slug.toLowerCase().includes(search.toLowerCase()) ||
        m.description.toLowerCase().includes(search.toLowerCase());
      return matchCategory && matchSearch;
    });
  }, [methods, search, category]);

  const categories = useMemo(() => {
    const cats = new Set(methods.map((m) => m.category));
    return Array.from(cats) as MethodCategory[];
  }, [methods]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            type="text"
            placeholder="Search 68 valuation methods..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value as MethodCategory | "all")}
          className="px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="all">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {CATEGORY_LABELS[cat]}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
        {filtered.map((method) => (
          <button
            key={method.slug}
            onClick={() => onSelect(method.slug)}
            className={cn(
              "text-left p-4 rounded-xl border transition-all",
              selected === method.slug
                ? "border-primary-500 bg-primary-50 dark:bg-primary-950 dark:border-primary-400 ring-2 ring-primary-500/20"
                : "border-neutral-200 dark:border-neutral-800 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-card"
            )}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-primary-500 uppercase tracking-wide">
                {CATEGORY_LABELS[method.category]}
              </span>
              <span
                className={cn(
                  "text-xs px-1.5 py-0.5 rounded-full",
                  method.complexity === "basic"
                    ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                    : method.complexity === "intermediate"
                      ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300"
                      : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                )}
              >
                {method.complexity}
              </span>
            </div>
            <h3 className="font-semibold text-sm text-neutral-900 dark:text-white mb-1">{method.name}</h3>
            <p className="text-xs text-neutral-500 line-clamp-2">{method.description}</p>
          </button>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-center text-neutral-500 py-8">No methods match your search.</p>
      )}
    </div>
  );
}
