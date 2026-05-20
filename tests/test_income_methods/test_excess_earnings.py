"""Tests for Excess Earnings income methods."""

import pytest

from intangible_valuation.income_methods.excess_earnings import (
    contributory_asset_charges,
    mpeem,
    single_period_excess_earnings,
)


class TestContributoryAssetCharges:
    """Tests for contributory_asset_charges function."""

    def test_basic_cac(self):
        """Basic CAC calculation."""
        assets = [
            {"type": "working_capital", "value": 500_000, "return_rate": 0.08},
            {"type": "fixed_assets", "value": 1_000_000, "return_rate": 0.10},
        ]
        result = contributory_asset_charges(assets)
        assert result["total_cac"] == pytest.approx(140_000.0, rel=1e-6)
        assert len(result["breakdown"]) == 2

    def test_single_asset(self):
        """Single asset CAC."""
        assets = [{"type": "net_working_capital", "value": 200_000, "return_rate": 0.06}]
        result = contributory_asset_charges(assets)
        assert result["total_cac"] == pytest.approx(12_000.0, rel=1e-6)

    def test_empty_assets_raises(self):
        """Empty assets list should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            contributory_asset_charges([])

    def test_invalid_asset_raises(self):
        """Invalid asset data should raise ValueError."""
        with pytest.raises(ValueError):
            contributory_asset_charges([{"type": "x", "value": -100, "return_rate": 0.10}])

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        assets = [{"type": "wc", "value": 100_000, "return_rate": 0.08}]
        result = contributory_asset_charges(assets)
        for key in ("total_cac", "breakdown", "method", "formula_reference", "steps", "assumptions"):
            assert key in result


class TestMPEEM:
    """Tests for mpeem function."""

    def test_basic_five_year(self):
        """Basic 5-year MPEEM with TAB."""
        cfs = [200_000, 220_000, 240_000, 260_000, 280_000]
        cacs = [
            {"total_cac": 50_000},
            {"total_cac": 52_000},
            {"total_cac": 54_000},
            {"total_cac": 56_000},
            {"total_cac": 58_000},
        ]
        result = mpeem(cfs, cacs, discount_rate=0.12, tax_rate=0.25)
        assert result["value"] > 0
        assert result["method"] == "Multi-Period Excess Earnings Method (MPEEM)"
        assert result["tab_factor"] > 1.0

    def test_tab_disabled(self):
        """TAB disabled should return pv_before_tab as value."""
        cfs = [200_000, 220_000]
        cacs = [{"total_cac": 50_000}, {"total_cac": 52_000}]
        result = mpeem(cfs, cacs, discount_rate=0.12, tax_rate=0.25, tab_enabled=False)
        assert result["value"] == pytest.approx(result["pv_before_tab"], rel=1e-6)

    def test_mismatched_lengths_raises(self):
        """Mismatched lengths should raise ValueError."""
        cfs = [200_000, 220_000]
        cacs = [{"total_cac": 50_000}]
        with pytest.raises(ValueError, match="must match"):
            mpeem(cfs, cacs, discount_rate=0.12, tax_rate=0.25)

    def test_empty_projections_raises(self):
        """Empty cash flow projections should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            mpeem([], [], discount_rate=0.12, tax_rate=0.25)

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        cfs = [200_000]
        cacs = [{"total_cac": 50_000}]
        result = mpeem(cfs, cacs, discount_rate=0.12, tax_rate=0.25)
        for key in ("value", "method", "formula_reference", "pv_before_tab", "tab_factor", "steps", "assumptions"):
            assert key in result


class TestSinglePeriodExcessEarnings:
    """Tests for single_period_excess_earnings function."""

    def test_basic_calculation(self):
        """Basic single-period calculation."""
        result = single_period_excess_earnings(
            normalized_earnings=500_000,
            contributory_asset_charges=[{"total_cac": 140_000}],
            capitalization_rate=0.12,
        )
        assert result["value"] == pytest.approx(3_000_000.0, rel=1e-6)
        assert result["excess_earnings"] == pytest.approx(360_000.0, rel=1e-6)
        assert result["total_cac"] == pytest.approx(140_000.0, rel=1e-6)

    def test_multiple_cacs(self):
        """Multiple CAC entries should sum correctly."""
        result = single_period_excess_earnings(
            normalized_earnings=500_000,
            contributory_asset_charges=[
                {"total_cac": 40_000},
                {"total_cac": 100_000},
            ],
            capitalization_rate=0.10,
        )
        assert result["total_cac"] == pytest.approx(140_000.0, rel=1e-6)
        assert result["value"] == pytest.approx(3_600_000.0, rel=1e-6)

    def test_empty_cacs_raises(self):
        """Empty CAC list should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            single_period_excess_earnings(
                normalized_earnings=500_000,
                contributory_asset_charges=[],
                capitalization_rate=0.12,
            )

    def test_negative_excess_raises(self):
        """Negative excess earnings should raise ValueError."""
        with pytest.raises(ValueError, match="Excess earnings must be positive"):
            single_period_excess_earnings(
                normalized_earnings=100_000,
                contributory_asset_charges=[{"total_cac": 200_000}],
                capitalization_rate=0.12,
            )

    def test_zero_cap_rate_raises(self):
        """Zero capitalization rate should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            single_period_excess_earnings(
                normalized_earnings=500_000,
                contributory_asset_charges=[{"total_cac": 140_000}],
                capitalization_rate=0,
            )

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        result = single_period_excess_earnings(
            normalized_earnings=500_000,
            contributory_asset_charges=[{"total_cac": 140_000}],
            capitalization_rate=0.12,
        )
        for key in ("value", "method", "formula_reference", "total_cac", "excess_earnings", "steps", "assumptions"):
            assert key in result
