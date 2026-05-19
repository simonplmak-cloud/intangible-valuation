"""Transfer pricing calculations.

Implements Section 16.1 and 16.3:
- Currency-adjusted discount rate (re-exports from core.discount_rates)
- CUP (Comparable Uncontrolled Price) transfer price analysis
"""

from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field

from src.core.discount_rates import currency_adjusted_discount_rate
from src.core import ValuationResult


class CUPInput(BaseModel):
    controlled_price: float = Field(gt=0, description="Price in controlled transaction")
    uncontrolled_prices: list[float] = Field(min_length=3, description="Comparable uncontrolled prices (min 3)")


def cup_transfer_price(
    controlled_price: float,
    uncontrolled_prices: list[float],
) -> ValuationResult:
    """Calculate arm's length range using the Comparable Uncontrolled Price (CUP) method.

    The CUP method compares the price charged in a controlled transaction to the price
    charged in comparable uncontrolled transactions. Returns the interquartile range (IQR)
    of uncontrolled prices as the arm's length range, per OECD Transfer Pricing Guidelines.

    Args:
        controlled_price: Price charged in the controlled (related-party) transaction.
        uncontrolled_prices: List of prices from comparable uncontrolled transactions.

    Returns:
        ValuationResult with arm's length range, controlled price assessment,
        and statistical analysis of comparables.

    Raises:
        ValueError: If controlled_price <= 0 or fewer than 3 uncontrolled prices.

    Example:
        >>> result = cup_transfer_price(100, [90, 95, 100, 105, 110])
        >>> result.assumptions["arms_length_range"]
        (95.0, 105.0)
    """
    if len(uncontrolled_prices) < 3:
        raise ValueError("At least 3 uncontrolled prices are required for CUP analysis")

    CUPInput(controlled_price=controlled_price, uncontrolled_prices=uncontrolled_prices)

    for p in uncontrolled_prices:
        if p <= 0:
            raise ValueError("All uncontrolled prices must be > 0")

    sorted_prices = sorted(uncontrolled_prices)
    q1 = float(np.percentile(sorted_prices, 25))
    q3 = float(np.percentile(sorted_prices, 75))
    median = float(np.median(sorted_prices))
    mean = float(np.mean(sorted_prices))
    iqr = q3 - q1

    within_range = q1 <= controlled_price <= q3

    steps = [
        {"step": 1, "description": "Collect comparable uncontrolled prices", "value": len(uncontrolled_prices)},
        {"step": 2, "description": "Sort and compute quartiles"},
        {"step": 3, "description": "Q1 (25th percentile)", "value": round(q1, 2)},
        {"step": 4, "description": "Median (50th percentile)", "value": round(median, 2)},
        {"step": 5, "description": "Q3 (75th percentile)", "value": round(q3, 2)},
        {"step": 6, "description": "Interquartile Range (IQR)", "value": round(iqr, 2)},
        {"step": 7, "description": "Controlled Price", "value": controlled_price},
        {"step": 8, "description": "Within arm's length range", "value": within_range},
    ]

    return ValuationResult(
        value=round(median, 2),
        method="Comparable Uncontrolled Price (CUP)",
        formula_reference="Ch 16.1, OECD TP Guidelines",
        steps=steps,
        assumptions={
            "controlled_price": controlled_price,
            "uncontrolled_prices": sorted_prices,
            "arms_length_range": (round(q1, 2), round(q3, 2)),
            "median": round(median, 2),
            "mean": round(mean, 2),
            "iqr": round(iqr, 2),
            "within_range": within_range,
        },
    )
