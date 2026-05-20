"""Tests for MCP tool registration and callable behavior."""

from __future__ import annotations

import json

import pytest

from mcp_server.tools import (
    adjust_royalty_rate,
    annuity_pv,
    assembled_workforce_valuation,
    build_up_discount_rate,
    capm_discount_rate,
    contributory_asset_charges,
    control_premium,
    copyright_valuation,
    cup_transfer_price,
    currency_adjusted_discount_rate,
    customer_relationship_valuation,
    data_asset_valuation,
    decision_tree_valuation,
    developed_technology_valuation,
    distribution_network_valuation,
    dlom_finnerty,
    estimate_useful_life,
    future_value,
    goodwill,
    goodwill_impairment_test,
    growing_annuity_pv,
    incremental_cashflow,
    intangible_impairment_test,
    key_person_value,
    market_approach_comparables,
    monte_carlo_valuation,
    mpeem,
    non_compete_valuation,
    patent_infringement_damages,
    patent_valuation,
    perpetuity_pv,
    platform_valuation,
    present_value,
    purchase_price_allocation,
    relief_from_royalty,
    replacement_cost,
    reproduction_cost,
    royalty_capitalization,
    royalty_rate_benchmark,
    sensitivity_analysis,
    single_period_excess_earnings,
    software_valuation,
    tax_amortization_benefit,
    terminal_value,
    trade_secret_valuation,
    trademark_valuation,
    twenty_five_percent_rule,
    wacc,
)


def _parse(result: str) -> dict:
    """Parse JSON string result."""
    return json.loads(result)


class TestCoreMathTools:
    def test_present_value(self):
        r = _parse(present_value(future_value=1000000, discount_rate=0.10, periods=5))
        assert "error" not in r
        assert r["value"] == pytest.approx(620921.32, rel=0.01)

    def test_future_value(self):
        r = _parse(future_value(present_value=620921.32, discount_rate=0.10, periods=5))
        assert "error" not in r
        assert r["value"] == pytest.approx(1000000, rel=0.01)

    def test_annuity_pv(self):
        r = _parse(annuity_pv(payment=50000, discount_rate=0.15, periods=10))
        assert "error" not in r
        assert r["value"] == pytest.approx(250937.50, rel=0.01)

    def test_perpetuity_pv(self):
        r = _parse(perpetuity_pv(payment=400000, discount_rate=0.15))
        assert "error" not in r
        assert r["value"] == pytest.approx(2666666.67, rel=0.01)

    def test_growing_annuity_pv(self):
        r = _parse(growing_annuity_pv(payment=100000, discount_rate=0.12, growth_rate=0.05, periods=5))
        assert "error" not in r
        assert r["value"] > 0

    def test_terminal_value_gordon(self):
        r = _parse(terminal_value(final_year_cashflow=1000000, perpetual_growth_rate=0.03, discount_rate=0.12))
        assert "error" not in r
        assert r["value"] == pytest.approx(11444444.44, rel=0.01)

    def test_build_up_discount_rate(self):
        r = _parse(build_up_discount_rate(risk_free_rate=0.04, equity_risk_premium=0.06, size_premium=0.02))
        assert "error" not in r
        assert r["value"] == pytest.approx(0.12, rel=0.001)

    def test_capm_discount_rate(self):
        r = _parse(capm_discount_rate(risk_free_rate=0.04, beta=1.2, market_return=0.10))
        assert "error" not in r
        assert r["value"] == pytest.approx(0.112, rel=0.001)

    def test_wacc(self):
        r = _parse(wacc(equity_value=600, debt_value=400, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25))
        assert "error" not in r
        assert r["value"] == pytest.approx(0.09, rel=0.001)

    def test_tax_amortization_benefit(self):
        r = _parse(tax_amortization_benefit(discount_rate=0.12, useful_life=10, tax_rate=0.25, asset_value=1000000))
        assert "error" not in r
        assert r["value"] > 0

    def test_control_premium(self):
        r = _parse(control_premium(minority_price=100, control_price=130))
        assert "error" not in r
        assert r["value"] == pytest.approx(0.30, rel=0.001)

    def test_dlom_finnerty(self):
        r = _parse(dlom_finnerty(restricted_period=2.0, volatility=0.40, risk_free_rate=0.04))
        assert "error" not in r
        assert 0 < r["value"] < 1

    def test_currency_adjusted_discount_rate(self):
        r = _parse(currency_adjusted_discount_rate(
            base_rate=0.12, currency_risk_premium=0.02, country_risk_premium=0.03,
        ))
        assert "error" not in r
        assert r["value"] == pytest.approx(0.17, rel=0.001)


