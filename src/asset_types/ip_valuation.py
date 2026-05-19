"""Intellectual property valuation methods.

Implements valuation for patents, copyrights, and trade secrets
using risk-adjusted income approaches.
"""

from __future__ import annotations

from typing import Sequence

from pydantic import BaseModel, Field, field_validator

from src.core import (
    ValuationResult,
    present_value,
    present_value_of_annuity,
    risk_adjusted_value,
)


class PatentInputs(BaseModel):
    """Inputs for patent valuation."""

    remaining_life: int = Field(ge=1, description="Remaining patent life in years")
    cash_flow_projections: list[float] = Field(
        min_length=1, description="Projected annual cash flows"
    )
    probability_of_success: float = Field(
        ge=0, le=1, description="Probability of commercial success"
    )
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")
    comparable_license_rates: list[float] | None = Field(
        default=None, description="Comparable license royalty rates"
    )

    @field_validator("cash_flow_projections")
    @classmethod
    def cash_flows_non_negative(cls, v: list[float]) -> list[float]:
        if any(cf < 0 for cf in v):
            raise ValueError("Cash flow projections must be non-negative")
        return v


def patent_valuation(
    remaining_life: int,
    cash_flow_projections: Sequence[float],
    probability_of_success: float,
    discount_rate: float,
    comparable_license_rates: Sequence[float] | None = None,
) -> dict:
    """Calculate risk-adjusted patent value with probability weighting.

    Values a patent by discounting projected cash flows and applying
    probability of commercial success. Comparable license rates provide
    a cross-check via the relief-from-royalty approach.

    Args:
        remaining_life: Remaining patent life in years.
        cash_flow_projections: Projected annual cash flows from the patent.
        probability_of_success: Probability of commercial success (0-1).
        discount_rate: Discount rate (decimal).
        comparable_license_rates: Optional comparable license royalty rates.

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = PatentInputs(
        remaining_life=remaining_life,
        cash_flow_projections=list(cash_flow_projections),
        probability_of_success=probability_of_success,
        discount_rate=discount_rate,
        comparable_license_rates=(
            list(comparable_license_rates) if comparable_license_rates else None
        ),
    )

    steps: list[str] = []
    assumptions: dict[str, float | str] = {}

    # Step 1: Calculate PV of cash flows
    pv_cash_flows = 0.0
    for t, cf in enumerate(inputs.cash_flow_projections, start=1):
        if t > inputs.remaining_life:
            break
        pv = present_value(cf, inputs.discount_rate, t)
        pv_cash_flows += pv
        steps.append(f"Year {t} CF: {cf:,.0f} -> PV: {pv:,.0f}")

    # Step 2: Apply probability of success
    risk_adjusted_pv = risk_adjusted_value(
        pv_cash_flows, inputs.probability_of_success
    )
    steps.append(
        f"Gross PV: {pv_cash_flows:,.0f} "
        f"x POS ({inputs.probability_of_success:.0%}) "
        f"= {risk_adjusted_pv:,.0f}"
    )

    # Step 3: Cross-check with comparable license rates if provided
    comparable_value: float | None = None
    if inputs.comparable_license_rates and len(inputs.comparable_license_rates) > 0:
        avg_rate = sum(inputs.comparable_license_rates) / len(
            inputs.comparable_license_rates
        )
        comparable_value = risk_adjusted_pv * (avg_rate / 0.05)  # normalize
        steps.append(
            f"Comparable avg rate: {avg_rate:.2%}, "
            f"cross-check value: {comparable_value:,.0f}"
        )

    final_value = risk_adjusted_pv

    assumptions = {
        "remaining_life": inputs.remaining_life,
        "number_of_projections": len(inputs.cash_flow_projections),
        "probability_of_success": inputs.probability_of_success,
        "discount_rate": inputs.discount_rate,
    }
    if comparable_license_rates:
        assumptions["comparable_license_rates"] = str(
            comparable_license_rates
        )

    return {
        "value": final_value,
        "method": "Risk-Adjusted Income Approach",
        "formula_reference": "PV = sum(CF_t / (1+r)^t) x POS",
        "steps": steps,
        "assumptions": assumptions,
    }


class CopyrightInputs(BaseModel):
    """Inputs for copyright valuation."""

    projected_revenue: float = Field(ge=0, description="Total projected revenue")
    useful_life: int = Field(ge=1, description="Useful life in years")
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")
    royalty_rate: float = Field(
        ge=0, le=1, description="Royalty rate (decimal)"
    )


def copyright_valuation(
    projected_revenue: float,
    useful_life: int,
    discount_rate: float,
    royalty_rate: float,
) -> dict:
    """Calculate PV of expected copyright royalty/licensing income.

    Uses the relief-from-royalty approach to value copyrights based on
    projected revenue streams over the asset's useful life.

    Args:
        projected_revenue: Total projected revenue over useful life.
        useful_life: Useful life in years.
        discount_rate: Discount rate (decimal).
        royalty_rate: Applicable royalty rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = CopyrightInputs(
        projected_revenue=projected_revenue,
        useful_life=useful_life,
        discount_rate=discount_rate,
        royalty_rate=royalty_rate,
    )

    annual_revenue = inputs.projected_revenue / inputs.useful_life
    annual_royalty = annual_revenue * inputs.royalty_rate

    value = present_value_of_annuity(
        annual_royalty, inputs.discount_rate, inputs.useful_life
    )

    steps = [
        f"Total projected revenue: {inputs.projected_revenue:,.0f}",
        f"Useful life: {inputs.useful_life} years",
        f"Annual revenue: {annual_revenue:,.0f}",
        f"Royalty rate: {inputs.royalty_rate:.2%}",
        f"Annual royalty income: {annual_royalty:,.0f}",
        f"PV of royalty stream: {value:,.0f}",
    ]

    return {
        "value": value,
        "method": "Relief-from-Royalty (Copyright)",
        "formula_reference": "PV = sum(R_t * r / (1+d)^t)",
        "steps": steps,
        "assumptions": {
            "projected_revenue": inputs.projected_revenue,
            "useful_life": inputs.useful_life,
            "discount_rate": inputs.discount_rate,
            "royalty_rate": inputs.royalty_rate,
        },
    }


