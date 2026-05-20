"""Tests for all newly added advanced functions.

Covers: patent_portfolio_valuation, option_pricing_patent, interbrand_brand_valuation,
brand_strength_index, technology_obsolescence_curve, api_valuation, algorithm_valuation,
customer_lifetime_value, backlog_valuation, churn_impact_analysis,
value_in_use, fair_value_less_costs_to_sell, cash_generating_unit_impairment,
bargain_purchase_analysis, contingent_consideration_valuation, deferred_tax_liability_ppa,
profit_split_method, analytical_method_valuation,
wacc_with_preferred, implied_erp, beta_unlevered/relevered, fama_french,
monte_carlo_with_correlation, sensitivity_tornado, scenario_analysis,
straight_line_amortization, SYD, DDB, valuation_multiple.
"""

import math

import pytest

from intangible_valuation.advanced.impairment_testing import (
    cash_generating_unit_impairment,
    fair_value_less_costs_to_sell,
    value_in_use,
)
from intangible_valuation.advanced.purchase_price_alloc import (
    bargain_purchase_analysis,
    contingent_consideration_valuation,
    deferred_tax_liability_ppa,
)
from intangible_valuation.advanced.royalty_benchmark import (
    analytical_method_valuation,
    profit_split_method,
)
from intangible_valuation.asset_types.brand_valuation import (
    brand_strength_index,
    interbrand_brand_valuation,
)
from intangible_valuation.asset_types.customer_valuation import (
    backlog_valuation,
    churn_impact_analysis,
    customer_lifetime_value,
)
from intangible_valuation.asset_types.ip_valuation import (
    option_pricing_patent,
    patent_portfolio_valuation,
)
from intangible_valuation.asset_types.technology_valuation import (
    algorithm_valuation,
    api_valuation,
    technology_obsolescence_curve,
)
from intangible_valuation.core.discount_rates import (
    beta_relevered,
    beta_unlevered,
    build_up_with_country_risk,
    cost_of_equity_fama_french,
    implied_erp,
    wacc_with_preferred,
)
from intangible_valuation.core.statistics import (
    monte_carlo_with_correlation,
    scenario_analysis,
    sensitivity_tornado,
)
from intangible_valuation.utils.formulas import (
    double_declining_balance_amortization,
    straight_line_amortization,
    sum_of_years_digits_amortization,
    valuation_multiple,
)


class TestPatentPortfolioValuation:
    """Tests for patent_portfolio_valuation."""

    def test_basic_portfolio(self):
        patents = [
            {"value": 1_000_000, "category": "pharma"},
            {"value": 500_000, "category": "tech"},
            {"value": 750_000, "category": "pharma"},
        ]
        result = patent_portfolio_valuation(patents)
        assert result["value"] > 0
        assert result["value"] < 2_250_000

    def test_single_category(self):
        patents = [
            {"value": 1_000_000, "category": "pharma"},
            {"value": 2_000_000, "category": "pharma"},
        ]
        result = patent_portfolio_valuation(patents)
        total_raw = 3_000_000
        assert result["value"] < total_raw

    def test_empty_patents_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            patent_portfolio_valuation([])

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            patent_portfolio_valuation([{"value": -100}])

    def test_no_categories(self):
        patents = [{"value": 1_000_000}, {"value": 500_000}]
        result = patent_portfolio_valuation(patents)
        assert result["value"] > 0


class TestOptionPricingPatent:
    """Tests for option_pricing_patent (Black-Scholes)."""

    def test_basic_option(self):
        result = option_pricing_patent(
            exercise_cost=5_000_000,
            expected_value=10_000_000,
            volatility=0.40,
            time_to_expiry=10,
            risk_free_rate=0.03,
        )
        assert result["value"] > 5_000_000
        assert result["method"] == "Real Options (Black-Scholes)"

    def test_deep_in_the_money(self):
        result = option_pricing_patent(
            exercise_cost=1_000_000,
            expected_value=10_000_000,
            volatility=0.20,
            time_to_expiry=5,
            risk_free_rate=0.03,
        )
        assert result["value"] > 8_000_000

    def test_out_of_the_money(self):
        result = option_pricing_patent(
            exercise_cost=10_000_000,
            expected_value=5_000_000,
            volatility=0.30,
            time_to_expiry=3,
            risk_free_rate=0.03,
        )
        assert result["value"] >= 0

    def test_high_volatility(self):
        result = option_pricing_patent(
            exercise_cost=5_000_000,
            expected_value=5_000_000,
            volatility=1.0,
            time_to_expiry=10,
            risk_free_rate=0.03,
        )
        assert result["value"] > 0


