"""Tests for royalty benchmark (TASK-038)."""

import pytest

from src.advanced.royalty_benchmark import (
    adjust_royalty_rate,
    analytical_method_valuation,
    profit_split_method,
    royalty_rate_benchmark,
    twenty_five_percent_rule,
)


class TestRoyaltyRateBenchmark:
    def test_patent_pharma(self):
        result = royalty_rate_benchmark("patent", "pharmaceutical")
        assert result.value == 0.08
        assert result.assumptions["recommended_range"] == (0.05, 0.15)

    def test_trademark_consumer(self):
        result = royalty_rate_benchmark("trademark", "consumer_goods")
        assert result.value == 0.04
        assert result.assumptions["recommended_range"] == (0.02, 0.08)

    def test_copyright_software(self):
        result = royalty_rate_benchmark("copyright", "software")
        assert result.value == 0.10
        assert result.assumptions["recommended_range"] == (0.05, 0.20)

    def test_technology_software(self):
        result = royalty_rate_benchmark("technology", "software")
        assert result.value == 0.10

    def test_trade_secret_tech(self):
        result = royalty_rate_benchmark("trade_secret", "technology")
        assert result.value == 0.05

    def test_unknown_industry_falls_back_to_general(self):
        result = royalty_rate_benchmark("patent", "unknown_industry")
        assert result.assumptions["recommended_range"] == (0.02, 0.08)

    def test_invalid_ip_type_raises(self):
        with pytest.raises(ValueError):
            royalty_rate_benchmark("invalid_type", "pharmaceutical")

    def test_with_user_comparables(self):
        comparables = [
            {"rate": 0.06, "source": "Deal A"},
            {"rate": 0.09, "source": "Deal B"},
            {"rate": 0.12, "source": "Deal C"},
        ]
        result = royalty_rate_benchmark("patent", "pharmaceutical", comparable_database=comparables)
        assert result.assumptions["recommended_range"][0] <= 0.06
        assert result.assumptions["recommended_range"][1] >= 0.12

    def test_returns_source(self):
        result = royalty_rate_benchmark("patent", "pharmaceutical")
        assert "source" in result.assumptions

    def test_returns_steps(self):
        result = royalty_rate_benchmark("patent", "pharmaceutical")
        assert len(result.steps) >= 4


class TestAdjustRoyaltyRate:
    def test_single_factor(self):
        result = adjust_royalty_rate(0.05, {"profit_margin": 1.2})
        assert result.value == pytest.approx(0.06, rel=1e-4)

    def test_multiple_factors(self):
        result = adjust_royalty_rate(0.05, {"profit_margin": 1.2, "exclusivity": 1.3})
        assert result.value == pytest.approx(0.078, rel=1e-4)

    def test_all_factors(self):
        result = adjust_royalty_rate(
            0.05,
            {
                "profit_margin": 1.2,
                "exclusivity": 1.3,
                "market_conditions": 1.1,
                "term": 0.9,
                "geographic_scope": 1.2,
            },
        )
        expected = 0.05 * 1.2 * 1.3 * 1.1 * 0.9 * 1.2
        assert result.value == pytest.approx(expected, rel=1e-4)

    def test_no_factors(self):
        result = adjust_royalty_rate(0.05, {})
        assert result.value == 0.05

    def test_invalid_factor_raises(self):
        with pytest.raises(ValueError, match="Unknown adjustment factors"):
            adjust_royalty_rate(0.05, {"invalid_factor": 1.0})

    def test_zero_base_rate_raises(self):
        with pytest.raises(ValueError):
            adjust_royalty_rate(0, {"profit_margin": 1.0})

    def test_base_rate_over_one_raises(self):
        with pytest.raises(ValueError):
            adjust_royalty_rate(1.5, {"profit_margin": 1.0})


