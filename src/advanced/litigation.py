"""Patent infringement damages calculation.

Implements Section 15.2: Calculates total damages including pre-judgment interest
on lost profits or reasonable royalty over the infringement period.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.core import ValuationResult
from src.core.time_value import annuity_pv


class PatentDamagesInput(BaseModel):
    lost_profits_or_royalty: float = Field(gt=0, description="Annual lost profits or reasonable royalty")
    infringement_period: int = Field(gt=0, description="Duration of infringement in years")
    discount_rate: float = Field(gt=0, le=1, description="Discount rate for present value")
    prejudgment_interest_rate: float = Field(ge=0, le=1, description="Pre-judgment interest rate")


def patent_infringement_damages(
    lost_profits_or_royalty: float,
    infringement_period: int,
    discount_rate: float,
    prejudgment_interest_rate: float,
) -> ValuationResult:
    """Calculate patent infringement damages with pre-judgment interest.

    Total damages = Present value of lost profits/royalty over infringement period
                    + Pre-judgment interest on the damages amount.

    The present value of the lost profits or reasonable royalty is calculated as
    an annuity over the infringement period. Pre-judgment interest is then applied
    to compensate for the time value of money from the date of infringement to
    the date of judgment.

    Args:
        lost_profits_or_royalty: Annual lost profits or reasonable royalty amount.
        infringement_period: Number of years the infringement occurred.
        discount_rate: Discount rate for present value calculation.
        prejudgment_interest_rate: Pre-judgment interest rate.

    Returns:
        ValuationResult with total damages, PV of lost profits, and interest amount.

    Raises:
        ValueError: If any input is invalid.

    Example:
        >>> result = patent_infringement_damages(1_000_000, 5, 0.10, 0.05)
        >>> result.value  # total damages with interest
    """
    PatentDamagesInput(
        lost_profits_or_royalty=lost_profits_or_royalty,
        infringement_period=infringement_period,
        discount_rate=discount_rate,
        prejudgment_interest_rate=prejudgment_interest_rate,
    )

    pv_result = annuity_pv(lost_profits_or_royalty, discount_rate, infringement_period)
    pv_damages = pv_result.value

    prejudgment_interest = pv_damages * ((1 + prejudgment_interest_rate) ** infringement_period - 1)
    total_damages = pv_damages + prejudgment_interest

    steps = [
        {"step": 1, "description": "Annual Lost Profits / Reasonable Royalty", "value": lost_profits_or_royalty},
        {"step": 2, "description": "Infringement Period (years)", "value": infringement_period},
        {"step": 3, "description": "Discount Rate", "value": discount_rate},
        {"step": 4, "description": "PV of Lost Profits (annuity)", "value": round(pv_damages, 2)},
        {"step": 5, "description": "Pre-judgment Interest Rate", "value": prejudgment_interest_rate},
        {"step": 6, "description": "Pre-judgment Interest", "calculation": f"{pv_damages} * ((1 + {prejudgment_interest_rate})^{infringement_period} - 1)", "value": round(prejudgment_interest, 2)},
        {"step": 7, "description": "Total Damages", "calculation": f"{pv_damages} + {prejudgment_interest}", "value": round(total_damages, 2)},
    ]

    return ValuationResult(
        value=round(total_damages, 2),
        method="Patent Infringement Damages",
        formula_reference="Ch 15.2",
        steps=steps,
        assumptions={
            "lost_profits_or_royalty": lost_profits_or_royalty,
            "infringement_period": infringement_period,
            "discount_rate": discount_rate,
            "prejudgment_interest_rate": prejudgment_interest_rate,
            "pv_damages": round(pv_damages, 2),
            "prejudgment_interest": round(prejudgment_interest, 2),
        },
    )
