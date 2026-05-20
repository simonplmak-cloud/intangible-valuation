"""MCP integration tests.

Tests full MCP tool workflows, error handling, and tool description completeness.
"""

import json
import math
import pytest

from mcp_server.tools import (
    present_value,
    future_value,
    annuity_pv,
    perpetuity_pv,
    growing_annuity_pv,
    terminal_value,
    build_up_discount_rate,
    capm_discount_rate,
    wacc,
    tax_amortization_benefit,
    control_premium,
    dlom_finnerty,
    currency_adjusted_discount_rate,
    reproduction_cost,
    replacement_cost,
    market_approach_comparables,
    royalty_capitalization,
    relief_from_royalty,
    mpeem,
    single_period_excess_earnings,
    incremental_cashflow,
    contributory_asset_charges,
    patent_valuation,
    trademark_valuation,
    copyright_valuation,
    trade_secret_valuation,
    developed_technology_valuation,
    software_valuation,
    data_asset_valuation,
    platform_valuation,
    customer_relationship_valuation,
    distribution_network_valuation,
    non_compete_valuation,
    assembled_workforce_valuation,
    key_person_value,
    goodwill,
    purchase_price_allocation,
    goodwill_impairment_test,
    intangible_impairment_test,
    royalty_rate_benchmark,
    adjust_royalty_rate,
    twenty_five_percent_rule,
    cup_transfer_price,
    patent_infringement_damages,
    monte_carlo_valuation,
    monte_carlo_sensitivity,
    decision_tree_valuation,
    sensitivity_analysis,
    estimate_useful_life,
)


def parse_result(result_str):
    """Parse JSON result string from MCP tool."""
    return json.loads(result_str)


class TestMCPFullWorkflowPPA:
    """Full PPA workflow using multiple MCP tools in sequence."""

    def test_ppa_workflow(self):
        """Complete PPA: build discount rate → value intangibles → allocate purchase price."""
        discount_rate_result = build_up_discount_rate(
            risk_free_rate=0.04,
            equity_risk_premium=0.06,
            size_premium=0.02,
            industry_risk_premium=0.01,
            specific_risk_premium=0.02,
        )
        dr = parse_result(discount_rate_result)
        assert "error" not in dr
        assert dr["value"] > 0

        rfr_result = relief_from_royalty(
            revenue_projections=[5_000_000, 5_500_000, 6_000_000, 6_500_000, 7_000_000],
            royalty_rate=0.05,
            discount_rate=dr["value"],
            tax_rate=0.25,
            useful_life=5,
        )
        rfr = parse_result(rfr_result)
        assert "error" not in rfr
        assert rfr["value"] > 0

        ppa_result = purchase_price_allocation(
            purchase_price=100_000_000,
            tangible_assets_fv=15_000_000,
            identified_intangibles=[
                {"name": "Technology (RFR)", "value": rfr["value"], "method": "relief-from-royalty"},
                {"name": "Customer Relationships", "value": 20_000_000, "method": "MPEEM"},
            ],
            liabilities_fv=5_000_000,
        )
        ppa = parse_result(ppa_result)
        assert "error" not in ppa
        assert ppa["value"] >= 0

    def test_brand_valuation_workflow(self):
        """Brand valuation: benchmark → adjust → value."""
        benchmark = royalty_rate_benchmark("trademark", "consumer_goods")
        bm = parse_result(benchmark)
        assert "error" not in bm

        adjusted = adjust_royalty_rate(
            base_rate=bm["value"],
            adjustment_factors={"profit_margin": 1.2, "exclusivity": 1.1},
        )
        adj = parse_result(adjusted)
        assert "error" not in adj
        assert adj["value"] > bm["value"]

        tm = trademark_valuation(
            revenue=10_000_000,
            profit_margin=0.15,
            brand_strength_index=0.70,
            discount_rate=0.12,
            useful_life=10,
        )
        tm_result = parse_result(tm)
        assert "error" not in tm_result
        assert tm_result["value"] > 0

    def test_customer_valuation_workflow(self):
        """Customer valuation: relationship → CLV comparison."""
        rel = customer_relationship_valuation(
            customer_count=1000,
            avg_revenue_per_customer=1_000,
            retention_rate=0.80,
            profit_margin=0.20,
            discount_rate=0.10,
            projection_period=5,
        )
        rel_result = parse_result(rel)
        assert "error" not in rel_result
        assert rel_result["value"] > 0


