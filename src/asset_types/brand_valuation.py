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


class BrandStrengthInputs(BaseModel):
    """Inputs for brand strength index calculation."""

    revenue_stability: float = Field(ge=0, le=1, description="Revenue stability score (0-1)")
    market_share: float = Field(ge=0, le=1, description="Market share score (0-1)")
    geographic_reach: float = Field(ge=0, le=1, description="Geographic reach score (0-1)")
    customer_loyalty: float = Field(ge=0, le=1, description="Customer loyalty score (0-1)")
    investment_level: float = Field(ge=0, le=1, description="Brand investment level score (0-1)")


def brand_strength_index(
    revenue_stability: float,
    market_share: float,
    geographic_reach: float,
    customer_loyalty: float,
    investment_level: float,
) -> dict:
    """Calculate composite brand strength score on a 0-100 scale.

    Combines five dimensions of brand strength using weighted scoring:
    - Revenue stability (25%): Consistency and predictability of brand revenue
    - Market share (25%): Relative position in the market
    - Geographic reach (20%): Breadth of market coverage
    - Customer loyalty (20%): Retention and advocacy metrics
    - Investment level (10%): Ongoing brand investment and support

    Formula:
        BSI = (RS x 0.25 + MS x 0.25 + GR x 0.20 + CL x 0.20 + IL x 0.10) x 100

    Args:
        revenue_stability: Revenue stability score (0-1).
        market_share: Market share score (0-1).
        geographic_reach: Geographic reach score (0-1).
        customer_loyalty: Customer loyalty score (0-1).
        investment_level: Brand investment level score (0-1).

    Returns:
        Dict with value (0-100), method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is outside [0, 1].

    Example:
        >>> result = brand_strength_index(0.8, 0.6, 0.7, 0.9, 0.5)
        >>> result["value"]
        72.0
    """
    inputs = BrandStrengthInputs(
        revenue_stability=revenue_stability,
        market_share=market_share,
        geographic_reach=geographic_reach,
        customer_loyalty=customer_loyalty,
        investment_level=investment_level,
    )

    weights = {
        "revenue_stability": 0.25,
        "market_share": 0.25,
        "geographic_reach": 0.20,
        "customer_loyalty": 0.20,
        "investment_level": 0.10,
    }

    scores = {
        "revenue_stability": inputs.revenue_stability,
        "market_share": inputs.market_share,
        "geographic_reach": inputs.geographic_reach,
        "customer_loyalty": inputs.customer_loyalty,
        "investment_level": inputs.investment_level,
    }

    steps: list[str] = []
    weighted_sum = 0.0
    for name, weight in weights.items():
        contribution = scores[name] * weight
        weighted_sum += contribution
        steps.append(f"{name}: {scores[name]:.2f} x {weight:.0%} = {contribution:.4f}")

    bsi_score = weighted_sum * 100

    # Rating classification
    if bsi_score >= 80:
        rating = "Excellent"
    elif bsi_score >= 60:
        rating = "Strong"
    elif bsi_score >= 40:
        rating = "Moderate"
    elif bsi_score >= 20:
        rating = "Weak"
    else:
        rating = "Very Weak"

    steps.append(f"Weighted sum: {weighted_sum:.4f}")
    steps.append(f"Brand Strength Index: {bsi_score:.1f}/100 ({rating})")

    return {
        "value": bsi_score,
        "method": "Composite Brand Strength Index",
        "formula_reference": "BSI = sum(Factor_i x Weight_i) x 100",
        "steps": steps,
        "assumptions": {
            "weights": weights,
            "scores": scores,
            "rating": rating,
        },
    }


class InterbrandInputs(BaseModel):
    """Inputs for Interbrand brand valuation."""

    brand_earnings: float = Field(gt=0, description="Brand earnings (after-tax operating profit)")
    role_of_brand_index: float = Field(ge=0, le=1, description="Role of Brand index (0-1)")
    brand_strength_score: float = Field(ge=0, le=100, description="Brand strength score (0-100)")
    discount_rate: float = Field(gt=0, description="Discount rate (decimal)")


