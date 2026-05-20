# Advanced Methods Examples

Examples demonstrating advanced valuation methods from the Intangible Asset Valuation textbook.

## Purchase Price Allocation

```python
from intangible_valuation.advanced.purchase_price_alloc import purchase_price_allocation

ppa = purchase_price_allocation(
    purchase_price=100_000_000,
    tangible_assets_fv=15_000_000,
    identified_intangibles=[
        {"name": "Customer Relationships", "value": 25_000_000, "method": "MPEEM"},
        {"name": "Technology", "value": 20_000_000, "method": "relief-from-royalty"},
        {"name": "Trademark", "value": 15_000_000, "method": "relief-from-royalty"},
    ],
    liabilities_fv=0,
)
print(f"Goodwill: ${ppa.value:,.2f}")  # $25,000,000
```

## Monte Carlo Simulation

```python
from intangible_valuation.core.statistics import monte_carlo_valuation
```

## Decision Tree Analysis

```python
from intangible_valuation.core.statistics import decision_tree_valuation
```

## Goodwill Impairment Testing

```python
from intangible_valuation.advanced.impairment_testing import goodwill_impairment_test
```
