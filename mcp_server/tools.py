"""MCP tool definitions for intangible asset valuation.

Wraps all valuation library functions as MCP tools using fastmcp.
Each tool accepts validated parameters and returns JSON-serialized results.
"""

from __future__ import annotations

import json
from typing import Any

# Core Math - Time Value of Money
from src.core.time_value import (
    present_value as _present_value,
    future_value as _future_value,
    annuity_pv as _annuity_pv,
    perpetuity_pv as _perpetuity_pv,
    growing_annuity_pv as _growing_annuity_pv,
    terminal_value as _terminal_value,
)

# Core Math - Discount Rates
from src.core.discount_rates import (
    build_up_discount_rate as _build_up_discount_rate,
    capm_discount_rate as _capm_discount_rate,
    wacc as _wacc,
    tax_amortization_benefit as _tax_amortization_benefit,
    control_premium as _control_premium,
    dlom_finnerty as _dlom_finnerty,
    currency_adjusted_discount_rate as _currency_adjusted_discount_rate,
)

# Approaches
from src.approaches.cost_approach import (
    reproduction_cost as _reproduction_cost,
    replacement_cost as _replacement_cost,
)
from src.approaches.market_approach import (
    market_approach_comparables as _market_approach_comparables,
    royalty_capitalization as _royalty_capitalization,
)

# Income Methods
from src.income_methods.relief_from_royalty import (
    relief_from_royalty as _relief_from_royalty,
)
from src.income_methods.excess_earnings import (
    mpeem as _mpeem,
    single_period_excess_earnings as _single_period_excess_earnings,
    contributory_asset_charges as _contributory_asset_charges,
)
from src.income_methods.incremental_cashflow import (
    incremental_cashflow as _incremental_cashflow,
)

# Asset Types - IP
from src.asset_types.ip_valuation import (
    patent_valuation as _patent_valuation,
    copyright_valuation as _copyright_valuation,
    trade_secret_valuation as _trade_secret_valuation,
)

# Asset Types - Brand
from src.asset_types.brand_valuation import (
    trademark_valuation as _trademark_valuation,
)

# Asset Types - Technology
from src.asset_types.technology_valuation import (
    developed_technology_valuation as _developed_technology_valuation,
    software_valuation as _software_valuation,
    data_asset_valuation as _data_asset_valuation,
    platform_valuation as _platform_valuation,
)

# Asset Types - Customer
from src.asset_types.customer_valuation import (
    customer_relationship_valuation as _customer_relationship_valuation,
    distribution_network_valuation as _distribution_network_valuation,
    non_compete_valuation as _non_compete_valuation,
)

# Asset Types - Human Capital
from src.asset_types.human_capital import (
    assembled_workforce_valuation as _assembled_workforce_valuation,
    key_person_value as _key_person_value,
)

# Advanced
from src.advanced.goodwill import goodwill as _goodwill
from src.advanced.purchase_price_alloc import (
    purchase_price_allocation as _purchase_price_allocation,
)
from src.advanced.impairment_testing import (
    goodwill_impairment_test as _goodwill_impairment_test,
    intangible_impairment_test as _intangible_impairment_test,
)
from src.advanced.royalty_benchmark import (
    royalty_rate_benchmark as _royalty_rate_benchmark,
    adjust_royalty_rate as _adjust_royalty_rate,
    twenty_five_percent_rule as _twenty_five_percent_rule,
)
from src.advanced.transfer_pricing import (
    cup_transfer_price as _cup_transfer_price,
)
from src.advanced.litigation import (
    patent_infringement_damages as _patent_infringement_damages,
)
from src.advanced.monte_carlo import (
    monte_carlo_sensitivity as _monte_carlo_sensitivity,
)
from src.core.statistics import (
    monte_carlo_valuation as _monte_carlo_valuation,
    decision_tree_valuation as _decision_tree_valuation,
)
from src.utils.formulas import (
    estimate_useful_life as _estimate_useful_life,
    sensitivity_analysis as _sensitivity_analysis,
)


