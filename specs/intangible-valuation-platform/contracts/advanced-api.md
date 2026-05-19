# API Contract: Advanced Calculations

## Goodwill and PPA API

### purchase_price_allocation(purchase_price, tangible_assets_fv, identified_intangibles, liabilities_fv)

**Description:** Full purchase price allocation waterfall (Section 10.2, Appendix A.8)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| purchase_price | float | yes | - | Total acquisition price (> 0) |
| tangible_assets_fv | float | yes | - | Fair value of tangible assets (>= 0) |
| identified_intangibles | list[dict] | yes | - | Each: {"name": str, "value": float, "method": str} |
| liabilities_fv | float | no | 0 | Fair value of assumed liabilities (>= 0) |

**Response (200 OK):**
```json
{
  "value": 25000000,
  "method": "Purchase Price Allocation",
  "formula_reference": "Ch 10.2, Appendix A.8",
  "steps": [
    {"item": "Purchase Price", "value": 100000000},
    {"item": "Tangible Assets", "value": 15000000},
    {"item": "Identified Intangibles", "value": 60000000},
    {"item": "Liabilities", "value": 0},
    {"item": "Net Identifiable Assets", "value": 75000000},
    {"item": "Goodwill (residual)", "value": 25000000}
  ],
  "assumptions": {"allocation": {"tangible": "15.0%", "intangible": "60.0%", "goodwill": "25.0%"}}
}
```

---

### goodwill(purchase_price, fair_value_net_identifiable_assets)

**Description:** Calculate goodwill as residual (Section 10.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| purchase_price | float | yes | - | Purchase price (> 0) |
| fair_value_net_identifiable_assets | float | yes | - | FV of net identifiable assets (>= 0) |

**Error Codes:**
| Status | Code | When |
|--------|------|------|
| 400 | NEGATIVE_GOODWILL | purchase_price < fair_value_net_identifiable_assets (bargain purchase) |

---

### goodwill_impairment_test(carrying_value, fair_value, reporting_unit, standard)

**Description:** Goodwill impairment test per ASC 350 or IAS 36 (Section 10.4, A.9)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| carrying_value | float | yes | - | Reporting unit carrying value (> 0) |
| fair_value | float | yes | - | Reporting unit fair value (>= 0) |
| reporting_unit | str | no | "" | Reporting unit name |
| standard | str | no | "ASC350" | "ASC350" or "IAS36" |

---

### intangible_impairment_test(carrying_value, fair_value, recoverable_amount, standard)

**Description:** Intangible asset impairment test (Section 10.4, A.9)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| carrying_value | float | yes | - | Asset carrying value (> 0) |
| fair_value | float | conditional | - | Fair value (>= 0), required for ASC350 |
| recoverable_amount | float | conditional | - | Higher of FV less costs to sell and value in use, required for IAS36 |
| standard | str | no | "ASC350" | "ASC350" or "IAS36" |

---

## Royalty Benchmark API

### royalty_rate_benchmark(ip_type, industry, comparable_database)

**Description:** Benchmark royalty rates by IP type and industry (Section 6.2, A.10)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| ip_type | str | yes | - | "patent", "trademark", "copyright", "trade_secret", "technology" |
| industry | str | yes | - | Industry sector name |
| comparable_database | list[dict] | no | [] | User-provided comparable rates |

---

### adjust_royalty_rate(base_rate, adjustment_factors)

**Description:** Adjust base royalty rate for specific factors (Section 6.3, A.10)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| base_rate | float | yes | - | Base royalty rate (> 0, <= 1) |
| adjustment_factors | dict | yes | - | {"profit_margin": float, "exclusivity": float, "market_conditions": float, ...} |

---

### twenty_five_percent_rule(licensee_expected_profit, profit_attribution_to_ip)

**Description:** 25% rule of thumb for royalty rate estimation (Section 6.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| licensee_expected_profit | float | yes | - | Licensee's expected profit from IP (> 0) |
| profit_attribution_to_ip | float | no | 1.0 | Fraction of profit attributable to IP (0-1) |

---

## Transfer Pricing API

### currency_adjusted_discount_rate(base_rate, currency_risk_premium, country_risk_premium)

**Description:** Adjust discount rate for currency and country risk (Section 16.3)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| base_rate | float | yes | - | Base discount rate (> 0, <= 1) |
| currency_risk_premium | float | yes | - | Currency risk premium (>= 0) |
| country_risk_premium | float | yes | - | Country risk premium (>= 0) |

---

### cup_transfer_price(controlled_price, uncontrolled_prices)

**Description:** Arm's length price using Comparable Uncontrolled Price method (Section 16.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| controlled_price | float | yes | - | Price in controlled transaction (> 0) |
| uncontrolled_prices | list[float] | yes | - | Prices from comparable uncontrolled transactions (> 0 each) |

---

## Litigation API

### patent_infringement_damages(lost_profits_or_royalty, infringement_period, discount_rate, prejudgment_interest_rate)

**Description:** Calculate patent infringement damages with pre-judgment interest (Section 15.2)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| lost_profits_or_royalty | float | yes | - | Annual lost profits or reasonable royalty (> 0) |
| infringement_period | int | yes | - | Duration of infringement in years (> 0) |
| discount_rate | float | yes | - | Discount rate for present value (> 0, <= 1) |
| prejudgment_interest_rate | float | yes | - | Pre-judgment interest rate (>= 0, <= 1) |

---

## Monte Carlo API

### monte_carlo_valuation(valuation_function, input_variables, iterations, seed)

**Description:** Monte Carlo simulation for valuation under uncertainty (Section 2.4)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| valuation_function | str | yes | - | Name of valuation function to simulate |
| input_variables | list[dict] | yes | - | Each: {"name": str, "distribution": str, "params": dict} |
| iterations | int | no | 10000 | Number of iterations (>= 1000, <= 100000) |
| seed | int | no | null | Random seed for reproducibility |

---

## Decision Tree API

### decision_tree_valuation(tree)

**Description:** Decision tree analysis with expected value calculation (Section 2.4)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tree | dict | yes | - | Tree structure: {"nodes": [...], "edges": [...]} |

---

## Sensitivity Analysis API

### sensitivity_analysis(function_name, parameter_name, parameter_range, fixed_parameters)

**Description:** Sensitivity analysis across parameter range (Appendix A.15)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| function_name | str | yes | - | Name of valuation function |
| parameter_name | str | yes | - | Parameter to vary |
| parameter_range | list[float] | yes | - | Values to test |
| fixed_parameters | dict | yes | - | Fixed parameters for all runs |

---

## AC Coverage
- AC-20: royalty_rate_benchmark
- AC-21: adjust_royalty_rate
- AC-22: twenty_five_percent_rule
- AC-32: purchase_price_allocation
- AC-33: goodwill
- AC-34: goodwill_impairment_test
- AC-35: intangible_impairment_test
- AC-42: currency_adjusted_discount_rate
- AC-43: cup_transfer_price
- AC-44: patent_infringement_damages
- AC-6: monte_carlo_valuation
- AC-7: decision_tree_valuation
- AC-41: sensitivity_analysis
