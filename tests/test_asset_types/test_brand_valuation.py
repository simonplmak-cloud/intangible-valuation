"""Tests for brand valuation module."""

import pytest

from intangible_valuation.asset_types.brand_valuation import (
    brand_royalty_rate_from_comparables,
    brand_strength_index,
    interbrand_brand_valuation,
    trademark_valuation,
)


class TestTrademarkValuation:
    """Tests for trademark_valuation function."""

    def test_happy_path_rfr(self):
        result = trademark_valuation(
            revenue=1000000,
            profit_margin=0.20,
            brand_strength_index=0.75,
            discount_rate=0.10,
            useful_life=10,
            method="relief_from_royalty",
        )
        assert result["value"] > 0
        assert "Relief-from-Royalty" in result["method"]
        assert len(result["steps"]) > 0
        assert "brand_strength_index" in result["assumptions"]

    def test_happy_path_excess_earnings(self):
        result = trademark_valuation(
            revenue=1000000,
            profit_margin=0.20,
            brand_strength_index=0.75,
            discount_rate=0.10,
            useful_life=10,
            method="excess_earnings",
        )
        assert result["value"] > 0
        assert "Excess Earnings" in result["method"]

    def test_happy_path_default_method(self):
        result = trademark_valuation(
            revenue=500000,
            profit_margin=0.15,
            brand_strength_index=0.60,
            discount_rate=0.08,
            useful_life=5,
        )
        assert result["value"] > 0
        assert "Relief-from-Royalty" in result["method"]

    def test_happy_path_strong_brand(self):
        result = trademark_valuation(
            revenue=5000000,
            profit_margin=0.30,
            brand_strength_index=0.95,
            discount_rate=0.08,
            useful_life=15,
            method="relief_from_royalty",
        )
        assert result["value"] > 0

    def test_happy_path_weak_brand(self):
        result = trademark_valuation(
            revenue=500000,
            profit_margin=0.10,
            brand_strength_index=0.10,
            discount_rate=0.12,
            useful_life=5,
            method="relief_from_royalty",
        )
        assert result["value"] >= 0

    def test_happy_path_zero_revenue(self):
        result = trademark_valuation(
            revenue=0,
            profit_margin=0.20,
            brand_strength_index=0.50,
            discount_rate=0.10,
            useful_life=5,
        )
        assert result["value"] == 0.0

    def test_error_negative_revenue(self):
        with pytest.raises(ValueError):
            trademark_valuation(
                revenue=-100000,
                profit_margin=0.20,
                brand_strength_index=0.50,
                discount_rate=0.10,
                useful_life=5,
            )

    def test_error_invalid_brand_strength(self):
        with pytest.raises(ValueError):
            trademark_valuation(
                revenue=100000,
                profit_margin=0.20,
                brand_strength_index=150,
                discount_rate=0.10,
                useful_life=5,
            )

    def test_error_invalid_profit_margin(self):
        with pytest.raises(ValueError):
            trademark_valuation(
                revenue=100000,
                profit_margin=-0.10,
                brand_strength_index=0.50,
                discount_rate=0.10,
                useful_life=5,
            )

    def test_error_unknown_method(self):
        with pytest.raises(ValueError):
            trademark_valuation(
                revenue=100000,
                profit_margin=0.20,
                brand_strength_index=0.50,
                discount_rate=0.10,
                useful_life=5,
                method="unknown_method",
            )

    def test_error_zero_useful_life(self):
        with pytest.raises(ValueError):
            trademark_valuation(
                revenue=100000,
                profit_margin=0.20,
                brand_strength_index=0.50,
                discount_rate=0.10,
                useful_life=0,
            )

    def test_error_negative_discount_rate(self):
        with pytest.raises(ValueError):
            trademark_valuation(
                revenue=100000,
                profit_margin=0.20,
                brand_strength_index=0.50,
                discount_rate=-0.01,
                useful_life=5,
            )


class TestBrandStrengthIndex:
    """Tests for brand_strength_index function."""

    def test_happy_path_strong_brand(self):
        result = brand_strength_index(0.9, 0.8, 0.85, 0.9, 0.7)
        assert result["value"] > 70
        assert result["value"] <= 100
        assert "Composite" in result["method"]

    def test_happy_path_weak_brand(self):
        result = brand_strength_index(0.2, 0.1, 0.15, 0.2, 0.1)
        assert result["value"] < 30
        assert result["value"] >= 0

    def test_happy_path_all_max(self):
        result = brand_strength_index(1.0, 1.0, 1.0, 1.0, 1.0)
        assert result["value"] == pytest.approx(100.0, rel=1e-9)

    def test_happy_path_all_min(self):
        result = brand_strength_index(0.0, 0.0, 0.0, 0.0, 0.0)
        assert result["value"] == 0.0

    def test_happy_path_balanced(self):
        result = brand_strength_index(0.5, 0.5, 0.5, 0.5, 0.5)
        assert result["value"] == pytest.approx(50.0, rel=1e-9)

    def test_error_invalid_stability(self):
        with pytest.raises(ValueError):
            brand_strength_index(1.5, 0.5, 0.5, 0.5, 0.5)

    def test_error_negative_market_share(self):
        with pytest.raises(ValueError):
            brand_strength_index(0.5, -0.1, 0.5, 0.5, 0.5)

    def test_returns_rating(self):
        result = brand_strength_index(0.9, 0.8, 0.85, 0.9, 0.7)
        assert "rating" in result["assumptions"]
        assert result["assumptions"]["rating"] in ("Excellent", "Strong", "Moderate", "Weak", "Very Weak")

    def test_returns_weights(self):
        result = brand_strength_index(0.5, 0.5, 0.5, 0.5, 0.5)
        assert "weights" in result["assumptions"]
        assert result["assumptions"]["weights"]["revenue_stability"] == 0.25


