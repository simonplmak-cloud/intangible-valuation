"""Brand and trademark valuation methods.

Implements brand value using Relief-from-Royalty and Excess Earnings
methods with brand strength adjustments.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.core import (
    ValuationResult,
    present_value_of_annuity,
    present_value_of_growing_annuity,
)
from src.income_methods import relief_from_royalty


class TrademarkInputs(BaseModel):
    """Inputs for trademark/brand valuation."""

    revenue: float = Field(ge=0, description="Annual revenue attributable to brand")
    profit_margin: float = Field(ge=0, le=1, description="Profit margin (decimal)")
    brand_strength_index: float = Field(
        ge=0, le=1, description="Brand strength index (0-1)"
    )
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")
    useful_life: int = Field(ge=1, description="Useful life in years")
    method: str = Field(
        default="relief_from_royalty",
        description="Valuation method: relief_from_royalty or excess_earnings",
    )


def trademark_valuation(
    revenue: float,
    profit_margin: float,
    brand_strength_index: float,
    discount_rate: float,
    useful_life: int,
    method: str = "relief_from_royalty",
) -> dict:
    """Calculate brand value using RFR or excess earnings method.

    Brand strength index adjusts the royalty rate in the relief-from-royalty
    method, or the excess earnings in the excess earnings method.

    Args:
        revenue: Annual revenue attributable to the brand.
        profit_margin: Profit margin (decimal).
        brand_strength_index: Brand strength index (0-1, higher = stronger).
        discount_rate: Discount rate (decimal).
        useful_life: Useful life in years.
        method: Valuation method ("relief_from_royalty" or "excess_earnings").

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid or method is unknown.
    """
    inputs = TrademarkInputs(
        revenue=revenue,
        profit_margin=profit_margin,
        brand_strength_index=brand_strength_index,
        discount_rate=discount_rate,
        useful_life=useful_life,
        method=method,
    )

    if inputs.method not in ("relief_from_royalty", "excess_earnings"):
        raise ValueError(
            f"Unknown method: {inputs.method}. "
            "Use 'relief_from_royalty' or 'excess_earnings'."
        )

    steps: list[str] = []

    # Brand strength adjusts the base royalty rate
    base_royalty_rate = 0.05  # 5% industry baseline
    adjusted_royalty_rate = base_royalty_rate * inputs.brand_strength_index

    if inputs.method == "relief_from_royalty":
        # RFR: PV of avoided royalty payments
        annual_royalty = inputs.revenue * adjusted_royalty_rate
        after_tax_royalty = annual_royalty * 0.75  # assume 25% tax rate

        value = present_value_of_annuity(
            after_tax_royalty, inputs.discount_rate, inputs.useful_life
        )

        steps = [
            f"Revenue base: {inputs.revenue:,.0f}",
            f"Base royalty rate: {base_royalty_rate:.2%}",
            f"Brand strength index: {inputs.brand_strength_index:.2f}",
            f"Adjusted royalty rate: {adjusted_royalty_rate:.2%}",
            f"Annual royalty: {annual_royalty:,.0f}",
            f"After-tax royalty (25% tax): {after_tax_royalty:,.0f}",
            f"PV over {inputs.useful_life} years at "
            f"{inputs.discount_rate:.2%}: {value:,.0f}",
        ]

    else:  # excess_earnings
        # Excess earnings: brand contributes to profit above normal return
        profit = inputs.revenue * inputs.profit_margin
        brand_contribution = profit * inputs.brand_strength_index

        value = present_value_of_annuity(
            brand_contribution, inputs.discount_rate, inputs.useful_life
        )

        steps = [
            f"Revenue: {inputs.revenue:,.0f}",
            f"Profit margin: {inputs.profit_margin:.2%}",
            f"Profit: {profit:,.0f}",
            f"Brand strength index: {inputs.brand_strength_index:.2f}",
            f"Brand contribution to profit: {brand_contribution:,.0f}",
            f"PV over {inputs.useful_life} years at "
            f"{inputs.discount_rate:.2%}: {value:,.0f}",
        ]

    return {
        "value": value,
        "method": (
            "Relief-from-Royalty (Brand)"
            if inputs.method == "relief_from_royalty"
            else "Excess Earnings (Brand)"
        ),
        "formula_reference": (
            "RFR = sum(Revenue x Royalty x (1-T) / (1+r)^t)"
            if inputs.method == "relief_from_royalty"
            else "EE = sum(Profit x BSI / (1+r)^t)"
        ),
        "steps": steps,
        "assumptions": {
            "revenue": inputs.revenue,
            "profit_margin": inputs.profit_margin,
            "brand_strength_index": inputs.brand_strength_index,
            "discount_rate": inputs.discount_rate,
            "useful_life": inputs.useful_life,
            "method": inputs.method,
            "tax_rate": 0.25,
        },
    }
