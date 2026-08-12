# Core Valuation Methods — Examples

Copy-paste runnable examples for every core valuation method.

## Present Value of a Single Cash Flow

Discount a $500,000 payment 8 years out at 10%.

```python
from intangible_valuation.core.time_value import present_value
result = present_value(future_value=500_000, discount_rate=0.10, periods=8)
print(f"PV: ${result.value:,.2f}")
# Output: PV: $233,253.69
```

**Formula:** PV = FV / (1 + r)^n = 500,000 / (1.10)^8 = $233,253.69

**Steps:** `result.steps` shows period-by-period discounting.

## Build-Up Discount Rate

Construct a 16% discount rate for a private company.

```python
from intangible_valuation.core.discount_rates import build_up_discount_rate
rate = build_up_discount_rate(
    risk_free_rate=0.04,       # 10-year Treasury
    equity_risk_premium=0.06,  # Duff & Phelps ERP
    size_premium=0.02,         # Micro-cap size premium
    industry_risk_premium=0.01,# Software industry risk
    specific_risk_premium=0.03,# Customer concentration risk
)
print(f"Rate: {rate.value:.2%}")
# Output: Rate: 16.00%
```

**Formula:** r = Rf + ERP + Size + Industry + Specific

## WACC (Weighted Average Cost of Capital)

Enterprise-level discount rate for a company with 70% equity / 30% debt.

```python
from intangible_valuation.core.discount_rates import wacc
result = wacc(
    equity_value=700, debt_value=300,
    cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25,
)
print(f"WACC: {result.value:.2%}")
# Output: WACC: 9.75%
```

## Annuity PV

PV of $10,000 annual payments for 5 years at 8%.

```python
from intangible_valuation.core.time_value import annuity_pv
result = annuity_pv(payment=10_000, discount_rate=0.08, periods=5)
print(f"Annuity PV: ${result.value:,.2f}")
# Output: Annuity PV: $39,927.10
```

## Terminal Value (Gordon Growth)

Perpetual value beyond 5-year forecast with 3% growth.

```python
from intangible_valuation.core.time_value import terminal_value
result = terminal_value(
    final_year_cashflow=1_400_000,
    perpetual_growth_rate=0.03,
    discount_rate=0.12,
)
print(f"Terminal Value: ${result.value:,.2f}")
# Output: Terminal Value: $16,022,222.22
```

## Tax Amortization Benefit

PV of tax savings from amortizing a $1M asset over 10 years.

```python
from intangible_valuation.core.discount_rates import tax_amortization_benefit
result = tax_amortization_benefit(
    discount_rate=0.16, useful_life=10,
    tax_rate=0.25, asset_value=1_000_000,
)
print(f"TAB: ${result.value:,.2f}")
```

## DLOM (Finnerty Model)

Discount for lack of marketability — 1-year restriction, 35% volatility.

```python
from intangible_valuation.core.discount_rates import dlom_finnerty
result = dlom_finnerty(restricted_period=1.0, volatility=0.35, risk_free_rate=0.04)
print(f"DLOM: {result.value:.2%}")
```

## Control Premium

Premium paid for controlling interest vs minority.

```python
from intangible_valuation.core.discount_rates import control_premium
result = control_premium(minority_price=85, control_price=100)
print(f"Control Premium: {result.value:.2%}")
# Output: Control Premium: 17.65%
```
