"""Purchase Price Allocation (PPA) waterfall analysis.

Implements Section 10.2 and Appendix A.8: Full allocation of purchase price
to tangible assets, identified intangibles, liabilities, and residual goodwill.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.core import ValuationResult
from src.advanced.goodwill import goodwill


class IdentifiedIntangible(BaseModel):
    name: str = Field(min_length=1, description="Name of the intangible asset")
    value: float = Field(gt=0, description="Fair value of the intangible asset")
    method: str = Field(min_length=1, description="Valuation method used (e.g., 'relief-from-royalty', 'MPEEM')")


class PPAInput(BaseModel):
    purchase_price: float = Field(gt=0, description="Total acquisition price")
    tangible_assets_fv: float = Field(ge=0, description="Fair value of tangible assets")
    identified_intangibles: list[IdentifiedIntangible] = Field(min_length=1, description="List of identified intangible assets")
    liabilities_fv: float = Field(ge=0, description="Fair value of assumed liabilities")


def purchase_price_allocation(
    purchase_price: float,
    tangible_assets_fv: float,
    identified_intangibles: list[dict],
    liabilities_fv: float = 0,
) -> ValuationResult:
    """Perform full purchase price allocation waterfall.

    Allocates the purchase price across:
    1. Tangible assets at fair value
    2. Identified intangible assets at fair value
    3. Assumed liabilities at fair value
    4. Goodwill as the residual

    Args:
        purchase_price: Total acquisition consideration.
        tangible_assets_fv: Fair value of all tangible assets acquired.
        identified_intangibles: List of dicts with keys: name, value, method.
        liabilities_fv: Fair value of liabilities assumed.

    Returns:
        ValuationResult with full allocation breakdown and percentages.

    Raises:
        ValueError: If inputs are invalid or result in negative goodwill.

    Example (Book Example):
        $100M purchase, $15M tangible, $60M identified intangibles, $0 liabilities
        Net identifiable = 15M + 60M - 0 = 75M
        Goodwill = 100M - 75M = 25M
    """
    validated_intangibles = [IdentifiedIntangible(**item) for item in identified_intangibles]
    PPAInput(
        purchase_price=purchase_price,
        tangible_assets_fv=tangible_assets_fv,
        identified_intangibles=validated_intangibles,
        liabilities_fv=liabilities_fv,
    )

    total_intangibles = sum(iv.value for iv in validated_intangibles)
    net_identifiable = tangible_assets_fv + total_intangibles - liabilities_fv

    gw_result = goodwill(purchase_price, net_identifiable)
    goodwill_value = gw_result.value

    total_alloc = tangible_assets_fv + total_intangibles + goodwill_value
    pct_tangible = (tangible_assets_fv / purchase_price * 100) if purchase_price else 0
    pct_intangible = (total_intangibles / purchase_price * 100) if purchase_price else 0
    pct_goodwill = (goodwill_value / purchase_price * 100) if purchase_price else 0

    steps = [
        {"item": "Purchase Price", "value": purchase_price},
        {"item": "Tangible Assets", "value": tangible_assets_fv},
        {"item": "Identified Intangibles", "value": total_intangibles},
        {"item": "Liabilities", "value": -liabilities_fv},
        {"item": "Net Identifiable Assets", "value": net_identifiable},
        {"item": "Goodwill (residual)", "value": goodwill_value},
    ]

    for iv in validated_intangibles:
        steps.insert(2, {"item": f"  - {iv.name} ({iv.method})", "value": iv.value})

    allocation = {
        "tangible": f"{pct_tangible:.1f}%",
        "intangible": f"{pct_intangible:.1f}%",
        "goodwill": f"{pct_goodwill:.1f}%",
    }

    return ValuationResult(
        value=goodwill_value,
        method="Purchase Price Allocation",
        formula_reference="Ch 10.2, Appendix A.8",
        steps=steps,
        assumptions={"allocation": allocation},
    )
