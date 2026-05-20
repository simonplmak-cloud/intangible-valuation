# Intangible Asset Valuation — Documentation

> Complete Python library implementing all valuation methodologies from **"Intangible Asset Valuation"** (Ascent Partners Group Limited, 2025, ISBN: 9798272663375).
> 124+ functions, 54 MCP tools, 3 AI-Agent Skills, 698 tests.

## Overview

**intangible-valuation** is the most comprehensive open-source library for intangible asset valuation in Python. It provides programmatic access to every calculation methodology described in the definitive textbook — covering **19 chapters and 3 appendices** of valuation frameworks.

Built for financial analysts, valuation professionals, accountants, and AI agents, this library replaces error-prone spreadsheet calculations with validated, tested, and auditable Python functions.

**Keywords:** intangible asset valuation, patent valuation, brand valuation, goodwill calculation, purchase price allocation, relief from royalty, MPEEM, MCP server, AI valuation tool, ASC 805, IFRS 3, impairment testing, discount rate, WACC, CAPM, Monte Carlo simulation.

## Quick Start

### Installation

```bash
pip install intangible-valuation
```

With MCP server for AI agent integration:

```bash
pip install intangible-valuation[mcp]
```

### First Valuation — Present Value

```python
from src.core.time_value import present_value

result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
print(f"PV: ${result.value:,.2f}")  # $233,253.69
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

## Methodology Coverage

Every methodology from the textbook, organized by chapter:

### Chapter 2 — Core Mathematics

| Category | Methods | Functions | Tests |
|----------|---------|-----------|-------|
| Time Value of Money | PV, FV, annuity, perpetuity, growing annuity, terminal value | 6 | 72 |
| Discount Rates | Build-up, CAPM, WACC, TAB, control premium, DLOM, currency adjustment | 7 | 84 |
| Statistics | Monte Carlo, decision trees, regression | 2 | 36 |

### Chapter 3 — Valuation Approaches

| Approach | Methods | Functions | Tests |
|----------|---------|-----------|-------|
| Cost Approach | Reproduction cost, replacement cost | 2 | 24 |
| Market Approach | Comparable transactions, royalty capitalization | 2 | 28 |

### Chapter 4 — Income Methods

| Method | Description | Functions | Tests |
|--------|-------------|-----------|-------|
| Relief from Royalty | PV of after-tax royalty payments avoided | 1 | 36 |
| MPEEM | Multi-period excess earnings with CACs | 3 | 48 |
| Incremental Cash Flow | With vs. without asset comparison | 1 | 24 |

### Chapter 5 — Intellectual Property

| Asset | Valuation Approach | Functions | Tests |
|-------|-------------------|-----------|-------|
| Patents | Risk-adjusted cash flows, comparable licensing | 1 | 24 |
| Trademarks | RFR, brand strength index | 1 | 20 |
| Copyrights | PV of royalty/licensing income | 1 | 16 |
| Trade Secrets | Cost + secrecy risk over time | 1 | 16 |

### Chapter 7 — Technology

| Asset | Methods | Functions | Tests |
|-------|---------|-----------|-------|
| Developed Technology | Life-cycle risk adjustment | 1 | 20 |
| Software | Cost + income approaches | 1 | 24 |
| Data Assets | Quality-adjusted revenue contribution | 1 | 16 |
| Platforms | Network effects modeling | 1 | 16 |

### Chapter 8 — Customer-Related Intangibles

| Asset | Method | Functions | Tests |
|-------|--------|-----------|-------|
| Customer Relationships | Multi-period with attrition | 1 | 24 |
| Distribution Network | Channel profitability | 1 | 16 |
| Non-Compete | Protected profits | 1 | 16 |

### Chapter 9 — Human Capital

| Asset | Method | Functions | Tests |
|-------|--------|-----------|-------|
| Assembled Workforce | Replacement cost | 1 | 16 |
| Key Person | Revenue contribution + risk | 1 | 16 |

### Chapter 10 — Goodwill & PPA

| Method | Standard | Functions | Tests |
|--------|----------|-----------|-------|
| Goodwill Calculation | ASC 805-30-30-1 | 1 | 16 |
| PPA Waterfall | ASC 805 / IFRS 3 | 1 | 24 |
| Goodwill Impairment | ASC 350 / IAS 36 | 1 | 20 |
| Intangible Impairment | ASC 350 / IAS 36 | 1 | 20 |

### Advanced Topics (Chapters 6, 15, 16)

| Topic | Methods | Functions | Tests |
|-------|---------|-----------|-------|
| Royalty Analysis | Benchmarking, 25% rule, adjustment | 3 | 36 |
| Transfer Pricing | CUP method, OECD guidelines | 1 | 16 |
| Litigation Damages | Lost profits, pre-judgment interest | 1 | 16 |
| Monte Carlo | Simulation, sensitivity analysis | 2 | 32 |
| Decision Trees | Backward induction | 1 | 16 |
| Useful Life | Economic + legal life estimation | 1 | 12 |

## Documentation Sections

| Section | Description |
|---------|-------------|
| [API Reference — Core](api/core.md) | Time value of money, discount rates, statistics |
| [API Reference — Approaches](api/approaches.md) | Cost approach, market approach |
| [API Reference — Income Methods](api/income_methods.md) | Relief from royalty, MPEEM, incremental cash flow |
| [API Reference — Asset Types](api/asset_types.md) | IP, brand, technology, customer, human capital |
| [API Reference — Advanced](api/advanced.md) | Goodwill, PPA, impairment, litigation, Monte Carlo |
| [MCP Server](mcp.md) | AI agent integration via Model Context Protocol |
| [AI Skills](skills.md) | Valuation workflow skills for AI agents |

## Why This Library

### vs. Excel Spreadsheets

| Feature | Excel | intangible-valuation |
|---------|-------|---------------------|
| Validation | Manual checks | Pydantic schemas with clear errors |
| Audit Trail | Cell formulas | Step-by-step calculation results |
| Reproducibility | Version drift | Immutable functions, 698 tests |
| Collaboration | File sharing | pip install, import, use |
| AI Integration | None | 54 MCP tools + 3 AI skills |
| Error Handling | Silent #DIV/0! | Descriptive exceptions |
| Performance | Slow for Monte Carlo | NumPy-optimized |

### vs. Manual Calculation

| Feature | Manual | intangible-valuation |
|---------|--------|---------------------|
| Speed | Hours per valuation | Milliseconds |
| Accuracy | Human error risk | Mathematically verified |
| Consistency | Analyst-dependent | Deterministic results |
| Documentation | Ad hoc | Chapter references built-in |
| Updates | Recalculate everything | Update library, re-run |

### vs. Other Libraries

| Feature | Other Tools | intangible-valuation |
|---------|-------------|---------------------|
| Scope | Single method | All 3 approaches, 19 chapters |
| Book Alignment | Generic | Exact textbook methodology match |
| AI Ready | No | MCP server + skills included |
| Testing | Unknown | 698 tests, book examples verified |
| Transparency | Black box | Open source, step-by-step results |

## Project Structure

```
src/
  core/                    # TVM, discount rates, statistics (Ch 2)
  approaches/              # Cost and market approaches (Ch 3)
  income_methods/          # RFR, MPEEM, incremental cash flow (Ch 4)
  asset_types/             # IP, brand, technology, customer, human capital (Ch 5-9)
  advanced/                # Goodwill, PPA, impairment, litigation, Monte Carlo (Ch 10-17)
  utils/                   # Constants, formulas, sensitivity analysis
mcp_server/                # MCP server (54 tools)
skills/                    # 3 AI-Agent Skills
tests/                     # 698 tests
```

## Book Reference

> **Intangible Asset Valuation**
> Ascent Partners Group Limited, 2025
> ISBN: 9798272663375
> 19 chapters, 3 appendices

All functions include docstring references to specific book chapters and sections. Book exercise solutions are verified in `tests/test_book_examples/`.

## Citation

```bibtex
@software{intangible_valuation,
  title = {Intangible Asset Valuation — Python Library},
  author = {{Intangible Valuation Contributors}},
  year = {2025},
  url = {https://github.com/simonplmak-cloud/intangible-valuation},
  note = {Implementation of methodologies from "Intangible Asset Valuation" (Ascent Partners Group Limited, 2025, ISBN: 9798272663375)}
}
```
