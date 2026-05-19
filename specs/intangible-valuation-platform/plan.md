# Technical Plan: Intangible Asset Valuation Platform

## Spec Reference
Implements: `specs/intangible-valuation-platform/spec.md`

## Architecture Overview

The platform is structured as three layers:
1. **Core Python Library** (`src/`) — Pure functions implementing every valuation formula from the book. No I/O, no side effects, fully testable.
2. **MCP Server** (`mcp_server/`) — Exposes all library functions as MCP tools using fastmcp. Handles input validation, error formatting, and tool discovery.
3. **AI-Agent Skills** (`skills/`) — Markdown skill definitions that guide AI agents through valuation workflows, referencing the library via MCP tools.

Each calculation module maps directly to a book chapter/section, making it easy to trace implementation back to source material.

## Component Breakdown

### Core Math Module (`src/core/`)
- **Responsibility:** Foundational financial mathematics (Ch 2, Appendix A)
- **Location:** `src/core/time_value.py`, `src/core/discount_rates.py`, `src/core/statistics.py`
- **Accepts:** Numeric parameters (rates, cash flows, periods)
- **Returns:** Numeric results or structured result objects
- **AC Coverage:** AC-1 through AC-7, AC-36 through AC-41

### Valuation Approaches Module (`src/approaches/`)
- **Responsibility:** Three core valuation approaches (Ch 3)
- **Location:** `src/approaches/cost_approach.py`, `src/approaches/market_approach.py`, `src/approaches/income_approach.py`
- **Accepts:** Asset-specific parameters (costs, comparables, cash flows)
- **Returns:** Valuation results with methodology metadata
- **AC Coverage:** AC-8 through AC-11

### Income Methods Module (`src/income_methods/`)
- **Responsibility:** Advanced income-based methods (Ch 4)
- **Location:** `src/income_methods/relief_from_royalty.py`, `src/income_methods/excess_earnings.py`, `src/income_methods/incremental_cashflow.py`
- **Accepts:** Revenue projections, royalty rates, CACs, discount rates
- **Returns:** Detailed valuation with step-by-step breakdown
- **AC Coverage:** AC-12 through AC-15

### Asset Types Module (`src/asset_types/`)
- **Responsibility:** Asset-specific valuation methods (Ch 5-9)
- **Location:** `src/asset_types/ip_valuation.py`, `src/asset_types/brand_valuation.py`, `src/asset_types/technology_valuation.py`, `src/asset_types/customer_valuation.py`, `src/asset_types/human_capital.py`
- **Accepts:** Asset-specific parameters (patent life, brand strength, customer retention, etc.)
- **Returns:** Asset valuations with risk adjustments
- **AC Coverage:** AC-16 through AC-31

### Advanced Module (`src/advanced/`)
- **Responsibility:** Specialized calculations (Ch 10, 15-17, Appendix A)
- **Location:** `src/advanced/goodwill.py`, `src/advanced/purchase_price_alloc.py`, `src/advanced/impairment_testing.py`, `src/advanced/royalty_benchmark.py`, `src/advanced/transfer_pricing.py`, `src/advanced/litigation.py`, `src/advanced/monte_carlo.py`
- **Accepts:** Complex multi-asset parameters
- **Returns:** Allocation waterfalls, impairment amounts, damages calculations
- **AC Coverage:** AC-32 through AC-44

### MCP Server (`mcp_server/`)
- **Responsibility:** Expose all functions as MCP tools
- **Location:** `mcp_server/server.py`, `mcp_server/tools.py`
- **Accepts:** MCP tool calls with JSON parameters
- **Returns:** Structured JSON results with calculation steps
- **AC Coverage:** AC-45, AC-46, AC-E4

### AI Skills (`skills/`)
- **Responsibility:** Guide AI agents through valuation workflows
- **Location:** `skills/valuation-calculator/SKILL.md`, `skills/ppa-workflow/SKILL.md`, `skills/impairment-checker/SKILL.md`
- **Accepts:** Natural language user queries
- **Returns:** Structured workflows with MCP tool calls
- **AC Coverage:** AC-47 through AC-49

## Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Validation | Pydantic v2 | Industry standard, excellent error messages, MCP schema generation |
| MCP Framework | fastmcp | Lightweight, native Pydantic integration, auto-generates tool schemas |
| Math | NumPy | Vectorized operations for Monte Carlo, well-tested numerical routines |
| Testing | pytest + pytest-cov | Parametric testing, coverage reports, industry standard |
| Type Checking | mypy (strict) | Catches type errors before runtime |
| Linting | ruff | Fast, comprehensive, auto-fix capability |
| Build | uv | Fast dependency resolution, modern Python tooling |
| Docs | MkDocs + mkdocstrings | Auto-generated from docstrings, GitHub Pages compatible |

## Integration Points

- **MCP Clients**: Any AI agent supporting MCP protocol (Claude Desktop, Cursor, opencode)
- **PyPI Distribution**: pip installable as `intangible-valuation`
- **GitHub Pages**: Documentation site auto-built from docstrings
- **GitHub Actions**: CI/CD pipeline for test, lint, type-check, publish

