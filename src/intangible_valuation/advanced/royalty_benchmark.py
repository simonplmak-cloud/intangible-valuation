"""Royalty rate benchmarking and adjustment.

Implements Section 6.1-6.3 and Appendix A.10:
- Built-in benchmark database for common IP types and industries
- 25% rule for royalty rate estimation
- Adjustment factors for customizing base rates
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from intangible_valuation.core import ValuationResult, present_value_of_annuity

VALID_IP_TYPES = {"patent", "trademark", "copyright", "trade_secret", "technology"}

BENCHMARK_DATABASE: dict[str, dict[str, dict]] = {
    "patent": {
        "pharmaceutical": {"min_rate": 0.05, "max_rate": 0.15, "median": 0.08, "source": "RoyaltyStat, ktMINE"},
        "technology": {"min_rate": 0.02, "max_rate": 0.10, "median": 0.05, "source": "RoyaltyStat, ktMINE"},
        "biotechnology": {"min_rate": 0.05, "max_rate": 0.12, "median": 0.07, "source": "RoyaltyStat, ktMINE"},
        "manufacturing": {"min_rate": 0.01, "max_rate": 0.05, "median": 0.03, "source": "RoyaltyStat"},
        "chemical": {"min_rate": 0.02, "max_rate": 0.06, "median": 0.04, "source": "RoyaltyStat"},
        "general": {"min_rate": 0.02, "max_rate": 0.08, "median": 0.05, "source": "Industry average"},
    },
    "trademark": {
        "consumer_goods": {"min_rate": 0.02, "max_rate": 0.08, "median": 0.04, "source": "RoyaltyStat, ktMINE"},
        "retail": {"min_rate": 0.01, "max_rate": 0.05, "median": 0.03, "source": "RoyaltyStat"},
        "food_beverage": {"min_rate": 0.02, "max_rate": 0.06, "median": 0.04, "source": "RoyaltyStat"},
        "luxury": {"min_rate": 0.05, "max_rate": 0.12, "median": 0.08, "source": "ktMINE"},
        "general": {"min_rate": 0.02, "max_rate": 0.06, "median": 0.04, "source": "Industry average"},
    },
    "copyright": {
        "media_entertainment": {"min_rate": 0.05, "max_rate": 0.15, "median": 0.10, "source": "RoyaltyStat"},
        "software": {"min_rate": 0.05, "max_rate": 0.20, "median": 0.10, "source": "RoyaltyStat, ktMINE"},
        "publishing": {"min_rate": 0.05, "max_rate": 0.15, "median": 0.08, "source": "RoyaltyStat"},
        "music": {"min_rate": 0.05, "max_rate": 0.15, "median": 0.10, "source": "Industry average"},
        "general": {"min_rate": 0.05, "max_rate": 0.12, "median": 0.08, "source": "Industry average"},
    },
    "trade_secret": {
        "technology": {"min_rate": 0.02, "max_rate": 0.08, "median": 0.05, "source": "ktMINE"},
        "pharmaceutical": {"min_rate": 0.03, "max_rate": 0.10, "median": 0.06, "source": "ktMINE"},
        "manufacturing": {"min_rate": 0.01, "max_rate": 0.05, "median": 0.03, "source": "Industry average"},
        "general": {"min_rate": 0.02, "max_rate": 0.06, "median": 0.04, "source": "Industry average"},
    },
    "technology": {
        "software": {"min_rate": 0.05, "max_rate": 0.20, "median": 0.10, "source": "RoyaltyStat, ktMINE"},
        "semiconductor": {"min_rate": 0.01, "max_rate": 0.05, "median": 0.03, "source": "RoyaltyStat"},
        "telecommunications": {"min_rate": 0.01, "max_rate": 0.05, "median": 0.03, "source": "RoyaltyStat"},
        "general": {"min_rate": 0.03, "max_rate": 0.10, "median": 0.05, "source": "Industry average"},
    },
}


class RoyaltyBenchmarkInput(BaseModel):
    ip_type: str = Field(pattern=f"^({'|'.join(VALID_IP_TYPES)})$", description="Type of IP")
    industry: str = Field(min_length=1, description="Industry sector")


class RoyaltyAdjustmentInput(BaseModel):
    base_rate: float = Field(gt=0, le=1, description="Base royalty rate")


class TwentyFivePercentInput(BaseModel):
    licensee_expected_profit: float = Field(gt=0, description="Licensee's expected profit from IP")
    profit_attribution_to_ip: float = Field(ge=0, le=1, description="Fraction of profit attributable to IP")


def royalty_rate_benchmark(
    ip_type: str,
    industry: str,
    comparable_database: list[dict] | None = None,
) -> ValuationResult:
    """Get benchmark royalty rate range by IP type and industry.

    Uses built-in benchmark database compiled from RoyaltyStat, ktMINE,
    and industry surveys. Can be supplemented with user-provided comparables.

    Args:
        ip_type: One of "patent", "trademark", "copyright", "trade_secret", "technology".
        industry: Industry sector name.
        comparable_database: Optional list of {"rate": float, "source": str} for custom comparables.

    Returns:
        ValuationResult with recommended rate range, median, and source data.

    Raises:
        ValueError: If ip_type is invalid.

    Example:
        >>> result = royalty_rate_benchmark("patent", "pharmaceutical")
        >>> result.assumptions["recommended_range"]
        (0.05, 0.15)
    """
    RoyaltyBenchmarkInput(ip_type=ip_type, industry=industry)

    ip_data = BENCHMARK_DATABASE.get(ip_type, {})
    industry_data = ip_data.get(industry.lower(), ip_data.get("general", {}))

    if not industry_data:
        industry_data = {"min_rate": 0.02, "max_rate": 0.08, "median": 0.05, "source": "Default benchmark"}

    min_rate = industry_data["min_rate"]
    max_rate = industry_data["max_rate"]
    median_rate = industry_data["median"]
    source = industry_data["source"]

    if comparable_database:
        user_rates = [c["rate"] for c in comparable_database if "rate" in c]
        if user_rates:
            min_rate = min(min_rate, *user_rates)
            max_rate = max(max_rate, *user_rates)
            median_rate = sorted(user_rates)[len(user_rates) // 2]
            source = f"{source}; User comparables ({len(user_rates)} entries)"

    steps = [
        {"step": 1, "description": f"IP Type: {ip_type}"},
        {"step": 2, "description": f"Industry: {industry}"},
        {"step": 3, "description": f"Benchmark source: {source}"},
        {"step": 4, "description": "Recommended range", "calculation": f"{min_rate:.1%} - {max_rate:.1%}"},
        {"step": 5, "description": "Median rate", "value": median_rate},
    ]

    return ValuationResult(
        value=median_rate,
        method="Royalty Rate Benchmark",
        formula_reference="Ch 6.2, Appendix A.10",
        steps=steps,
        assumptions={
            "ip_type": ip_type,
            "industry": industry,
            "recommended_range": (min_rate, max_rate),
            "median_rate": median_rate,
            "source": source,
        },
    )


def adjust_royalty_rate(
    base_rate: float,
    adjustment_factors: dict,
) -> ValuationResult:
    """Adjust base royalty rate for specific deal factors.

    Each factor in adjustment_factors is a multiplier:
    - profit_margin: Higher margins support higher rates (typical range 0.8-1.3)
    - exclusivity: Exclusive licenses command premium (typical range 1.0-1.5)
    - market_conditions: Favorable markets support higher rates (typical range 0.8-1.2)
    - term: Longer terms may reduce per-period rate (typical range 0.8-1.2)
    - geographic_scope: Broader scope increases rate (typical range 0.8-1.4)

    Adjusted Rate = Base Rate * product(all factors)

    Args:
        base_rate: Base royalty rate from benchmark (0 < rate <= 1).
        adjustment_factors: Dict of factor name to multiplier value.

    Returns:
        ValuationResult with adjusted rate and factor breakdown.

    Raises:
        ValueError: If base_rate is invalid.

    Example:
        >>> adjust_royalty_rate(0.05, {"profit_margin": 1.2, "exclusivity": 1.3})
        ValuationResult(value=0.078, ...)
    """
    RoyaltyAdjustmentInput(base_rate=base_rate)

    valid_factors = {"profit_margin", "exclusivity", "market_conditions", "term", "geographic_scope"}
    invalid = set(adjustment_factors.keys()) - valid_factors
    if invalid:
        raise ValueError(f"Unknown adjustment factors: {invalid}. Valid: {valid_factors}")

    adjusted = base_rate
    factor_steps: list[dict] = []
    for factor_name, multiplier in adjustment_factors.items():
        adjusted *= multiplier
        factor_steps.append({
            "step": len(factor_steps) + 1,
            "description": f"Apply {factor_name} factor",
            "calculation": f"{adjusted / multiplier:.4f} * {multiplier} = {adjusted:.4f}",
            "value": round(adjusted, 6),
        })

    steps = [
        {"step": 1, "description": "Base royalty rate", "value": base_rate},
    ] + factor_steps + [
        {"step": len(factor_steps) + 2, "description": "Adjusted royalty rate", "value": round(adjusted, 6)},
    ]

    return ValuationResult(
        value=round(adjusted, 6),
        method="Adjusted Royalty Rate",
        formula_reference="Ch 6.3, Appendix A.10",
        steps=steps,
        assumptions={
            "base_rate": base_rate,
            "adjustment_factors": adjustment_factors,
            "adjusted_rate": round(adjusted, 6),
        },
    )


def twenty_five_percent_rule(
    licensee_expected_profit: float,
    profit_attribution_to_ip: float = 1.0,
) -> ValuationResult:
    """Apply the 25% rule of thumb for royalty rate estimation.

    The 25% rule suggests the licensor should receive 25% of the licensee's
    expected profit attributable to the licensed IP.

    Royalty = Licensee Expected Profit * Profit Attribution to IP * 25%

    Note: This rule has been criticized and rejected by some courts (e.g.,
    Uniloc v. Microsoft), but remains a useful starting point for negotiations.

    Args:
        licensee_expected_profit: Expected profit from using the IP (> 0).
        profit_attribution_to_ip: Fraction of profit attributable to IP (0-1).

    Returns:
        ValuationResult with royalty amount.

    Raises:
        ValueError: If inputs are invalid.

    Example:
        >>> result = twenty_five_percent_rule(10_000_000, 0.8)
        >>> result.value
        2000000.0
    """
    TwentyFivePercentInput(
        licensee_expected_profit=licensee_expected_profit,
        profit_attribution_to_ip=profit_attribution_to_ip,
    )

    ip_profit = licensee_expected_profit * profit_attribution_to_ip
    royalty = ip_profit * 0.25

    steps = [
        {"step": 1, "description": "Licensee Expected Profit", "value": licensee_expected_profit},
        {"step": 2, "description": "Profit Attribution to IP", "value": profit_attribution_to_ip},
        {"step": 3, "description": "IP-Attributable Profit",
         "calculation": f"{licensee_expected_profit} * {profit_attribution_to_ip}",
         "value": round(ip_profit, 2)},
        {"step": 4, "description": "Apply 25% Rule", "calculation": f"{ip_profit} * 0.25"},
        {"step": 5, "description": "Estimated Royalty", "value": round(royalty, 2)},
    ]

    return ValuationResult(
        value=round(royalty, 2),
        method="25% Rule",
        formula_reference="Ch 6.1",
        steps=steps,
        assumptions={
            "licensee_expected_profit": licensee_expected_profit,
            "profit_attribution_to_ip": profit_attribution_to_ip,
            "rule_percentage": 0.25,
        },
    )


class ProfitSplitInputs(BaseModel):
    """Inputs for profit split royalty approach."""

    licensor_contribution_pct: float = Field(
        gt=0, le=1, description="Licensor's contribution to total profit (decimal)"
    )
    licensee_contribution_pct: float = Field(
        gt=0, le=1, description="Licensee's contribution to total profit (decimal)"
    )
    total_profit: float = Field(gt=0, description="Total profit from the licensed product")


def profit_split_method(
    licensor_contribution_pct: float,
    licensee_contribution_pct: float,
    total_profit: float,
) -> dict:
    """Calculate royalty using the profit split approach.

    The profit split method allocates total profit between licensor and licensee
    based on their relative contributions to the value creation process.

    Formula:
        Total Contribution = Licensor% + Licensee%
        Licensor Share = Licensor% / Total Contribution
        Royalty = Total Profit x Licensor Share

    The resulting royalty rate can be derived as:
        Royalty Rate = Royalty / Net Sales

    Args:
        licensor_contribution_pct: Licensor's contribution to profit (0-1).
        licensee_contribution_pct: Licensee's contribution to profit (0-1).
        total_profit: Total profit generated from the licensed product.

    Returns:
        Dict with value (licensor's profit share), method, formula_reference,
        steps, and assumptions.

    Raises:
        ValueError: If contribution percentages are invalid.

    Example:
        >>> result = profit_split_method(0.40, 0.60, 10_000_000)
        >>> result["value"]  # 10M x (0.4 / 1.0) = 4M
        4000000.0

    Reference:
        OECD Transfer Pricing Guidelines (2022), Chapter II: Profit Split Method.
        Treas. Reg. § 1.482-7: Cost sharing arrangements.
    """
    inputs = ProfitSplitInputs(
        licensor_contribution_pct=licensor_contribution_pct,
        licensee_contribution_pct=licensee_contribution_pct,
        total_profit=total_profit,
    )

    steps: list[str] = []

    total_contribution = inputs.licensor_contribution_pct + inputs.licensee_contribution_pct
    licensor_share = inputs.licensor_contribution_pct / total_contribution
    licensee_share = inputs.licensee_contribution_pct / total_contribution
    licensor_profit = inputs.total_profit * licensor_share
    licensee_profit = inputs.total_profit * licensee_share

    steps.append(f"Total profit: {inputs.total_profit:,.0f}")
    steps.append(f"Licensor contribution: {inputs.licensor_contribution_pct:.0%}")
    steps.append(f"Licensee contribution: {inputs.licensee_contribution_pct:.0%}")
    steps.append(f"Total contribution: {total_contribution:.0%}")
    steps.append(f"Licensor share: {licensor_share:.1%}")
    steps.append(f"Licensee share: {licensee_share:.1%}")
    steps.append(f"Licensor profit (royalty): {licensor_profit:,.0f}")
    steps.append(f"Licensee profit: {licensee_profit:,.0f}")

    return {
        "value": licensor_profit,
        "method": "Profit Split Method",
        "formula_reference": "OECD TPSM, Royalty = Profit x (Licensor% / Total%)",
        "steps": steps,
        "assumptions": {
            "total_profit": inputs.total_profit,
            "licensor_contribution_pct": inputs.licensor_contribution_pct,
            "licensee_contribution_pct": inputs.licensee_contribution_pct,
            "licensor_share_pct": round(licensor_share, 4),
            "licensee_share_pct": round(licensee_share, 4),
            "licensor_profit": round(licensor_profit, 2),
            "licensee_profit": round(licensee_profit, 2),
        },
    }


class AnalyticalMethodInputs(BaseModel):
    """Inputs for analytical method royalty valuation."""

    advantage_margin: float = Field(
        gt=0, le=1, description="Profit advantage from the IP (decimal)"
    )
    volume: float = Field(gt=0, description="Projected sales volume (units or revenue)")
    discount_rate: float = Field(gt=0, description="Discount rate (decimal)")
    economic_life: int = Field(ge=1, description="Economic life of the IP (years)")


def analytical_method_valuation(
    advantage_margin: float,
    volume: float,
    discount_rate: float,
    economic_life: int,
) -> dict:
    """Calculate royalty rate using the analytical method.

    The analytical method determines the value of an IP asset by quantifying
    the profit advantage it provides over the next-best alternative, then
    discounting those advantages over the economic life.

    Formula:
        Annual Advantage = Volume x Advantage Margin
        IP Value = PV of Annual Advantage over economic life
        Implied Royalty Rate = IP Value / PV of Volume

    This method is particularly useful for technology and process patents
    where the cost savings or margin improvement can be directly measured.

    Args:
        advantage_margin: Profit margin advantage from using the IP (0-1).
        volume: Projected annual sales volume (units or revenue base).
        discount_rate: Discount rate reflecting IP-specific risk (decimal).
        economic_life: Expected economic life of the IP (years).

    Returns:
        Dict with value (IP value), method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If inputs are invalid.

    Example:
        >>> result = analytical_method_valuation(
        ...     advantage_margin=0.05,
        ...     volume=10_000_000,
        ...     discount_rate=0.12,
        ...     economic_life=7,
        ... )
        >>> result["value"] > 0
        True

    Reference:
        Reilly, R. & Smith, G. (1998). Intangible Assets: Valuation and
        Economic Benefit. Chapter 7: Analytical Method.
    """
    inputs = AnalyticalMethodInputs(
        advantage_margin=advantage_margin,
        volume=volume,
        discount_rate=discount_rate,
        economic_life=economic_life,
    )

    steps: list[str] = []

    annual_advantage = inputs.volume * inputs.advantage_margin

    steps.append(f"Volume base: {inputs.volume:,.0f}")
    steps.append(f"Advantage margin: {inputs.advantage_margin:.2%}")
    steps.append(f"Annual advantage: {annual_advantage:,.0f}")
    steps.append(f"Economic life: {inputs.economic_life} years")
    steps.append(f"Discount rate: {inputs.discount_rate:.2%}")

    ip_value = present_value_of_annuity(
        annual_advantage, inputs.discount_rate, inputs.economic_life
    )
    pv_volume = present_value_of_annuity(
        inputs.volume, inputs.discount_rate, inputs.economic_life
    )
    implied_royalty_rate = ip_value / pv_volume if pv_volume > 0 else 0

    steps.append(f"PV of advantages: {ip_value:,.0f}")
    steps.append(f"PV of volume: {pv_volume:,.0f}")
    steps.append(f"Implied royalty rate: {implied_royalty_rate:.4f} ({implied_royalty_rate:.2%})")

    return {
        "value": ip_value,
        "method": "Analytical Method",
        "formula_reference": "V = PV(Volume x Advantage Margin, r, n)",
        "steps": steps,
        "assumptions": {
            "volume": inputs.volume,
            "advantage_margin": inputs.advantage_margin,
            "annual_advantage": annual_advantage,
            "discount_rate": inputs.discount_rate,
            "economic_life": inputs.economic_life,
            "ip_value": round(ip_value, 2),
            "implied_royalty_rate": round(implied_royalty_rate, 4),
        },
    }
