"""Time value of money functions for valuation calculations.

Implements present value, future value, annuity, perpetuity, growing annuity,
and terminal value calculations from Chapter 2 of the Ascent Partners textbook.

All functions return a ValuationResult dict with:
    - value: The computed result
    - method: The calculation method used
    - formula_reference: Reference to the mathematical formula
    - steps: Step-by-step calculation breakdown
    - assumptions: List of assumptions made during calculation
"""

from __future__ import annotations

import math
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from src.utils.constants import METHOD_EXIT_MULTIPLE, METHOD_GORDON_GROWTH


class ValuationResult(BaseModel):
    """Standardized result container for all valuation calculations."""

    model_config = {"extra": "allow"}

    value: float
    method: str
    formula_reference: str
    steps: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to plain dictionary."""
        return self.model_dump()

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access to result fields."""
        return getattr(self, key)


class TVMInputs(BaseModel):
    """Validated inputs for time value of money calculations."""

    future_value: float | None = None
    present_value: float | None = None
    discount_rate: float | None = None
    periods: int | None = None
    payment: float | None = None
    growth_rate: float | None = None
    perpetual_growth_rate: float | None = None
    exit_multiple: float | None = None
    final_year_cashflow: float | None = None

    @field_validator("discount_rate", "growth_rate", "perpetual_growth_rate")
    @classmethod
    def validate_rate(cls, v: float | None) -> float | None:
        if v is not None and v < -1.0:
            raise ValueError("Rate must be >= -1.0 (cannot lose more than 100%)")
        if v is not None and v > 10.0:
            raise ValueError("Rate must be <= 10.0 (1000%)")
        return v

    @field_validator("periods")
    @classmethod
    def validate_periods(cls, v: int | None) -> int | None:
        if v is not None and v < 0:
            raise ValueError("Periods must be non-negative")
        return v

    @field_validator(
        "future_value", "present_value", "payment",
        "final_year_cashflow", "exit_multiple",
    )
    @classmethod
    def validate_amount(cls, v: float | None) -> float | None:
        if v is not None and math.isnan(v):
            raise ValueError("Amount cannot be NaN")
        return v


def present_value(
    future_value: float,
    discount_rate: float,
    periods: int,
) -> ValuationResult:
    """Calculate the present value of a single future cash flow.

    Formula:
        PV = FV / (1 + r)^n

    Parameters:
        future_value: The future cash flow amount (FV)
        discount_rate: The discount rate per period (r), as a decimal
        periods: Number of periods (n)

    Returns:
        ValuationResult with computed present value

    Raises:
        ValueError: If future_value is negative, discount_rate < -1, or periods < 0

    Book Reference:
        Chapter 2, Section 2.1 — Present Value of a Single Sum
        Chapter 2, Basic Exercise Q1: PV of $500,000 in 8 years at 10% = $233,253
    """
    inputs = TVMInputs(future_value=future_value, discount_rate=discount_rate, periods=periods)

    if inputs.future_value is None or inputs.discount_rate is None or inputs.periods is None:
        raise ValueError("future_value, discount_rate, and periods are required")

    if inputs.future_value < 0:
        raise ValueError("future_value must be non-negative")
    if inputs.discount_rate < -1:
        raise ValueError("discount_rate must be >= -1.0")
    if inputs.periods < 0:
        raise ValueError("periods must be non-negative")

    fv = inputs.future_value
    r = inputs.discount_rate
    n = inputs.periods

    discount_factor = (1 + r) ** n
    pv = fv / discount_factor

    return ValuationResult(
        value=round(pv, 2),
        method="Present Value of Single Sum",
        formula_reference="PV = FV / (1 + r)^n",
        steps=[
            f"Future Value (FV) = ${fv:,.2f}",
            f"Discount Rate (r) = {r:.2%}",
            f"Number of Periods (n) = {n}",
            f"Discount Factor = (1 + {r})^{n} = {discount_factor:,.6f}",
            f"PV = ${fv:,.2f} / {discount_factor:,.6f} = ${pv:,.2f}",
        ],
        assumptions=[
            "Cash flow occurs at end of period",
            "Discount rate is constant across all periods",
            "No intermediate cash flows",
        ],
    )


