# Core Methods Examples

Examples demonstrating core valuation methods from the Intangible Asset Valuation textbook.

## Present Value

```python
from intangible_valuation.core.time_value import present_value

result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
print(f"PV: ${result.value:,.2f}")  # $233,253.69
```

## Build-Up Discount Rate

```python
from intangible_valuation.core.discount_rates import build_up_discount_rate

rate = build_up_discount_rate(
    risk_free_rate=0.04,
    equity_risk_premium=0.06,
    size_premium=0.02,
    industry_risk_premium=0.01,
    specific_risk_premium=0.03,
)
print(f"Discount rate: {rate.value:.2%}")  # 16.00%
```

## Scorecard Method

```python
from intangible_valuation.approaches.market_approach import market_approach_comparables
```

## Relief from Royalty

```python
from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty

value = relief_from_royalty(
    revenue_projections=[1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
    royalty_rate=0.05,
    discount_rate=0.12,
    tax_rate=0.25,
    useful_life=5,
)
print(f"Patent value: ${value.value:,.2f}")
```