class TestInterbrandBrandValuation:
    """Tests for interbrand_brand_valuation."""

    def test_basic_interbrand(self):
        result = interbrand_brand_valuation(
            brand_earnings=50_000_000,
            role_of_brand_index=0.60,
            brand_strength_score=75,
            discount_rate=0.08,
        )
        assert result["value"] > 0
        assert result["method"] == "Interbrand Brand Valuation"

    def test_strong_brand(self):
        result = interbrand_brand_valuation(
            brand_earnings=100_000_000,
            role_of_brand_index=0.80,
            brand_strength_score=90,
            discount_rate=0.06,
        )
        assert result["value"] > 100_000_000

    def test_weak_brand(self):
        result = interbrand_brand_valuation(
            brand_earnings=10_000_000,
            role_of_brand_index=0.20,
            brand_strength_score=20,
            discount_rate=0.15,
        )
        assert result["value"] > 0

    def test_zero_earnings_raises(self):
        with pytest.raises(ValueError):
            interbrand_brand_valuation(
                brand_earnings=0,
                role_of_brand_index=0.50,
                brand_strength_score=50,
                discount_rate=0.10,
            )


class TestBrandStrengthIndex:
    """Tests for brand_strength_index."""

    def test_basic_bsi(self):
        result = brand_strength_index(0.8, 0.6, 0.7, 0.9, 0.5)
        assert math.isclose(result["value"], 72.0, abs_tol=0.1)

    def test_perfect_scores(self):
        result = brand_strength_index(1.0, 1.0, 1.0, 1.0, 1.0)
        assert math.isclose(result["value"], 100.0, abs_tol=0.1)

    def test_zero_scores(self):
        result = brand_strength_index(0.0, 0.0, 0.0, 0.0, 0.0)
        assert math.isclose(result["value"], 0.0, abs_tol=0.1)

    def test_rating_classification(self):
        assert brand_strength_index(0.9, 0.9, 0.9, 0.9, 0.9)["assumptions"]["rating"] == "Excellent"
        assert brand_strength_index(0.7, 0.7, 0.7, 0.7, 0.7)["assumptions"]["rating"] == "Strong"
        assert brand_strength_index(0.5, 0.5, 0.5, 0.5, 0.5)["assumptions"]["rating"] == "Moderate"

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError):
            brand_strength_index(1.5, 0.5, 0.5, 0.5, 0.5)


class TestTechnologyObsolescenceCurve:
    """Tests for technology_obsolescence_curve."""

    def test_basic_obsolescence(self):
        result = technology_obsolescence_curve(1_000_000, 0.20, 5)
        assert math.isclose(result["value"], 327_680, abs_tol=1)

    def test_no_obsolescence(self):
        result = technology_obsolescence_curve(1_000_000, 0.01, 5)
        assert result["value"] > 0
        assert result["value"] < 1_000_000

    def test_high_obsolescence(self):
        result = technology_obsolescence_curve(1_000_000, 0.50, 3)
        assert math.isclose(result["value"], 125_000, abs_tol=1)

    def test_value_decay_monotonic(self):
        result = technology_obsolescence_curve(1_000_000, 0.15, 10)
        values = result["assumptions"]["value_at_each_period"]
        for i in range(1, len(values)):
            assert values[i] < values[i - 1]

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError):
            technology_obsolescence_curve(1_000_000, 0.0, 5)


class TestAPIValuation:
    """Tests for api_valuation."""

    def test_basic_api(self):
        result = api_valuation(
            api_calls_per_month=1_000_000,
            revenue_per_call=0.001,
            growth_rate=0.15,
            useful_life=5,
            discount_rate=0.10,
        )
        assert result["value"] > 0

    def test_no_growth(self):
        result = api_valuation(
            api_calls_per_month=100_000,
            revenue_per_call=0.01,
            growth_rate=0.0,
            useful_life=3,
            discount_rate=0.10,
        )
        assert result["value"] > 0

    def test_zero_calls_raises(self):
        with pytest.raises(ValueError):
            api_valuation(
                api_calls_per_month=0,
                revenue_per_call=0.001,
                growth_rate=0.10,
                useful_life=5,
                discount_rate=0.10,
            )


