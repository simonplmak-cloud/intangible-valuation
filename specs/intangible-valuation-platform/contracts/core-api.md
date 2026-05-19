# API Contract: Core Math Functions

## Core Math API

All functions return `ValuationResult` objects with fields: `value`, `method`, `formula_reference`, `steps`, `assumptions`.

### present_value(future_value, discount_rate, periods)

**Description:** Calculate present value of a single future cash flow (Section 2.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| future_value | float | yes | - | Future cash flow amount (> 0) |
| discount_rate | float | yes | - | Discount rate as decimal (> 0, <= 1) |
| periods | int | yes | - | Number of periods (> 0) |

**Response (200 OK):**
```json
{
  "value": 360478.02,
  "method": "Present Value",
  "formula_reference": "Ch 2.1, Appendix A.1",
  "steps": [
    {"step": 1, "description": "Apply PV = FV / (1 + r)^n", "calculation": "100000 / (1 + 0.12)^5"},
    {"step": 2, "description": "Calculate denominator", "value": 1.76234},
    {"step": 3, "description": "Final PV", "value": 360478.02}
  ],
  "assumptions": {"future_value": 100000, "discount_rate": 0.12, "periods": 5}
}
```

**Error Codes:**
| Status | Code | When |
|--------|------|------|
| 400 | VALIDATION_ERROR | future_value <= 0 |
| 400 | VALIDATION_ERROR | discount_rate <= 0 or > 1 |
| 400 | VALIDATION_ERROR | periods <= 0 |

---

### future_value(present_value, discount_rate, periods)

**Description:** Calculate future value of a present amount (Section 2.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| present_value | float | yes | - | Present amount (> 0) |
| discount_rate | float | yes | - | Discount rate as decimal (> 0, <= 1) |
| periods | int | yes | - | Number of periods (> 0) |

**Response (200 OK):** `{"value": ..., "method": "Future Value", "formula_reference": "Ch 2.1, Appendix A.1", ...}`

---

### annuity_pv(payment, discount_rate, periods)

**Description:** Calculate present value of an ordinary annuity (Section 2.1, A.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| payment | float | yes | - | Periodic payment amount (> 0) |
| discount_rate | float | yes | - | Discount rate as decimal (> 0, <= 1) |
| periods | int | yes | - | Number of periods (> 0) |

**Response (200 OK):** `{"value": ..., "method": "Annuity PV", "formula_reference": "Ch 2.1, Appendix A.1", ...}`

---

### perpetuity_pv(payment, discount_rate)

**Description:** Calculate present value of a perpetuity (A.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| payment | float | yes | - | Periodic payment amount (> 0) |
| discount_rate | float | yes | - | Discount rate as decimal (> 0, <= 1) |

**Error Codes:**
| Status | Code | When |
|--------|------|------|
| 400 | DIVISION_BY_ZERO | discount_rate == 0 |

---

### growing_annuity_pv(payment, discount_rate, growth_rate, periods)

**Description:** Calculate present value of a growing annuity (A.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| payment | float | yes | - | First period payment (> 0) |
| discount_rate | float | yes | - | Discount rate as decimal (> 0, <= 1) |
| growth_rate | float | yes | - | Growth rate as decimal (>= 0, < 1) |
| periods | int | yes | - | Number of periods (> 0) |

---

### build_up_discount_rate(risk_free_rate, equity_risk_premium, size_premium, industry_risk_premium, specific_risk_premium)

**Description:** Construct discount rate using build-up method (Section 2.3, A.5)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| risk_free_rate | float | yes | - | Risk-free rate (>= 0, <= 1) |
| equity_risk_premium | float | yes | - | Equity risk premium (>= 0) |
| size_premium | float | no | 0 | Size premium (>= 0) |
| industry_risk_premium | float | no | 0 | Industry risk premium (>= 0) |
| specific_risk_premium | float | no | 0 | Specific asset risk premium (>= 0) |

**Response (200 OK):**
```json
{
  "value": 0.18,
  "method": "Build-Up Discount Rate",
  "formula_reference": "Ch 2.3, Appendix A.5",
  "steps": [
    {"component": "Risk-Free Rate", "value": 0.04},
    {"component": "Equity Risk Premium", "value": 0.06},
    {"component": "Size Premium", "value": 0.03},
    {"component": "Industry Risk Premium", "value": 0.03},
    {"component": "Specific Risk Premium", "value": 0.02},
    {"component": "Total", "value": 0.18}
  ],
  "assumptions": {}
}
```

---

### capm_discount_rate(risk_free_rate, beta, market_return)

**Description:** Calculate discount rate using CAPM (A.5)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| risk_free_rate | float | yes | - | Risk-free rate (>= 0, <= 1) |
| beta | float | yes | - | Asset beta (> 0) |
| market_return | float | yes | - | Expected market return (> 0, <= 1) |

---

### wacc(equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate)

**Description:** Calculate weighted average cost of capital (A.5)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| equity_value | float | yes | - | Market value of equity (> 0) |
| debt_value | float | yes | - | Market value of debt (>= 0) |
| cost_of_equity | float | yes | - | Cost of equity (> 0, <= 1) |
| cost_of_debt | float | yes | - | Cost of debt (> 0, <= 1) |
| tax_rate | float | yes | - | Corporate tax rate (>= 0, <= 1) |

---

### tax_amortization_benefit(discount_rate, useful_life, tax_rate, asset_value)

**Description:** Calculate present value of tax amortization benefit (Appendix A.7)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| useful_life | int | yes | - | Amortization period in years (> 0) |
| tax_rate | float | yes | - | Tax rate (>= 0, <= 1) |
| asset_value | float | yes | - | Asset value for amortization base (> 0) |

---

### terminal_value(final_year_cashflow, perpetual_growth_rate, discount_rate, method)

**Description:** Calculate terminal value using Gordon Growth or Exit Multiple (Appendix A.12)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| final_year_cashflow | float | yes | - | Cash flow in final projection year (> 0) |
| perpetual_growth_rate | float | yes | - | Perpetual growth rate (>= 0, < discount_rate) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| method | str | no | "gordon_growth" | "gordon_growth" or "exit_multiple" |
| exit_multiple | float | conditional | - | Required if method="exit_multiple" (> 0) |

**Error Codes:**
| Status | Code | When |
|--------|------|------|
| 400 | VALIDATION_ERROR | perpetual_growth_rate >= discount_rate |
| 400 | VALIDATION_ERROR | method="exit_multiple" but exit_multiple not provided |

---

### AC Coverage
- AC-1: present_value, future_value, annuity_pv, perpetuity_pv, growing_annuity_pv
- AC-2: build_up_discount_rate
- AC-3: capm_discount_rate
- AC-4: wacc
- AC-5: tax_amortization_benefit
- AC-36: control_premium (in discount_rates.py)
- AC-37: dlom (in discount_rates.py)
- AC-38: terminal_value
- AC-39: estimate_useful_life (in utils/formulas.py)
- AC-41: sensitivity_analysis (in utils/formulas.py)
