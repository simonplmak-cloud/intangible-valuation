"""Tests for Relief from Royalty income method."""

import pytest

from src.income_methods.relief_from_royalty import relief_from_royalty


class TestReliefFromRoyalty:
    """Tests for relief_from_royalty function."""

    def test_basic_five_year_projection(self):
        """Basic 5-year projection with TAB enabled."""
        result = relief_from_royalty(
            revenue_projections=[1_000_000, 1_100_000, 1_200_000, 1_300_000, 1_400_000],
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=5,
        )
        assert result["value"] > 0
        assert result["method"] == "Relief from Royalty"
        assert result["tab_factor"] > 1.0
        assert result["pv_before_tab"] > 0

    def test_tab_disabled(self):
        """TAB disabled should return pv_before_tab as value."""
        result = relief_from_royalty(
            revenue_projections=[1_000_000, 1_100_000, 1_200_000],
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=3,
            tab_enabled=False,
        )
        assert result["value"] == pytest.approx(result["pv_before_tab"], rel=1e-6)
        assert result["tab_factor"] == 1.0

    def test_zero_tax_rate_no_tab(self):
        """Zero tax rate should result in TAB factor of 1.0."""
        result = relief_from_royalty(
            revenue_projections=[1_000_000, 1_000_000],
            royalty_rate=0.05,
            discount_rate=0.10,
            tax_rate=0.0,
            useful_life=2,
            tab_enabled=True,
        )
        assert result["tab_factor"] == 1.0

    def test_mismatched_length_raises(self):
        """Mismatched revenue_projections length and useful_life should raise."""
        with pytest.raises(ValueError, match="must match"):
            relief_from_royalty(
                revenue_projections=[1_000_000, 1_100_000],
                royalty_rate=0.05,
                discount_rate=0.12,
                tax_rate=0.25,
                useful_life=3,
            )

    def test_empty_projections_raises(self):
        """Empty revenue_projections should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            relief_from_royalty(
                revenue_projections=[],
                royalty_rate=0.05,
                discount_rate=0.12,
                tax_rate=0.25,
                useful_life=0,
            )

    def test_invalid_royalty_rate_raises(self):
        """Royalty rate out of range should raise ValueError."""
        with pytest.raises(ValueError, match="between 0 and 1"):
            relief_from_royalty(
                revenue_projections=[1_000_000],
                royalty_rate=0,
                discount_rate=0.12,
                tax_rate=0.25,
                useful_life=1,
            )

    def test_negative_discount_rate_raises(self):
        """Negative discount rate should raise ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            relief_from_royalty(
                revenue_projections=[1_000_000],
                royalty_rate=0.05,
                discount_rate=-0.01,
                tax_rate=0.25,
                useful_life=1,
            )

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        result = relief_from_royalty(
            revenue_projections=[1_000_000],
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=1,
        )
        for key in ("value", "method", "formula_reference", "pv_before_tab", "tab_factor", "steps", "assumptions"):
            assert key in result

    def test_steps_not_empty(self):
        """Steps list should not be empty."""
        result = relief_from_royalty(
            revenue_projections=[1_000_000],
            royalty_rate=0.05,
            discount_rate=0.12,
            tax_rate=0.25,
            useful_life=1,
        )
        assert len(result["steps"]) > 0
