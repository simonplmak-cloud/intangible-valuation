# Core Math API

Time value of money, discount rate construction, and statistical functions.

## Time Value of Money

::: intangible_valuation.core.time_value
    options:
        members:
            - present_value
            - future_value
            - annuity_pv
            - perpetuity_pv
            - growing_annuity_pv
            - terminal_value
            - present_value_of_series
            - ValuationResult
            - TVMInputs

## Discount Rates

::: intangible_valuation.core.discount_rates
    options:
        members:
            - build_up_discount_rate
            - capm_discount_rate
            - wacc
            - tax_amortization_benefit
            - control_premium
            - dlom_finnerty
            - currency_adjusted_discount_rate
            - DiscountRateInputs

## Statistics

::: intangible_valuation.core.statistics
    options:
        members:
            - monte_carlo_valuation
            - decision_tree_valuation
            - DistributionInput
            - TreeNode
            - TreeEdge
            - DecisionTreeInput

## Constants

::: intangible_valuation.utils.constants
