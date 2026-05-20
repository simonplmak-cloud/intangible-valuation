"""Intellectual property valuation methods.

Implements valuation for patents, copyrights, and trade secrets
using risk-adjusted income approaches.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from pydantic import BaseModel, Field, field_validator

from src.core import (
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


class PatentPortfolioInputs(BaseModel):
    """Inputs for patent portfolio valuation."""

    patents: list[dict] = Field(
        min_length=1, description="List of patent dicts with value and category"
    )
    diversification_factor: float = Field(
        ge=0, le=1, default=0.1, description="Diversification adjustment factor"
    )

    @field_validator("patents")
    @classmethod
    def patents_valid(cls, v: list[dict]) -> list[dict]:
        for i, p in enumerate(v):
            if "value" not in p:
                raise ValueError(f"Patent {i} missing 'value' key")
            if p["value"] < 0:
                raise ValueError(f"Patent {i} value must be non-negative")
        return v


def patent_portfolio_valuation(
    patents: Sequence[dict],
    diversification_factor: float = 0.1,
) -> dict:
    """Calculate total patent portfolio value with diversification adjustment.

    Sums individual patent values and applies a diversification discount/premium
    based on portfolio concentration across technology categories. A more
    diversified portfolio receives a smaller adjustment.

    Formula:
        Portfolio Value = sum(individual_values) x (1 - diversification_factor x HHI)
    where HHI (Herfindahl-Hirschman Index) measures concentration.

    Args:
        patents: List of dicts, each with 'value' (float) and optionally
            'category' (str) and 'remaining_life' (int).
        diversification_factor: Adjustment factor (0-1), default 0.1.

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If patents list is empty or contains invalid data.

    Example:
        >>> patents = [
        ...     {"value": 1000000, "category": "pharma"},
        ...     {"value": 500000, "category": "tech"},
        ...     {"value": 750000, "category": "pharma"},
        ... ]
        >>> result = patent_portfolio_valuation(patents)
        >>> result["value"] < 2250000  # diversification adjustment
        True
    """
    patent_list = list(patents)
    if not patent_list:
        raise ValueError("Patents list cannot be empty")

    inputs = PatentPortfolioInputs(
        patents=patent_list, diversification_factor=diversification_factor
    )

    steps: list[str] = []

    # Step 1: Sum individual values
    total_raw = sum(p["value"] for p in inputs.patents)
    steps.append(f"Number of patents: {len(inputs.patents)}")
    steps.append(f"Sum of individual values: {total_raw:,.0f}")

    # Step 2: Calculate HHI for diversification adjustment
    categories: dict[str, float] = {}
    for p in inputs.patents:
        cat = p.get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + p["value"]

    hhi = sum((v / total_raw) ** 2 for v in categories.values()) if total_raw > 0 else 0.0

    steps.append(f"Categories: {len(categories)}")
    for cat, val in categories.items():
        steps.append(f"  {cat}: {val:,.0f} ({val / total_raw:.1%})")
    steps.append(f"HHI (concentration): {hhi:.4f}")

    # Step 3: Apply diversification adjustment
    adjustment = 1 - inputs.diversification_factor * hhi
    portfolio_value = total_raw * adjustment
    steps.append(
        f"Diversification adjustment: {adjustment:.4f} "
        f"(factor={inputs.diversification_factor}, HHI={hhi:.4f})"
    )
    steps.append(f"Portfolio value: {portfolio_value:,.0f}")

    return {
        "value": portfolio_value,
        "method": "Patent Portfolio with Diversification Adjustment",
        "formula_reference": "V = sum(Vi) x (1 - DF x HHI)",
        "steps": steps,
        "assumptions": {
            "num_patents": len(inputs.patents),
            "total_raw_value": total_raw,
            "hhi": hhi,
            "diversification_factor": inputs.diversification_factor,
            "num_categories": len(categories),
        },
    }


class OptionPricingInputs(BaseModel):
    """Inputs for real options patent valuation."""

    exercise_cost: float = Field(gt=0, description="Cost to commercialize patent")
    expected_value: float = Field(gt=0, description="Expected value of commercialized patent")
    volatility: float = Field(gt=0, le=2, description="Volatility of expected value (decimal)")
    time_to_expiry: float = Field(gt=0, description="Time to patent expiry in years")
    risk_free_rate: float = Field(ge=0, description="Risk-free rate (decimal)")


def option_pricing_patent(
    exercise_cost: float,
    expected_value: float,
    volatility: float,
    time_to_expiry: float,
    risk_free_rate: float,
) -> dict:
    """Value a patent using Black-Scholes real options approximation.

    Treats a patent as a call option: the right (but not obligation) to
    commercialize at cost K. This captures the value of managerial flexibility
    to wait, expand, or abandon the project.

    Formula (Black-Scholes call option):
        d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)
        d2 = d1 - σ√T
        C = S·N(d1) - K·e^(-rT)·N(d2)

    Where:
        S = expected value of commercialized patent
        K = exercise cost (commercialization cost)
        σ = volatility of expected value
        T = time to patent expiry
        r = risk-free rate
        N() = cumulative standard normal distribution

    Args:
        exercise_cost: Cost to commercialize the patent (strike price K).
        expected_value: Expected value if commercialized (underlying S).
        volatility: Volatility of expected value (0-2, decimal).
        time_to_expiry: Time remaining until patent expires (years).
        risk_free_rate: Risk-free interest rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.

    Example:
        >>> result = option_pricing_patent(
        ...     exercise_cost=5_000_000,
        ...     expected_value=10_000_000,
        ...     volatility=0.40,
        ...     time_to_expiry=10,
        ...     risk_free_rate=0.03,
        ... )
        >>> result["value"] > 5_000_000  # option value > intrinsic
        True

    Reference:
        Trigeorgis, L. (1996). Real Options: Managerial Flexibility and Strategy.
        MIT Press. Chapter 5.
    """
    inputs = OptionPricingInputs(
        exercise_cost=exercise_cost,
        expected_value=expected_value,
        volatility=volatility,
        time_to_expiry=time_to_expiry,
        risk_free_rate=risk_free_rate,
    )

    S = inputs.expected_value  # noqa: N806 (standard Black-Scholes notation)
    K = inputs.exercise_cost  # noqa: N806 (standard Black-Scholes notation)
    sigma = inputs.volatility
    T = inputs.time_to_expiry  # noqa: N806 (standard Black-Scholes notation)
    r = inputs.risk_free_rate

    steps: list[str] = []

    # Black-Scholes calculation
    sqrt_t = math.sqrt(T)
    d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    # Approximation of cumulative normal distribution (Abramowitz & Stegun)
    def norm_cdf(x: float) -> float:
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        sign = 1 if x >= 0 else -1
        x = abs(x)
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x / 2)
        return 0.5 * (1.0 + sign * y)

    n_d1 = norm_cdf(d1)
    n_d2 = norm_cdf(d2)

    option_value = S * n_d1 - K * math.exp(-r * T) * n_d2
    intrinsic_value = max(S - K, 0)
    time_value = option_value - intrinsic_value

    steps.append(f"Expected value (S): {S:,.0f}")
    steps.append(f"Exercise cost (K): {K:,.0f}")
    steps.append(f"Volatility (σ): {sigma:.2%}")
    steps.append(f"Time to expiry (T): {T:.1f} years")
    steps.append(f"Risk-free rate (r): {r:.2%}")
    steps.append(f"d1: {d1:.4f}")
    steps.append(f"d2: {d2:.4f}")
    steps.append(f"N(d1): {n_d1:.4f}")
    steps.append(f"N(d2): {n_d2:.4f}")
    steps.append(f"Intrinsic value (S-K): {intrinsic_value:,.0f}")
    steps.append(f"Time value: {time_value:,.0f}")
    steps.append(f"Option value: {option_value:,.0f}")

    return {
        "value": max(option_value, 0),
        "method": "Real Options (Black-Scholes)",
        "formula_reference": "C = S·N(d1) - K·e^(-rT)·N(d2)",
        "steps": steps,
        "assumptions": {
            "expected_value": S,
            "exercise_cost": K,
            "volatility": sigma,
            "time_to_expiry": T,
            "risk_free_rate": r,
            "d1": round(d1, 4),
            "d2": round(d2, 4),
            "intrinsic_value": intrinsic_value,
            "time_value": round(time_value, 2),
        },
    }
