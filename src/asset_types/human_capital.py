"""Human capital valuation methods.

Implements valuation for assembled workforce and key person dependencies.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.core import present_value


class AssembledWorkforceInputs(BaseModel):
    """Inputs for assembled workforce valuation."""

    employee_count: int = Field(ge=1, description="Number of employees")
    avg_replacement_cost: float = Field(ge=0, description="Average replacement cost per employee")
    training_cost: float = Field(ge=0, description="Training cost per employee")
    productivity_factor: float = Field(
        ge=0, le=1, description="Productivity factor vs new hires (0-1)"
    )
    attrition_rate: float = Field(
        ge=0, le=1, description="Annual attrition rate (decimal)"
    )


def assembled_workforce_valuation(
    employee_count: int,
    avg_replacement_cost: float,
    training_cost: float,
    productivity_factor: float,
    attrition_rate: float,
) -> dict:
    """Value an assembled workforce using replacement cost approach.

    The value reflects the cost savings from having a trained, productive
    workforce versus hiring and training new employees. Accounts for
    attrition over a standard ramp-up period.

    Args:
        employee_count: Number of employees.
        avg_replacement_cost: Average cost to replace one employee.
        training_cost: Training cost per employee.
        productivity_factor: Productivity of new hires vs assembled workforce (0-1).
        attrition_rate: Annual attrition rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = AssembledWorkforceInputs(
        employee_count=employee_count,
        avg_replacement_cost=avg_replacement_cost,
        training_cost=training_cost,
        productivity_factor=productivity_factor,
        attrition_rate=attrition_rate,
    )

    steps: list[str] = [
        f"Employee count: {inputs.employee_count:,}",
        f"Avg replacement cost: {inputs.avg_replacement_cost:,.0f}",
        f"Training cost per employee: {inputs.training_cost:,.0f}",
        f"Productivity factor: {inputs.productivity_factor:.2f}",
        f"Attrition rate: {inputs.attrition_rate:.2%}",
    ]

    # Total replacement cost (hiring + training)
    total_replacement = inputs.employee_count * (
        inputs.avg_replacement_cost + inputs.training_cost
    )

    # Productivity loss during ramp-up (assume 1 year)
    productivity_loss = total_replacement * (1 - inputs.productivity_factor)

    # Attrition-adjusted value (workforce decays over time)
    # Use 3-year horizon for assembled workforce value
    horizon = 3
    total_pv = 0.0
    remaining_employees = inputs.employee_count

    for t in range(1, horizon + 1):
        remaining_employees = remaining_employees * (1 - inputs.attrition_rate)
        annual_value = remaining_employees * (
            inputs.avg_replacement_cost + inputs.training_cost
        )
        pv = present_value(annual_value, 0.10, t)  # 10% standard discount
        total_pv += pv
        steps.append(
            f"Year {t}: employees={remaining_employees:,.0f}, "
            f"value={annual_value:,.0f}, PV={pv:,.0f}"
        )

    # Final value is the PV of replacement costs over horizon
    value = total_pv

    steps.append(f"Total replacement cost: {total_replacement:,.0f}")
    steps.append(f"Productivity loss factor: {productivity_loss:,.0f}")
    steps.append(f"Final assembled workforce value: {value:,.0f}")

    return {
        "value": value,
        "method": "Replacement Cost with Attrition Adjustment",
        "formula_reference": "V = sum(N_t x (RC + TC) / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "employee_count": inputs.employee_count,
            "avg_replacement_cost": inputs.avg_replacement_cost,
            "training_cost": inputs.training_cost,
            "productivity_factor": inputs.productivity_factor,
            "attrition_rate": inputs.attrition_rate,
            "horizon_years": horizon,
        },
    }


class KeyPersonInputs(BaseModel):
    """Inputs for key person valuation."""

    revenue_contribution: float = Field(ge=0, description="Annual revenue contribution")
    replacement_cost: float = Field(ge=0, description="Cost to replace the person")
    departure_probability: float = Field(
        ge=0, le=1, description="Annual probability of departure"
    )
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")


def key_person_value(
    revenue_contribution: float,
    replacement_cost: float,
    departure_probability: float,
    discount_rate: float,
) -> dict:
    """Value a key person based on revenue contribution and replacement risk.

    Combines the cost to replace the person with the PV of their revenue
    contribution, adjusted for departure probability over a standard horizon.

    Args:
        revenue_contribution: Annual revenue attributable to the person.
        replacement_cost: Cost to find and train a replacement.
        departure_probability: Annual probability of departure (0-1).
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = KeyPersonInputs(
        revenue_contribution=revenue_contribution,
        replacement_cost=replacement_cost,
        departure_probability=departure_probability,
        discount_rate=discount_rate,
    )

    steps: list[str] = [
        f"Revenue contribution: {inputs.revenue_contribution:,.0f}",
        f"Replacement cost: {inputs.replacement_cost:,.0f}",
        f"Departure probability: {inputs.departure_probability:.2%}",
        f"Discount rate: {inputs.discount_rate:.2%}",
    ]

    # 3-year horizon for key person value
    horizon = 3
    total_pv = 0.0

    for t in range(1, horizon + 1):
        # Probability person is still present
        survival_prob = (1 - inputs.departure_probability) ** t
        expected_revenue = inputs.revenue_contribution * survival_prob
        pv = present_value(expected_revenue, inputs.discount_rate, t)
        total_pv += pv
        steps.append(
            f"Year {t}: survival={survival_prob:.2%}, "
            f"expected rev={expected_revenue:,.0f}, PV={pv:,.0f}"
        )

    # Value is PV of revenue contribution plus replacement cost
    value = total_pv + inputs.replacement_cost
    steps.append(
        f"PV of revenue contribution: {total_pv:,.0f}"
    )
    steps.append(f"Final value (PV + replacement cost): {value:,.0f}")

    return {
        "value": value,
        "method": "Key Person Income and Replacement Cost",
        "formula_reference": "V = RC + sum(Rev x P(survival)^t / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "revenue_contribution": inputs.revenue_contribution,
            "replacement_cost": inputs.replacement_cost,
            "departure_probability": inputs.departure_probability,
            "discount_rate": inputs.discount_rate,
            "horizon_years": horizon,
        },
    }
