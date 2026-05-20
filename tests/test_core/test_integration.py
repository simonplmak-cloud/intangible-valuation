"""Integration tests that chain multiple valuation functions together.

Tests full workflows: DCF chains, PPA chains, brand valuation chains,
CLV comparisons, and Monte Carlo → sensitivity → tornado pipelines.
"""

import math

from intangible_valuation.advanced.impairment_testing import (
    cash_generating_unit_impairment,
    fair_value_less_costs_to_sell,
    value_in_use,
)
from intangible_valuation.advanced.purchase_price_alloc import (
    deferred_tax_liability_ppa,
    purchase_price_allocation,
)
from intangible_valuation.advanced.royalty_benchmark import (
    analytical_method_valuation,
    profit_split_method,
)
from intangible_valuation.approaches.cost_approach import replacement_cost
from intangible_valuation.approaches.market_approach import market_approach_comparables
from intangible_valuation.asset_types.brand_valuation import (
    brand_strength_index,
    interbrand_brand_valuation,
    trademark_valuation,
)
from intangible_valuation.asset_types.customer_valuation import (
    churn_impact_analysis,
    customer_lifetime_value,
    customer_relationship_valuation,
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
    build_up_discount_rate,
    wacc,
)
from intangible_valuation.core.statistics import (
    monte_carlo_valuation,
    scenario_analysis,
    sensitivity_tornado,
)
from intangible_valuation.core.time_value import (
    annuity_pv,
    growing_annuity_pv,
    present_value,
    present_value_of_series,
    terminal_value,
)
from intangible_valuation.income_methods.excess_earnings import mpeem, single_period_excess_earnings
from intangible_valuation.income_methods.incremental_cashflow import incremental_cashflow
from intangible_valuation.income_methods.relief_from_royalty import relief_from_royalty
from intangible_valuation.utils.formulas import (
    contributory_asset_charges,
    sensitivity_analysis,
)


class TestFullDCFChain:
    """Full DCF: build_up → annuity_pv → terminal_value → total value."""

    def test_complete_dcf_valuation(self):
        """Chain build-up discount rate, annuity PV, and terminal value."""
        discount_rate = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
            size_premium=0.02,
            industry_risk_premium=0.01,
            specific_risk_premium=0.02,
        ).value

        annual_cf = 1_000_000
        projection_years = 5
        perpetual_growth = 0.02

        pv_annuity = annuity_pv(
            payment=annual_cf,
            discount_rate=discount_rate,
            periods=projection_years,
        ).value

        tv = terminal_value(
            final_year_cashflow=annual_cf,
            perpetual_growth_rate=perpetual_growth,
            discount_rate=discount_rate,
        ).value

        pv_terminal = present_value(
            future_value=tv,
            discount_rate=discount_rate,
            periods=projection_years,
        ).value

        total_value = pv_annuity + pv_terminal

        assert total_value > 0
        assert total_value > pv_annuity
        assert math.isfinite(total_value)

    def test_dcf_with_growing_cash_flows(self):
        """DCF with growing cash flows using growing_annuity_pv."""
        discount_rate = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
            size_premium=0.02,
        ).value

        first_cf = 1_000_000
        growth_rate = 0.03
        projection_years = 5
        perpetual_growth = 0.02

        pv_growing = growing_annuity_pv(
            payment=first_cf,
            discount_rate=discount_rate,
            growth_rate=growth_rate,
            periods=projection_years,
        ).value

        final_cf = first_cf * (1 + growth_rate) ** projection_years
        tv = terminal_value(
            final_year_cashflow=final_cf,
            perpetual_growth_rate=perpetual_growth,
            discount_rate=discount_rate,
        ).value

        pv_terminal = present_value(
            future_value=tv,
            discount_rate=discount_rate,
            periods=projection_years,
        ).value

        total = pv_growing + pv_terminal
        assert total > 0
        assert math.isfinite(total)

    def test_dcf_with_wacc(self):
        """DCF using WACC as discount rate."""
        wacc_rate = wacc(
            equity_value=600, debt_value=400,
            cost_of_equity=0.12, cost_of_debt=0.06,
            tax_rate=0.25,
        ).value

        cash_flows = [100, 110, 120, 130, 140]
        pv_cf = present_value_of_series(cash_flows, wacc_rate).value

        tv = terminal_value(
            final_year_cashflow=140,
            perpetual_growth_rate=0.02,
            discount_rate=wacc_rate,
        ).value

        pv_tv = present_value(future_value=tv, discount_rate=wacc_rate, periods=5).value
        total = pv_cf + pv_tv

        assert total > 0


