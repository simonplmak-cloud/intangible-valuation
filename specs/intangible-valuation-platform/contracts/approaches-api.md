# API Contract: Valuation Approaches

## Cost Approach API

### reproduction_cost(development_costs, obsolescence_factors)

**Description:** Estimate cost to create an exact replica of the intangible asset (Section 3.1, A.4)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| development_costs | dict | yes | - | {"labor": float, "materials": float, "overhead": float, ...} |
| obsolescence_factors | dict | no | {"functional": 0, "technological": 0, "economic": 0} | Obsolescence percentages (0-1) |

**Response (200 OK):**
```json
{
  "value": 390000,
  "method": "Reproduction Cost",
  "formula_reference": "Ch 3.1, Appendix A.4",
  "steps": [
    {"step": "Total Development Cost", "value": 650000},
    {"step": "Total Obsolescence", "value": 0.40},
    {"step": "Depreciated Value", "value": 390000}
  ],
  "assumptions": {"development_costs": {"labor": 500000, "materials": 100000, "overhead": 50000}}
}
```

---

### replacement_cost(current_cost, obsolescence_factors)

**Description:** Estimate cost to create asset with equivalent utility (Section 3.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| current_cost | float | yes | - | Current cost to create equivalent (> 0) |
| obsolescence_factors | dict | no | {} | Same as reproduction_cost |

---

## Market Approach API

### market_approach_comparables(comparables, subject_revenue, adjustments)

**Description:** Value asset using comparable transaction multiples (Section 3.2, A.3)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| comparables | list[dict] | yes | - | Each: {"sale_price": float, "revenue": float, "asset_type": str, ...} |
| subject_revenue | float | yes | - | Revenue of subject asset (> 0) |
| adjustments | dict | no | {} | Adjustment factors for differences |

**Response (200 OK):**
```json
{
  "value": 2666667,
  "method": "Market Approach - Comparables",
  "formula_reference": "Ch 3.2, Appendix A.3",
  "steps": [
    {"step": "Comparable Multiple Range", "value": {"min": 2.5, "max": 4.2, "median": 3.0}},
    {"step": "Selected Multiple", "value": 3.0},
    {"step": "Adjusted Multiple", "value": 2.67},
    {"step": "Valuation", "value": 2666667}
  ],
  "assumptions": {"comparables_count": 5, "selected_multiple": "median"}
}
```

---

### royalty_capitalization(revenue, royalty_rate, discount_rate)

**Description:** Capitalize royalty payments to estimate asset value (Section 3.2)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| revenue | float | yes | - | Annual revenue (> 0) |
| royalty_rate | float | yes | - | Royalty rate as decimal (> 0, <= 1) |
| discount_rate | float | yes | - | Capitalization rate (> 0, <= 1) |

**Error Codes:**
| Status | Code | When |
|--------|------|------|
| 400 | DIVISION_BY_ZERO | discount_rate == 0 |

---

## AC Coverage
- AC-8: reproduction_cost
- AC-9: replacement_cost
- AC-10: market_approach_comparables
- AC-11: royalty_capitalization