def _safe_json(obj: Any) -> str:
    """Serialize result to JSON, handling non-serializable types."""
    def default_handler(o: Any) -> Any:
        if hasattr(o, "model_dump"):
            return o.model_dump()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)
    return json.dumps(obj, default=default_handler, indent=2)


def _run(fn: Any, **kwargs: Any) -> str:
    """Run a valuation function and return JSON result with error handling."""
    try:
        result = fn(**kwargs)
        return _safe_json(result)
    except Exception as e:
        return _safe_json({"error": type(e).__name__, "message": str(e)})


# =============================================================================
# Core Math Tools
# =============================================================================

def present_value(future_value: float, discount_rate: float, periods: int) -> str:
    """Calculate present value of a single future cash flow.

    Formula: PV = FV / (1 + r)^n
    Book Reference: Chapter 2, Section 2.1
    """
    return _run(_present_value, future_value=future_value, discount_rate=discount_rate, periods=periods)


def future_value(present_value: float, discount_rate: float, periods: int) -> str:
    """Calculate future value of a present amount.

    Formula: FV = PV * (1 + r)^n
    Book Reference: Chapter 2, Section 2.2
    """
    return _run(_future_value, present_value=present_value, discount_rate=discount_rate, periods=periods)


def annuity_pv(payment: float, discount_rate: float, periods: int) -> str:
    """Calculate present value of an ordinary annuity.

    Formula: PV = PMT * [1 - (1 + r)^(-n)] / r
    Book Reference: Chapter 2, Section 2.3
    """
    return _run(_annuity_pv, payment=payment, discount_rate=discount_rate, periods=periods)


def perpetuity_pv(payment: float, discount_rate: float) -> str:
    """Calculate present value of a perpetuity.

    Formula: PV = PMT / r
    Book Reference: Chapter 2, Section 2.4
    """
    return _run(_perpetuity_pv, payment=payment, discount_rate=discount_rate)


def growing_annuity_pv(payment: float, discount_rate: float, growth_rate: float, periods: int) -> str:
    """Calculate present value of a growing annuity.

    Formula: PV = PMT * [1 - ((1 + g) / (1 + r))^n] / (r - g)
    Book Reference: Chapter 2, Section 2.5
    """
    return _run(_growing_annuity_pv, payment=payment, discount_rate=discount_rate, growth_rate=growth_rate, periods=periods)


def terminal_value(final_year_cashflow: float, perpetual_growth_rate: float, discount_rate: float, method: str = "gordon_growth", exit_multiple: float | None = None) -> str:
    """Calculate terminal value using Gordon Growth or Exit Multiple method.

    Gordon Growth: TV = FCF * (1 + g) / (r - g)
    Exit Multiple: TV = FCF * Exit Multiple
    Book Reference: Chapter 2, Section 2.6
    """
    return _run(_terminal_value, final_year_cashflow=final_year_cashflow, perpetual_growth_rate=perpetual_growth_rate, discount_rate=discount_rate, method=method, exit_multiple=exit_multiple)


def build_up_discount_rate(risk_free_rate: float, equity_risk_premium: float, size_premium: float = 0.0, industry_risk_premium: float = 0.0, specific_risk_premium: float = 0.0) -> str:
    """Calculate discount rate using the build-up method.

    Formula: r = Rf + ERP + Size Premium + Industry RP + Specific RP
    Book Reference: Chapter 2, Section 2.7
    """
    return _run(_build_up_discount_rate, risk_free_rate=risk_free_rate, equity_risk_premium=equity_risk_premium, size_premium=size_premium, industry_risk_premium=industry_risk_premium, specific_risk_premium=specific_risk_premium)


