# Impairment Testing Skill

## When to Use

Use this skill when a user asks to:
- Test goodwill for impairment
- Test intangible assets for impairment
- Perform annual impairment testing
- Assess whether an asset's carrying value exceeds its fair value
- Compare ASC 350 vs IAS 36 impairment methodologies
- Determine impairment loss amount for financial reporting

## ASC 350 vs IAS 36 Methodology Selection

| Feature | ASC 350 (US GAAP) | IAS 36 (IFRS) |
|---|---|---|
| **Goodwill Test** | One-step: Compare reporting unit FV to carrying value | Compare CGU carrying value to recoverable amount |
| **Recoverable Amount** | Not applicable | Higher of (FV less costs to sell, value in use) |
| **Intangible (indefinite)** | Compare FV to carrying value | Compare recoverable amount to carrying value |
| **Intangible (finite-lived)** | Test only if triggering events occur | Test only if triggering events occur |
| **Impairment Reversal** | Not permitted | Permitted for assets other than goodwill |
| **Reporting Unit** | Operating segment or one level below | Cash-Generating Unit (CGU) |
| **Frequency** | Annual (or when triggering events) | Annual (or when triggering events) |

### When to Use Each Standard
- **ASC 350**: US GAAP reporting entities, SEC filers, US subsidiaries
- **IAS 36**: IFRS reporting entities, non-US companies, international subsidiaries

## Step-by-Step Impairment Testing

### Step 1: Identify the Asset or Reporting Unit
Determine what is being tested:
- **Goodwill** — identify the reporting unit (ASC 350) or CGU (IAS 36)
- **Indefinite-lived intangible** — identify the specific asset (trademark, brand)
- **Finite-lived intangible** — only test if triggering events exist

**Triggering Events:**
- Significant decline in market capitalization
- Loss of key customers or contracts
- Adverse regulatory changes
- Technological obsolescence
- Significant increase in competition
- Deterioration in financial performance
- Change in business strategy

### Step 2: Gather Carrying Value
Collect the current book value:
- **Goodwill**: Carrying value of the reporting unit including allocated goodwill
- **Intangible asset**: Net book value (cost less accumulated amortization)

MCP Tool: None (obtain from accounting records)

### Step 3: Estimate Fair Value
Determine the fair value of the asset or reporting unit using:
- Market approach (comparable companies, precedent transactions)
- Income approach (DCF, relief from royalty, MPEEM)
- Cost approach (replacement cost)

MCP Tools for fair value estimation:
- `market_approach_comparables` — for market-based FV
- `relief_from_royalty` — for income-based FV of IP assets
- `mpeem` — for income-based FV of primary intangibles
- `royalty_capitalization` — for mature, stable assets
- `discounted_cashflow` — use `present_value_of_series` from core

### Step 4: Run Impairment Test

**For Goodwill:**
```
goodwill_impairment_test(
    carrying_value=<reporting_unit_cv>,
    fair_value=<reporting_unit_fv>,
    reporting_unit="<name>",
    standard="ASC350"  # or "IAS36"
)
```

**For Intangible Asset (ASC 350):**
```
intangible_impairment_test(
    carrying_value=<asset_cv>,
    fair_value=<asset_fv>,
    standard="ASC350"
)
```

**For Intangible Asset (IAS 36):**
```
intangible_impairment_test(
    carrying_value=<asset_cv>,
    recoverable_amount=<recoverable_amount>,
    standard="IAS36"
)
```

### Step 5: Report Results
The tool returns:
- `value` — impairment loss amount (0 if no impairment)
- `method` — test methodology
- `formula_reference` — standard reference
- `steps` — calculation breakdown
- `assumptions` — includes `impaired` boolean flag

Report format:
1. State the asset/reporting unit tested
2. State the accounting standard applied
3. Present carrying value vs fair value/recoverable amount
4. State whether impairment exists
5. If impaired, state the impairment loss amount
6. Note any required disclosures

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `goodwill_impairment_test` | Goodwill impairment per ASC 350 or IAS 36 |
| `intangible_impairment_test` | Intangible asset impairment per ASC 350 or IAS 36 |
| `market_approach_comparables` | Estimate fair value via market comparables |
| `relief_from_royalty` | Estimate fair value via income approach |
| `mpeem` | Estimate fair value for primary intangibles |
| `build_up_discount_rate` | Construct discount rate for DCF |
| `capm_discount_rate` | CAPM-based discount rate |

## Example Impairment Scenario

### Scenario: Goodwill Impairment Test

**Context:** Tech Division reporting unit has carrying value of $50M (including $15M goodwill). Recent market conditions suggest fair value may be $40M.

**Step 1:** Identify — Goodwill impairment test for "Tech Division" reporting unit
**Step 2:** Carrying value = $50,000,000
**Step 3:** Fair value = $40,000,000 (estimated via DCF and market comparables)
**Step 4:** Run test:

```
goodwill_impairment_test(
    carrying_value=50000000,
    fair_value=40000000,
    reporting_unit="Tech Division",
    standard="ASC350"
)
```

**Result:** Impairment loss of $10,000,000. The reporting unit is impaired.

### Scenario: Trademark Impairment Test (IAS 36)

**Context:** A brand acquired in a PPA has carrying value of $20M. Due to reputational damage, recoverable amount is estimated at $15M.

**Step 1:** Identify — Indefinite-lived intangible (trademark)
**Step 2:** Carrying value = $20,000,000
**Step 3:** Recoverable amount = $15,000,000 (higher of FV less costs to sell and value in use)
**Step 4:** Run test:

```
intangible_impairment_test(
    carrying_value=20000000,
    recoverable_amount=15000000,
    standard="IAS36"
)
```

**Result:** Impairment loss of $5,000,000. Under IAS 36, this impairment could be reversed in future periods if conditions improve (unlike ASC 350).

### Scenario: No Impairment

**Context:** Patent carrying value $8M, fair value estimated at $12M.

```
intangible_impairment_test(
    carrying_value=8000000,
    fair_value=12000000,
    standard="ASC350"
)
```

**Result:** No impairment (fair value exceeds carrying value). Impairment loss = $0.
