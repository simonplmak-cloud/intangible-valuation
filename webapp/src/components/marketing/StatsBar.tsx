const stats = [
  { value: "68", label: "Valuation Methods" },
  { value: "1,000+", label: "Verified Tests" },
  { value: "49", label: "MCP Tools" },
  { value: "4", label: "AI Skills" },
  { value: "124", label: "Python Functions" },
];

export function StatsBar() {
  return (
    <section className="border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950">
      <div className="container-page py-8">
        <div className="flex flex-wrap justify-center gap-x-12 gap-y-4">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-2xl font-bold font-mono text-primary-500">{stat.value}</p>
              <p className="text-xs text-neutral-400 uppercase tracking-wide">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
