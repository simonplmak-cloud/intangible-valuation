# Advanced Analytics API

Monte Carlo simulation, decision trees, purchase price allocation, goodwill, litigation damages, and transfer pricing.

## Monte Carlo Sensitivity

::: src.advanced.monte_carlo
    options:
        members:
            - monte_carlo_sensitivity

## Purchase Price Allocation

::: src.advanced.purchase_price_alloc
    options:
        members:
            - purchase_price_allocation
            - IdentifiedIntangible
            - PPAInput

## Goodwill

::: src.advanced.goodwill
    options:
        members:
            - goodwill
            - GoodwillInput

## Litigation Damages

::: src.advanced.litigation
    options:
        members:
            - patent_infringement_damages
            - PatentDamagesInput

## Royalty Benchmarking

::: src.advanced.royalty_benchmark
    options:
        members:
            - royalty_rate_benchmark
            - adjust_royalty_rate
            - twenty_five_percent_rule

## Impairment Testing

::: src.advanced.impairment_testing

## Transfer Pricing

::: src.advanced.transfer_pricing

## Utility Functions

::: src.utils.formulas
    options:
        members:
            - estimate_useful_life
            - sensitivity_analysis
            - contributory_asset_charges
