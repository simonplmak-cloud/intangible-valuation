"""Goodwill calculation as residual of purchase price over net identifiable assets.

Implements Section 10.1: Goodwill = Purchase Price - Fair Value of Net Identifiable Assets.
Raises ValueError for bargain purchases (negative goodwill).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from intangible_valuation.core import ValuationResult


class GoodwillInput(BaseModel):
    purchase_price: float = Field(gt=0, description="Total purchase price")
    fair_value_net_identifiable_assets: float = Field(ge=0, description="Fair value of net identifiable assets")


def goodwill(purchase_price: float, fair_value_net_identifiable_assets: float) -> ValuationResult:
    """Calculate goodwill as the residual of purchase price over fair value of net identifiable assets.

    Goodwill represents the premium paid for unidentifiable intangible assets such as
    synergies, assembled workforce, and brand reputation that cannot be separately identified.

    Args:
        purchase_price: Total acquisition consideration paid.
        fair_value_net_identifiable_assets: Fair value of all identifiable assets minus liabilities.

    Returns:
        ValuationResult with goodwill amount, calculation steps, and assumptions.

    Raises:
        ValueError: If purchase_price < fair_value_net_identifiable_assets (bargain purchase).
        ValueError: If purchase_price <= 0 or fair_value_net_identifiable_assets < 0.

    Example:
        >>> result = goodwill(100_000_000, 75_000_000)
        >>> result.value
        25000000.0
    """
    GoodwillInput(purchase_price=purchase_price, fair_value_net_identifiable_assets=fair_value_net_identifiable_assets)

    goodwill_value = purchase_price - fair_value_net_identifiable_assets

    if goodwill_value < 0:
        raise ValueError(
            f"Bargain purchase detected: purchase_price ({purchase_price}) < "
            f"fair_value_net_identifiable_assets ({fair_value_net_identifiable_assets}). "
            f"Resulting goodwill would be negative ({goodwill_value}). "
            f"Under ASC 805 / IFRS 3, this requires reassessment before recognizing a gain."
        )

    return ValuationResult(
        value=round(goodwill_value, 2),
        method="Goodwill (Residual Method)",
        formula_reference="Ch 10.1, ASC 805-30-30-1",
        steps=[
            {"step": 1, "description": "Purchase Price", "value": purchase_price},
            {
                "step": 2,
                "description": "Fair Value of Net Identifiable Assets",
                "value": fair_value_net_identifiable_assets,
            },
            {
                "step": 3,
                "description": "Goodwill = Purchase Price - Net Identifiable Assets",
                "calculation": f"{purchase_price} - {fair_value_net_identifiable_assets}",
            },
            {"step": 4, "description": "Goodwill", "value": round(goodwill_value, 2)},
        ],
        assumptions={
            "purchase_price": purchase_price,
            "fair_value_net_identifiable_assets": fair_value_net_identifiable_assets,
        },
    )
