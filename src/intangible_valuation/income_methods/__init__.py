"""Advanced income-based valuation methods.

Implements Relief-from-Royalty, Excess Earnings, and Incremental Cash Flow
methods from Chapter 4.
"""

from __future__ import annotations

from intangible_valuation.core import (
    ValuationResult,
    present_value_of_annuity,
    present_value_of_growing_annuity,
)


def relief_from_royalty(
    revenue: float,
    royalty_rate: float,
    tax_rate: float,
    discount_rate: float,
    useful_life: int,
    growth_rate: float = 0.0,
) -> ValuationResult:
    """Value an intangible using the Relief-from-Royalty method.

    The asset value equals the present value of royalty payments avoided
    by owning the asset rather than licensing it.

    Args:
        revenue: Annual revenue attributable to the asset.
        royalty_rate: Comparable royalty rate (decimal).
        tax_rate: Applicable tax rate (decimal).
        discount_rate: Discount rate (decimal).
        useful_life: Remaining useful life in years.
        growth_rate: Revenue growth rate (decimal).

    Returns:
        ValuationResult with after-tax royalty savings.
    """
    if revenue < 0:
        raise ValueError("Revenue must be non-negative")
    if not 0 <= royalty_rate <= 1:
        raise ValueError("Royalty rate must be between 0 and 1")
    if not 0 <= tax_rate <= 1:
        raise ValueError("Tax rate must be between 0 and 1")
    if discount_rate < 0:
        raise ValueError("Discount rate must be non-negative")
    if useful_life <= 0:
        raise ValueError("Useful life must be positive")

    after_tax_royalty = revenue * royalty_rate * (1 - tax_rate)

    if growth_rate == 0:
        value = present_value_of_annuity(
            after_tax_royalty, discount_rate, useful_life
        )
    else:
        value = present_value_of_growing_annuity(
            after_tax_royalty, discount_rate, growth_rate, useful_life
        )

    return ValuationResult(
        value=value,
        method="Relief-from-Royalty",
        formula_reference="RFR = sum(R_t * (1-T) / (1+r)^t)",
        steps=[
            f"Revenue base: {revenue:,.0f}",
            f"Royalty rate: {royalty_rate:.2%}",
            f"After-tax royalty: {after_tax_royalty:,.0f}",
            f"Discount rate: {discount_rate:.2%}",
            f"Useful life: {useful_life} years",
            f"Growth rate: {growth_rate:.2%}",
        ],
        assumptions={
            "revenue": revenue,
            "royalty_rate": royalty_rate,
            "tax_rate": tax_rate,
            "discount_rate": discount_rate,
            "useful_life": useful_life,
            "growth_rate": growth_rate,
        },
    )


def excess_earnings(
    net_income: float,
    contributory_asset_charges: float,
    discount_rate: float,
    useful_life: int,
    growth_rate: float = 0.0,
) -> ValuationResult:
    """Value an intangible using the Excess Earnings method.

    The asset value equals the present value of earnings after deducting
    charges for all contributory assets (working capital, fixed assets, etc.).

    Args:
        net_income: Annual net income attributable to the asset.
        contributory_asset_charges: Annual CAC for contributory assets.
        discount_rate: Discount rate (decimal).
        useful_life: Remaining useful life in years.
        growth_rate: Earnings growth rate (decimal).

    Returns:
        ValuationResult with excess earnings value.
    """
    if net_income < 0:
        raise ValueError("Net income must be non-negative")
    if contributory_asset_charges < 0:
        raise ValueError("CAC must be non-negative")
    if discount_rate < 0:
        raise ValueError("Discount rate must be non-negative")
    if useful_life <= 0:
        raise ValueError("Useful life must be positive")

    excess_earnings = net_income - contributory_asset_charges
    if excess_earnings < 0:
        raise ValueError("Excess earnings must be non-negative")

    if growth_rate == 0:
        value = present_value_of_annuity(
            excess_earnings, discount_rate, useful_life
        )
    else:
        value = present_value_of_growing_annuity(
            excess_earnings, discount_rate, growth_rate, useful_life
        )

    return ValuationResult(
        value=value,
        method="Excess Earnings",
        formula_reference="EE = sum((NI - CAC) / (1+r)^t)",
        steps=[
            f"Net income: {net_income:,.0f}",
            f"CAC: {contributory_asset_charges:,.0f}",
            f"Excess earnings: {excess_earnings:,.0f}",
            f"Discount rate: {discount_rate:.2%}",
            f"Useful life: {useful_life} years",
        ],
        assumptions={
            "net_income": net_income,
            "contributory_asset_charges": contributory_asset_charges,
            "discount_rate": discount_rate,
            "useful_life": useful_life,
            "growth_rate": growth_rate,
        },
    )


def incremental_cash_flow(
    cash_flow_with_asset: float,
    cash_flow_without_asset: float,
    discount_rate: float,
    useful_life: int,
    growth_rate: float = 0.0,
) -> ValuationResult:
    """Value an intangible using the Incremental Cash Flow method.

    The asset value equals the present value of the difference between
    cash flows with and without the asset.

    Args:
        cash_flow_with_asset: Annual cash flow with the asset.
        cash_flow_without_asset: Annual cash flow without the asset.
        discount_rate: Discount rate (decimal).
        useful_life: Remaining useful life in years.
        growth_rate: Cash flow growth rate (decimal).

    Returns:
        ValuationResult with incremental cash flow value.
    """
    if cash_flow_with_asset < 0:
        raise ValueError("Cash flow with asset must be non-negative")
    if cash_flow_without_asset < 0:
        raise ValueError("Cash flow without asset must be non-negative")
    if discount_rate < 0:
        raise ValueError("Discount rate must be non-negative")
    if useful_life <= 0:
        raise ValueError("Useful life must be positive")

    incremental = cash_flow_with_asset - cash_flow_without_asset
    if incremental < 0:
        raise ValueError("Incremental cash flow must be non-negative")

    if growth_rate == 0:
        value = present_value_of_annuity(
            incremental, discount_rate, useful_life
        )
    else:
        value = present_value_of_growing_annuity(
            incremental, discount_rate, growth_rate, useful_life
        )

    return ValuationResult(
        value=value,
        method="Incremental Cash Flow",
        formula_reference="ICF = sum((CF_with - CF_without) / (1+r)^t)",
        steps=[
            f"CF with asset: {cash_flow_with_asset:,.0f}",
            f"CF without asset: {cash_flow_without_asset:,.0f}",
            f"Incremental CF: {incremental:,.0f}",
            f"Discount rate: {discount_rate:.2%}",
            f"Useful life: {useful_life} years",
        ],
        assumptions={
            "cash_flow_with_asset": cash_flow_with_asset,
            "cash_flow_without_asset": cash_flow_without_asset,
            "discount_rate": discount_rate,
            "useful_life": useful_life,
            "growth_rate": growth_rate,
        },
    )
