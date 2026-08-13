export function Footer() {
  return (
    <footer className="border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950">
      <div className="container-page py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center text-white font-bold text-sm">
                IV
              </div>
              <span className="font-serif font-semibold text-lg">Intangible Valuation</span>
            </div>
            <p className="text-sm text-neutral-500">
              The most authoritative source for intangible asset valuation. Powered by Ascent Partners.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-sm text-neutral-900 dark:text-white mb-3">Calculator</h4>
            <ul className="space-y-2">
              <li><a href="/calculator" className="text-sm text-neutral-500 hover:text-primary-500">All Methods</a></li>
              <li><a href="/#core" className="text-sm text-neutral-500 hover:text-primary-500">Core Methods</a></li>
              <li><a href="/#income" className="text-sm text-neutral-500 hover:text-primary-500">Income Methods</a></li>
              <li><a href="/#advanced" className="text-sm text-neutral-500 hover:text-primary-500">Advanced Topics</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-sm text-neutral-900 dark:text-white mb-3">Resources</h4>
            <ul className="space-y-2">
              <li><a href="/docs" className="text-sm text-neutral-500 hover:text-primary-500">Documentation</a></li>
              <li><a href="/mcp" className="text-sm text-neutral-500 hover:text-primary-500">MCP Gateway</a></li>
              <li><a href="/skills" className="text-sm text-neutral-500 hover:text-primary-500">AI Skills</a></li>
              <li><a href="/about" className="text-sm text-neutral-500 hover:text-primary-500">About</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-sm text-neutral-900 dark:text-white mb-3">Community</h4>
            <ul className="space-y-2">
              <li><a href="https://github.com/simonplmak-cloud/intangible-valuation" className="text-sm text-neutral-500 hover:text-primary-500">GitHub</a></li>
              <li><a href="https://pypi.org/project/intangible-valuation/" className="text-sm text-neutral-500 hover:text-primary-500">PyPI</a></li>
              <li><a href="https://github.com/simonplmak-cloud/intangible-valuation/issues" className="text-sm text-neutral-500 hover:text-primary-500">Issues</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-neutral-200 dark:border-neutral-800 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-neutral-400">
            &copy; {new Date().getFullYear()} Ascent Partners. All valuation methods trace to the Intangible Asset Valuation textbook.
          </p>
          <p className="text-xs text-neutral-400">
            68 methods &middot; 1,000+ tests &middot; 49 MCP tools &middot; Open source
          </p>
        </div>
      </div>
    </footer>
  );
}
