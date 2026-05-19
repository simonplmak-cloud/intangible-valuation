"""Utility functions for valuation formulas, sensitivity analysis, and contributory asset charges.

Implements useful life estimation, sensitivity analysis, and contributory asset charge
calculations from Appendix A and Chapter 5 of the Ascent Partners textbook.

All functions return structured dicts with:
    - value: The computed result
    - method: The calculation method used
    - formula_reference: Reference to the methodology
    - steps: Step-by-step calculation breakdown
    - assumptions: List of assumptions made during calculation
"""

from __future__ import annotations

import math
from typing import Any, Callable

from pydantic import BaseModel, Field, field_validator

from src.core.time_value import ValuationResult
from src.utils.constants import DEFAULT_USEFUL_LIVES


class ContributoryAssetInput(BaseModel):
    """Validated contributory asset input."""

    type: str = Field(min_length=1)
    value: float
    return_rate: float

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Asset value must be non-negative")
        return v

    @field_validator("return_rate")
    @classmethod
    def validate_return_rate(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Return rate must be non-negative")
        return v


class UsefulLifeInput(BaseModel):
    """Validated inputs for useful life estimation."""

    asset_type: str = Field(min_length=1)
    legal_life: float | None = None
    obsolescence_rate: float = 0.05

    @field_validator("obsolescence_rate")
    @classmethod
    def validate_obsolescence(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("obsolescence_rate must be between 0 and 1")
        return v


def estimate_useful_life(
    asset_type: str,
    legal_life: float | None = None,
    economic_factors: dict[str, float] | None = None,
    obsolescence_rate: float = 0.05,
) -> ValuationResult:
    """Estimate the useful life of an intangible asset.

    The useful life is the shorter of:
    1. Legal life (if applicable)
    2. Economic life (based on obsolescence and market factors)

    Economic life is estimated using:
        Economic Life = -ln(threshold) / obsolescence_rate
        where threshold = 0.10 (value drops below 10% of original)

    Parameters:
        asset_type: Type of intangible asset (e.g., "patent", "trademark", "software")
        legal_life: Legal protection period in years (overrides default for asset type)
        economic_factors: Optional dict of economic adjustment factors
            - "market_growth": Market growth rate adjustment
            - "competition": Competitive pressure factor (0-1)
            - "tech_change": Rate of technological change
        obsolescence_rate: Annual obsolescence rate (default 0.05)

    Returns:
        ValuationResult with estimated useful life in years

    Raises:
        ValueError: If asset_type is unknown or parameters are invalid

    Book Reference:
        Appendix A, Section A.2 — Useful Life Estimation
        Chapter 5, Multi-Period Excess Earnings Method — Projection Period
    """
    inputs = UsefulLifeInput(
        asset_type=asset_type,
        legal_life=legal_life,
        obsolescence_rate=obsolescence_rate,
    )

    asset_type_lower = asset_type.lower()
    defaults = DEFAULT_USEFUL_LIVES.get(asset_type_lower)

    if defaults is None and legal_life is None:
        raise ValueError(
            f"Unknown asset type '{asset_type}'. "
            f"Provide legal_life or use one of: {', '.join(DEFAULT_USEFUL_LIVES.keys())}"
        )

    effective_obsolescence = obsolescence_rate

    if economic_factors:
        competition = economic_factors.get("competition", 0)
        tech_change = economic_factors.get("tech_change", 0)
        effective_obsolescence = obsolescence_rate + competition * 0.02 + tech_change * 0.03
        effective_obsolescence = min(effective_obsolescence, 0.50)

    threshold = 0.10
    if math.isclose(effective_obsolescence, 0.0, abs_tol=1e-12):
        economic_life = float("inf")
    else:
        economic_life = -math.log(threshold) / effective_obsolescence

    if legal_life is not None and legal_life > 0:
        useful_life = min(economic_life, legal_life)
    elif defaults and defaults["legal_max"] != float("inf") and defaults["legal_max"] is not None:
        useful_life = min(economic_life, defaults["legal_max"])
    else:
        useful_life = economic_life

    if math.isfinite(useful_life):
        useful_life = round(useful_life, 1)

    steps = [
        f"Asset Type: {asset_type}",
        f"Obsolescence Rate: {effective_obsolescence:.2%}",
        f"Economic Life (10% threshold): {economic_life:.1f} years",
    ]

    if legal_life is not None:
        steps.append(f"Legal Life: {legal_life} years")
        steps.append(f"Useful Life = min({economic_life:.1f}, {legal_life}) = {useful_life} years")
    else:
        steps.append(f"Useful Life: {useful_life} years (economic life, no legal limit)")

    return ValuationResult(
        value=useful_life,
        method="Useful Life Estimation",
        formula_reference="Economic Life = -ln(0.10) / obsolescence_rate; Useful Life = min(legal, economic)",
        steps=steps,
        assumptions=[
            f"Asset type: {asset_type}",
            f"Value threshold for economic life: {threshold:.0%} of original value",
            "Obsolescence compounds annually",
            "No legal renewal or extension assumed",
        ],
    )


def sensitivity_analysis(
    function_name: str,
    parameter_name: str,
    parameter_range: list[float],
    fixed_parameters: dict[str, Any],
) -> dict[str, Any]:
    """Perform sensitivity analysis on a valuation function.

    Evaluates the function across a range of values for one parameter
    while holding all others constant.

    Parameters:
        function_name: Name of the function to analyze. Supported:
            - "present_value"
            - "future_value"
            - "annuity_pv"
            - "perpetuity_pv"
            - "growing_annuity_pv"
            - "terminal_value"
            - "build_up_discount_rate"
            - "capm_discount_rate"
            - "wacc"
        parameter_name: The parameter to vary
        parameter_range: List of values to test for the parameter
        fixed_parameters: Dict of fixed parameter values for all other parameters

    Returns:
        Dict with keys:
            - function_name: Name of the analyzed function
            - parameter_name: Name of the varied parameter
            - results: List of {"parameter_value": float, "result": float}
            - min_result: Minimum result value
            - max_result: Maximum result value
            - sensitivity_range: max_result - min_result
            - method: "Sensitivity Analysis"
            - formula_reference: Reference description
            - steps: Description of the analysis
            - assumptions: List of assumptions

    Raises:
        ValueError: If function_name is not supported or parameter_range is empty

    Book Reference:
        Appendix A, Section A.3 — Sensitivity Analysis
        Used to assess how valuation changes with key input assumptions
    """
    if not parameter_range:
        raise ValueError("parameter_range must contain at least one value")

    function_map: dict[str, Callable] = {
        "present_value": _call_present_value,
        "future_value": _call_future_value,
        "annuity_pv": _call_annuity_pv,
        "perpetuity_pv": _call_perpetuity_pv,
        "growing_annuity_pv": _call_growing_annuity_pv,
        "terminal_value": _call_terminal_value,
        "build_up_discount_rate": _call_build_up,
        "capm_discount_rate": _call_capm,
        "wacc": _call_wacc,
    }

    if function_name not in function_map:
        raise ValueError(
            f"Unsupported function: {function_name}. "
            f"Supported: {', '.join(function_map.keys())}"
        )

    func = function_map[function_name]
    results = []

    for param_value in parameter_range:
        params = {**fixed_parameters, parameter_name: param_value}
        try:
            result = func(**params)
            results.append({
                "parameter_value": param_value,
                "result": result,
            })
        except (ValueError, TypeError) as e:
            results.append({
                "parameter_value": param_value,
                "result": None,
                "error": str(e),
            })

    valid_results = [r["result"] for r in results if r["result"] is not None]

    if valid_results:
        min_result = min(valid_results)
        max_result = max(valid_results)
        sensitivity_range = max_result - min_result
    else:
        min_result = None
        max_result = None
        sensitivity_range = None

    return {
        "function_name": function_name,
        "parameter_name": parameter_name,
        "results": results,
        "min_result": min_result,
        "max_result": max_result,
        "sensitivity_range": sensitivity_range,
        "method": "Sensitivity Analysis",
        "formula_reference": f"One-at-a-time sensitivity analysis on {parameter_name} for {function_name}",
        "steps": [
            f"Function: {function_name}",
            f"Parameter varied: {parameter_name}",
            f"Range: {parameter_range}",
            f"Fixed parameters: {list(fixed_parameters.keys())}",
            f"Results: {len(results)} evaluations",
            f"Output range: {min_result} to {max_result}" if valid_results else "No valid results",
        ],
        "assumptions": [
            "All other parameters held constant",
            "Parameter values are within valid ranges for the function",
            "Linear interpolation between tested points is reasonable",
        ],
    }


def _call_present_value(**kwargs: Any) -> float:
    from src.core.time_value import present_value
    return present_value(**kwargs).value


def _call_future_value(**kwargs: Any) -> float:
    from src.core.time_value import future_value
    return future_value(**kwargs).value


def _call_annuity_pv(**kwargs: Any) -> float:
    from src.core.time_value import annuity_pv
    return annuity_pv(**kwargs).value


def _call_perpetuity_pv(**kwargs: Any) -> float:
    from src.core.time_value import perpetuity_pv
    return perpetuity_pv(**kwargs).value


def _call_growing_annuity_pv(**kwargs: Any) -> float:
    from src.core.time_value import growing_annuity_pv
    return growing_annuity_pv(**kwargs).value


def _call_terminal_value(**kwargs: Any) -> float:
    from src.core.time_value import terminal_value
    return terminal_value(**kwargs).value


def _call_build_up(**kwargs: Any) -> float:
    from src.core.discount_rates import build_up_discount_rate
    return build_up_discount_rate(**kwargs).value


def _call_capm(**kwargs: Any) -> float:
    from src.core.discount_rates import capm_discount_rate
    return capm_discount_rate(**kwargs).value


def _call_wacc(**kwargs: Any) -> float:
    from src.core.discount_rates import wacc
    return wacc(**kwargs).value


def contributory_asset_charges(
    assets: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate contributory asset charges (CAC) for a set of supporting assets.

    Contributory asset charges represent the return required on supporting assets
    (working capital, fixed assets, assembled workforce, etc.) that contribute
    to the earnings of the subject intangible asset.

    Formula:
        CAC_i = Asset_Value_i * Return_Rate_i
        Total CAC = sum(CAC_i)

    Parameters:
        assets: List of dicts with keys:
            - type: Asset type (e.g., "working_capital", "fixed_assets", "assembled_workforce")
            - value: Asset value
            - return_rate: Required return rate for that asset type

    Returns:
        Dict with keys:
            - total_cac: Sum of all contributory asset charges
            - asset_charges: List of {"type": str, "value": float, "return_rate": float, "charge": float}
            - method: "Contributory Asset Charge"
            - formula_reference: Reference description
            - steps: Step-by-step calculation
            - assumptions: List of assumptions

    Raises:
        ValueError: If assets list is empty or values are invalid

    Book Reference:
        Chapter 5, Section 5.3 — Contributory Asset Charges
        Used in Multi-Period Excess Earnings Method (MPEEM) to isolate cash flows
        attributable to the subject intangible asset
    """
    if not assets:
        raise ValueError("assets list must contain at least one asset")

    validated_assets = [ContributoryAssetInput(**a) for a in assets]

    asset_charges = []
    total_cac = 0.0
    steps = []

    for asset in validated_assets:
        charge = asset.value * asset.return_rate
        total_cac += charge
        asset_charges.append({
            "type": asset.type,
            "value": asset.value,
            "return_rate": asset.return_rate,
            "charge": round(charge, 2),
        })
        steps.append(
            f"{asset.type}: ${asset.value:,.2f} * {asset.return_rate:.2%} = ${charge:,.2f}"
        )

    steps.append(f"Total CAC = ${total_cac:,.2f}")

    return {
        "total_cac": round(total_cac, 2),
        "asset_charges": asset_charges,
        "method": "Contributory Asset Charge",
        "formula_reference": "CAC_i = Asset_Value_i * Return_Rate_i; Total CAC = sum(CAC_i)",
        "steps": steps,
        "assumptions": [
            "Asset values represent fair market values",
            "Return rates reflect the risk of each asset class",
            "All contributory assets are necessary for the subject asset's earnings",
            "Charges represent opportunity cost of capital tied up in supporting assets",
        ],
    }