def future_value(
    present_value: float,
    discount_rate: float,
    periods: int,
) -> ValuationResult:
    """Calculate the future value of a present amount.

    Formula:
        FV = PV * (1 + r)^n

    Parameters:
        present_value: The present amount (PV)
        discount_rate: The growth/discount rate per period (r), as a decimal
        periods: Number of periods (n)

    Returns:
        ValuationResult with computed future value

    Raises:
        ValueError: If present_value is negative, discount_rate < -1, or periods < 0

    Book Reference:
        Chapter 2, Section 2.2 — Future Value of a Single Sum
        Chapter 2, Basic Exercise Q2: FV $1M, PV $620,921, 5 years -> discount rate = 10%
    """
    inputs = TVMInputs(present_value=present_value, discount_rate=discount_rate, periods=periods)

    if inputs.present_value is None or inputs.discount_rate is None or inputs.periods is None:
        raise ValueError("present_value, discount_rate, and periods are required")

    if inputs.present_value < 0:
        raise ValueError("present_value must be non-negative")
    if inputs.discount_rate < -1:
        raise ValueError("discount_rate must be >= -1.0")
    if inputs.periods < 0:
        raise ValueError("periods must be non-negative")

    pv = inputs.present_value
    r = inputs.discount_rate
    n = inputs.periods

    compounding_factor = (1 + r) ** n
    fv = pv * compounding_factor

    return ValuationResult(
        value=round(fv, 2),
        method="Future Value of Single Sum",
        formula_reference="FV = PV * (1 + r)^n",
        steps=[
            f"Present Value (PV) = ${pv:,.2f}",
            f"Rate (r) = {r:.2%}",
            f"Number of Periods (n) = {n}",
            f"Compounding Factor = (1 + {r})^{n} = {compounding_factor:,.6f}",
            f"FV = ${pv:,.2f} * {compounding_factor:,.6f} = ${fv:,.2f}",
        ],
        assumptions=[
            "Compounding occurs at end of each period",
            "Rate is constant across all periods",
            "No intermediate withdrawals or additions",
        ],
    )


def annuity_pv(
    payment: float,
    discount_rate: float,
    periods: int,
) -> ValuationResult:
    """Calculate the present value of an ordinary annuity.

    Formula:
        PV = PMT * [1 - (1 + r)^(-n)] / r

    Parameters:
        payment: The periodic payment amount (PMT)
        discount_rate: The discount rate per period (r), as a decimal
        periods: Number of periods (n)

    Returns:
        ValuationResult with computed annuity present value

    Raises:
        ValueError: If payment is negative, discount_rate <= -1 or == 0, or periods < 0

    Book Reference:
        Chapter 2, Section 2.3 — Present Value of an Annuity
        Chapter 2, Intermediate Exercise Q1: Annuity $50,000 for 10 years at 15% = $250,937
    """
    inputs = TVMInputs(payment=payment, discount_rate=discount_rate, periods=periods)

    if inputs.payment is None or inputs.discount_rate is None or inputs.periods is None:
        raise ValueError("payment, discount_rate, and periods are required")

    if inputs.payment < 0:
        raise ValueError("payment must be non-negative")
    if inputs.discount_rate <= -1:
        raise ValueError("discount_rate must be > -1.0")
    if math.isclose(inputs.discount_rate, 0.0, abs_tol=1e-12):
        raise ValueError("discount_rate cannot be zero for annuity calculation")
    if inputs.periods < 0:
        raise ValueError("periods must be non-negative")

    pmt = inputs.payment
    r = inputs.discount_rate
    n = inputs.periods

    annuity_factor = (1 - (1 + r) ** (-n)) / r
    pv = pmt * annuity_factor

    return ValuationResult(
        value=round(pv, 2),
        method="Present Value of Ordinary Annuity",
        formula_reference="PV = PMT * [1 - (1 + r)^(-n)] / r",
        steps=[
            f"Payment (PMT) = ${pmt:,.2f}",
            f"Discount Rate (r) = {r:.2%}",
            f"Number of Periods (n) = {n}",
            f"Annuity Factor = [1 - (1 + {r})^(-{n})] / {r} = {annuity_factor:,.6f}",
            f"PV = ${pmt:,.2f} * {annuity_factor:,.6f} = ${pv:,.2f}",
        ],
        assumptions=[
            "Payments occur at end of each period (ordinary annuity)",
            "Payment amount is constant",
            "Discount rate is constant across all periods",
        ],
    )


