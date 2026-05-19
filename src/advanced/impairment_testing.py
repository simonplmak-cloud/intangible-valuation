"""Goodwill and intangible asset impairment testing.

Implements Section 10.4 and Appendix A.9:
- ASC 350: Goodwill impairment = Carrying Value - Fair Value (one-step test)
- IAS 36: Uses recoverable amount (higher of FV less costs to sell and value in use)
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.core import ValuationResult


class GoodwillImpairmentInput(BaseModel):
    carrying_value: float = Field(gt=0, description="Reporting unit carrying value including goodwill")
    fair_value: float = Field(ge=0, description="Reporting unit fair value")
    reporting_unit: str = Field(default="", description="Name of the reporting unit")
    standard: str = Field(default="ASC350", pattern="^(ASC350|IAS36)$", description="Accounting standard")


class IntangibleImpairmentInput(BaseModel):
    carrying_value: float = Field(gt=0, description="Asset carrying value")
    fair_value: float | None = Field(default=None, ge=0, description="Fair value (required for ASC350)")
    recoverable_amount: float | None = Field(default=None, ge=0, description="Recoverable amount (required for IAS36)")
    standard: str = Field(default="ASC350", pattern="^(ASC350|IAS36)$", description="Accounting standard")


def goodwill_impairment_test(
    carrying_value: float,
    fair_value: float,
    reporting_unit: str = "",
    standard: str = "ASC350",
) -> ValuationResult:
    """Test goodwill for impairment per ASC 350 or IAS 36.

    ASC 350 (US GAAP):
        Impairment = Carrying Value - Fair Value (if FV < CV, else 0)
        Single-step quantitative test.

    IAS 36 (IFRS):
        Impairment = Carrying Value - Recoverable Amount
        Recoverable amount = higher of (FV less costs to sell, value in use)
        For goodwill, the reporting unit is the cash-generating unit (CGU).

    Args:
        carrying_value: Carrying value of the reporting unit (including goodwill).
        fair_value: Fair value of the reporting unit.
        reporting_unit: Name of the reporting unit being tested.
        standard: "ASC350" for US GAAP, "IAS36" for IFRS.

    Returns:
        ValuationResult with impairment amount (0 if no impairment).

    Raises:
        ValueError: If inputs are invalid.

    Example:
        >>> result = goodwill_impairment_test(50_000_000, 40_000_000, "Tech Division")
        >>> result.value
        10000000.0
    """
    GoodwillImpairmentInput(
        carrying_value=carrying_value,
        fair_value=fair_value,
        reporting_unit=reporting_unit,
        standard=standard,
    )

    if standard == "ASC350":
        if fair_value < carrying_value:
            impairment = carrying_value - fair_value
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {"step": 1, "description": f"Standard: ASC 350 (US GAAP) - One-step goodwill impairment test"},
            {"step": 2, "description": f"Reporting Unit: {reporting_unit or 'N/A'}"},
            {"step": 3, "description": "Carrying Value", "value": carrying_value},
            {"step": 4, "description": "Fair Value", "value": fair_value},
            {"step": 5, "description": "Impairment = max(0, CV - FV)", "calculation": f"max(0, {carrying_value} - {fair_value})"},
            {"step": 6, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, ASC 350-20-35"

    elif standard == "IAS36":
        recoverable_amount = fair_value
        if recoverable_amount < carrying_value:
            impairment = carrying_value - recoverable_amount
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {"step": 1, "description": f"Standard: IAS 36 (IFRS) - Impairment of Assets"},
            {"step": 2, "description": f"Reporting Unit (CGU): {reporting_unit or 'N/A'}"},
            {"step": 3, "description": "Carrying Value", "value": carrying_value},
            {"step": 4, "description": "Recoverable Amount (using fair value)", "value": recoverable_amount},
            {"step": 5, "description": "Impairment = max(0, CV - Recoverable Amount)", "calculation": f"max(0, {carrying_value} - {recoverable_amount})"},
            {"step": 6, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, IAS 36"
    else:
        raise ValueError(f"Unsupported standard: {standard}. Use 'ASC350' or 'IAS36'.")

    return ValuationResult(
        value=round(impairment, 2),
        method=f"Goodwill Impairment Test ({standard})",
        formula_reference=formula_ref,
        steps=steps,
        assumptions={
            "carrying_value": carrying_value,
            "fair_value": fair_value,
            "reporting_unit": reporting_unit,
            "standard": standard,
            "impaired": impaired,
        },
    )


def intangible_impairment_test(
    carrying_value: float,
    fair_value: float | None = None,
    recoverable_amount: float | None = None,
    standard: str = "ASC350",
) -> ValuationResult:
    """Test intangible asset for impairment per ASC 350 or IAS 36.

    ASC 350 (US GAAP):
        For indefinite-lived intangibles: Compare carrying value to fair value.
        Impairment = CV - FV (if FV < CV).

    IAS 36 (IFRS):
        Compare carrying value to recoverable amount.
        Recoverable amount = higher of (FV less costs to sell, value in use).
        Impairment = CV - Recoverable Amount (if RA < CV).

    Args:
        carrying_value: Carrying value of the intangible asset.
        fair_value: Fair value of the asset (required for ASC350).
        recoverable_amount: Recoverable amount (required for IAS36).
        standard: "ASC350" for US GAAP, "IAS36" for IFRS.

    Returns:
        ValuationResult with impairment amount (0 if no impairment).

    Raises:
        ValueError: If required parameters are missing for the chosen standard.

    Example:
        >>> result = intangible_impairment_test(20_000_000, fair_value=15_000_000)
        >>> result.value
        5000000.0
    """
    IntangibleImpairmentInput(
        carrying_value=carrying_value,
        fair_value=fair_value,
        recoverable_amount=recoverable_amount,
        standard=standard,
    )

    if standard == "ASC350":
        if fair_value is None:
            raise ValueError("fair_value is required for ASC350 impairment test")

        if fair_value < carrying_value:
            impairment = carrying_value - fair_value
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {"step": 1, "description": "Standard: ASC 350 - Indefinite-lived intangible impairment test"},
            {"step": 2, "description": "Carrying Value", "value": carrying_value},
            {"step": 3, "description": "Fair Value", "value": fair_value},
            {"step": 4, "description": "Impairment = max(0, CV - FV)", "calculation": f"max(0, {carrying_value} - {fair_value})"},
            {"step": 5, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, ASC 350-30-35"

    elif standard == "IAS36":
        if recoverable_amount is None:
            raise ValueError("recoverable_amount is required for IAS36 impairment test")

        if recoverable_amount < carrying_value:
            impairment = carrying_value - recoverable_amount
            impaired = True
        else:
            impairment = 0.0
            impaired = False

        steps = [
            {"step": 1, "description": "Standard: IAS 36 - Impairment of Assets"},
            {"step": 2, "description": "Carrying Value", "value": carrying_value},
            {"step": 3, "description": "Recoverable Amount", "value": recoverable_amount},
            {"step": 4, "description": "Impairment = max(0, CV - Recoverable Amount)", "calculation": f"max(0, {carrying_value} - {recoverable_amount})"},
            {"step": 5, "description": "Impairment Loss", "value": round(impairment, 2)},
        ]
        formula_ref = "Ch 10.4, IAS 36"
    else:
        raise ValueError(f"Unsupported standard: {standard}. Use 'ASC350' or 'IAS36'.")

    return ValuationResult(
        value=round(impairment, 2),
        method=f"Intangible Impairment Test ({standard})",
        formula_reference=formula_ref,
        steps=steps,
        assumptions={
            "carrying_value": carrying_value,
            "fair_value": fair_value,
            "recoverable_amount": recoverable_amount,
            "standard": standard,
            "impaired": impaired,
        },
    )
