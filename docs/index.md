# Intangible Asset Valuation

Complete implementation of all valuation methodologies from the Ascent Partners textbook.

## Overview

This library provides a comprehensive suite of intangible asset valuation methods, including:

- **Time Value of Money** — PV, FV, annuity, perpetuity, growing annuity, terminal value
- **Discount Rate Construction** — Build-up method, CAPM, WACC, DLOM, control premiums
- **Valuation Approaches** — Cost approach (reproduction/replacement), Market approach
- **Income Methods** — Relief from Royalty, Multi-Period Excess Earnings, Incremental Cash Flow
- **Asset-Specific Models** — IP, brand, technology, customer relationships, human capital
- **Advanced Analytics** — Monte Carlo simulation, decision trees, purchase price allocation, goodwill, litigation damages

## Quick Start

### Installation

```bash
pip install intangible-valuation
```

### Basic Usage

```python
from src.core.time_value import present_value, annuity_pv, perpetuity_pv
from src.core.discount_rates import build_up_discount_rate, wacc
from src.income_methods.relief_from_royalty import relief_from_royalty
from src.advanced.purchase_price_alloc import purchase_price_allocation

# Present value of a single cash flow
result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
print(f"PV: ${result.value:,.2f}")  # $233,253.69

# Build-up discount rate
rate = build_up_discount_rate(
    risk_free_rate=0.04,
    equity_risk_premium=0.06,
    size_premium=0.02,
    industry_risk_premium=0.01,
    specific_risk_premium=0.03,
)
print(f"Discount rate: {rate.value:.2%}")  # 16.00%

# Relief from Royalty valuation
value = relief_from_royalty(
    revenue_projections=[1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
    royalty_rate=0.05,
    discount_rate=0.12,
    tax_rate=0.25,
    useful_life=5,
)
print(f"Asset value: ${value['value']:,.2f}")

# Purchase Price Allocation
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

## Project Structure

```
src/
├── core/               # TVM, discount rates, statistics
├── approaches/         # Cost and market approaches
├── income_methods/     # Relief from royalty, MPEEM, incremental cashflow
├── asset_types/        # IP, brand, technology, customer, human capital
├── advanced/           # Monte Carlo, decision trees, PPA, goodwill, litigation
├── utils/              # Constants, formulas, sensitivity analysis
mcp_server/             # MCP server for AI agent integration
skills/                 # AI-Agent Skills for valuation workflows
tests/                  # Comprehensive test suite
```

## Key Features

| Feature | Description |
|---------|-------------|
| Pydantic Validation | All inputs validated with clear error messages |
| Step-by-Step Results | Every calculation returns detailed breakdown |
| Monte Carlo | Uncertainty analysis with configurable distributions |
| Decision Trees | Backward induction for contingent valuations |
| PPA Waterfall | Full purchase price allocation with goodwill |
| MCP Server | AI agent integration via Model Context Protocol |

## Documentation

- [API Reference](api/core.md) — Full API documentation
- [MCP Server](mcp.md) — AI agent integration setup
- [AI Skills](skills.md) — Valuation workflow skills

## Testing

```bash
pytest tests/ -v
pytest tests/test_book_examples/ -v  # Textbook example tests
```