def perpetuity_pv(
    payment: float,
    discount_rate: float,
) -> ValuationResult:
    """Calculate the present value of a perpetuity.

    Formula:
        PV = PMT / r

    Parameters:
        payment: The periodic payment amount (PMT)
        discount_rate: The discount rate per period (r), as a decimal

    Returns:
        ValuationResult with computed perpetuity present value

    Raises:
        ValueError: If payment is negative or discount_rate <= 0

    Book Reference:
        Chapter 2, Section 2.4 — Present Value of a Perpetuity
        Chapter 3, Royalty Relief: $10M revenue, 4% royalty, 15% discount = $2,666,667
    """
    inputs = TVMInputs(payment=payment, discount_rate=discount_rate)

    if inputs.payment is None or inputs.discount_rate is None:
        raise ValueError("payment and discount_rate are required")

    if inputs.payment < 0:
        raise ValueError("payment must be non-negative")
    if inputs.discount_rate <= 0:
        raise ValueError("discount_rate must be positive for perpetuity calculation")

    pmt = inputs.payment
    r = inputs.discount_rate

    pv = pmt / r

    return ValuationResult(
        value=round(pv, 2),
        method="Present Value of Perpetuity",
        formula_reference="PV = PMT / r",
        steps=[
            f"Payment (PMT) = ${pmt:,.2f}",
            f"Discount Rate (r) = {r:.2%}",
            f"PV = ${pmt:,.2f} / {r} = ${pv:,.2f}",
        ],
        assumptions=[
            "Payments continue indefinitely (perpetual)",
            "Payment amount is constant",
            "Discount rate is constant",
            "First payment occurs one period from now",
        ],
    )


