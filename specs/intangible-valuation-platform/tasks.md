# Task List: Intangible Asset Valuation Platform

## Plan Reference
Implements: `specs/intangible-valuation-platform/plan.md`

## Tasks

### Setup

- [ ] **TASK-001** [S] Set up project skeleton with pyproject.toml, uv, and directory structure
  - Creates: `pyproject.toml`, `src/__init__.py`, `tests/__init__.py`, `mcp_server/__init__.py`, `.gitignore`
  - Depends on: none

- [ ] **TASK-002** [S] [P] Write tests for project setup and import validation
  - Tests: All modules can be imported without errors
  - Depends on: TASK-001

- [ ] **TASK-003** [S] [P] Write tests for Pydantic schema validation (all input/output models)
  - Tests: AC-E1 (validation errors for all invalid inputs)
  - Depends on: TASK-001

- [ ] **TASK-004** [S] Implement Pydantic schemas (ValuationResult, CashFlowStream, DiscountRateInput, etc.)
  - Contract: `contracts/core-api.md`, `data-model.md`
  - Depends on: TASK-001

### Core Math Module (Chapter 2, Appendix A)

- [ ] **TASK-005** [M] [P] Write tests for time value of money functions
  - Tests: AC-1 (present_value, future_value, annuity_pv, perpetuity_pv, growing_annuity_pv)
  - Depends on: TASK-001

- [ ] **TASK-006** [M] Implement time value of money functions
  - Contract: `contracts/core-api.md`
  - Depends on: TASK-005
  - Creates: `src/core/time_value.py`

- [ ] **TASK-007** [M] [P] Write tests for discount rate functions
  - Tests: AC-2, AC-3, AC-4, AC-5, AC-36, AC-37
  - Depends on: TASK-001

- [ ] **TASK-008** [M] Implement discount rate functions
  - Contract: `contracts/core-api.md`
  - Depends on: TASK-007
  - Creates: `src/core/discount_rates.py`

- [ ] **TASK-009** [M] [P] Write tests for statistical functions
  - Tests: AC-6, AC-7
  - Depends on: TASK-001

- [ ] **TASK-010** [M] Implement statistical functions (Monte Carlo, decision tree)
  - Contract: `contracts/core-api.md`, `contracts/advanced-api.md`
  - Depends on: TASK-009
  - Creates: `src/core/statistics.py`

- [ ] **TASK-011** [S] [P] Write tests for utility functions (terminal value, sensitivity, useful life)
  - Tests: AC-38, AC-39, AC-41
  - Depends on: TASK-001

- [ ] **TASK-012** [S] Implement utility functions
  - Contract: `contracts/core-api.md`
  - Depends on: TASK-011
  - Creates: `src/utils/formulas.py`

### Valuation Approaches (Chapter 3)

- [ ] **TASK-013** [M] [P] Write tests for cost approach functions
  - Tests: AC-8, AC-9
  - Depends on: TASK-006 (uses time_value functions)

- [ ] **TASK-014** [M] Implement cost approach functions
  - Contract: `contracts/approaches-api.md`
  - Depends on: TASK-013
  - Creates: `src/approaches/cost_approach.py`

- [ ] **TASK-015** [M] [P] Write tests for market approach functions
  - Tests: AC-10, AC-11
  - Depends on: TASK-006 (uses time_value functions)

- [ ] **TASK-016** [M] Implement market approach functions
  - Contract: `contracts/approaches-api.md`
  - Depends on: TASK-015
  - Creates: `src/approaches/market_approach.py`

### Income Methods (Chapter 4)

- [ ] **TASK-017** [M] [P] Write tests for relief-from-royalty method
  - Tests: AC-12
  - Depends on: TASK-006 (uses time_value functions)

- [ ] **TASK-018** [M] Implement relief-from-royalty method
  - Contract: `contracts/income-api.md`
  - Depends on: TASK-017
  - Creates: `src/income_methods/relief_from_royalty.py`

- [ ] **TASK-019** [M] [P] Write tests for excess earnings methods (MPEEM + SPEEM)
  - Tests: AC-13, AC-14, AC-40
  - Depends on: TASK-006 (uses time_value functions)

- [ ] **TASK-020** [M] Implement excess earnings methods
  - Contract: `contracts/income-api.md`
  - Depends on: TASK-019
  - Creates: `src/income_methods/excess_earnings.py`

- [ ] **TASK-021** [M] [P] Write tests for incremental cash flow method
  - Tests: AC-15
  - Depends on: TASK-006 (uses time_value functions)

- [ ] **TASK-022** [M] Implement incremental cash flow method
  - Contract: `contracts/income-api.md`
  - Depends on: TASK-021
  - Creates: `src/income_methods/incremental_cashflow.py`

