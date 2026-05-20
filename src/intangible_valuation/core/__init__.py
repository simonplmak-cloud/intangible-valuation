"""Core mathematical foundations for valuation calculations.

Implements time value of money, discount rate construction,
and statistical methods from Chapter 2 and Appendix A.
"""

from __future__ import annotations

from collections.abc import Sequence

from intangible_valuation.core.time_value import ValuationResult as ValuationResult


def present_value(
    future_value: float, discount_rate: float, periods: int
) -> float:
    """Calculate present value of a single future cash flow."""
    if future_value < 0:
        raise ValueError("Future value must be non-negative")
    if discount_rate < 0:
        raise ValueError("Discount rate must be non-negative")
    if periods < 0:
        raise ValueError("Periods must be non-negative")
    return future_value / ((1 + discount_rate) ** periods)


def present_value_of_annuity(
    payment: float, discount_rate: float, periods: int
) -> float:
    """Calculate present value of an annuity (equal periodic payments)."""
    if payment < 0:
        raise ValueError("Payment must be non-negative")
    if discount_rate < 0:
        raise ValueError("Discount rate must be non-negative")
    if periods < 0:
        raise ValueError("Periods must be non-negative")
    if discount_rate == 0:
        return payment * periods
    return payment * (1 - (1 + discount_rate) ** -periods) / discount_rate


def present_value_of_growing_annuity(
    first_payment: float,
    discount_rate: float,
    growth_rate: float,
    periods: int,
) -> float:
    """Calculate present value of a growing annuity."""
    if first_payment < 0:
        raise ValueError("First payment must be non-negative")
    if discount_rate < 0:
        raise ValueError("Discount rate must be non-negative")
    if periods < 0:
        raise ValueError("Periods must be non-negative")
    if discount_rate == growth_rate:
        return first_payment * periods / (1 + discount_rate)
    return first_payment * (
        1 - ((1 + growth_rate) / (1 + discount_rate)) ** periods
    ) / (discount_rate - growth_rate)


def discount_factor(discount_rate: float, period: int) -> float:
    """Calculate discount factor for a given period."""
    if discount_rate < 0:
        raise ValueError("Discount rate must be non-negative")
    if period < 0:
        raise ValueError("Period must be non-negative")
    return 1 / ((1 + discount_rate) ** period)


def risk_adjusted_value(
    base_value: float, probability_of_success: float
) -> float:
    """Apply probability weighting to a base value."""
    if base_value < 0:
        raise ValueError("Base value must be non-negative")
    if not 0 <= probability_of_success <= 1:
        raise ValueError("Probability must be between 0 and 1")
    return base_value * probability_of_success


def terminal_value(
    final_cash_flow: float,
    perpetual_growth_rate: float,
    discount_rate: float,
) -> float:
    """Calculate terminal value using Gordon Growth Model."""
    if final_cash_flow < 0:
        raise ValueError("Final cash flow must be non-negative")
    if discount_rate <= perpetual_growth_rate:
        raise ValueError(
            "Discount rate must exceed perpetual growth rate"
        )
    return (
        final_cash_flow * (1 + perpetual_growth_rate)
    ) / (discount_rate - perpetual_growth_rate)


def weighted_average(
    values: Sequence[float], weights: Sequence[float]
) -> float:
    """Calculate weighted average."""
    if len(values) != len(weights):
        raise ValueError("Values and weights must have same length")
    if any(w < 0 for w in weights):
        raise ValueError("Weights must be non-negative")
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("Total weight must be positive")
    return sum(v * w for v, w in zip(values, weights, strict=False)) / total_weight
