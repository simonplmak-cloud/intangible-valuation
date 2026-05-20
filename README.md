# Intangible Asset Valuation

[![Python Versions](https://img.shields.io/pypi/pyversions/intangible-valuation.svg)](https://pypi.org/project/intangible-valuation/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/simonplmak-cloud/intangible-valuation/actions/workflows/ci.yml/badge.svg)](https://github.com/simonplmak-cloud/intangible-valuation/actions/workflows/ci.yml)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> Complete intangible asset valuation library implementing all methodologies from
> **"Intangible Asset Valuation"** (Ascent Partners Group Limited, 2025, ISBN: 9798272663375).
> Python library + MCP server + AI-Agent Skills for financial analysts, accountants, and AI agents.

## Overview

**intangible-valuation** is the most comprehensive open-source Python library for intangible asset valuation. It provides programmatic access to every calculation methodology described in the definitive textbook "Intangible Asset Valuation" — covering 19 chapters and 3 appendices of valuation frameworks, from foundational time value of math to advanced purchase price allocation and litigation damages.

Built for **financial analysts**, **valuation professionals**, **accountants**, and **AI agents**, this library eliminates error-prone spreadsheet calculations with validated, tested, and auditable Python functions. Every formula includes step-by-step breakdowns, Pydantic input validation, and textbook chapter references.

### Who This Is For

- **Financial Analysts** — Replace Excel models with reusable, tested Python functions
- **Accountants & Auditors** — Perform ASC 805 / IFRS 3 purchase price allocations with audit trails
- **Valuation Professionals** — Access all three approaches (cost, market, income) in one library
- **AI Agents** — Connect via MCP server for automated valuation workflows
- **Students & Educators** — Verify textbook examples with 698 passing tests

## Key Features

- **124+ valuation functions** across 22 modules — every methodology from the textbook
- **54 MCP tools** — AI agent integration via Model Context Protocol
- **3 AI-Agent Skills** — valuation-calculator, ppa-workflow, impairment-checker
- **698 tests** — 100% of book exercise solutions verified
- **Pydantic validation** — clear error messages for every input parameter
- **Step-by-step results** — detailed calculation breakdowns, not just final numbers
- **Monte Carlo simulation** — uncertainty analysis with configurable distributions
- **Decision trees** — backward induction for contingent valuations
- **PPA waterfall** — full purchase price allocation with goodwill calculation
- **Zero dependencies** for core math — only Pydantic + NumPy required

## Installation

```bash
pip install intangible-valuation
```

With MCP server support:

```bash
pip install intangible-valuation[mcp]
```

For development:

```bash
pip install intangible-valuation[dev]
```

## Quick Start

### Present Value Calculation

```python
from src.core.time_value import present_value

# PV of $500,000 received in 8 years at 10% discount rate
result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
print(f"PV: ${result.value:,.2f}")  # $233,253.69
```

### Build-Up Discount Rate

```python
from src.core.discount_rates import build_up_discount_rate

rate = build_up_discount_rate(
    risk_free_rate=0.04,
    equity_risk_premium=0.06,
    size_premium=0.02,
    industry_risk_premium=0.01,
    specific_risk_premium=0.03,
)
print(f"Discount rate: {rate.value:.2%}")  # 16.00%
```

### Relief from Royalty — Patent Valuation

```python
from src.income_methods.relief_from_royalty import relief_from_royalty

value = relief_from_royalty(
    revenue_projections=[1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
    royalty_rate=0.05,
    discount_rate=0.12,
    tax_rate=0.25,
    useful_life=5,
)
print(f"Patent value: ${value.value:,.2f}")
```

### Multi-Period Excess Earnings Method (MPEEM)

```python
from src.income_methods.excess_earnings import mpeem

result = mpeem(
    cash_flow_projections=[5_000_000, 5_500_000, 6_000_000, 6_200_000, 6_000_000],
    contributory_asset_charges=[500_000, 520_000, 540_000, 550_000, 530_000],
    discount_rate=0.15,
    tax_rate=0.25,
)
print(f"Customer relationship value: ${result.value:,.2f}")
```

### Purchase Price Allocation

```python
from src.advanced.purchase_price_alloc import purchase_price_allocation

ppa = purchase_price_allocation(
    purchase_price=100_000_000,
    tangible_assets_fv=15_000_000,
    identified_intangibles=[
        {"name": "Customer Relationships", "value": 25_000_000, "method": "MPEEM"},
        {"name": "Technology", "value": 20_000_000, "method": "relief-from-royalty"},
        {"name": "Trademark", "value": 15_000_000, "method": "relief-from-royalty"},
    ],
    liabilities_fv=0,
)
print(f"Goodwill: ${ppa.value:,.2f}")  # $25,000,000
```

### Brand Valuation

```python
from src.asset_types.brand_valuation import trademark_valuation

brand = trademark_valuation(
    revenue=50_000_000,
    profit_margin=0.20,
    brand_strength_index=0.75,
    discount_rate=0.12,
    useful_life=10,
    method="relief_from_royalty",
)
print(f"Brand value: ${brand.value:,.2f}")
```

## Valuation Methods Covered

### Chapter 2 — Core Mathematics (Time Value of Money & Discount Rates)

| Method | Function | MCP Tool |
|--------|----------|----------|
| Present Value | `present_value()` | `present_value` |
| Future Value | `future_value()` | `future_value` |
| Ordinary Annuity | `annuity_pv()` | `annuity_pv` |
| Perpetuity | `perpetuity_pv()` | `perpetuity_pv` |
| Growing Annuity | `growing_annuity_pv()` | `growing_annuity_pv` |
| Terminal Value | `terminal_value()` | `terminal_value` |
| Build-Up Discount Rate | `build_up_discount_rate()` | `build_up_discount_rate` |
| CAPM | `capm_discount_rate()` | `capm_discount_rate` |
| WACC | `wacc()` | `wacc` |
| Tax Amortization Benefit | `tax_amortization_benefit()` | `tax_amortization_benefit` |
| Control Premium | `control_premium()` | `control_premium` |
| DLOM (Finnerty) | `dlom_finnerty()` | `dlom_finnerty` |
| Currency-Adjusted Rate | `currency_adjusted_discount_rate()` | `currency_adjusted_discount_rate` |

### Chapter 3 — Valuation Approaches (Cost & Market)

| Method | Function | MCP Tool |
|--------|----------|----------|
| Reproduction Cost | `reproduction_cost()` | `reproduction_cost` |
| Replacement Cost | `replacement_cost()` | `replacement_cost` |
| Market Comparables | `market_approach_comparables()` | `market_approach_comparables` |
| Royalty Capitalization | `royalty_capitalization()` | `royalty_capitalization` |

### Chapter 4 — Income Methods

| Method | Function | MCP Tool |
|--------|----------|----------|
| Relief from Royalty | `relief_from_royalty()` | `relief_from_royalty` |
| MPEEM | `mpeem()` | `mpeem` |
| Single-Period Excess Earnings | `single_period_excess_earnings()` | `single_period_excess_earnings` |
| Incremental Cash Flow | `incremental_cashflow()` | `incremental_cashflow` |
| Contributory Asset Charges | `contributory_asset_charges()` | `contributory_asset_charges` |

### Chapter 5 — Intellectual Property Valuation

| Asset Type | Function | MCP Tool |
|------------|----------|----------|
| Patent | `patent_valuation()` | `patent_valuation` |
| Trademark | `trademark_valuation()` | `trademark_valuation` |
| Copyright | `copyright_valuation()` | `copyright_valuation` |
| Trade Secret | `trade_secret_valuation()` | `trade_secret_valuation` |

### Chapter 7 — Technology Valuation

| Asset Type | Function | MCP Tool |
|------------|----------|----------|
| Developed Technology | `developed_technology_valuation()` | `developed_technology_valuation` |
| Software | `software_valuation()` | `software_valuation` |
| Data Assets | `data_asset_valuation()` | `data_asset_valuation` |
| Platform (Network Effects) | `platform_valuation()` | `platform_valuation` |

### Chapter 8 — Customer-Related Intangibles

| Asset Type | Function | MCP Tool |
|------------|----------|----------|
| Customer Relationships | `customer_relationship_valuation()` | `customer_relationship_valuation` |
| Distribution Network | `distribution_network_valuation()` | `distribution_network_valuation` |
| Non-Compete Agreement | `non_compete_valuation()` | `non_compete_valuation` |

### Chapter 9 — Human Capital

| Asset Type | Function | MCP Tool |
|------------|----------|----------|
| Assembled Workforce | `assembled_workforce_valuation()` | `assembled_workforce_valuation` |
| Key Person | `key_person_value()` | `key_person_value` |

### Chapter 10 — Goodwill & Purchase Price Allocation

| Method | Function | MCP Tool |
|--------|----------|----------|
| Goodwill Calculation | `goodwill()` | `goodwill` |
| PPA Waterfall | `purchase_price_allocation()` | `purchase_price_allocation` |
| Goodwill Impairment (ASC 350 / IAS 36) | `goodwill_impairment_test()` | `goodwill_impairment_test` |
| Intangible Impairment | `intangible_impairment_test()` | `intangible_impairment_test` |

### Chapters 6, 15, 16 — Advanced Topics

| Method | Function | MCP Tool |
|--------|----------|----------|
| Royalty Rate Benchmark | `royalty_rate_benchmark()` | `royalty_rate_benchmark` |
| 25% Rule | `twenty_five_percent_rule()` | `twenty_five_percent_rule` |
| Royalty Rate Adjustment | `adjust_royalty_rate()` | `adjust_royalty_rate` |
| Transfer Pricing (CUP) | `cup_transfer_price()` | `cup_transfer_price` |
| Patent Infringement Damages | `patent_infringement_damages()` | `patent_infringement_damages` |
| Monte Carlo Simulation | `monte_carlo_valuation()` | `monte_carlo_valuation` |
| Decision Tree | `decision_tree_valuation()` | `decision_tree_valuation` |
| Sensitivity Analysis | `sensitivity_analysis()` | `sensitivity_analysis` |
| Useful Life Estimation | `estimate_useful_life()` | `estimate_useful_life` |

## MCP Server — AI Agent Integration

Connect AI agents (Claude Desktop, Cursor, opencode, Windsurf) to all 54 valuation tools via the Model Context Protocol.

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "intangible-valuation": {
      "command": "uv",
      "args": ["run", "--with", "intangible-valuation[mcp]", "intangible-valuation-mcp"]
    }
  }
}
```

### Cursor / Windsurf

Add to `.cursor/mcp.json` or your IDE's MCP configuration:

```json
{
  "mcpServers": {
    "intangible-valuation": {
      "command": "intangible-valuation-mcp",
      "args": []
    }
  }
}
```

### opencode

Add to `mcp.json`:

```json
{
  "mcpServers": {
    "intangible-valuation": {
      "command": "intangible-valuation-mcp",
      "args": []
    }
  }
}
```

### Standalone

```bash
intangible-valuation-mcp
```

## AI-Agent Skills

Three specialized skills guide AI agents through complex valuation workflows:

| Skill | Purpose | Key Workflows |
|-------|---------|---------------|
| **valuation-calculator** | End-to-end asset valuation | Method selection, discount rate construction, royalty benchmarking, result validation |
| **ppa-workflow** | Purchase price allocation | ASC 805 / IFRS 3 compliance, intangible identification, goodwill calculation, waterfall validation |
| **impairment-checker** | Impairment testing | ASC 350 / IAS 36 testing, recoverable amount analysis, impairment loss calculation |

Skills are located in `skills/` and integrate with the MCP server — the skill provides workflow logic, the MCP tools execute calculations.

## Project Structure

```
src/
  core/                    # TVM, discount rates, statistics (Ch 2)
  approaches/              # Cost and market approaches (Ch 3)
  income_methods/          # RFR, MPEEM, incremental cash flow (Ch 4)
  asset_types/             # IP, brand, technology, customer, human capital (Ch 5-9)
  advanced/                # Goodwill, PPA, impairment, litigation, Monte Carlo (Ch 10-17)
  utils/                   # Constants, formulas, sensitivity analysis