class TestMCPErrorHandling:
    """MCP error handling: invalid inputs, missing params, wrong types."""

    def test_pv_negative_fv(self):
        result = parse_result(present_value(future_value=-100, discount_rate=0.10, periods=5))
        assert "error" in result

    def test_annuity_zero_rate(self):
        result = parse_result(annuity_pv(payment=1_000, discount_rate=0.0, periods=10))
        assert "error" in result

    def test_perpetuity_zero_rate(self):
        result = parse_result(perpetuity_pv(payment=1_000, discount_rate=0.0))
        assert "error" in result

    def test_wacc_zero_capital(self):
        result = parse_result(wacc(
            equity_value=0, debt_value=0,
            cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25,
        ))
        assert "error" in result

    def test_goodwill_bargain_purchase(self):
        result = parse_result(goodwill(
            purchase_price=40_000_000,
            fair_value_net_identifiable_assets=50_000_000,
        ))
        assert "error" in result

    def test_rfr_mismatched_periods(self):
        result = parse_result(relief_from_royalty(
            revenue_projections=[1_000_000, 1_100_000],
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=5,
        ))
        assert "error" in result

    def test_mpeem_mismatched_cacs(self):
        result = parse_result(mpeem(
            cash_flow_projections=[100, 200, 300],
            contributory_asset_charges=[{"total_cac": 10}],
            discount_rate=0.10,
            tax_rate=0.25,
        ))
        assert "error" in result

    def test_terminal_value_rate_le_growth(self):
        result = parse_result(terminal_value(
            final_year_cashflow=1_000_000,
            perpetual_growth_rate=0.10,
            discount_rate=0.10,
        ))
        assert "error" in result

    def test_capm_market_below_rf(self):
        result = parse_result(capm_discount_rate(
            risk_free_rate=0.05, beta=1.0, market_return=0.03,
        ))
        assert "error" in result

    def test_control_premium_reversed(self):
        result = parse_result(control_premium(minority_price=100, control_price=90))
        assert "error" in result

    def test_cup_too_few_prices(self):
        result = parse_result(cup_transfer_price(
            controlled_price=100,
            uncontrolled_prices=[90, 95],
        ))
        assert "error" in result

    def test_empty_sensitivity_range(self):
        result = parse_result(sensitivity_analysis(
            function_name="present_value",
            parameter_name="discount_rate",
            parameter_range=[],
            fixed_parameters={"future_value": 1000, "periods": 5},
        ))
        assert "error" in result


class TestMCPToolDescriptions:
    """Verify all MCP tools have meaningful descriptions."""

    @pytest.mark.parametrize("tool_fn", [
        present_value,
        future_value,
        annuity_pv,
        perpetuity_pv,
        growing_annuity_pv,
        terminal_value,
        build_up_discount_rate,
        capm_discount_rate,
        wacc,
        tax_amortization_benefit,
        control_premium,
        dlom_finnerty,
        currency_adjusted_discount_rate,
        reproduction_cost,
        replacement_cost,
        market_approach_comparables,
        royalty_capitalization,
        relief_from_royalty,
        mpeem,
        single_period_excess_earnings,
        incremental_cashflow,
        contributory_asset_charges,
        patent_valuation,
        trademark_valuation,
        copyright_valuation,
        trade_secret_valuation,
        developed_technology_valuation,
        software_valuation,
        data_asset_valuation,
        platform_valuation,
        customer_relationship_valuation,
        distribution_network_valuation,
        non_compete_valuation,
        assembled_workforce_valuation,
        key_person_value,
        goodwill,
        purchase_price_allocation,
        goodwill_impairment_test,
        intangible_impairment_test,
        royalty_rate_benchmark,
        adjust_royalty_rate,
        twenty_five_percent_rule,
        cup_transfer_price,
        patent_infringement_damages,
        monte_carlo_valuation,
        monte_carlo_sensitivity,
        decision_tree_valuation,
        sensitivity_analysis,
        estimate_useful_life,
    ])
    def test_tool_has_description(self, tool_fn):
        """Every MCP tool should have a non-empty docstring."""
        doc = tool_fn.__doc__
        assert doc is not None, f"{tool_fn.__name__} has no docstring"
        assert len(doc.strip()) > 10, f"{tool_fn.__name__} has insufficient docstring: {doc[:50]}"

    @pytest.mark.parametrize("tool_fn", [
        present_value,
        annuity_pv,
        perpetuity_pv,
        build_up_discount_rate,
        wacc,
        relief_from_royalty,
        purchase_price_allocation,
        goodwill,
    ])
    def test_tool_description_references_book(self, tool_fn):
        """Core tools should reference the book chapter in their description."""
        doc = tool_fn.__doc__
        assert doc is not None
        assert "Book" in doc or "Chapter" in doc or "Formula" in doc, (
            f"{tool_fn.__name__} description should reference book/formula"
        )