### Asset Types (Chapters 5-9)

- [ ] **TASK-023** [M] [P] Write tests for IP valuation functions
  - Tests: AC-16, AC-18, AC-19
  - Depends on: TASK-018 (uses relief_from_royalty)

- [ ] **TASK-024** [M] Implement IP valuation functions (patent, copyright, trade secret)
  - Contract: `contracts/asset-types-api.md`
  - Depends on: TASK-023
  - Creates: `src/asset_types/ip_valuation.py`

- [ ] **TASK-025** [M] [P] Write tests for brand valuation function
  - Tests: AC-17
  - Depends on: TASK-018 (uses relief_from_royalty)

- [ ] **TASK-026** [M] Implement brand valuation function
  - Contract: `contracts/asset-types-api.md`
  - Depends on: TASK-025
  - Creates: `src/asset_types/brand_valuation.py`

- [ ] **TASK-027** [M] [P] Write tests for technology valuation functions
  - Tests: AC-23, AC-24, AC-25, AC-26
  - Depends on: TASK-014, TASK-018 (uses cost and income approaches)

- [ ] **TASK-028** [M] Implement technology valuation functions
  - Contract: `contracts/asset-types-api.md`
  - Depends on: TASK-027
  - Creates: `src/asset_types/technology_valuation.py`

- [ ] **TASK-029** [M] [P] Write tests for customer valuation functions
  - Tests: AC-27, AC-28, AC-29
  - Depends on: TASK-020 (uses excess_earnings)

- [ ] **TASK-030** [M] Implement customer valuation functions
  - Contract: `contracts/asset-types-api.md`
  - Depends on: TASK-029
  - Creates: `src/asset_types/customer_valuation.py`

- [ ] **TASK-031** [M] [P] Write tests for human capital functions
  - Tests: AC-30, AC-31
  - Depends on: TASK-014 (uses cost_approach)

- [ ] **TASK-032** [M] Implement human capital functions
  - Contract: `contracts/asset-types-api.md`
  - Depends on: TASK-031
  - Creates: `src/asset_types/human_capital.py`

### Advanced Calculations (Chapters 10, 15-17)

- [ ] **TASK-033** [M] [P] Write tests for goodwill and PPA functions
  - Tests: AC-32, AC-33
  - Depends on: TASK-001

- [ ] **TASK-034** [M] Implement goodwill and PPA functions
  - Contract: `contracts/advanced-api.md`
  - Depends on: TASK-033
  - Creates: `src/advanced/goodwill.py`, `src/advanced/purchase_price_alloc.py`

- [ ] **TASK-035** [M] [P] Write tests for impairment testing functions
  - Tests: AC-34, AC-35
  - Depends on: TASK-001

- [ ] **TASK-036** [M] Implement impairment testing functions
  - Contract: `contracts/advanced-api.md`
  - Depends on: TASK-035
  - Creates: `src/advanced/impairment_testing.py`

- [ ] **TASK-037** [M] [P] Write tests for royalty benchmark functions
  - Tests: AC-20, AC-21, AC-22
  - Depends on: TASK-001

- [ ] **TASK-038** [M] Implement royalty benchmark functions
  - Contract: `contracts/advanced-api.md`
  - Depends on: TASK-037
  - Creates: `src/advanced/royalty_benchmark.py`

- [ ] **TASK-039** [M] [P] Write tests for transfer pricing functions
  - Tests: AC-42, AC-43
  - Depends on: TASK-008 (uses discount_rates)

- [ ] **TASK-040** [M] Implement transfer pricing functions
  - Contract: `contracts/advanced-api.md`
  - Depends on: TASK-039
  - Creates: `src/advanced/transfer_pricing.py`

- [ ] **TASK-041** [M] [P] Write tests for litigation/damages functions
  - Tests: AC-44
  - Depends on: TASK-006 (uses time_value functions)

- [ ] **TASK-042** [M] Implement litigation/damages functions
  - Contract: `contracts/advanced-api.md`
  - Depends on: TASK-041
  - Creates: `src/advanced/litigation.py`

### Book Example Tests

- [ ] **TASK-043** [L] Write and verify all book example tests
  - Tests: All chapter exercises and examples from the book
  - Depends on: TASK-006, TASK-008, TASK-014, TASK-016, TASK-018, TASK-020, TASK-022, TASK-024, TASK-026, TASK-028, TASK-030, TASK-032, TASK-034, TASK-036, TASK-038, TASK-040, TASK-042
  - Creates: `tests/test_book_examples/`

### MCP Server

- [ ] **TASK-044** [M] [P] Write tests for MCP server and tool definitions
  - Tests: AC-45, AC-46, AC-E4
  - Depends on: TASK-001