def capm_discount_rate(risk_free_rate: float, beta: float, market_return: float) -> str:
    """Calculate discount rate using CAPM.

    Formula: r = Rf + beta * (Rm - Rf)
    Book Reference: Chapter 2, Section 2.8
    """
    return _run(_capm_discount_rate, risk_free_rate=risk_free_rate, beta=beta, market_return=market_return)


def wacc(equity_value: float, debt_value: float, cost_of_equity: float, cost_of_debt: float, tax_rate: float) -> str:
    """Calculate Weighted Average Cost of Capital.

    Formula: WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)
    Book Reference: Chapter 2, Section 2.9
    """
    return _run(_wacc, equity_value=equity_value, debt_value=debt_value, cost_of_equity=cost_of_equity, cost_of_debt=cost_of_debt, tax_rate=tax_rate)


def tax_amortization_benefit(discount_rate: float, useful_life: int, tax_rate: float, asset_value: float) -> str:
    """Calculate present value of tax amortization benefit.

    Formula: TAB = Asset Value * Tax Rate * [1 - (1 + r)^(-n)] / (r * n)
    Book Reference: Chapter 3, Section 3.4
    """
    return _run(_tax_amortization_benefit, discount_rate=discount_rate, useful_life=useful_life, tax_rate=tax_rate, asset_value=asset_value)


def control_premium(minority_price: float, control_price: float) -> str:
    """Calculate control premium percentage.

    Formula: (Control Price - Minority Price) / Minority Price
    Book Reference: Chapter 4, Section 4.3
    """
    return _run(_control_premium, minority_price=minority_price, control_price=control_price)


def dlom_finnerty(restricted_period: float, volatility: float, risk_free_rate: float) -> str:
    """Calculate DLOM using Finnerty average-strike put option model.

    Book Reference: Chapter 4, Section 4.4
    """
    return _run(_dlom_finnerty, restricted_period=restricted_period, volatility=volatility, risk_free_rate=risk_free_rate)


def currency_adjusted_discount_rate(base_rate: float, currency_risk_premium: float = 0.0, country_risk_premium: float = 0.0) -> str:
    """Calculate discount rate adjusted for currency and country risk.

    Formula: r_adjusted = base_rate + Currency RP + Country RP
    Book Reference: Chapter 4, Section 4.5
    """
    return _run(_currency_adjusted_discount_rate, base_rate=base_rate, currency_risk_premium=currency_risk_premium, country_risk_premium=country_risk_premium)


# =============================================================================
# Approach Tools
# =============================================================================

def reproduction_cost(development_costs: dict, obsolescence_factors: dict | None = None) -> str:
    """Calculate depreciated reproduction cost of an intangible asset.

    Formula: Reproduction Cost = Sum(costs) * (1 - total_obsolescence)
    Book Reference: Chapter 3, Cost Approach
    """
    return _run(_reproduction_cost, development_costs=development_costs, obsolescence_factors=obsolescence_factors)


def replacement_cost(current_cost: float, obsolescence_factors: dict | None = None) -> str:
    """Calculate depreciated replacement cost with equivalent utility.

    Formula: Replacement Cost = current_cost * (1 - total_obsolescence)
    Book Reference: Chapter 3, Cost Approach
    """
    return _run(_replacement_cost, current_cost=current_cost, obsolescence_factors=obsolescence_factors)


def market_approach_comparables(comparables: list, subject_revenue: float, adjustments: dict | None = None) -> str:
    """Valuation based on comparable market transactions using revenue multiples.

    Book Reference: Chapter 3, Market Approach
    """
    return _run(_market_approach_comparables, comparables=comparables, subject_revenue=subject_revenue, adjustments=adjustments)


def royalty_capitalization(revenue: float, royalty_rate: float, discount_rate: float) -> str:
    """Capitalize a perpetual royalty stream into present value.

    Formula: Value = (revenue * royalty_rate) / discount_rate
    Book Reference: Chapter 3, Market Approach
    """
    return _run(_royalty_capitalization, revenue=revenue, royalty_rate=royalty_rate, discount_rate=discount_rate)


