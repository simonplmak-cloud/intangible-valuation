"""Excess Earnings methods.

Implements Multi-Period Excess Earnings Method (MPEEM) and
Single-Period Excess Earnings Method from Chapter 4.
Includes Contributory Asset Charge (CAC) calculations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.core.time_value import present_value_of_series


class ContributoryAssetInput(BaseModel):
    """Validated contributory asset input."""

    type: str = Field(..., min_length=1, description="Asset type (e.g., 'working_capital', 'fixed_assets')")
    value: float = Field(..., gt=0, description="Asset value")
    return_rate: float = Field(..., gt=0, description="Required return rate as decimal")


def contributory_asset_charges(assets: list[dict]) -> dict:
    """Calculate total contributory asset charges (CACs).

    Contributory asset charges represent the return required by providers
    of capital to each contributory asset that supports the subject
    intangible asset's earnings.

    Formula:
        CAC_i = asset_value_i * return_rate_i
        Total_CAC = sum(CAC_i)

    Args:
        assets: List of dicts with 'type', 'value', 'return_rate' keys.
            value must be positive, return_rate must be between 0 and 1.

    Returns:
        Dict with:
            - total_cac: Sum of all contributory asset charges
            - breakdown: List of individual CAC calculations
            - method: 'Contributory Asset Charges'
            - formula_reference: 'Chapter 4: Income Methods - Excess Earnings'
            - steps: List of calculation steps
            - assumptions: Key assumptions used

    Raises:
        ValueError: If assets is empty or contains invalid data.

    Example:
        >>> assets = [
        ...     {"type": "working_capital", "value": 500000, "return_rate": 0.08},
        ...     {"type": "fixed_assets", "value": 1000000, "return_rate": 0.10},
        ... ]
        >>> result = contributory_asset_charges(assets)
        >>> result["total_cac"]
        140000.0
    """
    if not assets:
        raise ValueError("assets list cannot be empty")

    steps = ["Contributory Asset Charge calculation:"]
    breakdown = []
    total_cac = 0.0

    for asset_data in assets:
        asset = ContributoryAssetInput(**asset_data)
        cac = asset.value * asset.return_rate
        total_cac += cac

        breakdown.append(
            {
                "type": asset.type,
                "value": asset.value,
                "return_rate": asset.return_rate,
                "cac": cac,
            }
        )
        steps.append(
            f"  {asset.type}: ${asset.value:,.2f} x {asset.return_rate:.2%} = ${cac:,.2f}"
        )

    steps.append(f"Total CAC: ${total_cac:,.2f}")

    assumptions = [
        "Return rates reflect the required return for each asset class",
        "Asset values represent the economic investment in each asset",
        "CACs are charged against cash flows attributable to the subject asset",
    ]

    return {
        "total_cac": total_cac,
        "breakdown": breakdown,
        "method": "Contributory Asset Charges",
        "formula_reference": "Chapter 4: Income Methods - Excess Earnings",
        "steps": steps,
        "assumptions": assumptions,
    }


def mpeem(
    cash_flow_projections: list[float],
    contributory_asset_charges: list[dict],
    discount_rate: float,
    tax_rate: float,
    tab_enabled: bool = True,
) -> dict:
    """Calculate asset value using the Multi-Period Excess Earnings Method (MPEEM).

    MPEEM values an intangible asset as the present value of projected cash flows
    after deducting contributory asset charges (returns on all other assets
    that contribute to generating those cash flows).

    Formula:
        For each period t:
            Excess_Earnings_t = (CashFlow_t - Total_CAC_t) * (1 - tax_rate)
            PV_t = Excess_Earnings_t / (1 + discount_rate)^t

        With TAB:
            TAB = 1 / (1 - (tax_rate * PV_annuity_factor / n))
            Value = PV_of_excess_earnings * TAB

    Args:
        cash_flow_projections: Projected cash flows for each period.
        contributory_asset_charges: List of dicts, one per period, with CAC breakdowns.
            Each dict must have 'total_cac' key. Length must match cash_flow_projections.
        discount_rate: Discount rate as decimal.
        tax_rate: Corporate tax rate as decimal.
        tab_enabled: Whether to include Tax Amortization Benefit. Defaults to True.

    Returns:
        Dict with:
            - value: Present value of excess earnings (with TAB if enabled)
            - method: 'Multi-Period Excess Earnings Method (MPEEM)'
            - formula_reference: 'Chapter 4: Income Methods - MPEEM'
            - pv_before_tab: PV before tax amortization benefit
            - tab_factor: TAB multiplier (1.0 if disabled)
            - steps: List of calculation steps
            - assumptions: Key assumptions used

    Raises:
        ValueError: If inputs are invalid or inconsistent.

    Example:
        >>> cfs = [200000, 220000, 240000, 260000, 280000]
        >>> cacs = [
        ...     {"total_cac": 50000}, {"total_cac": 52000}, {"total_cac": 54000},
        ...     {"total_cac": 56000}, {"total_cac": 58000},
        ... ]
        >>> result = mpeem(cfs, cacs, discount_rate=0.12, tax_rate=0.25)
        >>> result["value"] > 0
        True
    """
    if not cash_flow_projections:
        raise ValueError("cash_flow_projections cannot be empty")
    if len(cash_flow_projections) != len(contributory_asset_charges):
        raise ValueError(
            f"cash_flow_projections length ({len(cash_flow_projections)}) must match "
            f"contributory_asset_charges length ({len(contributory_asset_charges)})"
        )
    if discount_rate <= 0:
        raise ValueError(f"discount_rate must be positive, got {discount_rate}")
    if not (0 <= tax_rate < 1):
        raise ValueError(f"tax_rate must be between 0 and 1 (inclusive of 0), got {tax_rate}")

    n = len(cash_flow_projections)
    steps = [
        f"Projection periods: {n}",
        f"Discount rate: {discount_rate:.2%}",
        f"Tax rate: {tax_rate:.2%}",
        f"TAB enabled: {tab_enabled}",
    ]

    excess_earnings = []
    steps.append("Period-by-period excess earnings calculation:")

    for i, (cf, cac_data) in enumerate(zip(cash_flow_projections, contributory_asset_charges, strict=False), start=1):
        total_cac = cac_data.get("total_cac", 0)
        pre_tax_excess = cf - total_cac
        after_tax_excess = pre_tax_excess * (1 - tax_rate)
        excess_earnings.append(after_tax_excess)

        steps.append(
            f"  Period {i}: cash_flow=${cf:,.2f}, CAC=${total_cac:,.2f}, "
            f"pre-tax excess=${pre_tax_excess:,.2f}, "
            f"after-tax excess=${after_tax_excess:,.2f}"
        )

    pv_result = present_value_of_series(excess_earnings, discount_rate)
    pv_before_tab = pv_result["present_value"]

    steps.append(f"PV of after-tax excess earnings (before TAB): ${pv_before_tab:,.2f}")

    tab_factor = 1.0
    if tab_enabled and tax_rate > 0:
        annuity_factor = sum(1 / ((1 + discount_rate) ** t) for t in range(1, n + 1))
        tab_denominator = 1 - (tax_rate * annuity_factor / n)
        if tab_denominator <= 0:
            raise ValueError(
                f"TAB denominator is non-positive ({tab_denominator:.4f}). "
                "Check tax_rate, discount_rate, and projection period inputs."
            )
        tab_factor = 1 / tab_denominator
        value = pv_before_tab * tab_factor
        steps.append(f"TAB annuity factor: {annuity_factor:.4f}")
        steps.append(f"TAB factor: {tab_factor:.4f}")
        steps.append(f"Value with TAB: ${value:,.2f}")
    else:
        value = pv_before_tab
        steps.append("TAB not applied")

    assumptions = [
        "Cash flow projections are attributable to the subject asset",
        "Contributory asset charges reflect required returns on supporting assets",
        "Discount rate reflects the risk of the excess earnings stream",
        "Tax amortization is deductible over the projection period",
    ]
    if tab_enabled:
        assumptions.append("Tax amortization benefit is available and realizable")

    return {
        "value": value,
        "method": "Multi-Period Excess Earnings Method (MPEEM)",
        "formula_reference": "Chapter 4: Income Methods - MPEEM",
        "pv_before_tab": pv_before_tab,
        "tab_factor": tab_factor,
        "steps": steps,
        "assumptions": assumptions,
    }


def single_period_excess_earnings(
    normalized_earnings: float,
    contributory_asset_charges: list[dict],
    capitalization_rate: float,
) -> dict:
    """Calculate asset value using the Single-Period Excess Earnings Method.

    Values an intangible asset by capitalizing a single period of normalized
    excess earnings (earnings after deducting CACs).

    Formula:
        Total_CAC = sum(cac['total_cac'] for cac in contributory_asset_charges)
        Excess_Earnings = normalized_earnings - Total_CAC
        Value = Excess_Earnings / capitalization_rate

    Args:
        normalized_earnings: Normalized earnings attributable to all assets.
        contributory_asset_charges: List of dicts with 'total_cac' key.
        capitalization_rate: Capitalization rate as decimal. Must be positive.

    Returns:
        Dict with:
            - value: Capitalized excess earnings value
            - method: 'Single-Period Excess Earnings Method'
            - formula_reference: 'Chapter 4: Income Methods - Single Period Excess Earnings'
            - total_cac: Sum of contributory asset charges
            - excess_earnings: Normalized earnings minus total CAC
            - steps: List of calculation steps
            - assumptions: Key assumptions used

    Raises:
        ValueError: If inputs are invalid or excess earnings are non-positive.

    Example:
        >>> result = single_period_excess_earnings(
        ...     normalized_earnings=500000,
        ...     contributory_asset_charges=[{"total_cac": 140000}],
        ...     capitalization_rate=0.12,
        ... )
        >>> result["value"]
        3000000.0
    """
    if not contributory_asset_charges:
        raise ValueError("contributory_asset_charges cannot be empty")
    if capitalization_rate <= 0:
        raise ValueError(f"capitalization_rate must be positive, got {capitalization_rate}")

    total_cac = sum(cac.get("total_cac", 0) for cac in contributory_asset_charges)
    excess_earnings = normalized_earnings - total_cac

    if excess_earnings <= 0:
        raise ValueError(
            f"Excess earnings must be positive. normalized_earnings ({normalized_earnings}) "
            f"minus total_cac ({total_cac}) = {excess_earnings}"
        )

    value = excess_earnings / capitalization_rate

    steps = [
        f"Normalized earnings: ${normalized_earnings:,.2f}",
        f"Total contributory asset charges: ${total_cac:,.2f}",
        f"Excess earnings: ${excess_earnings:,.2f}",
        f"Capitalization rate: {capitalization_rate:.2%}",
        f"Value: ${value:,.2f}",
    ]

    assumptions = [
        "Normalized earnings represent sustainable, maintainable earnings",
        "Contributory asset charges reflect required returns on all supporting assets",
        "Capitalization rate reflects the risk and growth profile of excess earnings",
        "Single-period method assumes stable excess earnings in perpetuity",
    ]

    return {
        "value": value,
        "method": "Single-Period Excess Earnings Method",
        "formula_reference": "Chapter 4: Income Methods - Single Period Excess Earnings",
        "total_cac": total_cac,
        "excess_earnings": excess_earnings,
        "steps": steps,
        "assumptions": assumptions,
    }
