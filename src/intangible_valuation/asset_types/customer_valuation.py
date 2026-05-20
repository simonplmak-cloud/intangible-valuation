"""Customer-related asset valuation methods.

Implements valuation for customer relationships, distribution networks,
and non-compete agreements.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from intangible_valuation.core import ValuationResult, present_value


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
) -> ValuationResult:
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
    current_customers = float(inputs.customer_count)

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

    return ValuationResult(value=total_pv, method="Multi-Period Customer Cash Flow with Attrition", formula_reference="V = sum(C0 x r^t x RPU x PM / (1+d)^t)", steps=steps, assumptions={
            "customer_count": inputs.customer_count,
            "avg_revenue_per_customer": inputs.avg_revenue_per_customer,
            "retention_rate": inputs.retention_rate,
            "profit_margin": inputs.profit_margin,
            "discount_rate": inputs.discount_rate,
            "projection_period": inputs.projection_period,
        })


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
) -> ValuationResult:
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

    return ValuationResult(value=pv, method="Distribution Network Income Approach", formula_reference="V = sum(Channels x Rev/Ch x Margin / (1+r)^t)", steps=steps, assumptions={
            "channel_count": inputs.channel_count,
            "revenue_per_channel": inputs.revenue_per_channel,
            "channel_margin": inputs.channel_margin,
            "useful_life": inputs.useful_life,
            "discount_rate": inputs.discount_rate,
        })


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
) -> ValuationResult:
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

    return ValuationResult(value=total_pv, method="Non-Compete Income Approach with Enforcement Risk", formula_reference="V = sum(Rev x PM x P(enforce) / (1+r)^t)", steps=steps, assumptions={
            "protected_revenue": inputs.protected_revenue,
            "profit_margin": inputs.profit_margin,
            "term": inputs.term,
            "enforcement_probability": inputs.enforcement_probability,
            "discount_rate": inputs.discount_rate,
        })


class CLVInputs(BaseModel):
    """Inputs for customer lifetime value calculation."""

    revenue_per_period: float = Field(gt=0, description="Revenue per period per customer")
    retention_rate: float = Field(ge=0, lt=1, description="Retention rate per period (decimal)")
    discount_rate: float = Field(ge=0, description="Discount rate per period (decimal)")
    margin: float = Field(ge=0, le=1, description="Profit margin (decimal)")


def customer_lifetime_value(
    revenue_per_period: float,
    retention_rate: float,
    discount_rate: float,
    margin: float,
) -> ValuationResult:
    """Calculate customer lifetime value using the infinite horizon CLV formula.

    Formula:
        CLV = margin x revenue_per_period x retention_rate / (1 + discount_rate - retention_rate)

    This is the closed-form solution for an infinite-horizon CLV with constant
    retention and discount rates.

    Args:
        revenue_per_period: Revenue generated per customer per period.
        retention_rate: Probability a customer remains active (0-1, must be < 1).
        discount_rate: Discount rate per period (decimal).
        margin: Profit margin on revenue (0-1, decimal).

    Returns:
        Dict with value (CLV per customer), method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If retention_rate >= 1 or other inputs are invalid.

    Example:
        >>> result = customer_lifetime_value(100, 0.80, 0.10, 0.30)
        >>> result.value  # 0.30 * 100 * 0.80 / (1 + 0.10 - 0.80) = 80.0
        80.0

    Reference:
        Gupta, S. & Lehmann, D. (2005). Managing Customers as Investments.
        Wharton School Publishing.
    """
    inputs = CLVInputs(
        revenue_per_period=revenue_per_period,
        retention_rate=retention_rate,
        discount_rate=discount_rate,
        margin=margin,
    )

    steps: list[str] = []

    profit_per_period = inputs.revenue_per_period * inputs.margin
    denominator = 1 + inputs.discount_rate - inputs.retention_rate

    if denominator <= 0:
        raise ValueError(
            "Discount rate must be greater than retention_rate - 1. "
            f"Got discount_rate={inputs.discount_rate}, retention_rate={inputs.retention_rate}"
        )

    clv = profit_per_period * inputs.retention_rate / denominator

    steps.append(f"Revenue per period: {inputs.revenue_per_period:,.2f}")
    steps.append(f"Profit margin: {inputs.margin:.2%}")
    steps.append(f"Profit per period: {profit_per_period:,.2f}")
    steps.append(f"Retention rate: {inputs.retention_rate:.2%}")
    steps.append(f"Discount rate: {inputs.discount_rate:.2%}")
    steps.append(f"Denominator (1+r-retention): {denominator:.4f}")
    steps.append(f"CLV: {clv:,.2f}")

    return ValuationResult(value=clv, method="Customer Lifetime Value (Infinite Horizon)", formula_reference="CLV = margin x RPP x r / (1 + d - r)", steps=steps, assumptions={
            "revenue_per_period": inputs.revenue_per_period,
            "retention_rate": inputs.retention_rate,
            "discount_rate": inputs.discount_rate,
            "margin": inputs.margin,
            "profit_per_period": profit_per_period,
        })


class BacklogValuationInputs(BaseModel):
    """Inputs for order backlog valuation."""

    contract_backlog: list[dict] = Field(
        min_length=1, description="List of contracts with 'value' and optional 'period'"
    )
    probability_of_completion: float = Field(
        ge=0, le=1, description="Probability of contract completion"
    )
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")


def backlog_valuation(
    contract_backlog: list[dict],
    probability_of_completion: float,
    discount_rate: float,
) -> ValuationResult:
    """Value order backlog as risk-adjusted present value of contracted revenue.

    Each contract in the backlog is discounted to present value and adjusted
    for the probability of successful completion.

    Formula:
        Value = sum(contract_value x P(completion) / (1 + r)^period)

    Args:
        contract_backlog: List of dicts with 'value' (float) and optional
            'period' (int, default 1) for each contract.
        probability_of_completion: Overall probability contracts will be
            fulfilled (0-1).
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value, method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If backlog is empty or inputs are invalid.

    Example:
        >>> backlog = [
        ...     {"value": 500_000, "period": 1},
        ...     {"value": 300_000, "period": 2},
        ... ]
        >>> result = backlog_valuation(backlog, 0.90, 0.10)
        >>> result.value > 0
        True
    """
    if not contract_backlog:
        raise ValueError("Contract backlog cannot be empty")

    inputs = BacklogValuationInputs(
        contract_backlog=contract_backlog,
        probability_of_completion=probability_of_completion,
        discount_rate=discount_rate,
    )

    steps: list[str] = []
    total_pv = 0.0
    total_nominal = 0.0

    for i, contract in enumerate(inputs.contract_backlog, start=1):
        value = contract["value"]
        period = contract.get("period", 1)
        total_nominal += value

        expected_value = value * inputs.probability_of_completion
        pv = present_value(expected_value, inputs.discount_rate, period)
        total_pv += pv

        steps.append(
            f"Contract {i}: value={value:,.0f}, period={period}, "
            f"expected={expected_value:,.0f}, PV={pv:,.0f}"
        )

    steps.append(f"Total nominal backlog: {total_nominal:,.0f}")
    steps.append(f"Risk-adjusted PV: {total_pv:,.0f}")

    return ValuationResult(value=total_pv, method="Order Backlog Risk-Adjusted PV", formula_reference="V = sum(Value x P(complete) / (1+r)^t)", steps=steps, assumptions={
            "num_contracts": len(inputs.contract_backlog),
            "total_nominal_value": total_nominal,
            "probability_of_completion": inputs.probability_of_completion,
            "discount_rate": inputs.discount_rate,
        })


class ChurnImpactInputs(BaseModel):
    """Inputs for churn impact analysis."""

    current_customers: int = Field(ge=1, description="Current customer count")
    churn_rate_before: float = Field(ge=0, lt=1, description="Churn rate before change")
    churn_rate_after: float = Field(ge=0, lt=1, description="Churn rate after change")
    revenue_per_customer: float = Field(gt=0, description="Annual revenue per customer")
    discount_rate: float = Field(ge=0, description="Discount rate (decimal)")


def churn_impact_analysis(
    current_customers: int,
    churn_rate_before: float,
    churn_rate_after: float,
    revenue_per_customer: float,
    discount_rate: float,
) -> ValuationResult:
    """Analyze the value impact of a change in customer churn rate.

    Compares the present value of the customer base under two churn scenarios
    over a 5-year projection period.

    Formula:
        Customers(t) = Initial x (1 - churn_rate)^t
        Revenue(t) = Customers(t) x revenue_per_customer
        PV = sum(Revenue(t) / (1 + r)^t)
        Impact = PV(before) - PV(after)

    Args:
        current_customers: Current number of customers.
        churn_rate_before: Annual churn rate before the change (0-1).
        churn_rate_after: Annual churn rate after the change (0-1).
        revenue_per_customer: Annual revenue per customer.
        discount_rate: Discount rate (decimal).

    Returns:
        Dict with value (impact = PV_before - PV_after), method,
        formula_reference, steps, and assumptions.

    Raises:
        ValueError: If churn rates are >= 1 or other inputs are invalid.

    Example:
        >>> result = churn_impact_analysis(
        ...     current_customers=1000,
        ...     churn_rate_before=0.20,
        ...     churn_rate_after=0.15,
        ...     revenue_per_customer=5000,
        ...     discount_rate=0.10,
        ... )
        >>> result.value > 0  # reducing churn creates value
        True
    """
    inputs = ChurnImpactInputs(
        current_customers=current_customers,
        churn_rate_before=churn_rate_before,
        churn_rate_after=churn_rate_after,
        revenue_per_customer=revenue_per_customer,
        discount_rate=discount_rate,
    )

    steps: list[str] = []
    projection_years = 5

    def calc_pv(churn_rate: float) -> tuple[float, list[tuple[int, int, float, float]]]:
        total = 0.0
        yearly_details: list[tuple[int, int, float, float]] = []
        customers = float(inputs.current_customers)
        for t in range(1, projection_years + 1):
            customers = customers * (1 - churn_rate)
            revenue = customers * inputs.revenue_per_customer
            pv = present_value(revenue, inputs.discount_rate, t)
            total += pv
            yearly_details.append((t, int(customers), revenue, pv))
        return total, yearly_details

    pv_before, details_before = calc_pv(inputs.churn_rate_before)
    pv_after, details_after = calc_pv(inputs.churn_rate_after)
    impact = pv_after - pv_before

    steps.append(f"Current customers: {inputs.current_customers:,}")
    steps.append(f"Revenue per customer: {inputs.revenue_per_customer:,.0f}")
    steps.append(f"Projection period: {projection_years} years")
    steps.append("")
    steps.append("Scenario 1 (Before):")
    steps.append(f"  Churn rate: {inputs.churn_rate_before:.2%}")
    for t, cust, rev, pv in details_before:
        steps.append(f"  Year {t}: {cust:,} customers, revenue={rev:,.0f}, PV={pv:,.0f}")
    steps.append(f"  Total PV: {pv_before:,.0f}")
    steps.append("")
    steps.append("Scenario 2 (After):")
    steps.append(f"  Churn rate: {inputs.churn_rate_after:.2%}")
    for t, cust, rev, pv in details_after:
        steps.append(f"  Year {t}: {cust:,} customers, revenue={rev:,.0f}, PV={pv:,.0f}")
    steps.append(f"  Total PV: {pv_after:,.0f}")
    steps.append("")
    steps.append(f"Value impact (PV_after - PV_before): {impact:,.0f}")

    return ValuationResult(value=impact, method="Churn Impact Analysis", formula_reference="Impact = PV(churn_after) - PV(churn_before)", steps=steps, assumptions={
            "current_customers": inputs.current_customers,
            "churn_rate_before": inputs.churn_rate_before,
            "churn_rate_after": inputs.churn_rate_after,
            "revenue_per_customer": inputs.revenue_per_customer,
            "discount_rate": inputs.discount_rate,
            "projection_years": projection_years,
            "pv_before": round(pv_before, 2),
            "pv_after": round(pv_after, 2),
        })