# =============================================================================
# Income Method Tools
# =============================================================================

def relief_from_royalty(revenue_projections: list, royalty_rate: float, discount_rate: float, tax_rate: float, useful_life: int, tab_enabled: bool = True) -> str:
    """Value asset as PV of after-tax royalty payments avoided by ownership.

    Book Reference: Chapter 4, Income Methods - Relief from Royalty
    """
    return _run(_relief_from_royalty, revenue_projections=revenue_projections, royalty_rate=royalty_rate, discount_rate=discount_rate, tax_rate=tax_rate, useful_life=useful_life, tab_enabled=tab_enabled)


def mpeem(cash_flow_projections: list, contributory_asset_charges: list, discount_rate: float, tax_rate: float, tab_enabled: bool = True) -> str:
    """Multi-Period Excess Earnings Method. Values asset as PV of cash flows after CACs.

    Book Reference: Chapter 4, Income Methods - MPEEM
    """
    return _run(_mpeem, cash_flow_projections=cash_flow_projections, contributory_asset_charges=contributory_asset_charges, discount_rate=discount_rate, tax_rate=tax_rate, tab_enabled=tab_enabled)


def single_period_excess_earnings(normalized_earnings: float, contributory_asset_charges: list, capitalization_rate: float) -> str:
    """Value asset by capitalizing a single period of normalized excess earnings.

    Formula: Value = (Normalized Earnings - Total CAC) / cap_rate
    Book Reference: Chapter 4, Income Methods
    """
    return _run(_single_period_excess_earnings, normalized_earnings=normalized_earnings, contributory_asset_charges=contributory_asset_charges, capitalization_rate=capitalization_rate)


def incremental_cashflow(cash_flows_with: list, cash_flows_without: list, discount_rate: float) -> str:
    """Value asset as PV of additional cash flows with vs without the asset.

    Book Reference: Chapter 4, Income Methods - Incremental Cash Flow
    """
    return _run(_incremental_cashflow, cash_flows_with=cash_flows_with, cash_flows_without=cash_flows_without, discount_rate=discount_rate)


def contributory_asset_charges(assets: list) -> str:
    """Calculate total contributory asset charges (CACs).

    Formula: CAC_i = asset_value_i * return_rate_i
    Book Reference: Chapter 4, Income Methods - Excess Earnings
    """
    return _run(_contributory_asset_charges, assets=assets)


# =============================================================================
# Asset Type Tools
# =============================================================================

def patent_valuation(remaining_life: int, cash_flow_projections: list, probability_of_success: float, discount_rate: float, comparable_license_rates: list | None = None) -> str:
    """Calculate risk-adjusted patent value with probability weighting.

    Book Reference: Chapter 5, IP Valuation
    """
    return _run(_patent_valuation, remaining_life=remaining_life, cash_flow_projections=cash_flow_projections, probability_of_success=probability_of_success, discount_rate=discount_rate, comparable_license_rates=comparable_license_rates)


def trademark_valuation(revenue: float, profit_margin: float, brand_strength_index: float, discount_rate: float, useful_life: int, method: str = "relief_from_royalty") -> str:
    """Calculate brand/trademark value using RFR or excess earnings method.

    Book Reference: Chapter 5, Brand Valuation
    """
    return _run(_trademark_valuation, revenue=revenue, profit_margin=profit_margin, brand_strength_index=brand_strength_index, discount_rate=discount_rate, useful_life=useful_life, method=method)


def copyright_valuation(projected_revenue: float, useful_life: int, discount_rate: float, royalty_rate: float) -> str:
    """Calculate PV of expected copyright royalty/licensing income.

    Book Reference: Chapter 5, IP Valuation
    """
    return _run(_copyright_valuation, projected_revenue=projected_revenue, useful_life=useful_life, discount_rate=discount_rate, royalty_rate=royalty_rate)