class TestApproachTools:
    def test_reproduction_cost(self):
        r = _parse(reproduction_cost({"labor": 400000, "materials": 150000, "overhead": 100000}))
        assert "error" not in r
        assert r["value"] == 650000

    def test_reproduction_cost_with_obsolescence(self):
        r = _parse(reproduction_cost(
            {"labor": 400000, "materials": 150000, "overhead": 100000},
            {"functional": 0.15, "technological": 0.20, "economic": 0.05},
        ))
        assert "error" not in r
        assert r["value"] == pytest.approx(419900, rel=0.01)

    def test_replacement_cost(self):
        r = _parse(replacement_cost(
            current_cost=500000,
            obsolescence_factors={"functional": 0.10, "technological": 0.30},
        ))
        assert "error" not in r
        assert r["value"] == pytest.approx(315000, rel=0.01)

    def test_market_approach_comparables(self):
        comps = [
            {"sale_price": 5000000, "revenue": 2000000, "asset_type": "trademark"},
            {"sale_price": 8000000, "revenue": 3000000, "asset_type": "trademark"},
            {"sale_price": 12000000, "revenue": 4000000, "asset_type": "trademark"},
        ]
        r = _parse(market_approach_comparables(comparables=comps, subject_revenue=2500000))
        assert "error" not in r
        assert r["value"] == pytest.approx(6666666.67, rel=0.01)

    def test_royalty_capitalization(self):
        r = _parse(royalty_capitalization(revenue=10000000, royalty_rate=0.04, discount_rate=0.15))
        assert "error" not in r
        assert r["value"] == pytest.approx(2666666.67, rel=0.01)


