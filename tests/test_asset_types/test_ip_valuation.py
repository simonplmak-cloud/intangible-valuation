"""Tests for IP valuation module."""

import pytest

from src.asset_types.ip_valuation import (
    copyright_valuation,
    patent_valuation,
    trade_secret_valuation,
)


class TestPatentValuation:
    """Tests for patent_valuation function."""

    def test_happy_path_basic(self):
        result = patent_valuation(
            remaining_life=10,
            cash_flow_projections=[100000, 120000, 140000, 160000, 180000],
            probability_of_success=0.7,
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert result["method"] == "Risk-Adjusted Income Approach"
        assert "PV = sum" in result["formula_reference"]
        assert len(result["steps"]) > 0
        assert "remaining_life" in result["assumptions"]

    def test_happy_path_with_comparables(self):
        result = patent_valuation(
            remaining_life=5,
            cash_flow_projections=[50000, 60000, 70000],
            probability_of_success=0.8,
            discount_rate=0.12,
            comparable_license_rates=[0.03, 0.04, 0.05],
        )
        assert result["value"] > 0
        assert "comparable_license_rates" in result["assumptions"]

    def test_happy_path_zero_probability(self):
        result = patent_valuation(
            remaining_life=5,
            cash_flow_projections=[100000],
            probability_of_success=0.0,
            discount_rate=0.10,
        )
        assert result["value"] == 0.0

    def test_error_negative_cash_flow(self):
        with pytest.raises(ValueError):
            patent_valuation(
                remaining_life=5,
                cash_flow_projections=[-100000],
                probability_of_success=0.5,
                discount_rate=0.10,
            )

    def test_error_invalid_probability(self):
        with pytest.raises(ValueError):
            patent_valuation(
                remaining_life=5,
                cash_flow_projections=[100000],
                probability_of_success=1.5,
                discount_rate=0.10,
            )

    def test_error_negative_remaining_life(self):
        with pytest.raises(ValueError):
            patent_valuation(
                remaining_life=0,
                cash_flow_projections=[100000],
                probability_of_success=0.5,
                discount_rate=0.10,
            )

    def test_error_negative_discount_rate(self):
        with pytest.raises(ValueError):
            patent_valuation(
                remaining_life=5,
                cash_flow_projections=[100000],
                probability_of_success=0.5,
                discount_rate=-0.01,
            )

    def test_error_empty_cash_flows(self):
        with pytest.raises(ValueError):
            patent_valuation(
                remaining_life=5,
                cash_flow_projections=[],
                probability_of_success=0.5,
                discount_rate=0.10,
            )


class TestCopyrightValuation:
    """Tests for copyright_valuation function."""

    def test_happy_path_basic(self):
        result = copyright_valuation(
            projected_revenue=500000,
            useful_life=10,
            discount_rate=0.08,
            royalty_rate=0.05,
        )
        assert result["value"] > 0
        assert "Relief-from-Royalty" in result["method"]
        assert len(result["steps"]) > 0

    def test_happy_path_zero_revenue(self):
        result = copyright_valuation(
            projected_revenue=0,
            useful_life=5,
            discount_rate=0.10,
            royalty_rate=0.03,
        )
        assert result["value"] == 0.0

    def test_happy_path_high_royalty(self):
        result = copyright_valuation(
            projected_revenue=1000000,
            useful_life=20,
            discount_rate=0.05,
            royalty_rate=0.10,
        )
        assert result["value"] > 0

    def test_error_negative_revenue(self):
        with pytest.raises(ValueError):
            copyright_valuation(
                projected_revenue=-100000,
                useful_life=5,
                discount_rate=0.10,
                royalty_rate=0.05,
            )

    def test_error_invalid_royalty_rate(self):
        with pytest.raises(ValueError):
            copyright_valuation(
                projected_revenue=100000,
                useful_life=5,
                discount_rate=0.10,
                royalty_rate=1.5,
            )

    def test_error_zero_useful_life(self):
        with pytest.raises(ValueError):
            copyright_valuation(
                projected_revenue=100000,
                useful_life=0,
                discount_rate=0.10,
                royalty_rate=0.05,
            )


class TestTradeSecretValuation:
    """Tests for trade_secret_valuation function."""

    def test_happy_path_basic(self):
        result = trade_secret_valuation(
            development_cost=500000,
            economic_life=10,
            competitive_advantage_period=5,
            discount_rate=0.10,
            secrecy_probability=0.9,
        )
        assert result["value"] > 0
        assert "Secrecy Risk" in result["method"]
        assert len(result["steps"]) > 0

    def test_happy_path_high_secrecy(self):
        result = trade_secret_valuation(
            development_cost=1000000,
            economic_life=5,
            competitive_advantage_period=3,
            discount_rate=0.08,
            secrecy_probability=0.95,
        )
        assert result["value"] > 0

    def test_happy_path_low_secrecy(self):
        result = trade_secret_valuation(
            development_cost=1000000,
            economic_life=10,
            competitive_advantage_period=5,
            discount_rate=0.10,
            secrecy_probability=0.3,
        )
        # Low secrecy should still return at least cost floor
        assert result["value"] >= 1000000

    def test_error_negative_cost(self):
        with pytest.raises(ValueError):
            trade_secret_valuation(
                development_cost=-100000,
                economic_life=5,
                competitive_advantage_period=3,
                discount_rate=0.10,
                secrecy_probability=0.8,
            )

    def test_error_invalid_secrecy_probability(self):
        with pytest.raises(ValueError):
            trade_secret_valuation(
                development_cost=100000,
                economic_life=5,
                competitive_advantage_period=3,
                discount_rate=0.10,
                secrecy_probability=-0.1,
            )

    def test_error_zero_economic_life(self):
        with pytest.raises(ValueError):
            trade_secret_valuation(
                development_cost=100000,
                economic_life=0,
                competitive_advantage_period=3,
                discount_rate=0.10,
                secrecy_probability=0.8,
            )