def trade_secret_valuation(development_cost: float, economic_life: int, competitive_advantage_period: int, discount_rate: float, secrecy_probability: float) -> str:
    """Value trade secret incorporating secrecy risk over time.

    Book Reference: Chapter 5, IP Valuation
    """
    return _run(_trade_secret_valuation, development_cost=development_cost, economic_life=economic_life, competitive_advantage_period=competitive_advantage_period, discount_rate=discount_rate, secrecy_probability=secrecy_probability)


def developed_technology_valuation(rd_costs: float, life_cycle_stage: str, competitive_advantage: int, discount_rate: float, cash_flow_projections: list) -> str:
    """Value developed technology with life-cycle risk adjustment.

    Book Reference: Chapter 7, Technology Valuation
    """
    return _run(_developed_technology_valuation, rd_costs=rd_costs, life_cycle_stage=life_cycle_stage, competitive_advantage=competitive_advantage, discount_rate=discount_rate, cash_flow_projections=cash_flow_projections)


def software_valuation(development_cost: float, maintenance_cost: float, user_base: int, revenue_model: dict, useful_life: int, discount_rate: float) -> str:
    """Value software using cost and income approaches.

    Book Reference: Chapter 7, Technology Valuation
    """
    return _run(_software_valuation, development_cost=development_cost, maintenance_cost=maintenance_cost, user_base=user_base, revenue_model=revenue_model, useful_life=useful_life, discount_rate=discount_rate)


def data_asset_valuation(acquisition_cost: float, quality_score: float, revenue_contribution: float, useful_life: int, discount_rate: float) -> str:
    """Value data asset with quality-adjusted revenue contribution.

    Book Reference: Chapter 7, Technology Valuation
    """
    return _run(_data_asset_valuation, acquisition_cost=acquisition_cost, quality_score=quality_score, revenue_contribution=revenue_contribution, useful_life=useful_life, discount_rate=discount_rate)


def platform_valuation(network_size: int, network_effects_coefficient: float, revenue_per_user: float, growth_rate: float, discount_rate: float) -> str:
    """Value platform incorporating network effects in revenue projection.

    Book Reference: Chapter 7, Technology Valuation
    """
    return _run(_platform_valuation, network_size=network_size, network_effects_coefficient=network_effects_coefficient, revenue_per_user=revenue_per_user, growth_rate=growth_rate, discount_rate=discount_rate)


def customer_relationship_valuation(customer_count: int, avg_revenue_per_customer: float, retention_rate: float, profit_margin: float, discount_rate: float, projection_period: int) -> str:
    """Value customer relationships with multi-period cash flow and attrition.

    Book Reference: Chapter 8, Customer Valuation
    """
    return _run(_customer_relationship_valuation, customer_count=customer_count, avg_revenue_per_customer=avg_revenue_per_customer, retention_rate=retention_rate, profit_margin=profit_margin, discount_rate=discount_rate, projection_period=projection_period)


def distribution_network_valuation(channel_count: int, revenue_per_channel: float, channel_margin: float, useful_life: int, discount_rate: float) -> str:
    """Value distribution network based on channel profitability.

    Book Reference: Chapter 8, Customer Valuation
    """
    return _run(_distribution_network_valuation, channel_count=channel_count, revenue_per_channel=revenue_per_channel, channel_margin=channel_margin, useful_life=useful_life, discount_rate=discount_rate)


def non_compete_valuation(protected_revenue: float, profit_margin: float, term: int, enforcement_probability: float, discount_rate: float) -> str:
    """Value non-compete agreement based on protected profits.

    Book Reference: Chapter 8, Customer Valuation
    """
    return _run(_non_compete_valuation, protected_revenue=protected_revenue, profit_margin=profit_margin, term=term, enforcement_probability=enforcement_probability, discount_rate=discount_rate)


