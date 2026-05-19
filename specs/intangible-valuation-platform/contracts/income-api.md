# API Contract: Income Methods

## Relief-from-Royalty API

### relief_from_royalty(revenue_projections, royalty_rate, discount_rate, tax_rate, useful_life, tab_enabled)

**Description:** Value asset as present value of after-tax royalty savings (Section 4.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| revenue_projections | list[float] | yes | - | Projected annual revenue (> 0 each) |
| royalty_rate | float | yes | - | Royalty rate as decimal (> 0, <= 1) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| tax_rate | float | yes | - | Tax rate (>= 0, <= 1) |
| useful_life | int | yes | - | Remaining useful life in years (> 0) |
| tab_enabled | bool | no | true | Include tax amortization benefit |

**Response (200 OK):**
```json
{
  "value": 4523891,
  "method": "Relief-from-Royalty",
  "formula_reference": "Ch 4.1",
  "steps": [
    {"period": 1, "revenue": 10000000, "royalty_payment": 400000, "after_tax_royalty": 280000, "pv": 250000},
    {"period": 2, "revenue": 11000000, "royalty_payment": 440000, "after_tax_royalty": 308000, "pv": 244000}
  ],
  "assumptions": {"tab_included": true, "tab_value": 123456}
}
```

---

## Excess Earnings API

### mpeem(cash_flow_projections, contributory_asset_charges, discount_rate, tax_rate, tab_enabled)

**Description:** Multi-Period Excess Earnings Method — present value of excess earnings after CACs (Section 4.2, A.11)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| cash_flow_projections | list[float] | yes | - | Projected annual cash flows (> 0 each) |
| contributory_asset_charges | list[dict] | yes | - | Each: {"asset_type": str, "asset_value": float, "charge_rate": float} |
| discount_rate | float | yes | - | Discount rate for subject intangible (> 0, <= 1) |
| tax_rate | float | yes | - | Tax rate (>= 0, <= 1) |
| tab_enabled | bool | no | true | Include tax amortization benefit |

**Response (200 OK):**
```json
{
  "value": 8234567,
  "method": "MPEEM",
  "formula_reference": "Ch 4.2, Appendix A.11",
  "steps": [
    {"period": 1, "cash_flow": 2000000, "total_cac": 500000, "excess_earnings": 1500000, "after_tax": 1050000, "pv": 937500},
    {"period": 2, "cash_flow": 2200000, "total_cac": 520000, "excess_earnings": 1680000, "after_tax": 1176000, "pv": 937500}
  ],
  "assumptions": {"cac_breakdown": {"working_capital": 100000, "fixed_assets": 200000, "other_intangibles": 200000}}
}
```

---

### single_period_excess_earnings(normalized_earnings, contributory_asset_charges, capitalization_rate)

**Description:** Single-period excess earnings capitalization (Section 4.2)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| normalized_earnings | float | yes | - | Normalized annual earnings (> 0) |
| contributory_asset_charges | list[dict] | yes | - | Same as MPEEM |
| capitalization_rate | float | yes | - | Cap rate (> 0, <= 1) |

---

### contributory_asset_charges(assets)

**Description:** Calculate total contributory asset charges (Appendix A.11)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| assets | list[dict] | yes | - | Each: {"type": str, "value": float, "return_rate": float} |

---

## Incremental Cash Flow API

### incremental_cashflow(cash_flows_with, cash_flows_without, discount_rate)

**Description:** Present value of incremental cash flows attributable to the asset (Section 4.3)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| cash_flows_with | list[float] | yes | - | Cash flows with the asset (> 0 each) |
| cash_flows_without | list[float] | yes | - | Cash flows without the asset (>= 0 each) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |

**Error Codes:**
| Status | Code | When |
|--------|------|------|
| 400 | VALIDATION_ERROR | cash_flows_with and cash_flows_without have different lengths |

---

## AC Coverage
- AC-12: relief_from_royalty
- AC-13: mpeem
- AC-14: single_period_excess_earnings
- AC-15: incremental_cashflow
- AC-40: contributory_asset_charges