class TestInterbrandBrandValuation:
    """Tests for interbrand_brand_valuation function."""

    def test_happy_path_basic(self):
        result = interbrand_brand_valuation(
            brand_earnings=50_000_000,
            role_of_brand_index=0.60,
            brand_strength_score=75,
            discount_rate=0.08,
        )
        assert result["value"] > 0
        assert "Interbrand" in result["method"]

    def test_happy_path_strong_brand(self):
        result = interbrand_brand_valuation(
            brand_earnings=100_000_000,
            role_of_brand_index=0.80,
            brand_strength_score=90,
            discount_rate=0.06,
        )
        assert result["value"] > 0

    def test_happy_path_weak_brand(self):
        result = interbrand_brand_valuation(
            brand_earnings=10_000_000,
            role_of_brand_index=0.20,
            brand_strength_score=25,
            discount_rate=0.15,
        )
        assert result["value"] >= 0

    def test_error_zero_earnings(self):
        with pytest.raises(ValueError):
            interbrand_brand_valuation(
                brand_earnings=0,
                role_of_brand_index=0.50,
                brand_strength_score=50,
                discount_rate=0.10,
            )

    def test_error_invalid_robi(self):
        with pytest.raises(ValueError):
            interbrand_brand_valuation(
                brand_earnings=50_000_000,
                role_of_brand_index=1.5,
                brand_strength_score=50,
                discount_rate=0.10,
            )

    def test_error_invalid_strength_score(self):
        with pytest.raises(ValueError):
            interbrand_brand_valuation(
                brand_earnings=50_000_000,
                role_of_brand_index=0.50,
                brand_strength_score=150,
                discount_rate=0.10,
            )

    def test_error_zero_discount_rate(self):
        with pytest.raises(ValueError):
            interbrand_brand_valuation(
                brand_earnings=50_000_000,
                role_of_brand_index=0.50,
                brand_strength_score=50,
                discount_rate=0,
            )

    def test_returns_brand_multiple(self):
        result = interbrand_brand_valuation(
            brand_earnings=50_000_000,
            role_of_brand_index=0.60,
            brand_strength_score=75,
            discount_rate=0.08,
        )
        assert "brand_multiple" in result["assumptions"]


class TestBrandRoyaltyRateFromComparables:
    """Tests for brand_royalty_rate_from_comparables function."""

    def test_happy_path_basic(self):
        rates = [0.03, 0.04, 0.05, 0.06, 0.04]
        result = brand_royalty_rate_from_comparables(rates)
        assert result["value"] > 0
        assert "Comparable" in result["method"]

    def test_happy_path_with_adjustment(self):
        rates = [0.03, 0.04, 0.05, 0.06, 0.04]
        result = brand_royalty_rate_from_comparables(rates, 0.10)
        assert result["value"] > 0.04

    def test_happy_path_negative_adjustment(self):
        rates = [0.03, 0.04, 0.05, 0.06, 0.04]
        result = brand_royalty_rate_from_comparables(rates, -0.10)
        assert result["value"] < 0.05

    def test_happy_path_single_comparable(self):
        rates = [0.05]
        result = brand_royalty_rate_from_comparables(rates)
        assert result["value"] == 0.05

    def test_happy_path_floor_at_zero(self):
        rates = [0.03, 0.04, 0.05]
        result = brand_royalty_rate_from_comparables(rates, -0.5)
        assert result["value"] >= 0

    def test_error_empty_rates(self):
        with pytest.raises(ValueError):
            brand_royalty_rate_from_comparables([])

    def test_error_adjustment_out_of_range(self):
        with pytest.raises(ValueError):
            brand_royalty_rate_from_comparables([0.05], 0.6)

    def test_returns_statistics(self):
        rates = [0.03, 0.04, 0.05, 0.06, 0.04]
        result = brand_royalty_rate_from_comparables(rates)
        assert "min_rate" in result["assumptions"]
        assert "max_rate" in result["assumptions"]
        assert "median_rate" in result["assumptions"]