class TestPPAIntegration:
    """Full PPA: cost + market + income → purchase_price_allocation."""

    def test_full_ppa_waterfall(self):
        """Chain all three approaches into a PPA."""
        purchase_price = 100_000_000

        cost_result = replacement_cost(
            current_cost=15_000_000,
            obsolescence_factors={"functional": 0.10},
        )

        market_result = market_approach_comparables(
            comparables=[
                {"sale_price": 30_000_000, "revenue": 10_000_000, "asset_type": "trademark"},
                {"sale_price": 42_000_000, "revenue": 12_000_000, "asset_type": "trademark"},
                {"sale_price": 22_400_000, "revenue": 8_000_000, "asset_type": "trademark"},
            ],
            subject_revenue=10_000_000,
        )

        rfr_result = relief_from_royalty(
            revenue_projections=[5_000_000, 5_500_000, 6_000_000, 6_500_000, 7_000_000],
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=5,
        )

        ppa_result = purchase_price_allocation(
            purchase_price=purchase_price,
            tangible_assets_fv=cost_result["value"] * 0.9,
            identified_intangibles=[
                {"name": "Technology (RFR)", "value": rfr_result["value"], "method": "relief-from-royalty"},
                {"name": "Customer Relationships", "value": market_result["value"] * 0.5, "method": "market"},
            ],
            liabilities_fv=2_000_000,
        )

        assert ppa_result.value >= 0
        assert ppa_result.method == "Purchase Price Allocation"

    def test_ppa_with_goodwill_and_dtls(self):
        """PPA with goodwill calculation and deferred tax liability."""
        intangibles = [
            {"name": "Patent", "fair_value": 20_000_000},
            {"name": "Trademark", "fair_value": 10_000_000},
        ]

        dtl_result = deferred_tax_liability_ppa(
            identified_intangibles=intangibles,
            tax_basis=0,
            statutory_rate=0.25,
        )

        sum(i["fair_value"] for i in intangibles)
        dtl = dtl_result["value"]

        ppa_result = purchase_price_allocation(
            purchase_price=80_000_000,
            tangible_assets_fv=10_000_000,
            identified_intangibles=[
                {"name": "Patent", "value": 20_000_000, "method": "RFR"},
                {"name": "Trademark", "value": 10_000_000, "method": "RFR"},
            ],
            liabilities_fv=dtl,
        )

        assert ppa_result.value >= 0
        assert dtl > 0


class TestBrandValuationChain:
    """Brand valuation: brand_strength_index → interbrand_brand_valuation."""

    def test_full_brand_chain(self):
        """Chain brand strength index into Interbrand valuation."""
        bsi_result = brand_strength_index(
            revenue_stability=0.80,
            market_share=0.60,
            geographic_reach=0.70,
            customer_loyalty=0.90,
            investment_level=0.50,
        )

        bsi_score = bsi_result["value"]
        assert 0 <= bsi_score <= 100

        brand_earnings = 50_000_000
        role_of_brand = 0.60
        discount_rate = 0.08

        interbrand_result = interbrand_brand_valuation(
            brand_earnings=brand_earnings,
            role_of_brand_index=role_of_brand,
            brand_strength_score=bsi_score,
            discount_rate=discount_rate,
        )

        assert interbrand_result["value"] > 0
        assert interbrand_result["value"] > brand_earnings * role_of_brand

    def test_trademark_with_brand_strength(self):
        """Trademark valuation using computed brand strength index."""
        bsi_result = brand_strength_index(
            revenue_stability=0.70,
            market_share=0.50,
            geographic_reach=0.60,
            customer_loyalty=0.80,
            investment_level=0.40,
        )

        bsi_normalized = bsi_result["value"] / 100

        tm_result = trademark_valuation(
            revenue=10_000_000,
            profit_margin=0.15,
            brand_strength_index=bsi_normalized,
            discount_rate=0.12,
            useful_life=10,
            method="relief_from_royalty",
        )

        assert tm_result["value"] > 0


