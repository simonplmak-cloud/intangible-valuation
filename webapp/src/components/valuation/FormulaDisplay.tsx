interface FormulaDisplayProps {
  formulaTex?: string;
  formulaReference: string;
}

export function FormulaDisplay({ formulaTex, formulaReference }: FormulaDisplayProps) {
  return (
    <div className="p-4 rounded-xl bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wide">Formula</span>
      </div>
      {formulaTex && (
        <div className="text-lg font-mono text-neutral-900 dark:text-white mb-2 overflow-x-auto">
          {formulaTex}
        </div>
      )}
      <p className="text-xs text-neutral-500">
        <span className="font-medium">Source:</span> {formulaReference}
      </p>
    </div>
  );
}
