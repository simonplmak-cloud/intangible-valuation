"""Technology asset valuation methods.

Implements valuation for developed technology, software, data assets,
and platforms with network effects.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.core import (
    present_value,
    present_value_of_annuity,
)

LIFE_CYCLE_RISK = {
    "emerging": 0.30,
    "growth": 0.20,
    "mature": 0.12,
    "decline": 0.25,
}


class DevelopedTechnologyInputs(BaseModel):
    """Inputs for developed technology valuation."""

    rd_costs: float = Field(ge=0, description="R&D development costs")
    life_cycle_stage: str = Field(
        description="Life cycle stage: emerging, growth, mature, decline"
    )
    competitive_advantage: int = Field(
        ge=1, description="Competitive advantage period in years"
    )
    discount_rate: float = Field(ge=0, description="Base discount rate (decimal)")
    cash_flow_projections: list[float] = Field(
        min_length=1, description="Projected annual cash flows"
    )

    @field_validator("life_cycle_stage")
    @classmethod
    def valid_stage(cls, v: str) -> str:
        if v not in LIFE_CYCLE_RISK:
            raise ValueError(
                f"Invalid life cycle stage: {v}. "
                f"Must be one of: {list(LIFE_CYCLE_RISK.keys())}"
            )
        return v

    @field_validator("cash_flow_projections")
    @classmethod
    def cash_flows_non_negative(cls, v: list[float]) -> list[float]:
        if any(cf < 0 for cf in v):
            raise ValueError("Cash flow projections must be non-negative")
        return v


def developed_technology_valuation(
    rd_costs: float,
    life_cycle_stage: str,
    competitive_advantage: int,
    discount_rate: float,
    cash_flow_projections: list[float],
) -> dict:
    """Value developed technology with life-cycle risk adjustment.

    Combines cost approach (R&D costs as floor) with income approach,
    where the life cycle stage adjusts the discount rate for risk.

    Args:
        rd_costs: R&D development costs.
        life_cycle_stage: One of "emerging", "growth", "mature", "decline".
        competitive_advantage: Competitive advantage period in years.
        discount_rate: Base discount rate (decimal).
        cash_flow_projections: Projected annual cash flows.

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = DevelopedTechnologyInputs(
        rd_costs=rd_costs,
        life_cycle_stage=life_cycle_stage,
        competitive_advantage=competitive_advantage,
        discount_rate=discount_rate,
        cash_flow_projections=cash_flow_projections,
    )

    # Risk-adjusted discount rate based on life cycle stage
    risk_premium = LIFE_CYCLE_RISK[inputs.life_cycle_stage]
    adjusted_discount_rate = inputs.discount_rate + risk_premium

    steps: list[str] = [
        f"R&D costs (floor): {inputs.rd_costs:,.0f}",
        f"Life cycle stage: {inputs.life_cycle_stage}",
        f"Risk premium: {risk_premium:.2%}",
        f"Adjusted discount rate: {adjusted_discount_rate:.2%}",
    ]

    # PV of cash flows over competitive advantage period
    pv_cash_flows = 0.0
    for t, cf in enumerate(inputs.cash_flow_projections, start=1):
        if t > inputs.competitive_advantage:
            break
        pv = present_value(cf, adjusted_discount_rate, t)
        pv_cash_flows += pv
        steps.append(f"Year {t} CF: {cf:,.0f} -> PV: {pv:,.0f}")

    # Value is max of cost floor and income approach
    value = max(inputs.rd_costs, pv_cash_flows)
    steps.append(
        f"Final value (max of cost {inputs.rd_costs:,.0f} "
        f"and income {pv_cash_flows:,.0f}): {value:,.0f}"
    )

    return {
        "value": value,
        "method": "Cost-Income Hybrid with Life Cycle Risk",
        "formula_reference": "V = max(Cost, sum(CF_t / (1+r+risk)^t))",
        "steps": steps,
        "assumptions": {
            "rd_costs": inputs.rd_costs,
            "life_cycle_stage": inputs.life_cycle_stage,
            "risk_premium": risk_premium,
            "competitive_advantage": inputs.competitive_advantage,
            "base_discount_rate": inputs.discount_rate,
            "adjusted_discount_rate": adjusted_discount_rate,
        },
    }