class TradeSecretInputs(BaseModel):
    """Inputs for trade secret valuation."""

    development_cost: float = Field(ge=0, description="Development cost")
    economic_life: int = Field(ge=1, description="Economic life in years")
    competitive_advantage_period: int = Field(
        ge=1, description="Period of competitive advantage in years"
    )
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")
    secrecy_probability: float = Field(
        ge=0, le=1, description="Probability of maintaining secrecy"
    )


def trade_secret_valuation(
    development_cost: float,
    economic_life: int,
    competitive_advantage_period: int,
    discount_rate: float,
    secrecy_probability: float,
) -> dict:
    """Value a trade secret incorporating secrecy risk over time.

    Combines cost approach (development cost) with income approach
    (competitive advantage period), adjusted for the probability of
    maintaining secrecy over time.

    Args:
        development_cost: Cost to develop the trade secret.
        economic_life: Expected economic life in years.
        competitive_advantage_period: Period of competitive advantage in years.
        discount_rate: Discount rate (decimal).
        secrecy_probability: Probability of maintaining secrecy (0-1).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = TradeSecretInputs(
        development_cost=development_cost,
        economic_life=economic_life,
        competitive_advantage_period=competitive_advantage_period,
        discount_rate=discount_rate,
        secrecy_probability=secrecy_probability,
    )

    steps: list[str] = []

    # Step 1: Cost approach floor
    cost_floor = inputs.development_cost
    steps.append(f"Development cost (floor): {cost_floor:,.0f}")

    # Step 2: Income approach - PV of competitive advantage
    annual_benefit = inputs.development_cost / inputs.competitive_advantage_period
    income_value = present_value_of_annuity(
        annual_benefit,
        inputs.discount_rate,
        inputs.competitive_advantage_period,
    )
    steps.append(
        f"Annual benefit: {annual_benefit:,.0f}, "
        f"Income PV: {income_value:,.0f}"
    )

    # Step 3: Apply secrecy risk (probability decays over economic life)
    cumulative_secrecy = inputs.secrecy_probability ** inputs.economic_life
    risk_adjusted_income = income_value * cumulative_secrecy
    steps.append(
        f"Cumulative secrecy probability "
        f"({inputs.secrecy_probability:.0%}^{inputs.economic_life}): "
        f"{cumulative_secrecy:.4f}"
    )
    steps.append(f"Risk-adjusted income value: {risk_adjusted_income:,.0f}")

    # Step 4: Take higher of cost floor and risk-adjusted income
    value = max(cost_floor, risk_adjusted_income)
    steps.append(
        f"Final value (max of cost floor {cost_floor:,.0f} "
        f"and risk-adjusted income {risk_adjusted_income:,.0f}): "
        f"{value:,.0f}"
    )

    return {
        "value": value,
        "method": "Cost-Income Hybrid with Secrecy Risk",
        "formula_reference": "V = max(Cost, PV(Benefit) x P(secrecy)^t)",
        "steps": steps,
        "assumptions": {
            "development_cost": inputs.development_cost,
            "economic_life": inputs.economic_life,
            "competitive_advantage_period": inputs.competitive_advantage_period,
            "discount_rate": inputs.discount_rate,
            "secrecy_probability": inputs.secrecy_probability,
        },
    }