def interbrand_brand_valuation(
    brand_earnings: float,
    role_of_brand_index: float,
    brand_strength_score: float,
    discount_rate: float,
) -> dict:
    """Value a brand using the Interbrand methodology.

    The Interbrand method calculates brand value as:
        Brand Value = Branded Earnings x Brand Multiple

    Where:
        Branded Earnings = Brand Earnings x Role of Brand Index
        Brand Multiple = derived from Brand Strength Score via discount rate

    The brand strength score (0-100) maps to a discount rate via the
    brand-specific discount rate curve. Stronger brands have lower discount
    rates, resulting in higher multiples.

    Formula:
        Branded Earnings = Earnings x ROBI
        Brand Multiple = 1 / (discount_rate - g)  [Gordon Growth approximation]
        Brand Value = Branded Earnings x Brand Multiple

    Args:
        brand_earnings: After-tax operating profit attributable to the brand.
        role_of_brand_index: Proportion of purchase decision driven by brand (0-1).
        brand_strength_score: Brand strength score from 0-100.
        discount_rate: Brand-specific discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.

    Example:
        >>> result = interbrand_brand_valuation(
        ...     brand_earnings=50_000_000,
        ...     role_of_brand_index=0.60,
        ...     brand_strength_score=75,
        ...     discount_rate=0.08,
        ... )
        >>> result["value"] > 0
        True

    Reference:
        Interbrand. "Best Global Brands Methodology."
        https://interbrand.com/best-brands/
    """
    inputs = InterbrandInputs(
        brand_earnings=brand_earnings,
        role_of_brand_index=role_of_brand_index,
        brand_strength_score=brand_strength_score,
        discount_rate=discount_rate,
    )

    steps: list[str] = []

    # Step 1: Calculate branded earnings
    branded_earnings = inputs.brand_earnings * inputs.role_of_brand_index
    steps.append(f"Brand earnings: {inputs.brand_earnings:,.0f}")
    steps.append(f"Role of Brand Index: {inputs.role_of_brand_index:.2%}")
    steps.append(f"Branded earnings: {branded_earnings:,.0f}")

    # Step 2: Map brand strength to brand multiple
    # Interbrand uses an S-curve: stronger brands get higher multiples
    # Approximate: multiple = strength_score / (discount_rate * 100)
    brand_multiple = inputs.brand_strength_score / (inputs.discount_rate * 100)
    steps.append(f"Brand strength score: {inputs.brand_strength_score:.0f}/100")
    steps.append(f"Discount rate: {inputs.discount_rate:.2%}")
    steps.append(f"Brand multiple: {brand_multiple:.2f}x")

    # Step 3: Calculate brand value
    brand_value = branded_earnings * brand_multiple
    steps.append(f"Brand value: {brand_value:,.0f}")

    return {
        "value": brand_value,
        "method": "Interbrand Brand Valuation",
        "formula_reference": "BV = (Earnings x ROBI) x (BS / (r x 100))",
        "steps": steps,
        "assumptions": {
            "brand_earnings": inputs.brand_earnings,
            "role_of_brand_index": inputs.role_of_brand_index,
            "brand_strength_score": inputs.brand_strength_score,
            "discount_rate": inputs.discount_rate,
            "brand_multiple": round(brand_multiple, 2),
        },
    }


class BrandRoyaltyInputs(BaseModel):
    """Inputs for brand royalty rate from comparables."""

    comparable_rates: list[float] = Field(
        min_length=1, description="Comparable brand royalty rates"
    )
    brand_strength_adjustment: float = Field(
        ge=-0.5, le=0.5, description="Adjustment for brand strength relative to comparables"
    )


def brand_royalty_rate_from_comparables(
    comparable_rates: Sequence[float],
    brand_strength_adjustment: float = 0.0,
) -> dict:
    """Derive brand royalty rate from comparable brand licensing agreements.

    Calculates a base rate from comparable transactions (median), then
    adjusts for the subject brand's relative strength. A stronger brand
    commands a higher rate; a weaker brand commands a lower rate.

    Formula:
        Base Rate = Median(comparable_rates)
        Adjusted Rate = Base Rate x (1 + brand_strength_adjustment)

    Args:
        comparable_rates: List of comparable brand royalty rates (as decimals).
        brand_strength_adjustment: Adjustment factor (-0.5 to +0.5).
            Positive for stronger brands, negative for weaker.

    Returns:
        Dict with value (royalty rate), method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If comparable_rates is empty or adjustment is out of range.

    Example:
        >>> rates = [0.03, 0.04, 0.05, 0.06, 0.04]
        >>> result = brand_royalty_rate_from_comparables(rates, 0.10)
        >>> result["value"]  # 0.04 * 1.10 = 0.044
        0.044
    """
    rates = list(comparable_rates)
    if not rates:
        raise ValueError("Comparable rates list cannot be empty")

    inputs = BrandRoyaltyInputs(
        comparable_rates=rates,
        brand_strength_adjustment=brand_strength_adjustment,
    )

    steps: list[str] = []

    # Calculate statistics
    sorted_rates = sorted(rates)
    n = len(sorted_rates)
    median_rate = sorted_rates[n // 2] if n % 2 == 1 else (sorted_rates[n // 2 - 1] + sorted_rates[n // 2]) / 2
    mean_rate = sum(rates) / n
    min_rate = min(rates)
    max_rate = max(rates)

    steps.append(f"Number of comparables: {n}")
    steps.append(f"Rate range: {min_rate:.2%} - {max_rate:.2%}")
    steps.append(f"Mean rate: {mean_rate:.4f}")
    steps.append(f"Median rate: {median_rate:.4f}")

    # Apply brand strength adjustment
    adjusted_rate = median_rate * (1 + inputs.brand_strength_adjustment)
    adjusted_rate = max(0.0, adjusted_rate)  # floor at zero

    steps.append(f"Brand strength adjustment: {inputs.brand_strength_adjustment:+.0%}")
    steps.append(f"Adjusted royalty rate: {adjusted_rate:.4f} ({adjusted_rate:.2%})")

    return {
        "value": adjusted_rate,
        "method": "Comparable Brand Royalty Rate",
        "formula_reference": "Rate = Median(comparables) x (1 + adjustment)",
        "steps": steps,
        "assumptions": {
            "num_comparables": n,
            "min_rate": min_rate,
            "max_rate": max_rate,
            "mean_rate": round(mean_rate, 4),
            "median_rate": median_rate,
            "brand_strength_adjustment": inputs.brand_strength_adjustment,
        },
    }
