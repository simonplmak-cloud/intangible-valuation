"""Relief from Royalty method.

Values an intangible asset as the present value of after-tax royalty
payments that the owner avoids by owning the asset rather than licensing it.

Implements the method from Chapter 4 with Tax Amortization Benefit (TAB).
"""

from __future__ import annotations

from intangible_valuation.core import ValuationResult
from intangible_valuation.core.time_value import present_value_of_series


def relief_from_royalty(
    revenue_projections: list[float],
    royalty_rate: float,
    discount_rate: float,
    tax_rate: float,
    useful_life: int,
    tab_enabled: bool = True,
) -> ValuationResult:
    """Calculate asset value using the Relief from Royalty method.

    The Relief from Royalty method values an intangible asset as the present
    value of the after-tax royalty payments the owner avoids by owning the
    asset rather than licensing it from a third party.

    Formula:
        For each period t:
            Royalty_t = Revenue_t * royalty_rate
            AfterTax_Royalty_t = Royalty_t * (1 - tax_rate)
            PV_t = AfterTax_Royalty_t / (1 + discount_rate)^t

        With TAB (Tax Amortization Benefit):
            TAB = 1 / (1 - (tax_rate * PV_annuity_factor / useful_life))
            Value = PV_of_after_tax_royalties * TAB

    Args:
        revenue_projections: Projected revenue for each period of useful life.
        royalty_rate: Arm's length royalty rate as decimal (e.g., 0.04 for 4%).
        discount_rate: Discount rate as decimal.
        tax_rate: Corporate tax rate as decimal.
        useful_life: Expected useful life in periods.
        tab_enabled: Whether to include Tax Amortization Benefit. Defaults to True.

    Returns:
        ValuationResult with value, method, formula_reference, steps, assumptions.
        Extra fields: pv_before_tab, tab_factor.

    Raises:
        ValueError: If inputs are invalid or inconsistent.

    Example:
        >>> result = relief_from_royalty(
        ...     revenue_projections=[1000000, 1100000, 1200000, 1300000, 1400000],
        ...     royalty_rate=0.05,
        ...     discount_rate=0.12,
        ...     tax_rate=0.25,
        ...     useful_life=5,
        ... )
        >>> result.value > 0
        True
    """
    if not revenue_projections:
        raise ValueError("revenue_projections cannot be empty")
    if len(revenue_projections) != useful_life:
        raise ValueError(
            f"revenue_projections length ({len(revenue_projections)}) must match useful_life ({useful_life})"
        )
    if not (0 < royalty_rate < 1):
        raise ValueError(f"royalty_rate must be between 0 and 1 (exclusive), got {royalty_rate}")
    if discount_rate <= 0:
        raise ValueError(f"discount_rate must be positive, got {discount_rate}")
    if not (0 <= tax_rate < 1):
        raise ValueError(f"tax_rate must be between 0 and 1 (inclusive of 0), got {tax_rate}")
    if useful_life <= 0:
        raise ValueError(f"useful_life must be positive, got {useful_life}")

    steps = [
        f"Useful life: {useful_life} periods",
        f"Royalty rate: {royalty_rate:.2%}",
        f"Discount rate: {discount_rate:.2%}",
        f"Tax rate: {tax_rate:.2%}",
        f"TAB enabled: {tab_enabled}",
    ]

    pv_result = present_value_of_series(
        [r * royalty_rate * (1 - tax_rate) for r in revenue_projections],
        discount_rate,
    )

    pv_before_tab = pv_result["present_value"]

    steps.append("Period-by-period calculation:")
    for period_detail in pv_result["pv_by_period"]:
        period = period_detail["period"]
        rev = revenue_projections[period - 1]
        royalty = rev * royalty_rate
        after_tax = royalty * (1 - tax_rate)
        steps.append(
            f"  Period {period}: revenue=${rev:,.2f}, "
            f"royalty=${royalty:,.2f}, "
            f"after-tax=${after_tax:,.2f}, "
            f"PV=${period_detail['present_value']:,.2f}"
        )

    steps.append(f"PV of after-tax royalties (before TAB): ${pv_before_tab:,.2f}")

    tab_factor = 1.0
    if tab_enabled and tax_rate > 0:
        annuity_factor = sum(
            1 / ((1 + discount_rate) ** t) for t in range(1, useful_life + 1)
        )
        tab_denominator = 1 - (tax_rate * annuity_factor / useful_life)
        if tab_denominator <= 0:
            raise ValueError(
                f"TAB denominator is non-positive ({tab_denominator:.4f}). "
                "Check tax_rate, discount_rate, and useful_life inputs."
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
        "Royalty rate reflects arm's length market rate for similar assets",
        "Revenue projections are reasonable and supportable",
        "Discount rate reflects risk of the royalty stream",
        "Tax amortization is deductible over the useful life",
    ]
    if tab_enabled:
        assumptions.append("Tax amortization benefit is available and realizable")

    return ValuationResult(
        value=value,
        method="Relief from Royalty",
        formula_reference="Chapter 4: Income Methods - Relief from Royalty",
        steps=steps,
        assumptions=assumptions,
        pv_before_tab=pv_before_tab,
        tab_factor=tab_factor,
    )
