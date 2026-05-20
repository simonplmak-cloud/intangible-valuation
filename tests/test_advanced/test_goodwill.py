"""Tests for goodwill calculation (TASK-034)."""

import pytest

from intangible_valuation.advanced.goodwill import goodwill


class TestGoodwill:
    def test_basic_goodwill(self):
        result = goodwill(100_000_000, 75_000_000)
        assert result.value == 25_000_000.0
        assert result.method == "Goodwill (Residual Method)"
        assert "Ch 10.1" in result.formula_reference

    def test_zero_goodwill(self):
        result = goodwill(50_000_000, 50_000_000)
        assert result.value == 0.0

    def test_small_goodwill(self):
        result = goodwill(1_000_001, 1_000_000)
        assert result.value == 1.0

    def test_bargain_purchase_raises(self):
        with pytest.raises(ValueError, match="Bargain purchase"):
            goodwill(50_000_000, 60_000_000)

    def test_negative_purchase_price_raises(self):
        with pytest.raises(ValueError):
            goodwill(-100, 50)

    def test_zero_purchase_price_raises(self):
        with pytest.raises(ValueError):
            goodwill(0, 50)

    def test_negative_net_assets_raises(self):
        with pytest.raises(ValueError):
            goodwill(100, -10)

    def test_returns_steps(self):
        result = goodwill(100, 75)
        assert len(result.steps) >= 4
        assert any(s.get("description") == "Goodwill" for s in result.steps)

    def test_returns_assumptions(self):
        result = goodwill(100, 75)
        assert result.assumptions["purchase_price"] == 100
        assert result.assumptions["fair_value_net_identifiable_assets"] == 75

    def test_large_acquisition(self):
        result = goodwill(5_000_000_000, 3_200_000_000)
        assert result.value == 1_800_000_000.0

    def test_book_example_ppa(self):
        result = goodwill(100_000_000, 75_000_000)
        assert result.value == 25_000_000.0