class TestCLVComparison:
    """CLV + customer_relationship_valuation comparison."""

    def test_clv_vs_relationship_valuation(self):
        """Compare CLV per-customer with multi-period customer relationship valuation."""
        clv_result = customer_lifetime_value(
            revenue_per_period=1_000,
            retention_rate=0.80,
            discount_rate=0.10,
            margin=0.30,
        )

        rel_result = customer_relationship_valuation(
            customer_count=1000,
            avg_revenue_per_customer=1_000,
            retention_rate=0.80,
            profit_margin=0.30,
            discount_rate=0.10,
            projection_period=5,
        )

        total_clv = clv_result["value"] * 1000
        rel_value = rel_result["value"]

        assert total_clv > 0
        assert rel_value > 0
        assert math.isfinite(total_clv)
        assert math.isfinite(rel_value)

    def test_churn_impact_on_clv(self):
        """Analyze how churn rate changes affect CLV."""
        base_clv = customer_lifetime_value(
            revenue_per_period=500,
            retention_rate=0.80,
            discount_rate=0.10,
            margin=0.25,
        )["value"]

        improved_clv = customer_lifetime_value(
            revenue_per_period=500,
            retention_rate=0.85,
            discount_rate=0.10,
            margin=0.25,
        )["value"]

        assert improved_clv > base_clv

        churn_result = churn_impact_analysis(
            current_customers=1000,
            churn_rate_before=0.20,
            churn_rate_after=0.15,
            revenue_per_customer=500,
            discount_rate=0.10,
        )

        assert churn_result["value"] > 0


class TestMonteCarloSensitivityTornado:
    """Monte Carlo → sensitivity_analysis → tornado diagram."""

    def test_mc_to_sensitivity_pipeline(self):
        """Run Monte Carlo, then sensitivity analysis on key parameters."""
        def simple_dcf(revenue, discount_rate):
            return revenue * 0.10 / discount_rate

        mc_result = monte_carlo_valuation(
            valuation_fn=simple_dcf,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 10_000_000, "std": 1_000_000}},
                {"name": "discount_rate", "distribution": "uniform", "params": {"low": 0.08, "high": 0.15}},
            ],
            iterations=1000,
            seed=42,
        )

        assert mc_result["mean"] > 0
        assert mc_result["std"] > 0

        tornado = sensitivity_tornado(
            function_name="perpetuity_pv",
            base_params={"payment": 1_000_000, "discount_rate": 0.10},
            parameter_ranges={
                "discount_rate": [0.08, 0.10, 0.12],
                "payment": [800_000, 1_000_000, 1_200_000],
            },
        )

        assert len(tornado["tornado"]) == 2
        assert tornado["tornado"][0]["impact"] >= tornado["tornado"][1]["impact"]

    def test_scenario_analysis_with_dcf(self):
        """Scenario analysis feeding into DCF parameters."""
        scenarios = [
            {
                "name": "Base",
                "probability": 0.50,
                "params": {"payment": 1_000_000, "discount_rate": 0.10},
                "function_name": "perpetuity_pv",
            },
            {
                "name": "Upside",
                "probability": 0.25,
                "params": {"payment": 1_500_000, "discount_rate": 0.09},
                "function_name": "perpetuity_pv",
            },
            {
                "name": "Downside",
                "probability": 0.25,
                "params": {"payment": 700_000, "discount_rate": 0.12},
                "function_name": "perpetuity_pv",
            },
        ]

        result = scenario_analysis(scenarios)

        assert result["expected_value"] > 0
        assert len(result["scenarios"]) == 3
        total_prob = sum(s["probability"] for s in result["scenarios"])
        assert math.isclose(total_prob, 1.0, abs_tol=1e-6)


class TestImpairmentIntegration:
    """Value in use → FVLCTS → CGU impairment chain."""

    def test_full_impairment_chain(self):
        """Chain value_in_use, fair_value_less_costs_to_sell, and CGU impairment."""
        viu_result = value_in_use(
            cash_flow_projections=[5_000_000, 5_500_000, 6_000_000],
            terminal_growth_rate=0.02,
            discount_rate=0.10,
        )

        fvlcts_result = fair_value_less_costs_to_sell(
            fair_value=50_000_000,
            disposal_costs=2_000_000,
        )

        recoverable_amount = max(viu_result.value, fvlcts_result.value)

        cgu_result = cash_generating_unit_impairment(
            cgu_carrying_value=70_000_000,
            cgu_recoverable_amount=recoverable_amount,
            goodwill_allocated=10_000_000,
            other_assets=[
                {"name": "Patents", "carrying_value": 30_000_000},
                {"name": "Equipment", "carrying_value": 30_000_000},
            ],
        )

        assert cgu_result.value >= 0
        assert viu_result.value > 0
        assert fvlcts_result.value > 0


