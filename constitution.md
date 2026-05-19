# Project Constitution

Version: 1.0.0
Last updated: 2026-05-20

## Project Overview

Intangible Asset Valuation Platform — a Python library, MCP server, and AI-Agent Skills
that implements all calculation methodologies from "Intangible Asset Valuation" (Ascent Partners, 2025).
The platform provides programmatic access to every valuation formula, method, and framework
described in the book's 19 chapters and 3 appendices.

## Architecture Principles

- Python-first: all valuation logic lives in a pure Python library (`src/`)
- MCP protocol: all calculations exposed via Model Context Protocol for AI agent integration
- Pure functions: valuation methods are stateless, deterministic, and side-effect free
- Validation-first: all inputs validated with Pydantic before any calculation
- Test-driven: every formula has unit tests with book example verification
- No hidden state: all parameters explicit, no global configuration
- Documentation as code: docstrings contain formula references (chapter/section)

## Technology Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Language | Python 3.11+ | Type hints everywhere, strict mypy |
| Core Library | Pure Python + NumPy | No heavy frameworks for calculation layer |
| Validation | Pydantic v2 | All input/output schemas |
| Testing | pytest | Unit tests, parametric tests, book example tests |
| MCP Server | fastmcp | Model Context Protocol server |
| AI Skills | OpenCode skill format | Markdown-based skill definitions |
| Build | uv | Package management and build |
| CI/CD | GitHub Actions | Test, lint, type-check, publish |
| Docs | GitHub Pages + MkDocs | Auto-generated from docstrings |
| Packaging | PyPI + GitHub Releases | pip installable |

## Security Constraints

- No secrets in source code — all credentials via environment variables
- No logging of input financial data (may contain confidential valuations)
- All external inputs validated before processing
- No network calls from calculation layer (pure library)
- MCP server requires local-only binding by default

## Naming Conventions

- Files: snake_case (`relief_from_royalty.py`)
- Variables/functions: snake_case
- Classes: PascalCase
- Constants: SCREAMING_SNAKE_CASE
- Modules: match book chapter naming (e.g., `discount_rates`, `royalty_analysis`)

## Banned Patterns

- No `any` type hints — use proper types
- No `print()` in library code (use logging)
- No global mutable state
- No hardcoded financial constants (rates, premiums must be parameters)
- No silent failures — all errors raised with descriptive messages
- No floating point comparison without tolerance (use `math.isclose`)

## File Structure

```
src/
  __init__.py
  core/                    # Foundational math (Ch 2, Appendix A)
    time_value.py          # PV, FV, annuities, perpetuities
    discount_rates.py      # Build-up, CAPM, WACC
    statistics.py          # Monte Carlo, regression, decision trees
  approaches/              # Three core approaches (Ch 3)
    cost_approach.py       # Reproduction cost, replacement cost
    market_approach.py     # Comparable transactions, royalty capitalization
    income_approach.py     # Base income approach utilities
  income_methods/          # Advanced income methods (Ch 4)
    relief_from_royalty.py # RFR method
    excess_earnings.py     # MPEEM, single-period excess earnings
    incremental_cashflow.py # Incremental cash flow method
  asset_types/             # Asset-specific valuation (Ch 5-9)
    ip_valuation.py        # Patents, trademarks, copyrights, trade secrets
    brand_valuation.py     # Brand-specific methods
    technology_valuation.py # Software, data, platform assets
    customer_valuation.py  # Customer relationships, distribution networks
    human_capital.py       # Workforce, training, organizational capital
  advanced/                # Specialized topics (Ch 10-17)
    goodwill.py            # Goodwill calculation, components
    purchase_price_alloc.py # PPA waterfall
    impairment_testing.py  # Goodwill & intangible impairment
    royalty_benchmark.py   # Royalty rate analysis (Ch 6)
    transfer_pricing.py    # Cross-border, OECD/BEPS (Ch 16)
    litigation.py          # Damages calculations (Ch 15)
    monte_carlo.py         # Simulation engine
  utils/
    formulas.py            # Formula reference (Appendix A)
    templates.py           # Report templates
    constants.py           # Industry defaults, reference data
mcp_server/
  server.py                # MCP server entry point
  tools.py                 # MCP tool definitions
skills/
  valuation-calculator/    # AI skill for calculations
  ppa-workflow/            # AI skill for purchase price allocation
  impairment-checker/      # AI skill for impairment testing
tests/
  test_core/
  test_approaches/
  test_income_methods/
  test_asset_types/
  test_advanced/
  test_book_examples/      # All book exercise solutions verified
  test_mcp/
mcp.json                   # MCP configuration
pyproject.toml
```

## Open Questions / Deferred Decisions

- [PENDING] Deployment target for MCP server: local-only vs cloud-hosted option
- [PENDING] Whether to include pre-loaded royalty benchmark database or external API
- [RESOLVED] Package name → `intangible-valuation` (PyPI)
- [RESOLVED] Python version → 3.11+ minimum