def assembled_workforce_valuation(employee_count: int, avg_replacement_cost: float, training_cost: float, productivity_factor: float, attrition_rate: float) -> str:
    """Value assembled workforce using replacement cost approach.

    Book Reference: Chapter 9, Human Capital
    """
    return _run(_assembled_workforce_valuation, employee_count=employee_count, avg_replacement_cost=avg_replacement_cost, training_cost=training_cost, productivity_factor=productivity_factor, attrition_rate=attrition_rate)


def key_person_value(revenue_contribution: float, replacement_cost: float, departure_probability: float, discount_rate: float) -> str:
    """Value key person based on revenue contribution and replacement risk.

    Book Reference: Chapter 9, Human Capital
    """
    return _run(_key_person_value, revenue_contribution=revenue_contribution, replacement_cost=replacement_cost, departure_probability=departure_probability, discount_rate=discount_rate)


# =============================================================================
# Advanced Tools
# =============================================================================

def goodwill(purchase_price: float, fair_value_net_identifiable_assets: float) -> str:
    """Calculate goodwill as residual of purchase price over net identifiable assets.

    Formula: Goodwill = Purchase Price - FV of Net Identifiable Assets
    Book Reference: Chapter 10.1, ASC 805-30-30-1
    """
    return _run(_goodwill, purchase_price=purchase_price, fair_value_net_identifiable_assets=fair_value_net_identifiable_assets)


def purchase_price_allocation(purchase_price: float, tangible_assets_fv: float, identified_intangibles: list, liabilities_fv: float = 0) -> str:
    """Perform full purchase price allocation waterfall.

    Book Reference: Chapter 10.2, Appendix A.8, ASC 805 / IFRS 3
    """
    return _run(_purchase_price_allocation, purchase_price=purchase_price, tangible_assets_fv=tangible_assets_fv, identified_intangibles=identified_intangibles, liabilities_fv=liabilities_fv)


def goodwill_impairment_test(carrying_value: float, fair_value: float, reporting_unit: str = "", standard: str = "ASC350") -> str:
    """Test goodwill for impairment per ASC 350 or IAS 36.

    Book Reference: Chapter 10.4, ASC 350-20-35 / IAS 36
    """
    return _run(_goodwill_impairment_test, carrying_value=carrying_value, fair_value=fair_value, reporting_unit=reporting_unit, standard=standard)


def intangible_impairment_test(carrying_value: float, fair_value: float | None = None, recoverable_amount: float | None = None, standard: str = "ASC350") -> str:
    """Test intangible asset for impairment per ASC 350 or IAS 36.

    Book Reference: Chapter 10.4, ASC 350-30-35 / IAS 36
    """
    return _run(_intangible_impairment_test, carrying_value=carrying_value, fair_value=fair_value, recoverable_amount=recoverable_amount, standard=standard)


def royalty_rate_benchmark(ip_type: str, industry: str, comparable_database: list | None = None) -> str:
    """Get benchmark royalty rate range by IP type and industry.

    Book Reference: Chapter 6.2, Appendix A.10
    """
    return _run(_royalty_rate_benchmark, ip_type=ip_type, industry=industry, comparable_database=comparable_database)


def adjust_royalty_rate(base_rate: float, adjustment_factors: dict) -> str:
    """Adjust base royalty rate for specific deal factors.

    Formula: Adjusted Rate = Base Rate * product(all factors)
    Book Reference: Chapter 6.3, Appendix A.10
    """
    return _run(_adjust_royalty_rate, base_rate=base_rate, adjustment_factors=adjustment_factors)


def twenty_five_percent_rule(licensee_expected_profit: float, profit_attribution_to_ip: float = 1.0) -> str:
    """Apply the 25% rule of thumb for royalty rate estimation.

    Formula: Royalty = Licensee Profit * IP Attribution * 25%
    Book Reference: Chapter 6.1
    """
    return _run(_twenty_five_percent_rule, licensee_expected_profit=licensee_expected_profit, profit_attribution_to_ip=profit_attribution_to_ip)


