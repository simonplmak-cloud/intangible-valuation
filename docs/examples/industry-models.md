# Industry-Specific Valuation Models — Examples

Real-world valuation examples across industries.

## Pharmaceutical — Patent Portfolio

Risk-adjusted patent valuation with probability of success.

```python
from intangible_valuation.asset_types.ip_valuation import patent_valuation
result = patent_valuation(
    remaining_life=12,                       # 12 years patent life
    cash_flow_projections=[                    # Phased revenue ramp
        5_000_000, 8_000_000, 15_000_000, 25_000_000, 40_000_000,
        60_000_000, 80_000_000, 70_000_000, 55_000_000, 40_000_000,
        25_000_000, 15_000_000,
    ],
    probability_of_success=0.35,             # Phase III success rate
    discount_rate=0.20,                      # Biotech WACC
    comparable_license_rates=[0.08, 0.10, 0.12],
)
print(f"Risk-Adjusted Patent Value: ${result.value:,.2f}")
```

## SaaS — Brand Valuation (Interbrand)

Brand value for a B2B SaaS company with strong brand recognition.

```python
from intangible_valuation.asset_types.brand_valuation import interbrand_brand_valuation
result = interbrand_brand_valuation(
    revenue=50_000_000,          # $50M ARR
    profit_margin=0.30,          # 30% SaaS margins
    brand_strength_score=78,     # Strong brand (0-100)
    discount_rate=0.15,          # SaaS WACC
)
print(f"Brand Value: ${result.value:,.2f}")
```

## Fintech — Platform Valuation with Network Effects

Value a payment platform with Metcalfe's law network effects.

```python
from intangible_valuation.asset_types.technology_valuation import platform_valuation
result = platform_valuation(
    network_size=2_000_000,                # 2M active users
    network_effects_coefficient=0.3,       # 30% value per new user
    revenue_per_user=15.0,                 # $15 ARPU
    growth_rate=0.40,                      # 40% YoY growth
    discount_rate=0.20,                    # VC-level risk
)
print(f"Platform Value: ${result.value:,.2f}")
```

## Enterprise Software — Developed Technology

Valuing proprietary algorithms with life-cycle risk adjustment.

```python
from intangible_valuation.asset_types.technology_valuation import developed_technology_valuation
result = developed_technology_valuation(
    rd_costs=5_000_000,              # $5M R&D investment
    life_cycle_stage="growth",       # Growth stage (lower risk)
    competitive_advantage=5,         # 5-year advantage window
    discount_rate=0.18,              # Technology WACC
    cash_flow_projections=[
        800_000, 1_500_000, 3_000_000, 5_000_000, 6_000_000,
    ],
)
print(f"Technology Value: ${result.value:,.2f}")
```

## Retail — Customer Relationship Portfolio

Multi-period customer valuation with attrition.

```python
from intangible_valuation.asset_types.customer_valuation import customer_relationship_valuation
result = customer_relationship_valuation(
    customer_count=50_000,                   # 50K customers
    avg_revenue_per_customer=2_500,         # $2,500/year per customer
    retention_rate=0.82,                     # 82% annual retention
    profit_margin=0.25,                      # 25% margin
    discount_rate=0.14,                      # Retail WACC
    projection_period=8,                     # 8-year projection
)
print(f"Customer Portfolio Value: ${result.value:,.2f}")
```

## Professional Services — Key Person Valuation

Value of a key revenue-generating partner.

```python
from intangible_valuation.asset_types.human_capital import key_person_value
result = key_person_value(
    revenue_contribution=3_500_000,    # $3.5M attributable revenue
    replacement_cost=750_000,          # Cost to replace + train
    departure_probability=0.10,        # 10% annual departure risk
    discount_rate=0.18,                # Professional services risk
)
print(f"Key Person Value: ${result.value:,.2f}")
```

## Manufacturing — Distribution Network

Value of exclusive distribution channels.

```python
from intangible_valuation.asset_types.customer_valuation import distribution_network_valuation
result = distribution_network_valuation(
    channel_count=120,                    # 120 distribution points
    revenue_per_channel=350_000,          # $350K per channel
    channel_margin=0.18,                  # 18% channel margin
    useful_life=12,                       # 12-year relationship life
    discount_rate=0.13,                   # Manufacturing WACC
)
print(f"Distribution Network Value: ${result.value:,.2f}")
```

## Media — Copyright Portfolio

Valuing publishing rights with declining revenue.

```python
from intangible_valuation.asset_types.ip_valuation import copyright_valuation
result = copyright_valuation(
    projected_revenue=2_000_000,       # Current annual royalty revenue
    useful_life=25,                     # Life of author + 70 years simplified
    discount_rate=0.11,                 # Media industry WACC
    royalty_rate=0.15,                  # Standard publishing royalty
)
print(f"Copyright Value: ${result.value:,.2f}")
```
