# Intangible Asset Valuation Engine

> Complete intangible asset valuation library implementing **124+ functions** from the Intangible Asset Valuation textbook. Python library + MCP server + AI-Agent Skills.

[![PyPI](https://img.shields.io/pypi/v/intangible-valuation.svg)](https://pypi.org/project/intangible-valuation/)
[![CI](https://github.com/simonplmak-cloud/intangible-valuation/actions/workflows/ci.yml/badge.svg)](https://github.com/simonplmak-cloud/intangible-valuation/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docs](https://img.shields.io/badge/docs-GitHub_Pages-blue)](https://simonplmak-cloud.github.io/intangible-valuation/)

## Overview

A production-grade Python library for intangible asset valuation, implementing every formula from the **[Intangible Asset Valuation](https://www.amazon.com/Intangible-Asset-Valuation-Comprehensive-Technology/dp/B0FZ8742R1)** textbook by Simon Mak, William Yuen, Paul Wu, and Wayne Hu (Valuation in Practice Series, Ascent Partners). Designed for developers, financial analysts, accountants, and AI agents who need auditable, structured valuation computations for ASC 805 / IFRS 3 compliant workflows.

**Three-layer architecture:**
1. **Python Library** — 22 modules, 124+ typed functions, all returning `ValuationResult` (value + assumptions + sensitivity)
2. **MCP Server** — 54 tools for AI agents (Claude, OpenCode, etc.) via stdio/SSE
3. **AI-Agent Skills** — 3 skill definitions with workflow guidance for valuation domains

## Installation

```bash
pip install intangible-valuation          # library only
pip install intangible-valuation[mcp]     # + MCP server
pip install intangible-valuation[dev]     # + pytest, ruff, mypy
```

## Quick Start

### Python Library

```python
from intangible_valuation.core.time_value import present_value
from intangible_valuation.core.discount_rates import build_up_discount_rate
from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty

# Present Value
result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
print(f"PV: ${result.value:,.2f}")  # $233,253.69

# Build-Up Discount Rate
rate = build_up_discount_rate(
    risk_free_rate=0.04, equity_risk_premium=0.06,
    size_premium=0.02, industry_risk_premium=0.01, specific_risk_premium=0.03,
)
print(f"Discount rate: {rate.value:.2%}")  # 16.00%

# Relief from Royalty — Patent Valuation
value = relief_from_royalty(
    revenue_projections=[1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
    royalty_rate=0.05, discount_rate=0.12, tax_rate=0.25, useful_life=5,
)
print(f"Patent value: ${value.value:,.2f}")
```

### MCP Server (for AI Agents)

```bash
cd mcp_server && python server.py
```

Connect with any MCP-compatible AI agent. All 54 valuation tools available.

### AI-Agent Skills

Copy the `skills/` directory to your agent's skills folder:
- **`asset-valuation`** — Patents, trademarks, technology, customer relationships, human capital
- **`discount-rate-construction`** — Build-up, CAPM, WACC, risk premiums, adjustments
- **`purchase-price-allocation`** — ASC 805 / IFRS 3 PPA workflow, goodwill calculation, impairment testing

## Valuation Methods by Category

| Category | Methods | Chapter |
|----------|---------|---------|
| **Time Value** | PV, FV, annuity, perpetuity, growing annuity, terminal value | 2 |
| **Discount Rates** | Build-up, CAPM, WACC, TAB, control premium, DLOM, currency adjustment | 2 |
| **Statistics** | Monte Carlo, decision trees, regression | 2 |
| **Cost Approach** | Reproduction cost, replacement cost | 3 |
| **Market Approach** | Comparable transactions, royalty capitalization | 3 |
| **Income Methods** | Relief from Royalty, MPEEM, incremental cash flow | 4 |
| **Intellectual Property** | Patent, trademark, copyright, trade secret | 5 |
| **Royalty Analysis** | Benchmarking, 25% rule, adjustment | 6 |
| **Technology** | Developed technology, software, data assets, platforms | 7 |
| **Customer-Related** | Customer relationships, distribution network, non-compete | 8 |
| **Human Capital** | Assembled workforce, key person | 9 |
| **Goodwill & PPA** | Goodwill calculation, PPA waterfall | 10 |
| **Impairment** | Goodwill & intangible impairment (ASC 350 / IAS 36) | 11 |
| **Monte Carlo** | Simulation, sensitivity analysis | 15 |
| **Decision Trees** | Backward induction | 16 |
| **Litigation** | Lost profits, pre-judgment interest | 17 |
| **Transfer Pricing** | CUP method, OECD guidelines | 18 |

## Why This Library?

- **Auditable** — Every function returns `ValuationResult` with value, method, inputs, assumptions, and step-by-step calculation breakdown
- **Textbook-accurate** — All 124+ formulas verified against book example values with 698 unit tests
- **AI-ready** — MCP server and Skills for seamless AI agent integration
- **Complete coverage** — All three valuation approaches (cost, market, income) across 19 chapters
- **Open source** — MIT license, extensible, well-documented

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Lint
ruff check .

# Type check
mypy src/
```

## Documentation

- **API Reference:** [GitHub Pages](https://simonplmak-cloud.github.io/intangible-valuation/)
- **PyPI:** [pypi.org/project/intangible-valuation](https://pypi.org/project/intangible-valuation/)
- **MCP Server Guide:** [docs/mcp.md](docs/mcp.md)
- **AI Skills Guide:** [docs/skills.md](docs/skills.md)

## Companion Textbook

**[Intangible Asset Valuation: A Comprehensive Guide to Valuing Brands, IP, Technology, and Human Capital](https://www.amazon.com/Intangible-Asset-Valuation-Comprehensive-Technology/dp/B0FZ8742R1)**  
*Theory, Methods, Regulation, and Practice* — Valuation in Practice Series by Ascent Partners  
By Simon Mak, William Yuen, Paul Wu, Wayne Hu · 176 pages · 19 chapters · 3 appendices

## Citing This Project

```bibtex
@software{intangible_valuation_engine,
  author = {Mak, Simon and Yuen, William and Wu, Paul and Hu, Wayne},
  title = {Intangible Asset Valuation Engine},
  year = {2026},
  url = {https://github.com/simonplmak-cloud/intangible-valuation},
  license = {MIT},
}
```

Based on formulas from the **Intangible Asset Valuation** textbook.

## License

MIT — see [LICENSE](LICENSE) for details.