class TestTwentyFivePercentRule:
    def test_basic(self):
        result = twenty_five_percent_rule(10_000_000)
        assert result.value == 2_500_000.0

    def test_with_attribution(self):
        result = twenty_five_percent_rule(10_000_000, profit_attribution_to_ip=0.8)
        assert result.value == 2_000_000.0

    def test_full_attribution_default(self):
        result = twenty_five_percent_rule(10_000_000, profit_attribution_to_ip=1.0)
        assert result.value == 2_500_000.0

    def test_zero_attribution(self):
        result = twenty_five_percent_rule(10_000_000, profit_attribution_to_ip=0)
        assert result.value == 0.0

    def test_negative_profit_raises(self):
        with pytest.raises(ValueError):
            twenty_five_percent_rule(-10_000_000)

    def test_attribution_over_one_raises(self):
        with pytest.raises(ValueError):
            twenty_five_percent_rule(10_000_000, profit_attribution_to_ip=1.5)

    def test_returns_steps(self):
        result = twenty_five_percent_rule(10_000_000, 0.8)
        assert len(result.steps) >= 4
        assert "25%" in result.method


class TestProfitSplitMethod:
    """Tests for profit_split_method function."""

    def test_happy_path_basic(self):
        result = profit_split_method(0.40, 0.60, 10_000_000)
        assert result["value"] == pytest.approx(4_000_000.0, rel=0.01)
        assert "Profit Split" in result["method"]

    def test_happy_path_equal_split(self):
        result = profit_split_method(0.50, 0.50, 10_000_000)
        assert result["value"] == pytest.approx(5_000_000.0, rel=0.01)

    def test_happy_path_licensor_dominant(self):
        result = profit_split_method(0.80, 0.20, 10_000_000)
        assert result["value"] == pytest.approx(8_000_000.0, rel=0.01)

    def test_happy_path_licensee_dominant(self):
        result = profit_split_method(0.20, 0.80, 10_000_000)
        assert result["value"] == pytest.approx(2_000_000.0, rel=0.01)

    def test_error_zero_licensor(self):
        with pytest.raises(ValueError):
            profit_split_method(0, 0.60, 10_000_000)

    def test_error_zero_licensee(self):
        with pytest.raises(ValueError):
            profit_split_method(0.40, 0, 10_000_000)

    def test_error_zero_profit(self):
        with pytest.raises(ValueError):
            profit_split_method(0.40, 0.60, 0)

    def test_error_over_one_contribution(self):
        with pytest.raises(ValueError):
            profit_split_method(1.5, 0.60, 10_000_000)

    def test_returns_shares(self):
        result = profit_split_method(0.40, 0.60, 10_000_000)
        assert "licensor_share_pct" in result["assumptions"]
        assert "licensee_share_pct" in result["assumptions"]


class TestAnalyticalMethodValuation:
    """Tests for analytical_method_valuation function."""

    def test_happy_path_basic(self):
        result = analytical_method_valuation(
            advantage_margin=0.05,
            volume=10_000_000,
            discount_rate=0.12,
            economic_life=7,
        )
        assert result["value"] > 0
        assert "Analytical Method" in result["method"]

    def test_happy_path_single_year(self):
        result = analytical_method_valuation(
            advantage_margin=0.10,
            volume=5_000_000,
            discount_rate=0.10,
            economic_life=1,
        )
        assert result["value"] == pytest.approx(500_000 / 1.10, rel=0.01)

    def test_happy_path_high_margin(self):
        result = analytical_method_valuation(
            advantage_margin=0.15,
            volume=20_000_000,
            discount_rate=0.10,
            economic_life=10,
        )
        assert result["value"] > 0

    def test_error_zero_margin(self):
        with pytest.raises(ValueError):
            analytical_method_valuation(0, 10_000_000, 0.12, 7)

    def test_error_zero_volume(self):
        with pytest.raises(ValueError):
            analytical_method_valuation(0.05, 0, 0.12, 7)

    def test_error_zero_discount_rate(self):
        with pytest.raises(ValueError):
            analytical_method_valuation(0.05, 10_000_000, 0, 7)

    def test_error_zero_economic_life(self):
        with pytest.raises(ValueError):
            analytical_method_valuation(0.05, 10_000_000, 0.12, 0)

    def test_returns_implied_royalty_rate(self):
        result = analytical_method_valuation(
            advantage_margin=0.05,
            volume=10_000_000,
            discount_rate=0.12,
            economic_life=7,
        )
        assert "implied_royalty_rate" in result["assumptions"]
        assert result["assumptions"]["implied_royalty_rate"] > 0
