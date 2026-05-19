"""Customer-related asset valuation methods.

Implements valuation for customer relationships, distribution networks,
and non-compete agreements.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.core import present_value


class CustomerRelationshipInputs(BaseModel):
    """Inputs for customer relationship valuation."""

    customer_count: int = Field(ge=1, description="Number of customers")
    avg_revenue_per_customer: float = Field(
        ge=0, description="Average revenue per customer"
    )
    retention_rate: float = Field(
        ge=0, le=1, description="Annual retention rate (decimal)"
    )
    profit_margin: float = Field(ge=0, le=1, description="Profit margin (decimal)")
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")
    projection_period: int = Field(ge=1, description="Projection period in years")


def customer_relationship_valuation(
    customer_count: int,
    avg_revenue_per_customer: float,
    retention_rate: float,
    profit_margin: float,
    discount_rate: float,
    projection_period: int,
) -> dict:
    """Value customer relationships with multi-period cash flow and attrition.

    Projects declining customer base over time using retention rate,
    calculates profit from remaining customers, and discounts to present value.

    Args:
        customer_count: Initial number of customers.
        avg_revenue_per_customer: Average annual revenue per customer.
        retention_rate: Annual customer retention rate (0-1).
        profit_margin: Profit margin (decimal).
        discount_rate: Discount rate (decimal).
        projection_period: Projection period in years.

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = CustomerRelationshipInputs(
        customer_count=customer_count,
        avg_revenue_per_customer=avg_revenue_per_customer,
        retention_rate=retention_rate,
        profit_margin=profit_margin,
        discount_rate=discount_rate,
        projection_period=projection_period,
    )

    steps: list[str] = [
        f"Initial customers: {inputs.customer_count:,}",
        f"Revenue per customer: {inputs.avg_revenue_per_customer:,.0f}",
        f"Retention rate: {inputs.retention_rate:.2%}",
        f"Profit margin: {inputs.profit_margin:.2%}",
    ]

    total_pv = 0.0
    current_customers = inputs.customer_count

    for t in range(1, inputs.projection_period + 1):
        # Attrition: customers decay by retention rate
        current_customers = current_customers * inputs.retention_rate
        revenue = current_customers * inputs.avg_revenue_per_customer
        profit = revenue * inputs.profit_margin
        pv = present_value(profit, inputs.discount_rate, t)
        total_pv += pv
        steps.append(
            f"Year {t}: customers={current_customers:,.0f}, "
            f"profit={profit:,.0f}, PV={pv:,.0f}"
        )

    return {
        "value": total_pv,
        "method": "Multi-Period Customer Cash Flow with Attrition",
        "formula_reference": "V = sum(C0 x r^t x RPU x PM / (1+d)^t)",
        "steps": steps,
        "assumptions": {
            "customer_count": inputs.customer_count,
            "avg_revenue_per_customer": inputs.avg_revenue_per_customer,
            "retention_rate": inputs.retention_rate,
            "profit_margin": inputs.profit_margin,
            "discount_rate": inputs.discount_rate,
            "projection_period": inputs.projection_period,
        },
    }


class DistributionNetworkInputs(BaseModel):
    """Inputs for distribution network valuation."""

    channel_count: int = Field(ge=1, description="Number of distribution channels")
    revenue_per_channel: float = Field(ge=0, description="Revenue per channel")
    channel_margin: float = Field(ge=0, le=1, description="Channel margin (decimal)")
    useful_life: int = Field(ge=1, description="Useful life in years")
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")