class SoftwareInputs(BaseModel):
    """Inputs for software valuation."""

    development_cost: float = Field(ge=0, description="Development cost")
    maintenance_cost: float = Field(ge=0, description="Annual maintenance cost")
    user_base: int = Field(ge=0, description="Number of users")
    revenue_model: dict = Field(
        description="Revenue model with 'type' and 'revenue_per_user'"
    )
    useful_life: int = Field(ge=1, description="Useful life in years")
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")

    @field_validator("revenue_model")
    @classmethod
    def valid_revenue_model(cls, v: dict) -> dict:
        if "type" not in v:
            raise ValueError("Revenue model must include 'type'")
        if "revenue_per_user" not in v:
            raise ValueError("Revenue model must include 'revenue_per_user'")
        if v["revenue_per_user"] < 0:
            raise ValueError("Revenue per user must be non-negative")
        return v


def software_valuation(
    development_cost: float,
    maintenance_cost: float,
    user_base: int,
    revenue_model: dict,
    useful_life: int,
    discount_rate: float,
) -> dict:
    """Value software using cost and income approaches.

    Combines replacement cost with PV of net cash flows from the user base.

    Args:
        development_cost: Cost to develop the software.
        maintenance_cost: Annual maintenance cost.
        user_base: Current number of users.
        revenue_model: Dict with "type" and "revenue_per_user".
        useful_life: Useful life in years.
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = SoftwareInputs(
        development_cost=development_cost,
        maintenance_cost=maintenance_cost,
        user_base=user_base,
        revenue_model=revenue_model,
        useful_life=useful_life,
        discount_rate=discount_rate,
    )

    annual_revenue = inputs.user_base * inputs.revenue_model["revenue_per_user"]
    net_cash_flow = annual_revenue - inputs.maintenance_cost

    steps = [
        f"Development cost: {inputs.development_cost:,.0f}",
        f"User base: {inputs.user_base:,}",
        f"Revenue model: {inputs.revenue_model['type']}",
        f"Revenue per user: {inputs.revenue_model['revenue_per_user']:,.2f}",
        f"Annual revenue: {annual_revenue:,.0f}",
        f"Annual maintenance: {inputs.maintenance_cost:,.0f}",
        f"Net annual cash flow: {net_cash_flow:,.0f}",
    ]

    if net_cash_flow > 0:
        income_value = present_value_of_annuity(
            net_cash_flow, inputs.discount_rate, inputs.useful_life
        )
    else:
        income_value = 0

    steps.append(f"Income approach PV: {income_value:,.0f}")

    # Value is max of cost and income
    value = max(inputs.development_cost, income_value)
    steps.append(
        f"Final value (max of cost {inputs.development_cost:,.0f} "
        f"and income {income_value:,.0f}): {value:,.0f}"
    )

    return {
        "value": value,
        "method": "Cost-Income Hybrid (Software)",
        "formula_reference": "V = max(Cost, sum((Rev - Maint) / (1+r)^t))",
        "steps": steps,
        "assumptions": {
            "development_cost": inputs.development_cost,
            "maintenance_cost": inputs.maintenance_cost,
            "user_base": inputs.user_base,
            "revenue_model_type": inputs.revenue_model["type"],
            "revenue_per_user": inputs.revenue_model["revenue_per_user"],
            "useful_life": inputs.useful_life,
            "discount_rate": inputs.discount_rate,
        },
    }


class DataAssetInputs(BaseModel):
    """Inputs for data asset valuation."""

    acquisition_cost: float = Field(ge=0, description="Data acquisition cost")
    quality_score: float = Field(ge=0, le=1, description="Data quality score (0-1)")
    revenue_contribution: float = Field(
        ge=0, description="Annual revenue contribution"
    )
    useful_life: int = Field(ge=1, description="Useful life in years")
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")


def data_asset_valuation(
    acquisition_cost: float,
    quality_score: float,
    revenue_contribution: float,
    useful_life: int,
    discount_rate: float,
) -> dict:
    """Value a data asset with quality-adjusted revenue contribution.

    Quality score (0-1) adjusts the revenue contribution to reflect
    data completeness, accuracy, and usability.

    Args:
        acquisition_cost: Cost to acquire the data.
        quality_score: Data quality score (0-1).
        revenue_contribution: Annual revenue contribution.
        useful_life: Useful life in years.
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = DataAssetInputs(
        acquisition_cost=acquisition_cost,
        quality_score=quality_score,
        revenue_contribution=revenue_contribution,
        useful_life=useful_life,
        discount_rate=discount_rate,
    )

    quality_adjusted_revenue = inputs.revenue_contribution * inputs.quality_score

    steps = [
        f"Acquisition cost: {inputs.acquisition_cost:,.0f}",
        f"Quality score: {inputs.quality_score:.2f}",
        f"Raw revenue contribution: {inputs.revenue_contribution:,.0f}",
        f"Quality-adjusted revenue: {quality_adjusted_revenue:,.0f}",
    ]

    income_value = present_value_of_annuity(
        quality_adjusted_revenue, inputs.discount_rate, inputs.useful_life
    )
    steps.append(f"Income approach PV: {income_value:,.0f}")

    value = max(inputs.acquisition_cost, income_value)
    steps.append(
        f"Final value (max of cost {inputs.acquisition_cost:,.0f} "
        f"and income {income_value:,.0f}): {value:,.0f}"
    )

    return {
        "value": value,
        "method": "Cost-Income Hybrid with Quality Adjustment",
        "formula_reference": "V = max(Cost, sum(Rev x Quality / (1+r)^t))",
        "steps": steps,
        "assumptions": {
            "acquisition_cost": inputs.acquisition_cost,
            "quality_score": inputs.quality_score,
            "revenue_contribution": inputs.revenue_contribution,
            "useful_life": inputs.useful_life,
            "discount_rate": inputs.discount_rate,
        },
    }