def growing_annuity_pv(
    payment: float,
    discount_rate: float,
    growth_rate: float,
    periods: int,
) -> ValuationResult:
    """Calculate the present value of a growing annuity.

    Formula (when r != g):
        PV = PMT * [1 - ((1 + g) / (1 + r))^n] / (r - g)

    Formula (when r == g):
        PV = PMT * n / (1 + r)

    Parameters:
        payment: The first period payment amount (PMT)
        discount_rate: The discount rate per period (r), as a decimal
        growth_rate: The growth rate of payments per period (g), as a decimal
        periods: Number of periods (n)

    Returns:
        ValuationResult with computed growing annuity present value

    Raises:
        ValueError: If payment is negative, periods < 0, or r < -1, g < -1

    Book Reference:
        Chapter 2, Section 2.5 — Present Value of a Growing Annuity
    """
    inputs = TVMInputs(
        payment=payment, discount_rate=discount_rate,
        growth_rate=growth_rate, periods=periods,
    )

    if (inputs.payment is None or inputs.discount_rate is None
            or inputs.growth_rate is None or inputs.periods is None):
        raise ValueError("payment, discount_rate, growth_rate, and periods are required")

    if inputs.payment < 0:
        raise ValueError("payment must be non-negative")
    if inputs.discount_rate < -1:
        raise ValueError("discount_rate must be >= -1.0")
    if inputs.growth_rate < -1:
        raise ValueError("growth_rate must be >= -1.0")
    if inputs.periods < 0:
        raise ValueError("periods must be non-negative")

    pmt = inputs.payment
    r = inputs.discount_rate
    g = inputs.growth_rate
    n = inputs.periods

    if math.isclose(r, g, abs_tol=1e-12):
        pv = pmt * n / (1 + r)
        formula_used = "PV = PMT * n / (1 + r) [special case: r = g]"
        steps = [
            f"Payment (PMT) = ${pmt:,.2f}",
            f"Discount Rate (r) = {r:.2%}",
            f"Growth Rate (g) = {g:.2%}",
            f"Number of Periods (n) = {n}",
            f"Special case: r = g, using PV = PMT * n / (1 + r)",
            f"PV = ${pmt:,.2f} * {n} / (1 + {r}) = ${pv:,.2f}",
        ]
    else:
        ratio = (1 + g) / (1 + r)
        pv = pmt * (1 - ratio ** n) / (r - g)
        formula_used = "PV = PMT * [1 - ((1 + g) / (1 + r))^n] / (r - g)"
        steps = [
            f"Payment (PMT) = ${pmt:,.2f}",
            f"Discount Rate (r) = {r:.2%}",
            f"Growth Rate (g) = {g:.2%}",
            f"Number of Periods (n) = {n}",
            f"Ratio (1+g)/(1+r) = {ratio:.6f}",
            f"PV = ${pmt:,.2f} * [1 - {ratio:.6f}^{n}] / ({r} - {g}) = ${pv:,.2f}",
        ]

    return ValuationResult(
        value=round(pv, 2),
        method="Present Value of Growing Annuity",
        formula_reference=formula_used,
        steps=steps,
        assumptions=[
            "First payment occurs at end of period 1",
            "Payments grow at constant rate g",
            "Discount rate is constant",
            f"Payment grows from ${pmt:,.2f} in period 1 to ${pmt * (1 + g) ** (n - 1):,.2f} in period {n}",
        ],
    )


def terminal_value(
    final_year_cashflow: float,
    perpetual_growth_rate: float,
    discount_rate: float,
    method: Literal["gordon_growth", "exit_multiple"] = "gordon_growth",
    exit_multiple: float | None = None,
) -> ValuationResult:
    """Calculate terminal value using Gordon Growth or Exit Multiple method.

    Gordon Growth Formula:
        TV = FCF * (1 + g) / (r - g)

    Exit Multiple Formula:
        TV = FCF * Exit Multiple

    Parameters:
        final_year_cashflow: The final year projected cash flow (FCF)
        perpetual_growth_rate: The perpetual growth rate (g), as a decimal
        discount_rate: The discount rate (r), as a decimal
        method: Calculation method ("gordon_growth" or "exit_multiple")
        exit_multiple: Required when method="exit_multiple"

    Returns:
        ValuationResult with computed terminal value

    Raises:
        ValueError: If parameters are invalid for the chosen method

    Book Reference:
        Chapter 2, Section 2.6 — Terminal Value Calculations
        Chapter 5, DCF Methodology — Terminal Value in Multi-Period DCF
    """
    inputs = TVMInputs(
        final_year_cashflow=final_year_cashflow,
        perpetual_growth_rate=perpetual_growth_rate,
        discount_rate=discount_rate,
        exit_multiple=exit_multiple,
    )

    if inputs.final_year_cashflow is None or inputs.perpetual_growth_rate is None or inputs.discount_rate is None:
        raise ValueError("final_year_cashflow, perpetual_growth_rate, and discount_rate are required")

    if inputs.final_year_cashflow < 0:
        raise ValueError("final_year_cashflow must be non-negative")
    if inputs.discount_rate <= -1:
        raise ValueError("discount_rate must be > -1.0")

    fcf = inputs.final_year_cashflow
    g = inputs.perpetual_growth_rate
    r = inputs.discount_rate

    if method == METHOD_GORDON_GROWTH:
        if r <= g:
            raise ValueError(
                f"discount_rate ({r:.2%}) must be greater than perpetual_growth_rate ({g:.2%}) "
                "for Gordon Growth model"
            )

        tv = fcf * (1 + g) / (r - g)

        return ValuationResult(
            value=round(tv, 2),
            method="Gordon Growth Model",
            formula_reference="TV = FCF * (1 + g) / (r - g)",
            steps=[
                f"Final Year Cash Flow (FCF) = ${fcf:,.2f}",
                f"Perpetual Growth Rate (g) = {g:.2%}",
                f"Discount Rate (r) = {r:.2%}",
                f"Next Year Cash Flow = ${fcf:,.2f} * (1 + {g}) = ${fcf * (1 + g):,.2f}",
                f"TV = ${fcf * (1 + g):,.2f} / ({r} - {g}) = ${tv:,.2f}",
            ],
            assumptions=[
                "Cash flows grow at constant perpetual rate g",
                "Discount rate exceeds growth rate (r > g)",
                "Terminal value is calculated at end of projection period",
                "Growth rate is sustainable in perpetuity (typically <= long-term GDP growth)",
            ],
        )

    elif method == METHOD_EXIT_MULTIPLE:
        if exit_multiple is None:
            raise ValueError("exit_multiple is required when method='exit_multiple'")
        if exit_multiple <= 0:
            raise ValueError("exit_multiple must be positive")

        tv = fcf * exit_multiple

        return ValuationResult(
            value=round(tv, 2),
            method="Exit Multiple Method",
            formula_reference="TV = FCF * Exit Multiple",
            steps=[
                f"Final Year Cash Flow (FCF) = ${fcf:,.2f}",
                f"Exit Multiple = {exit_multiple:.2f}x",
                f"TV = ${fcf:,.2f} * {exit_multiple:.2f} = ${tv:,.2f}",
            ],
            assumptions=[
                "Exit multiple is based on comparable company analysis",
                "Multiple reflects market conditions at terminal date",
                "Terminal value is calculated at end of projection period",
            ],
        )

    else:
        raise ValueError(f"Unknown method: {method}. Use 'gordon_growth' or 'exit_multiple'")