def cup_transfer_price(controlled_price: float, uncontrolled_prices: list) -> str:
    """Calculate arm's length range using Comparable Uncontrolled Price method.

    Book Reference: Chapter 16.1, OECD TP Guidelines
    """
    return _run(_cup_transfer_price, controlled_price=controlled_price, uncontrolled_prices=uncontrolled_prices)


def patent_infringement_damages(lost_profits_or_royalty: float, infringement_period: int, discount_rate: float, prejudgment_interest_rate: float) -> str:
    """Calculate patent infringement damages with pre-judgment interest.

    Book Reference: Chapter 15.2
    """
    return _run(_patent_infringement_damages, lost_profits_or_royalty=lost_profits_or_royalty, infringement_period=infringement_period, discount_rate=discount_rate, prejudgment_interest_rate=prejudgment_interest_rate)


def monte_carlo_valuation(input_distributions: list, iterations: int = 10000, seed: int | None = None) -> str:
    """Run Monte Carlo simulation for valuation uncertainty analysis.

    Note: This tool uses a simplified interface. For full flexibility, use the Python API.
    Supported distributions: normal (mean, std), uniform (low, high), triangular (low, high, mode).

    Book Reference: Chapter 6.2, Appendix B
    """
    def _simple_valuation(**params: float) -> float:
        """Simple sum-based valuation for MC demo. Use Python API for real valuations."""
        return sum(v for v in params.values() if isinstance(v, (int, float)))

    return _run(_monte_carlo_valuation, valuation_fn=_simple_valuation, input_distributions=input_distributions, iterations=iterations, seed=seed)


def monte_carlo_sensitivity(base_params: dict, distributions: dict, iterations: int = 10000, seed: int | None = None) -> str:
    """Run Monte Carlo sensitivity analysis on valuation parameters.

    Note: This tool uses a simplified interface. For full flexibility, use the Python API.

    Book Reference: Chapter 2.4, Appendix A.11, A.15
    """
    def _simple_valuation(params: dict) -> Any:
        class _Result:
            value = sum(v for v in params.values() if isinstance(v, (int, float)))
        return _Result()

    return _run(_monte_carlo_sensitivity, valuation_fn=_simple_valuation, base_params=base_params, distributions=distributions, iterations=iterations, seed=seed)


def decision_tree_valuation(tree: dict) -> str:
    """Evaluate a decision tree to compute expected values at each node.

    Tree format: {"nodes": [...], "edges": [...]}
    Node types: decision, chance, terminal.

    Book Reference: Chapter 6.3
    """
    return _run(_decision_tree_valuation, tree=tree)


def sensitivity_analysis(function_name: str, parameter_name: str, parameter_range: list, fixed_parameters: dict) -> str:
    """Perform one-at-a-time sensitivity analysis on a valuation function.

    Supported functions: present_value, future_value, annuity_pv, perpetuity_pv,
    growing_annuity_pv, terminal_value, build_up_discount_rate, capm_discount_rate, wacc.

    Book Reference: Appendix A, Section A.3
    """
    return _run(_sensitivity_analysis, function_name=function_name, parameter_name=parameter_name, parameter_range=parameter_range, fixed_parameters=fixed_parameters)


def estimate_useful_life(asset_type: str, legal_life: float | None = None, economic_factors: dict | None = None, obsolescence_rate: float = 0.05) -> str:
    """Estimate the useful life of an intangible asset.

    Formula: Economic Life = -ln(0.10) / obsolescence_rate
    Book Reference: Appendix A, Section A.2
    """
    return _run(_estimate_useful_life, asset_type=asset_type, legal_life=legal_life, economic_factors=economic_factors, obsolescence_rate=obsolescence_rate)
