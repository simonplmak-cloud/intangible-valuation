"""Discount rate construction functions for valuation calculations.

Implements build-up method, CAPM, WACC, tax amortization benefit,
control premium, DLOM (Finnerty), and currency-adjusted discount rates
from Chapters 2, 3, and 4 of the Ascent Partners textbook.

All functions return a ValuationResult dict with:
    - value: The computed discount rate or premium
    - method: The calculation method used
    - formula_reference: Reference to the mathematical formula
    - steps: Step-by-step calculation breakdown
    - assumptions: List of assumptions made during calculation
"""

from __future__ import annotations

import math
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.core.time_value import ValuationResult
from src.utils.constants import (
    METHOD_BUILD_UP,
    METHOD_CAPM,
    METHOD_FINNERTY,
    METHOD_WACC,
)


class DiscountRateInputs(BaseModel):
    """Validated inputs for discount rate calculations."""

    risk_free_rate: float | None = None
    equity_risk_premium: float | None = None
    market_return: float | None = None
    beta: float | None = None
    size_premium: float = 0.0
    industry_risk_premium: float = 0.0
    specific_risk_premium: float = 0.0
    cost_of_equity: float | None = None
    cost_of_debt: float | None = None
    tax_rate: float = 0.25
    equity_value: float | None = None
    debt_value: float | None = None
    useful_life: int | None = None
    asset_value: float | None = None
    minority_price: float | None = None
    control_price: float | None = None
    restricted_period: float | None = None
    volatility: float | None = None
    currency_risk_premium: float = 0.0
    country_risk_premium: float = 0.0
    discount_rate: float | None = None

    @field_validator(
        "risk_free_rate", "equity_risk_premium", "market_return",
        "beta", "size_premium", "industry_risk_premium",
        "specific_risk_premium", "cost_of_equity", "cost_of_debt",
        "tax_rate", "currency_risk_premium", "country_risk_premium",
        "volatility", "discount_rate",
    )
    @classmethod
    def validate_rate(cls, v: float | None) -> float | None:
        if v is not None and v < -1.0:
            raise ValueError("Rate must be >= -1.0")
        if v is not None and v > 10.0:
            raise ValueError("Rate must be <= 10.0 (1000%)")
        return v

    @field_validator("useful_life", "restricted_period")
    @classmethod
    def validate_positive(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("Value must be positive")
        return v


def build_up_discount_rate(
    risk_free_rate: float,
    equity_risk_premium: float,
    size_premium: float = 0.0,
    industry_risk_premium: float = 0.0,
    specific_risk_premium: float = 0.0,
) -> ValuationResult:
    """Calculate discount rate using the build-up method.

    Formula:
        r = Rf + ERP + Size Premium + Industry Risk Premium + Specific Risk Premium

    Parameters:
        risk_free_rate: Risk-free rate (Rf), typically government bond yield
        equity_risk_premium: Equity risk premium (ERP)
        size_premium: Additional premium for company size risk (default 0)
        industry_risk_premium: Additional premium for industry-specific risk (default 0)
        specific_risk_premium: Company-specific risk premium (default 0)

    Returns:
        ValuationResult with computed discount rate

    Raises:
        ValueError: If risk_free_rate or equity_risk_premium is negative

    Book Reference:
        Chapter 2, Section 2.7 — Build-Up Method for Discount Rate
        Commonly used for private company valuations where beta is unavailable
    """
    inputs = DiscountRateInputs(
        risk_free_rate=risk_free_rate,
        equity_risk_premium=equity_risk_premium,
        size_premium=size_premium,
        industry_risk_premium=industry_risk_premium,
        specific_risk_premium=specific_risk_premium,
    )

    rf = inputs.risk_free_rate
    erp = inputs.equity_risk_premium
    sp = inputs.size_premium
    irp = inputs.industry_risk_premium
    srp = inputs.specific_risk_premium

    if rf is None or erp is None:
        raise ValueError("risk_free_rate and equity_risk_premium are required")
    if rf < 0:
        raise ValueError("risk_free_rate must be non-negative")
    if erp < 0:
        raise ValueError("equity_risk_premium must be non-negative")

    rate = rf + erp + sp + irp + srp

    return ValuationResult(
        value=round(rate, 6),
        method=METHOD_BUILD_UP,
        formula_reference="r = Rf + ERP + Size Premium + Industry RP + Specific RP",
        steps=[
            f"Risk-Free Rate (Rf) = {rf:.2%}",
            f"Equity Risk Premium (ERP) = {erp:.2%}",
            f"Size Premium = {sp:.2%}",
            f"Industry Risk Premium = {irp:.2%}",
            f"Specific Risk Premium = {srp:.2%}",
            f"Discount Rate = {rf:.2%} + {erp:.2%} + {sp:.2%} + {irp:.2%} + {srp:.2%} = {rate:.2%}",
        ],
        assumptions=[
            "Risk-free rate reflects long-term government bond yield",
            "Equity risk premium is based on historical market returns",
            "All risk premiums are additive (no interaction effects)",
            "Premiums reflect the specific risk profile of the asset",
        ],
    )


def capm_discount_rate(
    risk_free_rate: float,
    beta: float,
    market_return: float,
) -> ValuationResult:
    """Calculate discount rate using the Capital Asset Pricing Model (CAPM).

    Formula:
        r = Rf + beta * (Rm - Rf)

    Parameters:
        risk_free_rate: Risk-free rate (Rf)
        beta: Systematic risk coefficient (beta)
        market_return: Expected market return (Rm)

    Returns:
        ValuationResult with computed cost of equity

    Raises:
        ValueError: If inputs are invalid

    Book Reference:
        Chapter 2, Section 2.8 — Capital Asset Pricing Model (CAPM)
        Standard approach for publicly traded company cost of equity
    """
    inputs = DiscountRateInputs(
        risk_free_rate=risk_free_rate,
        beta=beta,
        market_return=market_return,
    )

    rf = inputs.risk_free_rate
    b = inputs.beta
    rm = inputs.market_return

    if rf is None or b is None or rm is None:
        raise ValueError("risk_free_rate, beta, and market_return are required")
    if rf < 0:
        raise ValueError("risk_free_rate must be non-negative")
    if rm < rf:
        raise ValueError("market_return must be >= risk_free_rate")

    erp = rm - rf
    rate = rf + b * erp

    return ValuationResult(
        value=round(rate, 6),
        method=METHOD_CAPM,
        formula_reference="r = Rf + beta * (Rm - Rf)",
        steps=[
            f"Risk-Free Rate (Rf) = {rf:.2%}",
            f"Beta = {b:.4f}",
            f"Market Return (Rm) = {rm:.2%}",
            f"Equity Risk Premium (Rm - Rf) = {rm:.2%} - {rf:.2%} = {erp:.2%}",
            f"Cost of Equity = {rf:.2%} + {b:.4f} * {erp:.2%} = {rate:.2%}",
        ],
        assumptions=[
            "Market is efficient and investors are rational",
            "Beta accurately measures systematic risk",
            "CAPM assumptions hold (no taxes, no transaction costs, etc.)",
            "Risk-free rate and market return are expected forward-looking values",
        ],
    )


def wacc(
    equity_value: float,
    debt_value: float,
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float,
) -> ValuationResult:
    """Calculate the Weighted Average Cost of Capital (WACC).

    Formula:
        WACC = (E / V) * Re + (D / V) * Rd * (1 - Tc)
        where V = E + D

    Parameters:
        equity_value: Market value of equity (E)
        debt_value: Market value of debt (D)
        cost_of_equity: Cost of equity (Re)
        cost_of_debt: Pre-tax cost of debt (Rd)
        tax_rate: Corporate tax rate (Tc)

    Returns:
        ValuationResult with computed WACC

    Raises:
        ValueError: If equity_value + debt_value is zero or values are negative

    Book Reference:
        Chapter 2, Section 2.9 — Weighted Average Cost of Capital
        Used for enterprise value and firm-level discount rates
    """
    inputs = DiscountRateInputs(
        equity_value=equity_value,
        debt_value=debt_value,
        cost_of_equity=cost_of_equity,
        cost_of_debt=cost_of_debt,
        tax_rate=tax_rate,
    )

    e = inputs.equity_value
    d = inputs.debt_value
    re = inputs.cost_of_equity
    rd = inputs.cost_of_debt
    tc = inputs.tax_rate

    if e is None or d is None or re is None or rd is None:
        raise ValueError("equity_value, debt_value, cost_of_equity, and cost_of_debt are required")
    if e < 0 or d < 0:
        raise ValueError("equity_value and debt_value must be non-negative")
    if e + d == 0:
        raise ValueError("Total capital (equity + debt) must be positive")
    if tc < 0 or tc > 1:
        raise ValueError("tax_rate must be between 0 and 1")

    v = e + d
    weight_equity = e / v
    weight_debt = d / v
    after_tax_debt = rd * (1 - tc)
    result = weight_equity * re + weight_debt * after_tax_debt

    return ValuationResult(
        value=round(result, 6),
        method=METHOD_WACC,
        formula_reference="WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)",
        steps=[
            f"Equity Value (E) = ${e:,.2f}",
            f"Debt Value (D) = ${d:,.2f}",
            f"Total Capital (V) = ${v:,.2f}",
            f"Weight of Equity (E/V) = {weight_equity:.4f}",
            f"Weight of Debt (D/V) = {weight_debt:.4f}",
            f"Cost of Equity (Re) = {re:.2%}",
            f"Pre-tax Cost of Debt (Rd) = {rd:.2%}",
            f"Tax Rate (Tc) = {tc:.2%}",
            f"After-tax Cost of Debt = {rd:.2%} * (1 - {tc:.2%}) = {after_tax_debt:.2%}",
            f"WACC = {weight_equity:.4f} * {re:.2%} + {weight_debt:.4f} * {after_tax_debt:.2%} = {result:.2%}",
        ],
        assumptions=[
            "Capital structure weights are based on market values",
            "Cost of debt is the pre-tax yield to maturity",
            "Tax shield from debt interest is fully utilized",
            "Capital structure is stable over the projection period",
        ],
    )


def tax_amortization_benefit(
    discount_rate: float,
    useful_life: int,
    tax_rate: float,
    asset_value: float,
) -> ValuationResult:
    """Calculate the present value of the tax amortization benefit (TAB).

    The TAB represents the present value of tax savings from amortizing
    an intangible asset over its useful life.

    Formula:
        TAB = Asset Value * Tax Rate * [1 - (1 + r)^(-n)] / (r * n)

    Parameters:
        discount_rate: The discount rate (r), as a decimal
        useful_life: Amortization period in years (n)
        tax_rate: Corporate tax rate (Tc)
        asset_value: The value of the intangible asset

    Returns:
        ValuationResult with computed TAB value

    Raises:
        ValueError: If inputs are invalid

    Book Reference:
        Chapter 3, Section 3.4 — Tax Amortization Benefit
        Important adjustment in relief-from-royalty and multi-period excess earnings methods
    """
    inputs = DiscountRateInputs(
        discount_rate=discount_rate,
        useful_life=useful_life,
        tax_rate=tax_rate,
        asset_value=asset_value,
    )

    r = inputs.discount_rate
    n = inputs.useful_life
    tc = inputs.tax_rate
    av = inputs.asset_value

    if r is None or n is None or tc is None or av is None:
        raise ValueError("discount_rate, useful_life, tax_rate, and asset_value are required")
    if av < 0:
        raise ValueError("asset_value must be non-negative")
    if n <= 0:
        raise ValueError("useful_life must be positive")
    if tc < 0 or tc > 1:
        raise ValueError("tax_rate must be between 0 and 1")
    if r <= -1:
        raise ValueError("discount_rate must be > -1.0")

    if math.isclose(r, 0.0, abs_tol=1e-12):
        tab = av * tc
        steps = [
            f"Asset Value = ${av:,.2f}",
            f"Tax Rate = {tc:.2%}",
            f"Discount rate ~ 0, TAB = Asset Value * Tax Rate",
            f"TAB = ${av:,.2f} * {tc:.2%} = ${tab:,.2f}",
        ]
    else:
        annuity_factor = (1 - (1 + r) ** (-n)) / (r * n)
        tab = av * tc * annuity_factor
        steps = [
            f"Asset Value = ${av:,.2f}",
            f"Tax Rate = {tc:.2%}",
            f"Discount Rate (r) = {r:.2%}",
            f"Useful Life (n) = {n} years",
            f"Annual Amortization = ${av:,.2f} / {n} = ${av / n:,.2f}",
            f"Annual Tax Savings = ${av / n:,.2f} * {tc:.2%} = ${av / n * tc:,.2f}",
            f"Annuity Factor = [1 - (1 + {r})^(-{n})] / ({r} * {n}) = {annuity_factor:.6f}",
            f"TAB = ${av:,.2f} * {tc:.2%} * {annuity_factor:.6f} = ${tab:,.2f}",
        ]

    return ValuationResult(
        value=round(tab, 2),
        method="Tax Amortization Benefit",
        formula_reference="TAB = Asset Value * Tax Rate * [1 - (1 + r)^(-n)] / (r * n)",
        steps=steps,
        assumptions=[
            "Straight-line amortization over useful life",
            "Tax rate is constant over amortization period",
            "Discount rate reflects the risk of tax savings",
            "Full utilization of tax deductions assumed",
        ],
    )


def control_premium(
    minority_price: float,
    control_price: float,
) -> ValuationResult:
    """Calculate the control premium percentage.

    Formula:
        Control Premium = (Control Price - Minority Price) / Minority Price

    Parameters:
        minority_price: The trading price of minority shares
        control_price: The price paid for a controlling interest

    Returns:
        ValuationResult with computed control premium as a decimal

    Raises:
        ValueError: If prices are non-positive or control_price < minority_price

    Book Reference:
        Chapter 4, Section 4.3 — Control Premium
        Used to convert minority interest value to controlling interest value
    """
    inputs = DiscountRateInputs(
        minority_price=minority_price,
        control_price=control_price,
    )

    mp = inputs.minority_price
    cp = inputs.control_price

    if mp is None or cp is None:
        raise ValueError("minority_price and control_price are required")
    if mp <= 0:
        raise ValueError("minority_price must be positive")
    if cp <= 0:
        raise ValueError("control_price must be positive")
    if cp < mp:
        raise ValueError("control_price must be >= minority_price")

    premium = (cp - mp) / mp

    return ValuationResult(
        value=round(premium, 6),
        method="Control Premium",
        formula_reference="Control Premium = (Control Price - Minority Price) / Minority Price",
        steps=[
            f"Minority Share Price = ${mp:,.2f}",
            f"Control Price = ${cp:,.2f}",
            f"Premium = (${cp:,.2f} - ${mp:,.2f}) / ${mp:,.2f} = {premium:.2%}",
        ],
        assumptions=[
            "Minority price reflects market trading value",
            "Control price reflects value of decision-making power",
            "Premium captures synergies and control benefits",
        ],
    )


def dlom_finnerty(
    restricted_period: float,
    volatility: float,
    risk_free_rate: float,
) -> ValuationResult:
    """Calculate Discount for Lack of Marketability (DLOM) using Finnerty model.

    The Finnerty model uses an average strike put option approach to estimate
    the DLOM based on the cost of hedging the restriction period.

    Formula:
        DLOM = (1 / (r * T)) * [r * T * N(-d2) - (e^(rT) - 1) * N(-d1)]
        where:
            d1 = sigma * sqrt(T) / 2
            d2 = -sigma * sqrt(T) / 2

    Parameters:
        restricted_period: Restriction period in years (T)
        volatility: Annualized stock volatility (sigma)
        risk_free_rate: Risk-free rate (r)

    Returns:
        ValuationResult with computed DLOM as a decimal

    Raises:
        ValueError: If inputs are invalid

    Book Reference:
        Chapter 4, Section 4.4 — Discount for Lack of Marketability (DLOM)
        Finnerty, J.D. "An Average-Strike Put Option Model for DLOM"
    """
    inputs = DiscountRateInputs(
        restricted_period=restricted_period,
        volatility=volatility,
        risk_free_rate=risk_free_rate,
    )

    t = inputs.restricted_period
    sigma = inputs.volatility
    r = inputs.risk_free_rate

    if t is None or sigma is None or r is None:
        raise ValueError("restricted_period, volatility, and risk_free_rate are required")
    if t <= 0:
        raise ValueError("restricted_period must be positive")
    if sigma <= 0:
        raise ValueError("volatility must be positive")
    if sigma > 5.0:
        raise ValueError("volatility seems unreasonably high (> 500%)")
    if r < -1:
        raise ValueError("risk_free_rate must be >= -1.0")

    try:
        from math import exp, sqrt

        sigma_sqrt_t = sigma * sqrt(t)

        d1 = sigma_sqrt_t / 2
        d2 = -sigma_sqrt_t / 2

        n_d1 = _norm_cdf(-d1)
        n_d2 = _norm_cdf(-d2)

        exp_rt = exp(r * t)
        dlom = (1 / (r * t)) * (r * t * n_d2 - (exp_rt - 1) * n_d1)
        dlom = max(0.0, min(1.0, dlom))

    except (OverflowError, ValueError) as e:
        raise ValueError(f"Failed to compute Finnerty DLOM: {e}") from e

    return ValuationResult(
        value=round(dlom, 6),
        method=METHOD_FINNERTY,
        formula_reference="Finnerty Average-Strike Put Option Model",
        steps=[
            f"Restricted Period (T) = {t:.2f} years",
            f"Volatility (sigma) = {sigma:.2%}",
            f"Risk-Free Rate (r) = {r:.2%}",
            f"d1 = sigma*sqrt(T)/2 = {d1:.6f}",
            f"d2 = -sigma*sqrt(T)/2 = {d2:.6f}",
            f"N(-d1) = {n_d1:.6f}",
            f"N(-d2) = {n_d2:.6f}",
            f"DLOM = {dlom:.2%}",
        ],
        assumptions=[
            "Stock price follows geometric Brownian motion",
            "Volatility is constant over restriction period",
            "Restriction is absolute (no trading allowed)",
            "Model assumes European-style option characteristics",
        ],
    )


def _norm_cdf(x: float) -> float:
    """Approximation of the standard normal cumulative distribution function.

    Uses the Abramowitz and Stegun approximation (error < 7.5e-8).
    """
    if x < -10:
        return 0.0
    if x > 10:
        return 1.0

    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    sign = 1 if x >= 0 else -1
    x = abs(x) / math.sqrt(2)

    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

    return 0.5 * (1.0 + sign * y)


def currency_adjusted_discount_rate(
    base_rate: float,
    currency_risk_premium: float = 0.0,
    country_risk_premium: float = 0.0,
) -> ValuationResult:
    """Calculate a discount rate adjusted for currency and country risk.

    Formula:
        r_adjusted = base_rate + Currency Risk Premium + Country Risk Premium

    Parameters:
        base_rate: The base discount rate (e.g., from CAPM or build-up)
        currency_risk_premium: Additional premium for currency risk
        country_risk_premium: Additional premium for country/sovereign risk

    Returns:
        ValuationResult with computed currency-adjusted discount rate

    Raises:
        ValueError: If base_rate < -1 or premiums are negative

    Book Reference:
        Chapter 4, Section 4.5 — International/Currency Risk Adjustments
        Used for cross-border valuations and emerging market assets
    """
    inputs = DiscountRateInputs(
        risk_free_rate=base_rate,
        currency_risk_premium=currency_risk_premium,
        country_risk_premium=country_risk_premium,
    )

    base = inputs.risk_free_rate
    crp = inputs.currency_risk_premium
    ctrp = inputs.country_risk_premium

    if base is None:
        raise ValueError("base_rate is required")
    if base < -1:
        raise ValueError("base_rate must be >= -1.0")
    if crp < 0:
        raise ValueError("currency_risk_premium must be non-negative")
    if ctrp < 0:
        raise ValueError("country_risk_premium must be non-negative")

    adjusted = base + crp + ctrp

    return ValuationResult(
        value=round(adjusted, 6),
        method="Currency-Adjusted Discount Rate",
        formula_reference="r_adjusted = base_rate + Currency RP + Country RP",
        steps=[
            f"Base Discount Rate = {base:.2%}",
            f"Currency Risk Premium = {crp:.2%}",
            f"Country Risk Premium = {ctrp:.2%}",
            f"Adjusted Rate = {base:.2%} + {crp:.2%} + {ctrp:.2%} = {adjusted:.2%}",
        ],
        assumptions=[
            "Base rate reflects the asset's risk in local currency",
            "Currency risk premium captures exchange rate volatility",
            "Country risk premium captures sovereign and political risk",
            "Premiums are additive (no interaction effects)",
        ],
    )
