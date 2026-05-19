# API Contract: Asset Type Valuations

## Intellectual Property API

### patent_valuation(remaining_life, cash_flow_projections, probability_of_success, discount_rate, comparable_license_rates)

**Description:** Risk-adjusted patent valuation with probability-weighted scenarios (Section 5.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| remaining_life | int | yes | - | Remaining patent life in years (> 0) |
| cash_flow_projections | list[float] | yes | - | Projected annual cash flows (> 0 each) |
| probability_of_success | float | yes | - | Probability of patent validity/enforcement (> 0, <= 1) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| comparable_license_rates | list[float] | no | [] | Comparable license rates for cross-check |

---

### trademark_valuation(revenue, profit_margin, brand_strength_index, discount_rate, useful_life, method)

**Description:** Brand/trademark valuation using relief-from-royalty or excess earnings (Section 5.2)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| revenue | float | yes | - | Brand-attributable revenue (> 0) |
| profit_margin | float | yes | - | Brand-specific profit margin (> 0, <= 1) |
| brand_strength_index | float | yes | - | Brand strength score (0-100) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| useful_life | int | yes | - | Brand useful life (> 0) |
| method | str | no | "relief_from_royalty" | "relief_from_royalty" or "excess_earnings" |

---

### copyright_valuation(projected_revenue, useful_life, discount_rate, royalty_rate)

**Description:** Copyright valuation based on expected licensing income (Section 5.3)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| projected_revenue | list[float] | yes | - | Annual revenue from copyrighted work (> 0 each) |
| useful_life | int | yes | - | Remaining copyright life (> 0) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| royalty_rate | float | yes | - | Applicable royalty rate (> 0, <= 1) |

---

### trade_secret_valuation(development_cost, economic_life, competitive_advantage_period, discount_rate, secrecy_probability)

**Description:** Trade secret value incorporating secrecy risk (Section 5.4)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| development_cost | float | yes | - | Cost to develop the secret (> 0) |
| economic_life | int | yes | - | Expected economic life (> 0) |
| competitive_advantage_period | int | yes | - | Period of competitive advantage (> 0) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| secrecy_probability | float | yes | - | Probability of maintaining secrecy per year (> 0, <= 1) |

---

## Technology API

### developed_technology_valuation(rd_costs, life_cycle_stage, competitive_advantage, discount_rate, cash_flow_projections)

**Description:** Developed technology valuation (Section 7.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| rd_costs | float | yes | - | Total R&D investment (> 0) |
| life_cycle_stage | str | yes | - | "emerging", "growth", "mature", or "decline" |
| competitive_advantage | int | yes | - | Years of competitive advantage (> 0) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| cash_flow_projections | list[float] | yes | - | Projected cash flows (> 0 each) |

---

### software_valuation(development_cost, maintenance_cost, user_base, revenue_model, useful_life, discount_rate)

**Description:** Software valuation combining cost and income approaches (Section 7.2)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| development_cost | float | yes | - | Total development cost (> 0) |
| maintenance_cost | float | yes | - | Annual maintenance cost (>= 0) |
| user_base | int | yes | - | Number of active users (> 0) |
| revenue_model | dict | yes | - | {"type": str, "revenue_per_user": float} |
| useful_life | int | yes | - | Software useful life (> 0) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |

---

### data_asset_valuation(acquisition_cost, quality_score, revenue_contribution, useful_life, discount_rate)

**Description:** Data asset valuation with quality adjustments (Section 7.3)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| acquisition_cost | float | yes | - | Cost to acquire/build data (> 0) |
| quality_score | float | yes | - | Data quality score (0-1) |
| revenue_contribution | list[float] | yes | - | Annual revenue attributed to data (> 0 each) |
| useful_life | int | yes | - | Data useful life (> 0) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |

---

### platform_valuation(network_size, network_effects_coefficient, revenue_per_user, growth_rate, discount_rate)

**Description:** Platform valuation with network effects (Section 7.4)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| network_size | int | yes | - | Current network users (> 0) |
| network_effects_coefficient | float | yes | - | Network effects strength (> 0, <= 1) |
| revenue_per_user | float | yes | - | Annual revenue per user (> 0) |
| growth_rate | float | yes | - | User growth rate (>= 0, <= 1) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |

---

## Customer API

### customer_relationship_valuation(customer_count, avg_revenue_per_customer, retention_rate, profit_margin, discount_rate, projection_period)

**Description:** Customer relationship valuation using multi-period excess earnings (Section 8.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| customer_count | int | yes | - | Number of customers (> 0) |
| avg_revenue_per_customer | float | yes | - | Average annual revenue per customer (> 0) |
| retention_rate | float | yes | - | Annual retention rate (> 0, <= 1) |
| profit_margin | float | yes | - | Profit margin (> 0, <= 1) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |
| projection_period | int | yes | - | Projection period in years (> 0) |

---

### distribution_network_valuation(channel_count, revenue_per_channel, channel_margin, useful_life, discount_rate)

**Description:** Distribution network valuation (Section 8.2)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| channel_count | int | yes | - | Number of distribution channels (> 0) |
| revenue_per_channel | float | yes | - | Annual revenue per channel (> 0) |
| channel_margin | float | yes | - | Channel profit margin (> 0, <= 1) |
| useful_life | int | yes | - | Network useful life (> 0) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |

---

### non_compete_valuation(protected_revenue, profit_margin, term, enforcement_probability, discount_rate)

**Description:** Non-compete agreement valuation (Section 8.4)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| protected_revenue | float | yes | - | Annual revenue protected (> 0) |
| profit_margin | float | yes | - | Profit margin on protected revenue (> 0, <= 1) |
| term | int | yes | - | Agreement term in years (> 0) |
| enforcement_probability | float | yes | - | Probability of enforcement (> 0, <= 1) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |

---

## Human Capital API

### assembled_workforce_valuation(employee_count, avg_replacement_cost, training_cost, productivity_factor, attrition_rate)

**Description:** Assembled workforce valuation (Section 9.1)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| employee_count | int | yes | - | Number of employees (> 0) |
| avg_replacement_cost | float | yes | - | Average cost to replace one employee (> 0) |
| training_cost | float | yes | - | Average training cost per employee (>= 0) |
| productivity_factor | float | yes | - | Productivity adjustment (> 0, <= 1) |
| attrition_rate | float | yes | - | Annual attrition rate (>= 0, <= 1) |

---

### key_person_value(revenue_contribution, replacement_cost, departure_probability, discount_rate)

**Description:** Key person economic value (Section 9.2)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| revenue_contribution | float | yes | - | Annual revenue attributed to key person (> 0) |
| replacement_cost | float | yes | - | Cost to find and train replacement (> 0) |
| departure_probability | float | yes | - | Annual probability of departure (> 0, <= 1) |
| discount_rate | float | yes | - | Discount rate (> 0, <= 1) |

---

## AC Coverage
- AC-16: patent_valuation
- AC-17: trademark_valuation
- AC-18: copyright_valuation
- AC-19: trade_secret_valuation
- AC-23: developed_technology_valuation
- AC-24: software_valuation
- AC-25: data_asset_valuation
- AC-26: platform_valuation
- AC-27: customer_relationship_valuation
- AC-28: distribution_network_valuation
- AC-29: non_compete_valuation
- AC-30: assembled_workforce_valuation
- AC-31: key_person_value
