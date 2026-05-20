# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-05-20

### Added
- MIT LICENSE file
- Official GitHub Actions deployment workflow (bypasses Jekyll)
- PyPI publish workflow aligned with release triggers
- Example documentation pages (core methods, advanced methods, industry models)
- Chapter index documentation page

### Fixed
- 59 E501 line-too-long errors in `mcp_server/tools.py`
- Import sorting in `mcp_server/server.py`
- `monte_carlo.py` type annotation for strict mypy build
- PyPI description field length (under 512 char limit)
- GitHub Pages layout (switched from Jekyll branch to GitHub Actions)

### Changed
- Version bumped from 0.1.0 to 1.0.0
- Development status from Alpha to Production/Stable

## [0.1.0] — 2026-05-20

### Added
- Book-aligned documentation site with Amazon purchase link
- Book hero section on homepage with cover image and description
- Chapter-to-module mapping table
- Ascent Partners branding (logo, `#0083AB` color, Titillium Web/Open Sans fonts)
- 124+ valuation functions across 22 modules
- MCP server with 54 tools
- 3 AI-Agent Skills (asset-valuation, discount-rate-construction, purchase-price-allocation)
- 698 unit tests against textbook example values
- GitHub Pages documentation site (MkDocs Material)
- `CITATION.cff` for academic referencing
- mypy type checking in CI
- GitHub Actions CI/CD workflows

### Core Mathematics (Chapter 2)
- Time value of money: PV, FV, annuity, perpetuity, growing annuity, terminal value
- Discount rates: build-up, CAPM, WACC, TAB, control premium, DLOM, currency adjustment
- Statistics: Monte Carlo simulation, decision trees

### Valuation Approaches (Chapter 3)
- Cost approach: reproduction cost, replacement cost
- Market approach: comparable transactions, royalty capitalization

### Income Methods (Chapter 4)
- Relief from Royalty with tax amortization benefit
- Multi-Period Excess Earnings Method (MPEEM)
- Incremental cash flow analysis

### Asset Types (Chapters 5–9)
- Intellectual property: patent, trademark, copyright, trade secret
- Technology: developed technology, software, data assets, platforms
- Customer-related: customer relationships, distribution network, non-compete
- Human capital: assembled workforce, key person

### Advanced Topics (Chapters 10–18)
- Goodwill calculation and PPA waterfall (ASC 805 / IFRS 3)
- Impairment testing (ASC 350 / IAS 36)
- Royalty analysis: benchmarking, 25% rule, adjustment
- Transfer pricing: CUP method
- Litigation damages: lost profits, pre-judgment interest
- Monte Carlo simulation and sensitivity analysis
- Decision tree analysis with backward induction