class TestMCPTypeValidation:
    """MCP tools should handle wrong types gracefully."""

    def test_pv_wrong_type_periods(self):
        result = parse_result(present_value(future_value=1000, discount_rate=0.10, periods="five"))
        assert "error" in result

    def test_wacc_wrong_type_tax_rate(self):
        result = parse_result(wacc(
            equity_value=600, debt_value=400,
            cost_of_equity=0.12, cost_of_debt=0.06,
            tax_rate="high",
        ))
        assert "error" in result

    def test_rfr_wrong_type_revenue(self):
        result = parse_result(relief_from_royalty(
            revenue_projections="not_a_list",
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=5,
        ))
        assert "error" in result


class TestMCPHappyPath:
    """Verify all MCP tools return valid results for standard inputs."""

    def test_present_value(self):
        r = parse_result(present_value(future_value=1_000_000, discount_rate=0.10, periods=5))
        assert "error" not in r
        assert r["value"] > 0

    def test_future_value(self):
        r = parse_result(future_value(present_value=1_000_000, discount_rate=0.10, periods=5))
        assert "error" not in r
        assert r["value"] > 1_000_000

    def test_annuity_pv(self):
        r = parse_result(annuity_pv(payment=100_000, discount_rate=0.10, periods=5))
        assert "error" not in r
        assert r["value"] > 0

    def test_perpetuity_pv(self):
        r = parse_result(perpetuity_pv(payment=100_000, discount_rate=0.10))
        assert "error" not in r
        assert r["value"] > 0

    def test_growing_annuity_pv(self):
        r = parse_result(growing_annuity_pv(payment=100_000, discount_rate=0.10, growth_rate=0.03, periods=5))
        assert "error" not in r
        assert r["value"] > 0

    def test_terminal_value(self):
        r = parse_result(terminal_value(final_year_cashflow=1_000_000, perpetual_growth_rate=0.02, discount_rate=0.10))
        assert "error" not in r
        assert r["value"] > 0

    def test_build_up_discount_rate(self):
        r = parse_result(build_up_discount_rate(risk_free_rate=0.04, equity_risk_premium=0.06))
        assert "error" not in r
        assert math.isclose(r["value"], 0.10, abs_tol=1e-6)

    def test_capm_discount_rate(self):
        r = parse_result(capm_discount_rate(risk_free_rate=0.04, beta=1.0, market_return=0.10))
        assert "error" not in r
        assert math.isclose(r["value"], 0.10, abs_tol=1e-6)

    def test_wacc_tool(self):
        r = parse_result(wacc(equity_value=600, debt_value=400, cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25))
        assert "error" not in r
        assert 0 < r["value"] < 0.12

    def test_decision_tree(self):
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "Decision", "value": 0},
                {"id": "a", "type": "terminal", "label": "A", "value": 100},
                {"id": "b", "type": "terminal", "label": "B", "value": 200},
            ],
            "edges": [
                {"from": "root", "to": "a", "probability": 1.0, "cost": 0},
                {"from": "root", "to": "b", "probability": 1.0, "cost": 0},
            ],
        }
        r = parse_result(decision_tree_valuation(tree=tree))
        assert "error" not in r
        assert r["expected_value"] > 0

    def test_estimate_useful_life(self):
        r = parse_result(estimate_useful_life(asset_type="patent"))
        assert "error" not in r
        assert r["value"] > 0

    def test_sensitivity_analysis(self):
        r = parse_result(sensitivity_analysis(
            function_name="present_value",
            parameter_name="discount_rate",
            parameter_range=[0.08, 0.10, 0.12],
            fixed_parameters={"future_value": 1_000_000, "periods": 10},
        ))
        assert "error" not in r
        assert len(r["results"]) == 3
