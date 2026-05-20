"""Tests for transfer pricing (TASK-040)."""

import pytest

from src.advanced.transfer_pricing import cup_transfer_price


class TestCUPTransferPrice:
    def test_within_range(self):
        result = cup_transfer_price(100, [90, 95, 100, 105, 110])
        assert result.assumptions["within_range"] is True
        assert result.assumptions["arms_length_range"] == (95.0, 105.0)

    def test_outside_range(self):
        result = cup_transfer_price(200, [90, 95, 100, 105, 110])
        assert result.assumptions["within_range"] is False

    def test_below_range(self):
        result = cup_transfer_price(80, [90, 95, 100, 105, 110])
        assert result.assumptions["within_range"] is False

    def test_median_value(self):
        result = cup_transfer_price(100, [90, 95, 100, 105, 110])
        assert result.value == 100.0

    def test_even_number_of_comparables(self):
        result = cup_transfer_price(50, [40, 45, 55, 60])
        q1, q3 = result.assumptions["arms_length_range"]
        assert q1 <= 45
        assert q3 >= 55

    def test_too_few_comparables_raises(self):
        with pytest.raises(ValueError, match="At least 3"):
            cup_transfer_price(100, [90, 110])

    def test_negative_price_raises(self):
        with pytest.raises(ValueError):
            cup_transfer_price(100, [90, -5, 100, 105, 110])

    def test_zero_controlled_price_raises(self):
        with pytest.raises(ValueError):
            cup_transfer_price(0, [90, 95, 100])

    def test_returns_iqr(self):
        result = cup_transfer_price(100, [90, 95, 100, 105, 110])
        assert result.assumptions["iqr"] == 10.0

    def test_returns_steps(self):
        result = cup_transfer_price(100, [90, 95, 100, 105, 110])
        assert len(result.steps) >= 6


class TestCurrencyAdjustedDiscountRate:
    def test_basic(self):
        from src.core.discount_rates import currency_adjusted_discount_rate as car
        result = car(0.10, 0.02, 0.03)
        assert result.value == 0.15

    def test_zero_premiums(self):
        from src.core.discount_rates import currency_adjusted_discount_rate as car
        result = car(0.12, 0, 0)
        assert result.value == 0.12

    def test_negative_currency_premium_raises(self):
        from src.core.discount_rates import currency_adjusted_discount_rate as car
        with pytest.raises(ValueError):
            car(0.10, -0.01, 0.02)

    def test_negative_country_premium_raises(self):
        from src.core.discount_rates import currency_adjusted_discount_rate as car
        with pytest.raises(ValueError):
            car(0.10, 0.02, -0.01)

    def test_zero_base_rate(self):
        from src.core.discount_rates import currency_adjusted_discount_rate as car
        result = car(0, 0.02, 0.03)
        assert result.value == 0.05

    def test_base_rate_over_one(self):
        from src.core.discount_rates import currency_adjusted_discount_rate as car
        result = car(1.5, 0.02, 0.03)
        assert result.value == 1.55

    def test_returns_steps(self):
        from src.core.discount_rates import currency_adjusted_discount_rate as car
        result = car(0.10, 0.02, 0.03)
        assert len(result.steps) >= 3
        assert "Currency" in result.method
