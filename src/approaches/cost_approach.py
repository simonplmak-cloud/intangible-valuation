"""Cost approach valuation methods.

Implements reproduction cost and replacement cost methods
from Chapter 3, including obsolescence adjustments.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class CostApproachResult(BaseModel):
    """Result of a cost approach valuation."""

    value: float = Field(..., description="Estimated value after obsolescence adjustments")
    method: str = Field(..., description="Valuation method name")
    formula_reference: str = Field(..., description="Reference to formula in textbook")
    gross_cost: float = Field(..., description="Total cost before obsolescence")
    total_obsolescence_pct: float = Field(default=0.0, description="Combined obsolescence percentage")
    steps: list[str] = Field(default_factory=list, description="Calculation steps")
    assumptions: list[str] = Field(default_factory=list, description="Key assumptions")


class CostInput(BaseModel):
    """Validated development cost inputs."""

    labor: float = Field(..., ge=0, description="Labor costs")
    materials: float = Field(..., ge=0, description="Material costs")
    overhead: float = Field(..., ge=0, description="Overhead costs")

    @field_validator("labor", "materials", "overhead")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"Cost component must be non-negative, got {v}")
        return v


class ObsolescenceInput(BaseModel):
    """Validated obsolescence factors."""

    functional: float = Field(default=0.0, ge=0, le=1, description="Functional obsolescence (0-1)")
    technological: float = Field(default=0.0, ge=0, le=1, description="Technological obsolescence (0-1)")
    economic: float = Field(default=0.0, ge=0, le=1, description="Economic obsolescence (0-1)")


def reproduction_cost(
    development_costs: dict,
    obsolescence_factors: dict | None = None,
) -> dict:
    """Calculate depreciated reproduction cost of an intangible asset.

    Reproduction cost estimates the cost to create an exact replica of the
    subject asset using the same materials, design, and standards as the original.

    Formula:
        Reproduction Cost = Sum(development_costs) * (1 - total_obsolescence)
        total_obsolescence = 1 - (1 - functional) * (1 - technological) * (1 - economic)

    Args:
        development_costs: Dict with keys like 'labor', 'materials', 'overhead', etc.
            Each value must be a non-negative number.
        obsolescence_factors: Optional dict with 'functional', 'technological', 'economic'
            keys. Values must be between 0 and 1. Defaults to no obsolescence.

    Returns:
        Dict with:
            - value: Depreciated reproduction cost
            - method: 'Reproduction Cost'
            - formula_reference: 'Chapter 3: Cost Approach - Reproduction Cost Method'
            - gross_cost: Total development cost before obsolescence
            - total_obsolescence_pct: Combined obsolescence percentage
            - steps: List of calculation steps
            - assumptions: Key assumptions used

    Raises:
        ValueError: If development_costs is empty or contains negative values,
            or if obsolescence factors are out of range.

    Example:
        >>> result = reproduction_cost(
        ...     {"labor": 400000, "materials": 150000, "overhead": 100000},
        ...     {"functional": 0.15, "technological": 0.20, "economic": 0.05}
        ... )
        >>> result["value"]
        476000.0
    """
    if not development_costs:
        raise ValueError("development_costs cannot be empty")

    for key, val in development_costs.items():
        if not isinstance(val, (int, float)):
            raise ValueError(f"Cost component '{key}' must be a number, got {type(val).__name__}")
        if val < 0:
            raise ValueError(f"Cost component '{key}' must be non-negative, got {val}")

    gross_cost = sum(development_costs.values())

    steps = [
        f"Sum development costs: {development_costs}",
        f"Gross reproduction cost: ${gross_cost:,.2f}",
    ]

    if obsolescence_factors:
        obs = ObsolescenceInput(**obsolescence_factors)
        combined_retention = (
            (1 - obs.functional) * (1 - obs.technological) * (1 - obs.economic)
        )
        total_obsolescence = 1 - combined_retention
        value = gross_cost * combined_retention

        steps.append(
            f"Apply obsolescence: functional={obs.functional:.1%}, "
            f"technological={obs.technological:.1%}, economic={obs.economic:.1%}"
        )
        steps.append(f"Combined retention factor: {combined_retention:.4f}")
        steps.append(f"Total obsolescence: {total_obsolescence:.1%}")
        steps.append(f"Depreciated reproduction cost: ${value:,.2f}")

        assumptions = [
            "Obsolescence factors are multiplicative (combined retention)",
            "All cost components are in current dollars",
            "Development costs reflect exact reproduction standards",
        ]
    else:
        value = gross_cost
        total_obsolescence = 0.0
        steps.append("No obsolescence adjustments applied")
        assumptions = [
            "Asset is newly created with no obsolescence",
            "All cost components are in current dollars",
        ]

    return {
        "value": value,
        "method": "Reproduction Cost",
        "formula_reference": "Chapter 3: Cost Approach - Reproduction Cost Method",
        "gross_cost": gross_cost,
        "total_obsolescence_pct": total_obsolescence,
        "steps": steps,
        "assumptions": assumptions,
    }


def replacement_cost(
    current_cost: float,
    obsolescence_factors: dict | None = None,
) -> dict:
    """Calculate depreciated replacement cost of an intangible asset.

    Replacement cost estimates the cost to create an asset with equivalent
    utility using modern materials, design, and standards (not an exact replica).

    Formula:
        Replacement Cost = current_cost * (1 - total_obsolescence)
        total_obsolescence = 1 - (1 - functional) * (1 - technological) * (1 - economic)

    Args:
        current_cost: Current cost to replace the asset with equivalent utility.
            Must be non-negative.
        obsolescence_factors: Optional dict with 'functional', 'technological', 'economic'
            keys. Values must be between 0 and 1. Defaults to no obsolescence.

    Returns:
        Dict with:
            - value: Depreciated replacement cost
            - method: 'Replacement Cost'
            - formula_reference: 'Chapter 3: Cost Approach - Replacement Cost Method'
            - gross_cost: Current replacement cost before obsolescence
            - total_obsolescence_pct: Combined obsolescence percentage
            - steps: List of calculation steps
            - assumptions: Key assumptions used

    Raises:
        ValueError: If current_cost is negative or obsolescence factors are out of range.

    Example:
        >>> result = replacement_cost(
        ...     500000,
        ...     {"functional": 0.10, "technological": 0.30}
        ... )
        >>> result["value"]
        315000.0
    """
    if not isinstance(current_cost, (int, float)):
        raise ValueError(f"current_cost must be a number, got {type(current_cost).__name__}")
    if current_cost < 0:
        raise ValueError(f"current_cost must be non-negative, got {current_cost}")

    steps = [
        f"Current replacement cost: ${current_cost:,.2f}",
    ]

    if obsolescence_factors:
        obs = ObsolescenceInput(**obsolescence_factors)
        combined_retention = (
            (1 - obs.functional) * (1 - obs.technological) * (1 - obs.economic)
        )
        total_obsolescence = 1 - combined_retention
        value = current_cost * combined_retention

        steps.append(
            f"Apply obsolescence: functional={obs.functional:.1%}, "
            f"technological={obs.technological:.1%}, economic={obs.economic:.1%}"
        )
        steps.append(f"Combined retention factor: {combined_retention:.4f}")
        steps.append(f"Total obsolescence: {total_obsolescence:.1%}")
        steps.append(f"Depreciated replacement cost: ${value:,.2f}")

        assumptions = [
            "Obsolescence factors are multiplicative (combined retention)",
            "Current cost reflects modern equivalent utility",
            "Replacement uses current technology and materials",
        ]
    else:
        value = current_cost
        total_obsolescence = 0.0
        steps.append("No obsolescence adjustments applied")
        assumptions = [
            "Asset is newly created with no obsolescence",
            "Current cost reflects modern equivalent utility",
        ]

    return {
        "value": value,
        "method": "Replacement Cost",
        "formula_reference": "Chapter 3: Cost Approach - Replacement Cost Method",
        "gross_cost": current_cost,
        "total_obsolescence_pct": total_obsolescence,
        "steps": steps,
        "assumptions": assumptions,
    }