def present_value_of_series(
    cash_flows: list[float],
    discount_rate: float,
) -> ValuationResult:
    """Calculate present value of a series of uneven cash flows.

    Formula:
        PV = sum(CF_t / (1 + r)^t) for t = 1 to n

    Parameters:
        cash_flows: List of cash flows for each period (index 0 = period 1)
        discount_rate: The discount rate (r), as a decimal

    Returns:
        ValuationResult with computed present value and per-period breakdown

    Raises:
        ValueError: If cash_flows is empty or discount_rate is invalid

    Book Reference:
        Chapter 2, Section 2.1 — Present Value (general case)
        Chapter 4 — Used in all income-based methods
    """
    if not cash_flows:
        raise ValueError("cash_flows must not be empty")
    if discount_rate <= -1:
        raise ValueError("discount_rate must be > -1.0")

    pv = 0.0
    steps = []
    pv_by_period = []
    steps.append(f"Discount Rate (r) = {discount_rate:.2%}")
    steps.append(f"Number of Periods = {len(cash_flows)}")

    for t, cf in enumerate(cash_flows, 1):
        period_pv = cf / (1 + discount_rate) ** t
        pv += period_pv
        pv_by_period.append({
            "period": t,
            "cash_flow": cf,
            "present_value": round(period_pv, 2),
        })
        steps.append(f"Period {t}: CF=${cf:,.2f} / (1+{discount_rate})^{t} = ${period_pv:,.2f}")

    steps.append(f"Total PV = ${pv:,.2f}")

    return ValuationResult(
        value=round(pv, 2),
        method="Present Value of Cash Flow Series",
        formula_reference="PV = sum(CF_t / (1 + r)^t)",
        steps=steps,
        assumptions=[
            "Cash flows occur at end of each period",
            f"Discount rate is constant at {discount_rate:.2%}",
            f"Projection period is {len(cash_flows)} years",
        ],
        present_value=round(pv, 2),
        pv_by_period=pv_by_period,
    )