## AC Coverage Map

| AC | Component(s) | Contract(s) |
|----|-------------|-------------|
| AC-1 | time_value.py | contracts/core-api.md |
| AC-2 | discount_rates.py | contracts/core-api.md |
| AC-3 | discount_rates.py | contracts/core-api.md |
| AC-4 | discount_rates.py | contracts/core-api.md |
| AC-5 | discount_rates.py | contracts/core-api.md |
| AC-6 | statistics.py, monte_carlo.py | contracts/core-api.md |
| AC-7 | statistics.py | contracts/core-api.md |
| AC-8 | cost_approach.py | contracts/approaches-api.md |
| AC-9 | cost_approach.py | contracts/approaches-api.md |
| AC-10 | market_approach.py | contracts/approaches-api.md |
| AC-11 | market_approach.py | contracts/approaches-api.md |
| AC-12 | relief_from_royalty.py | contracts/income-api.md |
| AC-13 | excess_earnings.py | contracts/income-api.md |
| AC-14 | excess_earnings.py | contracts/income-api.md |
| AC-15 | incremental_cashflow.py | contracts/income-api.md |
| AC-16 | ip_valuation.py | contracts/asset-types-api.md |
| AC-17 | brand_valuation.py | contracts/asset-types-api.md |
| AC-18 | ip_valuation.py | contracts/asset-types-api.md |
| AC-19 | ip_valuation.py | contracts/asset-types-api.md |
| AC-20 | royalty_benchmark.py | contracts/advanced-api.md |
| AC-21 | royalty_benchmark.py | contracts/advanced-api.md |
| AC-22 | royalty_benchmark.py | contracts/advanced-api.md |
| AC-23 | technology_valuation.py | contracts/asset-types-api.md |
| AC-24 | technology_valuation.py | contracts/asset-types-api.md |
| AC-25 | technology_valuation.py | contracts/asset-types-api.md |
| AC-26 | technology_valuation.py | contracts/asset-types-api.md |
| AC-27 | customer_valuation.py | contracts/asset-types-api.md |
| AC-28 | customer_valuation.py | contracts/asset-types-api.md |
| AC-29 | customer_valuation.py | contracts/asset-types-api.md |
| AC-30 | human_capital.py | contracts/asset-types-api.md |
| AC-31 | human_capital.py | contracts/asset-types-api.md |
| AC-32 | purchase_price_alloc.py | contracts/advanced-api.md |
| AC-33 | goodwill.py | contracts/advanced-api.md |
| AC-34 | impairment_testing.py | contracts/advanced-api.md |
| AC-35 | impairment_testing.py | contracts/advanced-api.md |
| AC-36 | discount_rates.py | contracts/core-api.md |
| AC-37 | discount_rates.py | contracts/core-api.md |
| AC-38 | time_value.py | contracts/core-api.md |
| AC-39 | utils/formulas.py | contracts/core-api.md |
| AC-40 | excess_earnings.py | contracts/income-api.md |
| AC-41 | utils/formulas.py | contracts/core-api.md |
| AC-42 | transfer_pricing.py | contracts/advanced-api.md |
| AC-43 | transfer_pricing.py | contracts/advanced-api.md |
| AC-44 | litigation.py | contracts/advanced-api.md |
| AC-45 | mcp_server/tools.py | contracts/mcp-api.md |
| AC-46 | mcp_server/server.py | contracts/mcp-api.md |
| AC-47 | skills/valuation-calculator/ | contracts/skills-api.md |
| AC-48 | skills/ppa-workflow/ | contracts/skills-api.md |
| AC-49 | skills/impairment-checker/ | contracts/skills-api.md |
| AC-E1 | All modules (Pydantic) | contracts/error-handling.md |
| AC-E2 | All modules | contracts/error-handling.md |
| AC-E3 | All modules | contracts/error-handling.md |
| AC-E4 | mcp_server/server.py | contracts/error-handling.md |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Book formulas ambiguous or incomplete | Medium | High | Cross-reference with external sources (Damodaran, Pratt); document assumptions |
| Monte Carlo performance with large iterations | Low | Medium | Use NumPy vectorization; set sensible default iteration count (10,000) |
| MCP protocol changes break server | Low | Medium | Pin fastmcp version; add CI test for MCP compatibility |
| PyPI package name conflict | Low | High | Verify availability before first publish; use scoped name if needed |
| Floating point precision issues | Medium | Medium | Use `math.isclose` for comparisons; document precision limits |
| Scope creep — too many methods for v1 | High | High | Strictly limit to book-covered methods; defer extensions to v2 |

## Out of Scope (Technical)

- No database layer — all data passed as function parameters
- No web framework — MCP server only (no REST/GraphQL)
- No async I/O — synchronous calculations only
- No caching layer — pure functions, caller manages caching
- No internationalization — English only for v1