class TestAlgorithmValuation:
    """Tests for algorithm_valuation."""

    def test_basic_algorithm(self):
        result = algorithm_valuation(
            computational_savings=500_000,
            deployment_scale=3.0,
            competitive_advantage_years=5,
            discount_rate=0.12,
        )
        assert result["value"] > 0

    def test_large_scale(self):
        result = algorithm_valuation(
            computational_savings=1_000_000,
            deployment_scale=10.0,
            competitive_advantage_years=7,
            discount_rate=0.10,
        )
        assert result["value"] > 10_000_000

    def test_zero_savings_raises(self):
        with pytest.raises(ValueError):
            algorithm_valuation(
                computational_savings=0,
                deployment_scale=1.0,
                competitive_advantage_years=5,
                discount_rate=0.10,
            )


class TestCustomerLifetimeValue:
    """Tests for customer_lifetime_value."""

    def test_basic_clv(self):
        result = customer_lifetime_value(100, 0.80, 0.10, 0.30)
        assert math.isclose(result["value"], 80.0, abs_tol=0.1)

    def test_high_retention(self):
        result = customer_lifetime_value(100, 0.95, 0.10, 0.30)
        assert result["value"] > 100

    def test_low_margin(self):
        result = customer_lifetime_value(100, 0.80, 0.10, 0.05)
        assert result["value"] > 0

    def test_retention_near_one_raises(self):
        with pytest.raises(ValueError):
            customer_lifetime_value(100, 1.0, 0.10, 0.30)


class TestBacklogValuation:
    """Tests for backlog_valuation."""

    def test_basic_backlog(self):
        backlog = [
            {"value": 500_000, "period": 1},
            {"value": 300_000, "period": 2},
        ]
        result = backlog_valuation(backlog, 0.90, 0.10)
        assert result["value"] > 0

    def test_default_period(self):
        backlog = [{"value": 1_000_000}]
        result = backlog_valuation(backlog, 1.0, 0.0)
        assert math.isclose(result["value"], 1_000_000, abs_tol=1)

    def test_empty_backlog_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            backlog_valuation([], 0.90, 0.10)


class TestChurnImpactAnalysis:
    """Tests for churn_impact_analysis."""

    def test_basic_churn(self):
        result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.20,
            churn_rate_after=0.15,
            revenue_per_customer=5000,
            discount_rate=0.10,
        )
        assert result["value"] > 0

    def test_worse_churn(self):
        result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.10,
            churn_rate_after=0.20,
            revenue_per_customer=5000,
            discount_rate=0.10,
        )
        assert result["value"] < 0

    def test_same_churn(self):
        result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.15,
            churn_rate_after=0.15,
            revenue_per_customer=5000,
            discount_rate=0.10,
        )
        assert math.isclose(result["value"], 0, abs_tol=1)


class TestValueInUse:
    """Tests for value_in_use."""

    def test_basic_viu(self):
        result = value_in_use(
            cash_flow_projections=[5_000_000, 5_500_000, 6_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )
        assert result.value > 0
        assert result.method == "IAS 36 Value in Use"

    def test_rate_equals_growth_raises(self):
        with pytest.raises(ValueError, match="must exceed"):
            value_in_use(
                cash_flow_projections=[1_000_000],
                terminal_growth_rate=0.10,
                discount_rate=0.10,
            )

    def test_negative_cf_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            value_in_use(
                cash_flow_projections=[-100],
                terminal_growth_rate=0.02,
                discount_rate=0.10,
            )


class TestFairValueLessCostsToSell:
    """Tests for fair_value_less_costs_to_sell."""

    def test_basic_fvlcts(self):
        result = fair_value_less_costs_to_sell(10_000_000, 500_000)
        assert math.isclose(result.value, 9_500_000, abs_tol=1)

    def test_zero_costs(self):
        result = fair_value_less_costs_to_sell(5_000_000, 0)
        assert math.isclose(result.value, 5_000_000, abs_tol=1)

    def test_costs_exceed_value(self):
        """When costs exceed value, result raises validation error."""
        with pytest.raises(ValueError, match="non-negative"):
            fair_value_less_costs_to_sell(1_000_000, 2_000_000)


class TestCGUImpairment:
    """Tests for cash_generating_unit_impairment."""

    def test_basic_cgu(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=100_000_000,
            cgu_recoverable_amount=80_000_000,
            goodwill_allocated=15_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 40_000_000},
                {"name": "Equipment", "carrying_value": 45_000_000},
            ],
        )
        assert math.isclose(result.value, 20_000_000, abs_tol=1)

    def test_no_impairment(self):
        result = cash_generating_unit_impairment(
            cgu_carrying_value=50_000_000,
            cgu_recoverable_amount=60_000_000,
            goodwill_allocated=10_000_000,
            other_assets=[{"name": "Patents", "carrying_value": 40_000_000}],
        )
        assert math.isclose(result.value, 0, abs_tol=1)

    def test_empty_assets_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            cash_generating_unit_impairment(
                cgu_carrying_value=100_000_000,
                cgu_recoverable_amount=80_000_000,
                goodwill_allocated=10_000_000,
                other_assets=[],
            )


