# Data Model: Intangible Asset Valuation Platform

## Spec Reference
Implements: `specs/intangible-valuation-platform/spec.md`

## Schema Entities (Pydantic Models)

This project has no database. All "data models" are Pydantic schemas for input validation and output serialization.

### CashFlowStream
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| periods | list[int] | min 1 period | Time periods (e.g., [1, 2, 3, 4, 5]) |
| amounts | list[float] | same length as periods, all >= 0 | Cash flow amounts per period |
| currency | str | 3-letter ISO code | Currency of amounts (default: "USD") |

### DiscountRateInput
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| risk_free_rate | float | >= 0, <= 1 | Risk-free rate as decimal (e.g., 0.04 for 4%) |
| equity_risk_premium | float | >= 0 | Equity risk premium |
| size_premium | float | >= 0 | Size premium (default: 0) |
| industry_risk_premium | float | >= 0 | Industry-specific risk premium (default: 0) |
| specific_risk_premium | float | >= 0 | Asset-specific risk premium (default: 0) |

### ValuationResult
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| value | float | >= 0 | Calculated valuation amount |
| currency | str | 3-letter ISO code | Currency of value |
| method | str | non-empty | Valuation method name |
| assumptions | dict | optional | Key assumptions used |
| steps | list[dict] | optional | Step-by-step calculation breakdown |
| formula_reference | str | non-empty | Book chapter/section reference |
| sensitivity | dict | optional | Sensitivity analysis results |

### ComparableTransaction
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| name | str | non-empty | Transaction identifier |
| sale_price | float | > 0 | Transaction value |
| revenue | float | > 0 | Revenue of acquired entity |
| multiple | float | > 0 | Sale price / revenue multiple |
| asset_type | str | non-empty | Type of intangible asset |
| industry | str | non-empty | Industry sector |
| date | str | ISO date format | Transaction date |

### CustomerRelationshipInput
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| customer_count | int | > 0 | Number of customers |
| avg_revenue_per_customer | float | > 0 | Average annual revenue per customer |
| retention_rate | float | > 0, <= 1 | Annual customer retention rate |
| profit_margin | float | > 0, <= 1 | Profit margin on customer revenue |
| discount_rate | float | > 0, <= 1 | Discount rate |
| projection_period | int | > 0 | Number of years to project |

### PPAInput
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| purchase_price | float | > 0 | Total acquisition price |
| tangible_assets_fv | float | >= 0 | Fair value of tangible assets |
| identified_intangibles | list[dict] | each has name, value | Identified intangible assets with values |
| liabilities_fv | float | >= 0 | Fair value of assumed liabilities (default: 0) |

### PPAResult
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| purchase_price | float | > 0 | Total purchase price |
| tangible_assets | float | >= 0 | Fair value of tangible assets |
| identified_intangibles | list[dict] | each has name, value | Each identified intangible |
| total_identified | float | >= 0 | Sum of all identified assets |
| net_identifiable_assets | float | can be negative | Tangible + intangible - liabilities |
| goodwill | float | >= 0 | Residual (purchase price - net identifiable) |
| allocation_percentage | dict | each asset type -> % | Percentage allocation |

### MonteCarloInput
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| variables | list[dict] | each has name, distribution, params | Input variable distributions |
| iterations | int | >= 1000, <= 100000 | Number of simulation iterations |
| seed | int | optional | Random seed for reproducibility |

### MonteCarloResult
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| mean | float | - | Mean of simulated values |
| median | float | - | Median of simulated values |
| std | float | >= 0 | Standard deviation |
| percentile_5 | float | - | 5th percentile |
| percentile_25 | float | - | 25th percentile |
| percentile_75 | float | - | 75th percentile |
| percentile_95 | float | - | 95th percentile |
| min_value | float | - | Minimum simulated value |
| max_value | float | - | Maximum simulated value |
| histogram | list[dict] | optional | Binned distribution data |

### ImpairmentTestInput
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| carrying_value | float | > 0 | Current carrying value on balance sheet |
| fair_value | float | >= 0 | Estimated fair value |
| reporting_unit | str | optional | Reporting unit name (for goodwill) |
| standard | str | "ASC350" or "IAS36" | Accounting standard |

### ImpairmentTestResult
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| carrying_value | float | > 0 | Original carrying value |
| fair_value | float | >= 0 | Estimated fair value |
| impairment_loss | float | >= 0 | Calculated impairment (0 if none) |
| is_impaired | bool | - | Whether impairment exists |
| new_carrying_value | float | >= 0 | Carrying value after impairment |
| standard | str | "ASC350" or "IAS36" | Standard applied |

## Relationships

- `ValuationResult` is returned by all valuation functions
- `PPAResult` uses `ValuationResult` for each identified intangible
- `MonteCarloResult` wraps multiple `ValuationResult` simulations
- `ImpairmentTestResult` compares against prior `ValuationResult` values

## Constraints

- All rates expressed as decimals (0.05 = 5%), not percentages
- All currency amounts in base units (not thousands/millions)
- Cash flow periods must be consecutive integers starting from 1
- Retention rates must be between 0 and 1 (exclusive of 0)
- Discount rates must be positive (greater than 0)