class TestIncomeMethodTools:
    def test_relief_from_royalty(self):
        r = _parse(relief_from_royalty(
            revenue_projections=[1000000, 1100000, 1200000, 1300000, 1400000],
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=5,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_mpeem(self):
        cfs = [200000, 220000, 240000, 260000, 280000]
        cacs = [
            {"total_cac": 50000}, {"total_cac": 52000}, {"total_cac": 54000},
            {"total_cac": 56000}, {"total_cac": 58000},
        ]
        r = _parse(mpeem(cash_flow_projections=cfs, contributory_asset_charges=cacs, discount_rate=0.12, tax_rate=0.25))
        assert "error" not in r
        assert r["value"] > 0

    def test_single_period_excess_earnings(self):
        r = _parse(single_period_excess_earnings(
            normalized_earnings=500000,
            contributory_asset_charges=[{"total_cac": 140000}],
            capitalization_rate=0.12,
        ))
        assert "error" not in r
        assert r["value"] == pytest.approx(3000000, rel=0.01)

    def test_incremental_cashflow(self):
        r = _parse(incremental_cashflow(
            cash_flows_with=[500000, 550000, 600000, 650000, 700000],
            cash_flows_without=[400000, 420000, 440000, 460000, 480000],
            discount_rate=0.10,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_contributory_asset_charges(self):
        assets = [
            {"type": "working_capital", "value": 500000, "return_rate": 0.08},
            {"type": "fixed_assets", "value": 1000000, "return_rate": 0.10},
        ]
        r = _parse(contributory_asset_charges(assets=assets))
        assert "error" not in r
        assert r["total_cac"] == pytest.approx(140000, rel=0.01)


class TestAssetTypeTools:
    def test_patent_valuation(self):
        r = _parse(patent_valuation(
            remaining_life=10,
            cash_flow_projections=[100000] * 10,
            probability_of_success=0.7,
            discount_rate=0.15,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_trademark_valuation(self):
        r = _parse(trademark_valuation(
            revenue=10000000, profit_margin=0.20, brand_strength_index=0.75,
            discount_rate=0.12, useful_life=15,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_copyright_valuation(self):
        r = _parse(copyright_valuation(
            projected_revenue=5000000, useful_life=10, discount_rate=0.12, royalty_rate=0.08,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_trade_secret_valuation(self):
        r = _parse(trade_secret_valuation(
            development_cost=500000, economic_life=10, competitive_advantage_period=5,
            discount_rate=0.15, secrecy_probability=0.80,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_developed_technology_valuation(self):
        r = _parse(developed_technology_valuation(
            rd_costs=1000000, life_cycle_stage="growth", competitive_advantage=5,
            discount_rate=0.10, cash_flow_projections=[300000] * 5,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_software_valuation(self):
        r = _parse(software_valuation(
            development_cost=500000, maintenance_cost=100000, user_base=10000,
            revenue_model={"type": "subscription", "revenue_per_user": 120},
            useful_life=5, discount_rate=0.15,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_data_asset_valuation(self):
        r = _parse(data_asset_valuation(
            acquisition_cost=200000, quality_score=0.85, revenue_contribution=500000,
            useful_life=5, discount_rate=0.12,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_platform_valuation(self):
        r = _parse(platform_valuation(
            network_size=50000, network_effects_coefficient=0.3, revenue_per_user=50,
            growth_rate=0.15, discount_rate=0.18,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_customer_relationship_valuation(self):
        r = _parse(customer_relationship_valuation(
            customer_count=1000, avg_revenue_per_customer=5000, retention_rate=0.85,
            profit_margin=0.30, discount_rate=0.15, projection_period=10,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_distribution_network_valuation(self):
        r = _parse(distribution_network_valuation(
            channel_count=50, revenue_per_channel=200000, channel_margin=0.25,
            useful_life=10, discount_rate=0.12,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_non_compete_valuation(self):
        r = _parse(non_compete_valuation(
            protected_revenue=5000000, profit_margin=0.25, term=4,
            enforcement_probability=0.90, discount_rate=0.15,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_assembled_workforce_valuation(self):
        r = _parse(assembled_workforce_valuation(
            employee_count=100, avg_replacement_cost=15000, training_cost=5000,
            productivity_factor=0.70, attrition_rate=0.10,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_key_person_value(self):
        r = _parse(key_person_value(
            revenue_contribution=2000000, replacement_cost=500000,
            departure_probability=0.10, discount_rate=0.12,
        ))
        assert "error" not in r
        assert r["value"] > 0


class TestAdvancedTools:
    def test_goodwill(self):
        r = _parse(goodwill(purchase_price=100000000, fair_value_net_identifiable_assets=75000000))
        assert "error" not in r
        assert r["value"] == pytest.approx(25000000, rel=0.01)

    def test_goodwill_bargain_purchase_raises(self):
        r = _parse(goodwill(purchase_price=50000000, fair_value_net_identifiable_assets=75000000))
        assert "error" in r

    def test_purchase_price_allocation(self):
        r = _parse(purchase_price_allocation(
            purchase_price=100000000,
            tangible_assets_fv=15000000,
            identified_intangibles=[
                {"name": "Trademark", "value": 30000000, "method": "relief_from_royalty"},
                {"name": "Technology", "value": 30000000, "method": "mpeem"},
            ],
            liabilities_fv=0,
        ))
        assert "error" not in r
        assert r["value"] == pytest.approx(25000000, rel=0.01)

    def test_goodwill_impairment_test_impaired(self):
        r = _parse(goodwill_impairment_test(carrying_value=50000000, fair_value=40000000, reporting_unit="Tech"))
        assert "error" not in r
        assert r["value"] == pytest.approx(10000000, rel=0.01)

    def test_goodwill_impairment_test_not_impaired(self):
        r = _parse(goodwill_impairment_test(carrying_value=50000000, fair_value=55000000, reporting_unit="Tech"))
        assert "error" not in r
        assert r["value"] == 0

    def test_intangible_impairment_test(self):
        r = _parse(intangible_impairment_test(carrying_value=20000000, fair_value=15000000))
        assert "error" not in r
        assert r["value"] == pytest.approx(5000000, rel=0.01)

    def test_royalty_rate_benchmark(self):
        r = _parse(royalty_rate_benchmark(ip_type="patent", industry="pharmaceutical"))
        assert "error" not in r
        assert r["value"] == pytest.approx(0.08, rel=0.01)

    def test_adjust_royalty_rate(self):
        r = _parse(adjust_royalty_rate(base_rate=0.05, adjustment_factors={"profit_margin": 1.2, "exclusivity": 1.3}))
        assert "error" not in r
        assert r["value"] == pytest.approx(0.078, rel=0.01)

    def test_twenty_five_percent_rule(self):
        r = _parse(twenty_five_percent_rule(licensee_expected_profit=10000000, profit_attribution_to_ip=0.8))
        assert "error" not in r
        assert r["value"] == pytest.approx(2000000, rel=0.01)

    def test_cup_transfer_price(self):
        r = _parse(cup_transfer_price(controlled_price=100, uncontrolled_prices=[90, 95, 100, 105, 110]))
        assert "error" not in r
        assert r["value"] == pytest.approx(100, rel=0.01)

    def test_patent_infringement_damages(self):
        r = _parse(patent_infringement_damages(
            lost_profits_or_royalty=1000000, infringement_period=5,
            discount_rate=0.10, prejudgment_interest_rate=0.05,
        ))
        assert "error" not in r
        assert r["value"] > 0

    def test_monte_carlo_valuation(self):
        r = _parse(monte_carlo_valuation(
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1000000, "std": 100000}},
                {"name": "cost", "distribution": "uniform", "params": {"low": 200000, "high": 400000}},
            ],
            iterations=1000,
            seed=42,
        ))
        assert "error" not in r
        assert "mean" in r

    def test_decision_tree_valuation(self):
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "Invest?", "value": 0},
                {"id": "success", "type": "chance", "label": "Outcome", "value": 0},
                {"id": "high", "type": "terminal", "label": "High", "value": 1000000},
                {"id": "low", "type": "terminal", "label": "Low", "value": 200000},
            ],
            "edges": [
                {"from": "root", "to": "success", "probability": 1.0, "cost": 300000},
                {"from": "success", "to": "high", "probability": 0.6, "cost": 0},
                {"from": "success", "to": "low", "probability": 0.4, "cost": 0},
            ],
        }
        r = _parse(decision_tree_valuation(tree=tree))
        assert "error" not in r
        assert r["expected_value"] > 0

    def test_sensitivity_analysis(self):
        r = _parse(sensitivity_analysis(
            function_name="present_value",
            parameter_name="discount_rate",
            parameter_range=[0.05, 0.10, 0.15, 0.20],
            fixed_parameters={"future_value": 1000000, "periods": 5},
        ))
        assert "error" not in r
        assert len(r["results"]) == 4

    def test_estimate_useful_life(self):
        r = _parse(estimate_useful_life(asset_type="patent", legal_life=20, obsolescence_rate=0.10))
        assert "error" not in r
        assert r["value"] > 0


class TestErrorHandling:
    def test_invalid_inputs_return_error_not_exception(self):
        r = _parse(present_value(future_value=-100, discount_rate=0.10, periods=5))
        assert "error" in r

    def test_missing_required_params_return_error(self):
        r = _parse(mpeem(
            cash_flow_projections=[],
            contributory_asset_charges=[],
            discount_rate=0.12,
            tax_rate=0.25,
        ))
        assert "error" in r