class PlatformInputs(BaseModel):
    """Inputs for platform valuation."""

    network_size: int = Field(ge=0, description="Current network size (users)")
    network_effects_coefficient: float = Field(
        ge=0, le=1, description="Network effects coefficient (0-1)"
    )
    revenue_per_user: float = Field(ge=0, description="Revenue per user")
    growth_rate: float = Field(ge=0, description="Network growth rate (decimal)")
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")


def platform_valuation(
    network_size: int,
    network_effects_coefficient: float,
    revenue_per_user: float,
    growth_rate: float,
    discount_rate: float,
) -> dict:
    """Value a platform incorporating network effects in revenue projection.

    Network effects amplify revenue as the user base grows. The coefficient
    determines the strength of the network effect on per-user revenue.

    Args:
        network_size: Current network size (number of users).
        network_effects_coefficient: Network effects coefficient (0-1).
        revenue_per_user: Base revenue per user.
        growth_rate: Network growth rate (decimal).
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = PlatformInputs(
        network_size=network_size,
        network_effects_coefficient=network_effects_coefficient,
        revenue_per_user=revenue_per_user,
        growth_rate=growth_rate,
        discount_rate=discount_rate,
    )

    steps: list[str] = [
        f"Network size: {inputs.network_size:,}",
        f"Network effects coefficient: {inputs.network_effects_coefficient:.2f}",
        f"Base revenue per user: {inputs.revenue_per_user:,.2f}",
        f"Growth rate: {inputs.growth_rate:.2%}",
    ]

    # Project 5 years of cash flows with network effects
    projection_years = 5
    total_pv = 0.0
    current_size = float(inputs.network_size)

    for t in range(1, projection_years + 1):
        # Network grows
        current_size = current_size * (1 + inputs.growth_rate)
        # Network effects boost per-user revenue
        network_boost = 1 + inputs.network_effects_coefficient * (t / projection_years)
        effective_rpu = inputs.revenue_per_user * network_boost
        annual_revenue = current_size * effective_rpu

        pv = present_value(annual_revenue, inputs.discount_rate, t)
        total_pv += pv
        steps.append(
            f"Year {t}: users={current_size:,.0f}, "
            f"RPU={effective_rpu:,.2f}, "
            f"revenue={annual_revenue:,.0f}, PV={pv:,.0f}"
        )

    return {
        "value": total_pv,
        "method": "Network Effects Income Approach",
        "formula_reference": "V = sum(N_t x RPU_t x (1 + NE x t/T) / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "network_size": inputs.network_size,
            "network_effects_coefficient": inputs.network_effects_coefficient,
            "revenue_per_user": inputs.revenue_per_user,
            "growth_rate": inputs.growth_rate,
            "discount_rate": inputs.discount_rate,
            "projection_years": projection_years,
        },
    }


class TechObsolescenceInputs(BaseModel):
    """Inputs for technology obsolescence curve."""

    initial_value: float = Field(gt=0, description="Initial technology value")
    obsolescence_rate: float = Field(
        gt=0, le=1, description="Annual obsolescence rate (decimal)"
    )
    periods: int = Field(ge=1, description="Number of periods to project")


def technology_obsolescence_curve(
    initial_value: float,
    obsolescence_rate: float,
    periods: int,
) -> dict:
    """Calculate technology value decay over time due to obsolescence.

    Models the decline in technology value as newer alternatives emerge.
    Uses exponential decay: V(t) = V0 x (1 - obsolescence_rate)^t

    Args:
        initial_value: Initial technology value at t=0.
        obsolescence_rate: Annual rate of value decay (0-1, decimal).
        periods: Number of periods to project.

    Returns:
        Dict with value (remaining value at end), method, formula_reference,
        steps (value at each period), and assumptions.

    Raises:
        ValueError: If any input is invalid.

    Example:
        >>> result = technology_obsolescence_curve(1_000_000, 0.20, 5)
        >>> result["value"]  # ~327,680
        327680.0
    """
    inputs = TechObsolescenceInputs(
        initial_value=initial_value,
        obsolescence_rate=obsolescence_rate,
        periods=periods,
    )

    steps: list[str] = []
    values: list[float] = []
    current_value = inputs.initial_value

    steps.append(f"Initial value: {inputs.initial_value:,.0f}")
    steps.append(f"Annual obsolescence rate: {inputs.obsolescence_rate:.2%}")
    steps.append(f"Projection periods: {inputs.periods}")

    for t in range(1, inputs.periods + 1):
        current_value = current_value * (1 - inputs.obsolescence_rate)
        values.append(current_value)
        pct_remaining = current_value / inputs.initial_value
        steps.append(
            f"Period {t}: value = {current_value:,.0f} "
            f"({pct_remaining:.1%} of original)"
        )

    return {
        "value": current_value,
        "method": "Technology Obsolescence Curve",
        "formula_reference": "V(t) = V0 x (1 - r)^t",
        "steps": steps,
        "assumptions": {
            "initial_value": inputs.initial_value,
            "obsolescence_rate": inputs.obsolescence_rate,
            "periods": inputs.periods,
            "value_at_each_period": [round(v, 2) for v in values],
            "total_value_lost": round(inputs.initial_value - current_value, 2),
        },
    }


class ApiValuationInputs(BaseModel):
    """Inputs for API valuation."""

    api_calls_per_month: float = Field(gt=0, description="Monthly API call volume")
    revenue_per_call: float = Field(ge=0, description="Revenue per API call")
    growth_rate: float = Field(ge=0, description="Annual growth rate (decimal)")
    useful_life: int = Field(ge=1, description="Useful life in years")
    discount_rate: float = Field(gt=0, description="Discount rate (decimal)")


def api_valuation(
    api_calls_per_month: float,
    revenue_per_call: float,
    growth_rate: float,
    useful_life: int,
    discount_rate: float,
) -> dict:
    """Value an API as an intangible asset based on call volume and revenue.

    Projects annual revenue from API usage with growth, then discounts
    to present value over the API's useful life.

    Formula:
        Annual Revenue(t) = calls_per_month x 12 x revenue_per_call x (1 + g)^(t-1)
        Value = sum(Annual Revenue(t) / (1 + r)^t)

    Args:
        api_calls_per_month: Current monthly API call volume.
        revenue_per_call: Revenue generated per API call.
        growth_rate: Annual growth rate of API usage (decimal).
        useful_life: Expected useful life of the API (years).
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.

    Example:
        >>> result = api_valuation(
        ...     api_calls_per_month=1_000_000,
        ...     revenue_per_call=0.001,
        ...     growth_rate=0.15,
        ...     useful_life=5,
        ...     discount_rate=0.10,
        ... )
        >>> result["value"] > 0
        True
    """
    inputs = ApiValuationInputs(
        api_calls_per_month=api_calls_per_month,
        revenue_per_call=revenue_per_call,
        growth_rate=growth_rate,
        useful_life=useful_life,
        discount_rate=discount_rate,
    )

    steps: list[str] = []
    annual_calls = inputs.api_calls_per_month * 12
    annual_revenue_year1 = annual_calls * inputs.revenue_per_call

    steps.append(f"Monthly API calls: {inputs.api_calls_per_month:,.0f}")
    steps.append(f"Annual calls: {annual_calls:,.0f}")
    steps.append(f"Revenue per call: ${inputs.revenue_per_call:.4f}")
    steps.append(f"Year 1 annual revenue: {annual_revenue_year1:,.0f}")
    steps.append(f"Growth rate: {inputs.growth_rate:.2%}")
    steps.append(f"Useful life: {inputs.useful_life} years")

    total_pv = 0.0
    for t in range(1, inputs.useful_life + 1):
        revenue = annual_revenue_year1 * (1 + inputs.growth_rate) ** (t - 1)
        pv = present_value(revenue, inputs.discount_rate, t)
        total_pv += pv
        steps.append(
            f"Year {t}: revenue={revenue:,.0f}, PV={pv:,.0f}"
        )

    steps.append(f"Total PV: {total_pv:,.0f}")

    return {
        "value": total_pv,
        "method": "API Income Approach",
        "formula_reference": "V = sum(Calls x 12 x RPC x (1+g)^(t-1) / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "api_calls_per_month": inputs.api_calls_per_month,
            "revenue_per_call": inputs.revenue_per_call,
            "growth_rate": inputs.growth_rate,
            "useful_life": inputs.useful_life,
            "discount_rate": inputs.discount_rate,
            "year1_revenue": annual_revenue_year1,
        },
    }


class AlgorithmValuationInputs(BaseModel):
    """Inputs for ML algorithm valuation."""

    computational_savings: float = Field(
        gt=0, description="Annual computational cost savings"
    )
    deployment_scale: float = Field(gt=0, description="Deployment scale factor")
    competitive_advantage_years: int = Field(
        ge=1, description="Expected competitive advantage period (years)"
    )
    discount_rate: float = Field(gt=0, description="Discount rate (decimal)")


def algorithm_valuation(
    computational_savings: float,
    deployment_scale: float,
    competitive_advantage_years: int,
    discount_rate: float,
) -> dict:
    """Value an ML algorithm based on computational savings and competitive advantage.

    Values the algorithm by the cost savings it generates at scale,
    projected over the period of competitive advantage.

    Formula:
        Annual Benefit = Computational Savings x Deployment Scale
        Value = sum(Annual Benefit / (1 + r)^t) for t = 1 to advantage_years

    Args:
        computational_savings: Annual computational cost savings from the algorithm.
        deployment_scale: Scale factor representing breadth of deployment (>0).
        competitive_advantage_years: Expected years of competitive advantage.
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.

    Example:
        >>> result = algorithm_valuation(
        ...     computational_savings=500_000,
        ...     deployment_scale=3.0,
        ...     competitive_advantage_years=5,
        ...     discount_rate=0.12,
        ... )
        >>> result["value"] > 0
        True
    """
    inputs = AlgorithmValuationInputs(
        computational_savings=computational_savings,
        deployment_scale=deployment_scale,
        competitive_advantage_years=competitive_advantage_years,
        discount_rate=discount_rate,
    )

    steps: list[str] = []

    annual_benefit = inputs.computational_savings * inputs.deployment_scale

    steps.append(f"Computational savings: {inputs.computational_savings:,.0f}")
    steps.append(f"Deployment scale: {inputs.deployment_scale:.1f}x")
    steps.append(f"Annual benefit: {annual_benefit:,.0f}")
    steps.append(f"Competitive advantage: {inputs.competitive_advantage_years} years")
    steps.append(f"Discount rate: {inputs.discount_rate:.2%}")

    total_pv = 0.0
    for t in range(1, inputs.competitive_advantage_years + 1):
        pv = present_value(annual_benefit, inputs.discount_rate, t)
        total_pv += pv
        steps.append(f"Year {t}: PV={pv:,.0f}")

    steps.append(f"Total algorithm value: {total_pv:,.0f}")

    return {
        "value": total_pv,
        "method": "ML Algorithm Income Approach",
        "formula_reference": "V = sum(Savings x Scale / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "computational_savings": inputs.computational_savings,
            "deployment_scale": inputs.deployment_scale,
            "competitive_advantage_years": inputs.competitive_advantage_years,
            "discount_rate": inputs.discount_rate,
            "annual_benefit": annual_benefit,
        },
    }