def distribution_network_valuation(
    channel_count: int,
    revenue_per_channel: float,
    channel_margin: float,
    useful_life: int,
    discount_rate: float,
) -> dict:
    """Value a distribution network based on channel profitability.

    Calculates PV of expected profits from distribution channels over
    the network's useful life.

    Args:
        channel_count: Number of distribution channels.
        revenue_per_channel: Annual revenue per channel.
        channel_margin: Profit margin per channel (decimal).
        useful_life: Useful life in years.
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = DistributionNetworkInputs(
        channel_count=channel_count,
        revenue_per_channel=revenue_per_channel,
        channel_margin=channel_margin,
        useful_life=useful_life,
        discount_rate=discount_rate,
    )

    annual_profit = (
        inputs.channel_count
        * inputs.revenue_per_channel
        * inputs.channel_margin
    )

    # PV of annuity
    pv = 0.0
    for t in range(1, inputs.useful_life + 1):
        pv += present_value(annual_profit, inputs.discount_rate, t)

    steps = [
        f"Channel count: {inputs.channel_count:,}",
        f"Revenue per channel: {inputs.revenue_per_channel:,.0f}",
        f"Channel margin: {inputs.channel_margin:.2%}",
        f"Annual profit: {annual_profit:,.0f}",
        f"Useful life: {inputs.useful_life} years",
        f"Discount rate: {inputs.discount_rate:.2%}",
        f"PV of channel profits: {pv:,.0f}",
    ]

    return {
        "value": pv,
        "method": "Distribution Network Income Approach",
        "formula_reference": "V = sum(Channels x Rev/Ch x Margin / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "channel_count": inputs.channel_count,
            "revenue_per_channel": inputs.revenue_per_channel,
            "channel_margin": inputs.channel_margin,
            "useful_life": inputs.useful_life,
            "discount_rate": inputs.discount_rate,
        },
    }


class NonCompeteInputs(BaseModel):
    """Inputs for non-compete agreement valuation."""

    protected_revenue: float = Field(ge=0, description="Revenue protected by agreement")
    profit_margin: float = Field(ge=0, le=1, description="Profit margin (decimal)")
    term: int = Field(ge=1, description="Agreement term in years")
    enforcement_probability: float = Field(
        ge=0, le=1, description="Probability of enforcement"
    )
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")


def non_compete_valuation(
    protected_revenue: float,
    profit_margin: float,
    term: int,
    enforcement_probability: float,
    discount_rate: float,
) -> dict:
    """Value a non-compete agreement based on protected profits.

    Values the expected profit stream protected by the non-compete,
    adjusted for the probability of successful enforcement.

    Args:
        protected_revenue: Annual revenue protected by the agreement.
        profit_margin: Profit margin on protected revenue (decimal).
        term: Agreement term in years.
        enforcement_probability: Probability of enforcement (0-1).
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If any input is invalid.
    """
    inputs = NonCompeteInputs(
        protected_revenue=protected_revenue,
        profit_margin=profit_margin,
        term=term,
        enforcement_probability=enforcement_probability,
        discount_rate=discount_rate,
    )

    annual_profit = inputs.protected_revenue * inputs.profit_margin

    steps: list[str] = [
        f"Protected revenue: {inputs.protected_revenue:,.0f}",
        f"Profit margin: {inputs.profit_margin:.2%}",
        f"Annual protected profit: {annual_profit:,.0f}",
        f"Term: {inputs.term} years",
        f"Enforcement probability: {inputs.enforcement_probability:.2%}",
    ]

    # PV of protected profits adjusted for enforcement risk
    total_pv = 0.0
    for t in range(1, inputs.term + 1):
        expected_profit = annual_profit * inputs.enforcement_probability
        pv = present_value(expected_profit, inputs.discount_rate, t)
        total_pv += pv

    steps.append(f"PV of protected profits: {total_pv:,.0f}")

    return {
        "value": total_pv,
        "method": "Non-Compete Income Approach with Enforcement Risk",
        "formula_reference": "V = sum(Rev x PM x P(enforce) / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "protected_revenue": inputs.protected_revenue,
            "profit_margin": inputs.profit_margin,
            "term": inputs.term,
            "enforcement_probability": inputs.enforcement_probability,
            "discount_rate": inputs.discount_rate,
        },
    }