mcp_server/                # MCP server for AI agent integration (54 tools)
skills/                    # 3 AI-Agent Skills for valuation workflows
tests/                     # 698 tests across 24 test files
```

## Documentation

- [Full Documentation](https://simonplmak-cloud.github.io/intangible-valuation/) — MkDocs site with API reference
- [API Reference](docs/api/core.md) — Complete function documentation
- [MCP Server Guide](docs/mcp.md) — AI agent integration setup
- [AI Skills Guide](docs/skills.md) — Valuation workflow skills

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run book example tests only
pytest tests/test_book_examples/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest tests/ -v`)
5. Run linting (`ruff check src/`)
6. Run type checking (`mypy src/`)
7. Submit a Pull Request

### Development Setup

```bash
# Clone and install dev dependencies
git clone https://github.com/simonplmak-cloud/intangible-valuation.git
cd intangible-valuation
pip install -e ".[dev,mcp]"

# Run tests
pytest tests/ -v

# Lint and type-check
ruff check src/
mypy src/
```

## Book Reference

This library implements all calculation methodologies from:

> **Intangible Asset Valuation**
> Ascent Partners Group Limited, 2025
> ISBN: 9798272663375
> 19 chapters, 3 appendices, 700+ exercises

The book covers the complete framework for valuing intangible assets including patents, trademarks, customer relationships, technology, brands, and goodwill. All formulas, methods, and examples in this library are cross-referenced to specific chapters and sections.