class TestPatentValuationIntegration:
    """Patent portfolio + option pricing integration."""

    def test_portfolio_with_option_pricing(self):
        """Value individual patents with option pricing, then aggregate into portfolio."""
        patent1 = option_pricing_patent(
            exercise_cost=5_000_000,
            expected_value=10_000_000,
            volatility=0.40,
            time_to_expiry=10,
            risk_free_rate=0.03,
        )

        patent2 = option_pricing_patent(
            exercise_cost=3_000_000,
            expected_value=8_000_000,
            volatility=0.35,
            time_to_expiry=8,
            risk_free_rate=0.03,
        )

        portfolio = patent_portfolio_valuation(
            patents=[
                {"value": patent1["value"], "category": "pharma"},
                {"value": patent2["value"], "category": "tech"},
            ],
            diversification_factor=0.1,
        )

        assert portfolio["value"] > 0
        assert portfolio["value"] < patent1["value"] + patent2["value"]


class TestTechnologyValuationIntegration:
    """Technology obsolescence → API valuation → algorithm valuation."""

    def test_tech_chain(self):
        """Chain obsolescence curve with API and algorithm valuations."""
        obsolescence = technology_obsolescence_curve(
            initial_value=1_000_000,
            obsolescence_rate=0.20,
            periods=5,
        )

        api_val = api_valuation(
            api_calls_per_month=1_000_000,
            revenue_per_call=0.001,
            growth_rate=0.15,
            useful_life=5,
            discount_rate=0.10,
        )

        algo_val = algorithm_valuation(
            computational_savings=500_000,
            deployment_scale=3.0,
            competitive_advantage_years=5,
            discount_rate=0.12,
        )

        assert obsolescence["value"] > 0
        assert obsolescence["value"] < 1_000_000
        assert api_val["value"] > 0
        assert algo_val["value"] > 0


class TestRoyaltyBenchmarkIntegration:
    """Profit split + analytical method integration."""

    def test_profit_split_and_analytical(self):
        """Compare profit split method with analytical method valuation."""
        ps_result = profit_split_method(
            licensor_contribution_pct=0.40,
            licensee_contribution_pct=0.60,
            total_profit=10_000_000,
        )

        am_result = analytical_method_valuation(
            advantage_margin=0.05,
            volume=10_000_000,
            discount_rate=0.12,
            economic_life=7,
        )

        assert ps_result["value"] > 0
        assert am_result["value"] > 0
        assert ps_result["value"] == 4_000_000


class TestMPEEMIntegration:
    """MPEEM with contributory asset charges and TAB."""

    def test_full_mpeem_chain(self):
        """Build CACs, then run MPEEM with TAB."""
        cac_base = contributory_asset_charges([
            {"type": "working_capital", "value": 500_000, "return_rate": 0.08},
            {"type": "fixed_assets", "value": 1_000_000, "return_rate": 0.10},
        ])

        cacs_per_period = [
            {"total_cac": cac_base["total_cac"] * (1 + 0.02 * i)}
            for i in range(5)
        ]

        mpeem_result = mpeem(
            cash_flow_projections=[200_000, 220_000, 240_000, 260_000, 280_000],
            contributory_asset_charges=cacs_per_period,
            discount_rate=0.12,
            tax_rate=0.25,
            tab_enabled=True,
        )

        assert mpeem_result["value"] > 0
        assert mpeem_result["tab_factor"] > 1.0

    def test_mpeem_vs_single_period(self):
        """Compare MPEEM with single-period excess earnings."""
        cacs = [{"total_cac": 140_000}]

        sp_result = single_period_excess_earnings(
            normalized_earnings=500_000,
            contributory_asset_charges=cacs,
            capitalization_rate=0.12,
        )

        assert sp_result["value"] > 0
        assert math.isclose(sp_result["value"], 3_000_000, rel_tol=1e-4)


class TestIncrementalCashflowIntegration:
    """Incremental cashflow with sensitivity analysis."""

    def test_incremental_with_sensitivity(self):
        """Run incremental cashflow, then sensitivity on discount rate."""
        incr_result = incremental_cashflow(
            cash_flows_with=[500_000, 550_000, 600_000, 650_000, 700_000],
            cash_flows_without=[400_000, 420_000, 440_000, 460_000, 480_000],
            discount_rate=0.10,
        )

        assert incr_result["value"] > 0

        sensitivity = sensitivity_analysis(
            function_name="present_value",
            parameter_name="discount_rate",
            parameter_range=[0.08, 0.10, 0.12],
            fixed_parameters={"future_value": incr_result["value"], "periods": 5},
        )

        assert len(sensitivity["results"]) == 3
