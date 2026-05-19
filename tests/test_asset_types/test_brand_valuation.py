"""Tests for brand valuation module."""

import pytest

from src.asset_types.brand_valuation import trademark_valuation


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
                brand_strength_index=1.5,
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