class TestBargainPurchaseAnalysis:
    """Tests for bargain_purchase_analysis."""

    def test_basic_bargain(self):
        result = bargain_purchase_analysis(
            purchase_price=40_000_000,
            fair_value_net_assets=50_000_000,
        )
        assert math.isclose(result["value"], 10_000_000, abs_tol=1)

    def test_not_bargain_raises(self):
        with pytest.raises(ValueError, match="Not a bargain purchase"):
            bargain_purchase_analysis(
                purchase_price=60_000_000,
                fair_value_net_assets=50_000_000,
            )


class TestContingentConsideration:
    """Tests for contingent_consideration_valuation."""

    def test_basic_contingent(self):
        scenarios = [
            {"probability": 0.3, "payment": 5_000_000, "period": 1},
            {"probability": 0.5, "payment": 10_000_000, "period": 2},
            {"probability": 0.2, "payment": 15_000_000, "period": 3},
        ]
        result = contingent_consideration_valuation(scenarios, 0.10)
        assert result["value"] > 0

    def test_probabilities_not_summing_raises(self):
        with pytest.raises(ValueError, match="must sum to 1"):
            contingent_consideration_valuation(
                [{"probability": 0.3, "payment": 1_000_000}],
                0.10,
            )

    def test_empty_scenarios_raises(self):
        with pytest.raises(ValueError):
            contingent_consideration_valuation([], 0.10)


class TestDeferredTaxLiabilityPPA:
    """Tests for deferred_tax_liability_ppa."""

    def test_basic_dtl(self):
        intangibles = [
            {"name": "Customer Relationships", "fair_value": 20_000_000},
            {"name": "Technology", "fair_value": 25_000_000},
        ]
        result = deferred_tax_liability_ppa(intangibles, 0, 0.25)
        assert math.isclose(result["value"], 11_250_000, abs_tol=1)

    def test_with_tax_basis(self):
        intangibles = [{"name": "Patent", "fair_value": 10_000_000}]
        result = deferred_tax_liability_ppa(intangibles, 2_000_000, 0.25)
        assert math.isclose(result["value"], 2_000_000, abs_tol=1)

    def test_empty_intangibles_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            deferred_tax_liability_ppa([], 0, 0.25)


class TestProfitSplitMethod:
    """Tests for profit_split_method."""

    def test_basic_profit_split(self):
        result = profit_split_method(0.40, 0.60, 10_000_000)
        assert math.isclose(result["value"], 4_000_000, abs_tol=1)

    def test_equal_split(self):
        result = profit_split_method(0.50, 0.50, 1_000_000)
        assert math.isclose(result["value"], 500_000, abs_tol=1)

    def test_unequal_total(self):
        result = profit_split_method(0.30, 0.70, 5_000_000)
        assert math.isclose(result["value"], 1_500_000, abs_tol=1)


class TestAnalyticalMethodValuation:
    """Tests for analytical_method_valuation."""

    def test_basic_analytical(self):
        result = analytical_method_valuation(
            advantage_margin=0.05,
            volume=10_000_000,
            discount_rate=0.12,
            economic_life=7,
        )
        assert result["value"] > 0
        assert result["assumptions"]["implied_royalty_rate"] > 0

    def test_high_advantage(self):
        result = analytical_method_valuation(
            advantage_margin=0.10,
            volume=50_000_000,
            discount_rate=0.10,
            economic_life=10,
        )
        assert result["value"] > 10_000_000


