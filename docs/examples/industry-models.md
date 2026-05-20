# Industry Models Examples

Examples demonstrating industry-specific valuation models from the Intangible Asset Valuation textbook.

## Brand Valuation

```python
from intangible_valuation.asset_types.brand_valuation import trademark_valuation

brand = trademark_valuation(
    revenue=50_000_000,
    profit_margin=0.20,
    brand_strength_index=0.75,
    discount_rate=0.12,
    useful_life=10,
    method="relief_from_royalty",
)
print(f"Brand value: ${brand.value:,.2f}")
```

## Customer Relationship Valuation

```python
from intangible_valuation.asset_types.customer_valuation import customer_relationship_valuation
```

## Technology Valuation

```python
from intangible_valuation.asset_types.technology_valuation import software_valuation
```

## Patent Valuation

```python
from intangible_valuation.asset_types.ip_valuation import patent_valuation
```
