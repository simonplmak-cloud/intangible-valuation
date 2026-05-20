"""Tests for Incremental Cash Flow income method."""

import pytest

from intangible_valuation.income_methods.incremental_cashflow import incremental_cashflow


class TestIncrementalCashflow:
    """Tests for incremental_cashflow function."""

    def test_basic_five_year(self):
        """Basic 5-year incremental cash flow."""
        result = incremental_cashflow(
            cash_flows_with=[500_000, 550_000, 600_000, 650_000, 700_000],
            cash_flows_without=[400_000, 420_000, 440_000, 460_000, 480_000],
            discount_rate=0.10,
        )
        assert result["value"] > 0
        assert result["method"] == "Incremental Cash Flow"
        assert len(result["incremental_cash_flows"]) == 5

    def test_incremental_values(self):
        """Incremental cash flows should be the difference."""
        result = incremental_cashflow(
            cash_flows_with=[100, 200, 300],
            cash_flows_without=[80, 150, 250],
            discount_rate=0.10,
        )
        assert result["incremental_cash_flows"] == pytest.approx([20, 50, 50], rel=1e-6)

    def test_single_period(self):
        """Single period calculation."""
        result = incremental_cashflow(
            cash_flows_with=[1_000_000],
            cash_flows_without=[800_000],
            discount_rate=0.10,
        )
        expected = 200_000 / 1.10
        assert result["value"] == pytest.approx(expected, rel=1e-6)

    def test_mismatched_lengths_raises(self):
        """Mismatched lengths should raise ValueError."""
        with pytest.raises(ValueError, match="must match"):
            incremental_cashflow(
                cash_flows_with=[100, 200],
                cash_flows_without=[80],
                discount_rate=0.10,
            )

    def test_empty_cash_flows_raises(self):
        """Empty cash_flows_with should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            incremental_cashflow(
                cash_flows_with=[],
                cash_flows_without=[],
                discount_rate=0.10,
            )

    def test_zero_discount_rate_raises(self):
        """Zero discount rate should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            incremental_cashflow(
                cash_flows_with=[100],
                cash_flows_without=[80],
                discount_rate=0,
            )

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        result = incremental_cashflow(
            cash_flows_with=[100],
            cash_flows_without=[80],
            discount_rate=0.10,
        )
        for key in ("value", "method", "formula_reference", "incremental_cash_flows", "steps", "assumptions"):
            assert key in result

    def test_steps_not_empty(self):
        """Steps list should not be empty."""
        result = incremental_cashflow(
            cash_flows_with=[100],
            cash_flows_without=[80],
            discount_rate=0.10,
        )
        assert len(result["steps"]) > 0