### Companion Resources

- [Ascent Partners Group](https://www.ascentpartners.com) — Valuation advisory services
- Book exercises are verified in `tests/test_book_examples/`
- Industry benchmark data in `src/utils/constants.py`

## License

MIT License — see [LICENSE](LICENSE) for details.

## Citation

If you use this library in academic work, please cite:

```bibtex
@software{intangible_valuation,
  title = {Intangible Asset Valuation — Python Library},
  author = {{Intangible Valuation Contributors}},
  year = {2025},
  url = {https://github.com/simonplmak-cloud/intangible-valuation},
  note = {Implementation of methodologies from "Intangible Asset Valuation" (Ascent Partners Group Limited, 2025, ISBN: 9798272663375)}
}

@book{ascent_partners_2025,
  title = {Intangible Asset Valuation},
  author = {{Ascent Partners Group Limited}},
  year = {2025},
  isbn = {9798272663375},
  publisher = {Ascent Partners Group Limited}
}
```

## Related Projects

- [MCP Protocol](https://modelcontextprotocol.io) — Model Context Protocol specification
- [Pydantic](https://docs.pydantic.dev) — Data validation library used for input schemas
- [ASC 805](https://www.fasb.org) — Business combinations accounting standard
- [IFRS 3](https://www.ifrs.org) — International financial reporting standard for business combinations
- [IAS 36](https://www.ifrs.org) — Impairment of assets standard