- [ ] **TASK-045** [L] Implement MCP server with all tool registrations
  - Contract: `contracts/mcp-api.md`
  - Depends on: TASK-044, all TASK-006 through TASK-042
  - Creates: `mcp_server/server.py`, `mcp_server/tools.py`

- [ ] **TASK-046** [S] Create MCP configuration and documentation
  - Creates: `mcp.json`, README MCP section
  - Depends on: TASK-045

### AI-Agent Skills

- [ ] **TASK-047** [M] [P] Create valuation-calculator skill
  - Tests: AC-47
  - Depends on: TASK-046
  - Creates: `skills/valuation-calculator/SKILL.md`

- [ ] **TASK-048** [M] [P] Create ppa-workflow skill
  - Tests: AC-48
  - Depends on: TASK-046
  - Creates: `skills/ppa-workflow/SKILL.md`

- [ ] **TASK-049** [M] [P] Create impairment-checker skill
  - Tests: AC-49
  - Depends on: TASK-046
  - Creates: `skills/impairment-checker/SKILL.md`

### Documentation and Publishing

- [ ] **TASK-050** [M] Set up MkDocs documentation with auto-generated API docs
  - Creates: `docs/`, `mkdocs.yml`
  - Depends on: All implementation tasks

- [ ] **TASK-051** [M] Configure GitHub Actions CI/CD pipeline
  - Creates: `.github/workflows/ci.yml`, `.github/workflows/publish.yml`
  - Depends on: TASK-043

- [ ] **TASK-052** [S] Create README with installation, usage, and MCP configuration examples
  - Creates: `README.md`
  - Depends on: TASK-046, TASK-047, TASK-048, TASK-049

- [ ] **TASK-053** [S] Set up GitHub Pages for documentation site
  - Depends on: TASK-050, TASK-051

### Integration

- [ ] **TASK-054** [L] Full integration test: end-to-end PPA workflow via MCP
  - Tests: Complete PPA from deal input to goodwill calculation
  - Depends on: TASK-043, TASK-045, TASK-048

- [ ] **TASK-055** [M] Full integration test: impairment testing workflow via MCP
  - Tests: Complete impairment test from asset identification to impairment amount
  - Depends on: TASK-043, TASK-045, TASK-049

## Legend

- `[S]` Small — under 1 hour
- `[M]` Medium — 1–3 hours
- `[L]` Large — 3–6 hours (consider splitting)
- `[P]` Parallelizable — can run concurrently with other `[P]` tasks at same level

## Dependency Graph Summary

```
TASK-001 (setup)
├── TASK-002, TASK-003, TASK-004 (schemas/tests)
├── TASK-005 → TASK-006 (time_value)
├── TASK-007 → TASK-008 (discount_rates)
├── TASK-009 → TASK-010 (statistics)
├── TASK-011 → TASK-012 (formulas)
│
├── TASK-013 → TASK-014 (cost_approach) ← depends on TASK-006
├── TASK-015 → TASK-016 (market_approach) ← depends on TASK-006
│
├── TASK-017 → TASK-018 (relief_from_royalty) ← depends on TASK-006
├── TASK-019 → TASK-020 (excess_earnings) ← depends on TASK-006
├── TASK-021 → TASK-022 (incremental_cashflow) ← depends on TASK-006
│
├── TASK-023 → TASK-024 (ip_valuation) ← depends on TASK-018
├── TASK-025 → TASK-026 (brand_valuation) ← depends on TASK-018
├── TASK-027 → TASK-028 (technology_valuation) ← depends on TASK-014, TASK-018
├── TASK-029 → TASK-030 (customer_valuation) ← depends on TASK-020
├── TASK-031 → TASK-032 (human_capital) ← depends on TASK-014
│
├── TASK-033 → TASK-034 (goodwill/ppa)
├── TASK-035 → TASK-036 (impairment)
├── TASK-037 → TASK-038 (royalty_benchmark)
├── TASK-039 → TASK-040 (transfer_pricing) ← depends on TASK-008
├── TASK-041 → TASK-042 (litigation) ← depends on TASK-006
│
├── TASK-043 (book examples) ← depends on ALL above
│
├── TASK-044 → TASK-045 (MCP server) ← depends on ALL calculation tasks
│   └── TASK-046 (MCP config)
│       ├── TASK-047, TASK-048, TASK-049 (skills)
│       └── TASK-052 (README)
│
├── TASK-050 (docs) ← depends on ALL
├── TASK-051 (CI/CD) ← depends on TASK-043
├── TASK-053 (GitHub Pages) ← depends on TASK-050, TASK-051
│
└── TASK-054, TASK-055 (integration tests) ← depends on TASK-043, TASK-045, skills
```
