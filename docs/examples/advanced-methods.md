# Advanced Valuation Methods — Examples

## Relief from Royalty — Patent Valuation

Value a patent portfolio using the RFR method with Tax Amortization Benefit.

```python
from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty
value = relief_from_royalty(
    revenue_projections=[1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
    royalty_rate=0.05,      # 5% arm's length royalty rate
    discount_rate=0.12,     # 12% discount rate
    tax_rate=0.25,          # 25% corporate tax rate
    useful_life=5,          # 5-year useful life
    tab_enabled=True,       # Include Tax Amortization Benefit
)
print(f"Patent Value: ${value.value:,.2f}")
# Patent Value: $194,163.77 (with TAB)
```

**Step-by-step proof** in `value.steps` — shows period-by-period royalty savings, TAB factor, discounting.

## MPEEM — Customer Relationship Valuation

Value customer relationships using Multi-Period Excess Earnings Method.

```python
from intangible_valuation.income_methods.excess_earnings import mpeem
cfs = [200000, 220000, 240000, 260000, 280000]
cacs = [
    {"total_cac": 50000}, {"total_cac": 52000},
    {"total_cac": 54000}, {"total_cac": 56000}, {"total_cac": 58000},
]
result = mpeem(cfs, cacs, discount_rate=0.12, tax_rate=0.25)
print(f"Customer Value: ${result.value:,.2f}")
```

## Incremental Cash Flow

Value a proprietary technology by comparing cash flows with vs without.

```python
from intangible_valuation.income_methods.incremental_cashflow import incremental_cashflow
result = incremental_cashflow(
    cash_flows_with=[500000, 550000, 600000, 650000, 700000],
    cash_flows_without=[400000, 420000, 440000, 460000, 480000],
    discount_rate=0.10,
)
print(f"Technology Value: ${result.value:,.2f}")
```

## Goodwill Calculation

Calculate goodwill from a business acquisition.

```python
from intangible_valuation.advanced.goodwill import goodwill
result = goodwill(
    purchase_price=10_000_000,
    fair_value_net_identifiable_assets=7_000_000,
)
print(f"Goodwill: ${result.value:,.2f}")
# Goodwill: $3,000,000.00
```

## PPA Waterfall

Full purchase price allocation for ASC 805 / IFRS 3 compliance.

```python
from intangible_valuation.advanced.purchase_price_alloc import purchase_price_allocation
result = purchase_price_allocation(
    purchase_price=10_000_000,
    tangible_assets_fv=3_000_000,
    identified_intangibles=[
        {"name": "Patents", "value": 2_500_000, "method": "RFR"},
        {"name": "Customer List", "value": 1_800_000, "method": "MPEEM"},
        {"name": "Brand", "value": 1_200_000, "method": "RFR"},
    ],
    liabilities_fv=500_000,
)
print(f"Goodwill: ${result.value:,.2f}")
```

## Impairment Testing (ASC 350)

Test goodwill for impairment when market conditions change.

```python
from intangible_valuation.advanced.impairment_testing import goodwill_impairment_test
result = goodwill_impairment_test(
    carrying_value=15_000_000,
    fair_value=13_000_000,
    reporting_unit="Software Division",
    standard="ASC350",
)
print(f"Impairment: ${result.value:,.2f}")
```

## Monte Carlo Simulation

Model valuation uncertainty with probability distributions.

```python
from intangible_valuation.core.statistics import monte_carlo_valuation
result = monte_carlo_valuation(
    input_distributions=[
        {"name": "revenue", "distribution": "normal", "params": {"mean": 1000000, "std": 100000}},
        {"name": "cost", "distribution": "uniform", "params": {"low": 200000, "high": 400000}},
    ],
    iterations=10000, seed=42,
)
# Returns: mean, median, std, percentiles (5th, 25th, 75th, 95th)
```

## Decision Tree Analysis

Evaluate investment decisions with contingent outcomes.

```python
from intangible_valuation.core.statistics import decision_tree_valuation
tree = {
    "nodes": [
        {"id": "root", "type": "decision", "label": "Invest?", "value": 0},
        {"id": "success", "type": "terminal", "label": "Success", "value": 1000000},
        {"id": "failure", "type": "terminal", "label": "Failure", "value": 0},
    ],
    "edges": [
        {"from": "root", "to": "success", "probability": 0.6, "cost": 200000},
        {"from": "root", "to": "failure", "probability": 0.4, "cost": 200000},
    ],
}
result = decision_tree_valuation(tree=tree)
print(f"Expected Value: ${result.value:,.2f}")
```

## Transfer Pricing — CUP Method

Determine arm's length price for cross-border IP transfer.

```python
from intangible_valuation.advanced.transfer_pricing import cup_transfer_price
result = cup_transfer_price(
    controlled_price=1_500_000,
    uncontrolled_prices=[1_200_000, 1_350_000, 1_400_000, 1_550_000, 1_600_000],
)
```