class TestWACCWithPreferred:
    """Tests for wacc_with_preferred."""

    def test_basic_wacc_preferred(self):
        result = wacc_with_preferred(
            equity_value=600, debt_value=300, preferred_value=100,
            cost_of_equity=0.12, cost_of_debt=0.06, cost_of_preferred=0.08,
            tax_rate=0.25,
        )
        assert 0 < result.value < 0.12

    def test_no_preferred_equals_standard_wacc(self):
        from intangible_valuation.core.discount_rates import wacc
        result_pref = wacc_with_preferred(
            equity_value=600, debt_value=400, preferred_value=0,
            cost_of_equity=0.12, cost_of_debt=0.06, cost_of_preferred=0.08,
            tax_rate=0.25,
        )
        result_std = wacc(
            equity_value=600, debt_value=400,
            cost_of_equity=0.12, cost_of_debt=0.06,
            tax_rate=0.25,
        )
        assert math.isclose(result_pref.value, result_std.value, abs_tol=1e-6)


class TestImpliedERP:
    """Tests for implied_erp."""

    def test_basic_implied_erp(self):
        result = implied_erp(market_pe_ratio=20, perpetual_growth_rate=0.03)
        assert math.isclose(result.value, 0.02, abs_tol=1e-4)

    def test_low_pe(self):
        result = implied_erp(market_pe_ratio=10, perpetual_growth_rate=0.02)
        assert result.value > 0.05

    def test_negative_pe_raises(self):
        with pytest.raises(ValueError, match="positive"):
            implied_erp(market_pe_ratio=-5, perpetual_growth_rate=0.03)


class TestBetaUnleveredRelevered:
    """Tests for beta_unlevered and beta_relevered."""

    def test_unlevered_basic(self):
        result = beta_unlevered(beta_levered=1.2, debt_to_equity=0.5, tax_rate=0.25)
        assert result.value < 1.2

    def test_relevered_basic(self):
        result = beta_relevered(beta_unlevered=0.87, target_debt_to_equity=0.6, tax_rate=0.25)
        assert result.value > 0.87

    def test_roundtrip(self):
        unlevered = beta_unlevered(beta_levered=1.2, debt_to_equity=0.5, tax_rate=0.25).value
        relevered = beta_relevered(beta_unlevered=unlevered, target_debt_to_equity=0.5, tax_rate=0.25).value
        assert math.isclose(relevered, 1.2, abs_tol=1e-4)


class TestFamaFrench:
    """Tests for cost_of_equity_fama_french."""

    def test_basic_fama_french(self):
        result = cost_of_equity_fama_french(
            risk_free_rate=0.04, market_beta=1.1, smb_beta=0.5, hml_beta=0.3,
            market_premium=0.06, smb_premium=0.03, hml_premium=0.04,
        )
        assert result.value > 0.04

    def test_capm_equivalent(self):
        result = cost_of_equity_fama_french(
            risk_free_rate=0.04, market_beta=1.0, smb_beta=0.0, hml_beta=0.0,
            market_premium=0.06, smb_premium=0.03, hml_premium=0.04,
        )
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)


class TestBuildUpWithCountryRisk:
    """Tests for build_up_with_country_risk."""

    def test_basic_country_risk(self):
        result = build_up_with_country_risk(
            risk_free_rate=0.04, erp=0.06, size_premium=0.02,
            country_risk_premium=0.03,
        )
        assert math.isclose(result.value, 0.15, abs_tol=1e-6)

    def test_no_country_risk(self):
        result = build_up_with_country_risk(
            risk_free_rate=0.04, erp=0.06,
        )
        assert math.isclose(result.value, 0.10, abs_tol=1e-6)


class TestMonteCarloWithCorrelation:
    """Tests for monte_carlo_with_correlation."""

    def test_basic_correlated_mc(self):
        def simple_fn(revenue, cost):
            return revenue - cost

        result = monte_carlo_with_correlation(
            valuation_fn=simple_fn,
            distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 10_000_000, "std": 1_000_000}},
                {"name": "cost", "distribution": "normal", "params": {"mean": 6_000_000, "std": 500_000}},
            ],
            correlation_matrix=[[1.0, 0.5], [0.5, 1.0]],
            iterations=1000,
            seed=42,
        )

        assert result["mean"] > 0
        assert result["correlation_used"] is True

    def test_identity_correlation(self):
        def simple_fn(x, y):
            return x + y

        result = monte_carlo_with_correlation(
            valuation_fn=simple_fn,
            distributions=[
                {"name": "x", "distribution": "uniform", "params": {"low": 0, "high": 10}},
                {"name": "y", "distribution": "uniform", "params": {"low": 0, "high": 10}},
            ],
            correlation_matrix=[[1.0, 0.0], [0.0, 1.0]],
            iterations=1000,
            seed=42,
        )

        assert result["mean"] > 0

    def test_invalid_correlation_raises(self):
        """Non-positive-definite correlation matrix should raise."""
        with pytest.raises(ValueError):
            monte_carlo_with_correlation(
                valuation_fn=lambda x: x,
                distributions=[
                    {"name": "x", "distribution": "uniform", "params": {"low": 0, "high": 1}},
                    {"name": "y", "distribution": "uniform", "params": {"low": 0, "high": 1}},
                ],
                correlation_matrix=[[1.0, 2.0], [2.0, 1.0]],
                iterations=100,
            )


