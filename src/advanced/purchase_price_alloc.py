"""Purchase Price Allocation (PPA) waterfall analysis.

Implements Section 10.2 and Appendix A.8: Full allocation of purchase price
to tangible assets, identified intangibles, liabilities, and residual goodwill.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from src.core import ValuationResult, present_value
from src.advanced.goodwill import goodwill


class IdentifiedIntangible(BaseModel):
    name: str = Field(min_length=1, description="Name of the intangible asset")
    value: float = Field(gt=0, description="Fair value of the intangible asset")
    method: str = Field(min_length=1, description="Valuation method used (e.g., 'relief-from-royalty', 'MPEEM')")


class PPAInput(BaseModel):
    purchase_price: float = Field(gt=0, description="Total acquisition price")
    tangible_assets_fv: float = Field(ge=0, description="Fair value of tangible assets")
    identified_intangibles: list[IdentifiedIntangible] = Field(min_length=1, description="List of identified intangible assets")
    liabilities_fv: float = Field(ge=0, description="Fair value of assumed liabilities")


def purchase_price_allocation(
    purchase_price: float,
    tangible_assets_fv: float,
    identified_intangibles: list[dict],
    liabilities_fv: float = 0,
) -> ValuationResult:
    """Perform full purchase price allocation waterfall.

    Allocates the purchase price across:
    1. Tangible assets at fair value
    2. Identified intangible assets at fair value
    3. Assumed liabilities at fair value
    4. Goodwill as the residual

    Args:
        purchase_price: Total acquisition consideration.
        tangible_assets_fv: Fair value of all tangible assets acquired.
        identified_intangibles: List of dicts with keys: name, value, method.
        liabilities_fv: Fair value of liabilities assumed.

    Returns:
        ValuationResult with full allocation breakdown and percentages.

    Raises:
        ValueError: If inputs are invalid or result in negative goodwill.

    Example (Book Example):
        $100M purchase, $15M tangible, $60M identified intangibles, $0 liabilities
        Net identifiable = 15M + 60M - 0 = 75M
        Goodwill = 100M - 75M = 25M
    """
    validated_intangibles = [IdentifiedIntangible(**item) for item in identified_intangibles]
    PPAInput(
        purchase_price=purchase_price,
        tangible_assets_fv=tangible_assets_fv,
        identified_intangibles=validated_intangibles,
        liabilities_fv=liabilities_fv,
    )

    total_intangibles = sum(iv.value for iv in validated_intangibles)
    net_identifiable = tangible_assets_fv + total_intangibles - liabilities_fv

    gw_result = goodwill(purchase_price, net_identifiable)
    goodwill_value = gw_result.value

    total_alloc = tangible_assets_fv + total_intangibles + goodwill_value
    pct_tangible = (tangible_assets_fv / purchase_price * 100) if purchase_price else 0
    pct_intangible = (total_intangibles / purchase_price * 100) if purchase_price else 0
    pct_goodwill = (goodwill_value / purchase_price * 100) if purchase_price else 0

    steps = [
        {"item": "Purchase Price", "value": purchase_price},
        {"item": "Tangible Assets", "value": tangible_assets_fv},
        {"item": "Identified Intangibles", "value": total_intangibles},
        {"item": "Liabilities", "value": -liabilities_fv},
        {"item": "Net Identifiable Assets", "value": net_identifiable},
        {"item": "Goodwill (residual)", "value": goodwill_value},
    ]

    for iv in validated_intangibles:
        steps.insert(2, {"item": f"  - {iv.name} ({iv.method})", "value": iv.value})

    allocation = {
        "tangible": f"{pct_tangible:.1f}%",
        "intangible": f"{pct_intangible:.1f}%",
        "goodwill": f"{pct_goodwill:.1f}%",
    }

    return ValuationResult(
        value=goodwill_value,
        method="Purchase Price Allocation",
        formula_reference="Ch 10.2, Appendix A.8",
        steps=steps,
        assumptions={"allocation": allocation},
    )


class BargainPurchaseInputs(BaseModel):
    """Inputs for bargain purchase analysis."""

    purchase_price: float = Field(gt=0, description="Total acquisition price")
    fair_value_net_assets: float = Field(gt=0, description="Fair value of net identifiable assets")


def bargain_purchase_analysis(
    purchase_price: float,
    fair_value_net_assets: float,
) -> dict:
    """Analyze and document a bargain purchase (negative goodwill) situation.

    A bargain purchase occurs when the purchase price is less than the fair
    value of net identifiable assets acquired. Under ASC 805 / IFRS 3, this
    requires:
    1. Reassessment of asset/liability identification and valuation
    2. Recognition of any remaining excess as a gain in the income statement

    Formula:
        Bargain Purchase Gain = Fair Value of Net Assets - Purchase Price

    Args:
        purchase_price: Total acquisition consideration paid.
        fair_value_net_assets: Fair value of net identifiable assets acquired.

    Returns:
        Dict with value (gain amount), method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If not actually a bargain purchase (purchase_price >= fair_value_net_assets).

    Example:
        >>> result = bargain_purchase_analysis(
        ...     purchase_price=40_000_000,
        ...     fair_value_net_assets=50_000_000,
        ... )
        >>> result["value"]
        10000000.0

    Reference:
        ASC 805-30-25: Bargain purchase recognition.
        IFRS 3.34-36: Gain on bargain purchase.
    """
    inputs = BargainPurchaseInputs(
        purchase_price=purchase_price,
        fair_value_net_assets=fair_value_net_assets,
    )

    if inputs.purchase_price >= inputs.fair_value_net_assets:
        raise ValueError(
            "Not a bargain purchase: purchase price must be less than "
            f"fair value of net assets. Got purchase_price={inputs.purchase_price}, "
            f"fair_value_net_assets={inputs.fair_value_net_assets}"
        )

    gain = inputs.fair_value_net_assets - inputs.purchase_price
    gain_pct = gain / inputs.fair_value_net_assets

    steps: list[str] = [
        f"Purchase price: {inputs.purchase_price:,.0f}",
        f"Fair value of net identifiable assets: {inputs.fair_value_net_assets:,.0f}",
        f"Bargain purchase gain: {gain:,.0f} ({gain_pct:.1%} of net assets)",
        "",
        "Required actions under ASC 805 / IFRS 3:",
        "1. Reassess identification and measurement of acquired assets/liabilities",
        "2. Verify completeness of intangible asset identification",
        "3. Review fair value measurements for reasonableness",
        "4. Recognize remaining gain in current period income statement",
    ]

    return {
        "value": gain,
        "method": "Bargain Purchase Analysis",
        "formula_reference": "ASC 805-30-25, Gain = FV(Net Assets) - Purchase Price",
        "steps": steps,
        "assumptions": {
            "purchase_price": inputs.purchase_price,
            "fair_value_net_assets": inputs.fair_value_net_assets,
            "bargain_purchase_gain": gain,
            "gain_percentage": round(gain_pct, 4),
        },
    }


class ContingentConsiderationInputs(BaseModel):
    """Inputs for contingent consideration valuation."""

    scenarios: list[dict] = Field(
        min_length=1, description="List of scenarios with 'probability' and 'payment'"
    )
    discount_rate: float = Field(gt=0, description="Discount rate (decimal)")

    @field_validator("scenarios")
    @classmethod
    def scenarios_valid(cls, v: list[dict]) -> list[dict]:
        total_prob = sum(s.get("probability", 0) for s in v)
        if abs(total_prob - 1.0) > 0.01:
            raise ValueError(
                f"Scenario probabilities must sum to 1.0, got {total_prob:.4f}"
            )
        for i, s in enumerate(v):
            if "payment" not in s:
                raise ValueError(f"Scenario {i} missing 'payment' key")
            if s["payment"] < 0:
                raise ValueError(f"Scenario {i} payment must be non-negative")
        return v


def contingent_consideration_valuation(
    scenarios: list[dict],
    discount_rate: float,
) -> dict:
    """Value earn-out / contingent consideration using probability-weighted scenarios.

    Contingent consideration (earn-out) is valued as the probability-weighted
    expected payment, discounted to present value.

    Formula:
        Expected Payment = sum(probability_i x payment_i)
        Present Value = Expected Payment / (1 + r)^t

    Where t is the expected payment period (from 'period' key in each scenario,
    default 1).

    Args:
        scenarios: List of dicts with 'probability' (float), 'payment' (float),
            and optional 'period' (int, default 1). Probabilities must sum to ~1.0.
        discount_rate: Discount rate reflecting the risk of the contingent payment.

    Returns:
        Dict with value (PV of contingent consideration), method,
        formula_reference, steps, and assumptions.

    Raises:
        ValueError: If scenarios are invalid or probabilities don't sum to 1.

    Example:
        >>> scenarios = [
        ...     {"probability": 0.3, "payment": 5_000_000, "period": 1},
        ...     {"probability": 0.5, "payment": 10_000_000, "period": 2},
        ...     {"probability": 0.2, "payment": 15_000_000, "period": 3},
        ... ]
        >>> result = contingent_consideration_valuation(scenarios, 0.10)
        >>> result["value"] > 0
        True

    Reference:
        ASC 805-30-25: Contingent consideration at fair value.
        IFRS 3.40: Contingent consideration measurement.
    """
    inputs = ContingentConsiderationInputs(
        scenarios=scenarios,
        discount_rate=discount_rate,
    )

    steps: list[str] = []
    total_expected_pv = 0.0

    steps.append(f"Number of scenarios: {len(inputs.scenarios)}")
    steps.append(f"Discount rate: {inputs.discount_rate:.2%}")
    steps.append("")

    for i, scenario in enumerate(inputs.scenarios, start=1):
        prob = scenario["probability"]
        payment = scenario["payment"]
        period = scenario.get("period", 1)

        expected = prob * payment
        pv = present_value(expected, inputs.discount_rate, period)
        total_expected_pv += pv

        steps.append(
            f"Scenario {i}: prob={prob:.0%}, payment={payment:,.0f}, "
            f"period={period}, expected={expected:,.0f}, PV={pv:,.0f}"
        )

    steps.append("")
    steps.append(f"Total PV of contingent consideration: {total_expected_pv:,.0f}")

    return {
        "value": total_expected_pv,
        "method": "Contingent Consideration (Probability-Weighted)",
        "formula_reference": "ASC 805-30-25, PV = sum(p_i x payment_i / (1+r)^t)",
        "steps": steps,
        "assumptions": {
            "num_scenarios": len(inputs.scenarios),
            "discount_rate": inputs.discount_rate,
            "scenarios": inputs.scenarios,
            "total_expected_pv": round(total_expected_pv, 2),
        },
    }


class DTLPPAInputs(BaseModel):
    """Inputs for deferred tax liability from PPA."""

    identified_intangibles: list[dict] = Field(
        min_length=1, description="Intangibles with 'name' and 'fair_value'"
    )
    tax_basis: float = Field(ge=0, description="Tax basis of identified intangibles")
    statutory_rate: float = Field(gt=0, le=1, description="Statutory tax rate (decimal)")


def deferred_tax_liability_ppa(
    identified_intangibles: list[dict],
    tax_basis: float,
    statutory_rate: float,
) -> dict:
    """Calculate deferred tax liability arising from PPA step-up in basis.

    When intangible assets are recorded at fair value in a business combination
    but have a lower tax basis, a temporary difference arises. This creates a
    deferred tax liability that must be recognized.

    Formula:
        Book Value (FV) = sum(fair_value of identified intangibles)
        Temporary Difference = Book Value - Tax Basis
        DTL = Temporary Difference x Statutory Tax Rate

    The DTL increases the amount of goodwill recognized (gross-up effect).

    Args:
        identified_intangibles: List of dicts with 'name' and 'fair_value'.
        tax_basis: Tax basis of the identified intangibles (often zero or
            carryover basis).
        statutory_rate: Applicable statutory income tax rate (decimal).

    Returns:
        Dict with value (DTL amount), method, formula_reference, steps, and assumptions.

    Raises:
        ValueError: If inputs are invalid.

    Example:
        >>> intangibles = [
        ...     {"name": "Customer Relationships", "fair_value": 20_000_000},
        ...     {"name": "Technology", "fair_value": 25_000_000},
        ... ]
        >>> result = deferred_tax_liability_ppa(intangibles, 0, 0.25)
        >>> result["value"]  # (45M - 0) x 0.25 = 11.25M
        11250000.0

    Reference:
        ASC 805-740: Income taxes in business combinations.
        IAS 12.19: Deferred tax liabilities on temporary differences.
    """
    if not identified_intangibles:
        raise ValueError("identified_intangibles list cannot be empty")

    for i, item in enumerate(identified_intangibles):
        if "name" not in item:
            raise ValueError(f"Intangible {i} missing 'name' key")
        if "fair_value" not in item:
            raise ValueError(f"Intangible {i} missing 'fair_value' key")
        if item["fair_value"] < 0:
            raise ValueError(f"Intangible {i} fair_value must be non-negative")

    inputs = DTLPPAInputs(
        identified_intangibles=identified_intangibles,
        tax_basis=tax_basis,
        statutory_rate=statutory_rate,
    )

    steps: list[str] = []

    total_fv = sum(item["fair_value"] for item in inputs.identified_intangibles)
    temp_diff = total_fv - inputs.tax_basis
    dtl = temp_diff * inputs.statutory_rate

    steps.append(f"Identified intangibles:")
    for item in inputs.identified_intangibles:
        steps.append(f"  {item['name']}: {item['fair_value']:,.0f}")
    steps.append(f"Total fair value: {total_fv:,.0f}")
    steps.append(f"Tax basis: {inputs.tax_basis:,.0f}")
    steps.append(f"Temporary difference: {temp_diff:,.0f}")
    steps.append(f"Statutory tax rate: {inputs.statutory_rate:.2%}")
    steps.append(f"Deferred tax liability: {dtl:,.0f}")
    steps.append("")
    steps.append("Note: DTL increases goodwill in PPA (gross-up effect)")
    steps.append(f"Grossed-up goodwill increase: {dtl:,.0f}")

    return {
        "value": dtl,
        "method": "Deferred Tax Liability from PPA Step-Up",
        "formula_reference": "ASC 805-740, DTL = (FV - Tax Basis) x Tax Rate",
        "steps": steps,
        "assumptions": {
            "total_fair_value": total_fv,
            "tax_basis": inputs.tax_basis,
            "temporary_difference": temp_diff,
            "statutory_rate": inputs.statutory_rate,
            "dtl": dtl,
            "num_intangibles": len(inputs.identified_intangibles),
        },
    }
