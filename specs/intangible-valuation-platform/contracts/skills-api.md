# API Contract: AI-Agent Skills

## Skill: Valuation Calculator

**Name:** `valuation-calculator`
**Purpose:** Guide AI agents through any intangible asset valuation calculation
**MCP Tools Used:** All valuation tools

### Workflow

1. **Identify asset type** — Ask user what type of intangible asset they're valuing
2. **Select method** — Recommend appropriate valuation method based on asset type and available data
3. **Gather inputs** — Prompt user for required parameters with guidance on where to find them
4. **Execute calculation** — Call appropriate MCP tool(s)
5. **Present results** — Show value, methodology, assumptions, and sensitivity analysis
6. **Generate report** — Format results as a structured valuation summary

### Supported Asset Types

| Asset Type | Primary Method | Alternative Methods |
|------------|---------------|-------------------|
| Patent | Relief-from-Royalty | MPEEM, Cost Approach |
| Trademark/Brand | Relief-from-Royalty | Excess Earnings, Market Approach |
| Copyright | Relief-from-Royalty | Income Approach |
| Trade Secret | Cost Approach | Income Approach with risk adjustment |
| Software | Replacement Cost | Income Approach |
| Customer Relationships | MPEEM | Multi-period customer cash flow |
| Goodwill | Residual (PPA) | Excess Earnings |
| Workforce | Cost Approach | Replacement cost |

---

## Skill: PPA Workflow

**Name:** `ppa-workflow`
**Purpose:** Guide users through full Purchase Price Allocation process
**MCP Tools Used:** All asset valuation tools, purchase_price_allocation, goodwill

### Workflow

1. **Gather deal information** — Purchase price, target company details
2. **Identify tangible assets** — List and value all tangible assets at fair value
3. **Identify intangible assets** — Systematically identify all intangibles per IFRS 3 / ASC 805
4. **Value each intangible** — Call appropriate valuation method for each identified intangible
5. **Calculate goodwill** — Run purchase_price_allocation with all identified values
6. **Generate PPA report** — Full allocation table with percentages and methodology notes
7. **Disclosure checklist** — Verify IFRS/GAAP disclosure requirements are met

---

## Skill: Impairment Checker

**Name:** `impairment-checker`
**Purpose:** Guide users through impairment testing for goodwill and intangible assets
**MCP Tools Used:** goodwill_impairment_test, intangible_impairment_test, all valuation tools

### Workflow

1. **Identify asset/reporting unit** — What is being tested for impairment
2. **Determine standard** — ASC 350 (US GAAP) or IAS 36 (IFRS)
3. **Gather carrying values** — Current balance sheet values
4. **Estimate fair value** — Guide user through fair value estimation using valuation tools
5. **Run impairment test** — Call appropriate impairment test function
6. **Report results** — Impairment amount, new carrying value, disclosure notes

---

## AC Coverage
- AC-47: valuation-calculator skill
- AC-48: ppa-workflow skill
- AC-49: impairment-checker skill