class TestSensitivityTornado:
    """Tests for sensitivity_tornado."""

    def test_basic_tornado(self):
        result = sensitivity_tornado(
            function_name="present_value",
            base_params={"future_value": 1_000_000, "discount_rate": 0.10, "periods": 10},
            parameter_ranges={
                "discount_rate": [0.08, 0.10, 0.12],
                "periods": [8, 10, 12],
            },
        )
        assert len(result["tornado"]) == 2
        assert result["tornado"][0]["impact"] >= result["tornado"][1]["impact"]

    def test_single_parameter_tornado(self):
        result = sensitivity_tornado(
            function_name="perpetuity_pv",
            base_params={"payment": 100_000, "discount_rate": 0.10},
            parameter_ranges={"discount_rate": [0.08, 0.10, 0.12]},
        )
        assert len(result["tornado"]) == 1


class TestScenarioAnalysis:
    """Tests for scenario_analysis."""

    def test_basic_scenario(self):
        result = scenario_analysis([
            {
                "name": "Base", "probability": 0.6,
                "params": {"payment": 1_000_000, "discount_rate": 0.10},
                "function_name": "perpetuity_pv",
            },
            {
                "name": "Upside", "probability": 0.2,
                "params": {"payment": 1_500_000, "discount_rate": 0.09},
                "function_name": "perpetuity_pv",
            },
            {
                "name": "Downside", "probability": 0.2,
                "params": {"payment": 700_000, "discount_rate": 0.12},
                "function_name": "perpetuity_pv",
            },
        ])
        assert result["expected_value"] > 0
        assert len(result["scenarios"]) == 3

    def test_single_scenario(self):
        result = scenario_analysis([
            {
                "name": "Only", "probability": 1.0,
                "params": {"payment": 100_000, "discount_rate": 0.10},
                "function_name": "perpetuity_pv",
            },
        ])
        assert math.isclose(result["expected_value"], 1_000_000, rel_tol=1e-4)


class TestAmortizationMethods:
    """Tests for straight_line, SYD, and DDB amortization."""

    def test_straight_line_basic(self):
        result = straight_line_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["schedule"][0]["amortization"], 200_000, abs_tol=1)
        assert math.isclose(result["total_amortization"], 1_000_000, abs_tol=1)

    def test_syd_basic(self):
        result = sum_of_years_digits_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["schedule"][0]["amortization"], 333_333.33, abs_tol=1)
        assert result["schedule"][0]["amortization"] > result["schedule"][-1]["amortization"]

    def test_ddb_basic(self):
        result = double_declining_balance_amortization(asset_value=1_000_000, useful_life=5)
        assert math.isclose(result["schedule"][0]["amortization"], 400_000, abs_tol=1)
        assert math.isclose(result["schedule"][-1]["book_value"], 0, abs_tol=1)

    def test_all_methods_total_equal_asset(self):
        for fn in [straight_line_amortization, sum_of_years_digits_amortization, double_declining_balance_amortization]:
            result = fn(asset_value=500_000, useful_life=10)
            assert math.isclose(result["total_amortization"], 500_000, abs_tol=1)


class TestValuationMultiple:
    """Tests for valuation_multiple."""

    def test_ev_revenue(self):
        result = valuation_multiple(value=50_000_000, metric=10_000_000, multiple_type="EV/Revenue")
        assert math.isclose(result["multiple"], 5.0, abs_tol=0.01)

    def test_pe_ratio(self):
        result = valuation_multiple(value=100, metric=5, multiple_type="P/E")
        assert math.isclose(result["multiple"], 20.0, abs_tol=0.01)

    def test_zero_metric_raises(self):
        with pytest.raises(ValueError, match="cannot be zero"):
            valuation_multiple(value=100, metric=0, multiple_type="P/E")

    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            valuation_multiple(value=-100, metric=10, multiple_type="P/E")
