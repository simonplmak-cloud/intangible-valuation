"""Tests for cost approach valuation methods."""

import pytest

from src.approaches.cost_approach import replacement_cost, reproduction_cost


class TestReproductionCost:
    """Tests for reproduction_cost function."""

    def test_book_example_software_650k_40pct_obsolescence(self):
        """Book example: software $650K cost, 40% obsolescence = $390K."""
        result = reproduction_cost(
            development_costs={"labor": 400000, "materials": 150000, "overhead": 100000},
            obsolescence_factors={"functional": 0.40},
        )
        assert result["value"] == pytest.approx(390000.0, rel=1e-6)
        assert result["gross_cost"] == 650000.0
        assert result["total_obsolescence_pct"] == pytest.approx(0.40, rel=1e-6)
        assert result["method"] == "Reproduction Cost"

    def test_no_obsolescence(self):
        """No obsolescence should return gross cost."""
        result = reproduction_cost(
            development_costs={"labor": 100000, "materials": 50000, "overhead": 25000},
        )
        assert result["value"] == pytest.approx(175000.0, rel=1e-6)
        assert result["total_obsolescence_pct"] == 0.0

    def test_multiple_obsolescence_factors(self):
        """Multiple obsolescence factors should combine multiplicatively."""
        result = reproduction_cost(
            development_costs={"labor": 500000},
            obsolescence_factors={"functional": 0.10, "technological": 0.20, "economic": 0.05},
        )
        expected_retention = 0.9 * 0.8 * 0.95
        expected_value = 500000 * expected_retention
        assert result["value"] == pytest.approx(expected_value, rel=1e-6)

    def test_empty_development_costs_raises(self):
        """Empty development_costs should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            reproduction_cost(development_costs={})

    def test_negative_cost_raises(self):
        """Negative cost component should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            reproduction_cost(development_costs={"labor": -100})

    def test_invalid_cost_type_raises(self):
        """Non-numeric cost component should raise ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            reproduction_cost(development_costs={"labor": "not_a_number"})

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        result = reproduction_cost({"labor": 100})
        expected_keys = (
            "value", "method", "formula_reference", "gross_cost",
            "total_obsolescence_pct", "steps", "assumptions",
        )
        for key in expected_keys:
            assert key in result

    def test_steps_not_empty(self):
        """Steps list should not be empty."""
        result = reproduction_cost({"labor": 100})
        assert len(result["steps"]) > 0


class TestReplacementCost:
    """Tests for replacement_cost function."""

    def test_no_obsolescence(self):
        """No obsolescence should return current cost."""
        result = replacement_cost(current_cost=500000)
        assert result["value"] == pytest.approx(500000.0, rel=1e-6)

    def test_with_obsolescence(self):
        """Obsolescence should reduce value."""
        result = replacement_cost(
            current_cost=500000,
            obsolescence_factors={"functional": 0.10, "technological": 0.30},
        )
        expected_retention = 0.9 * 0.7
        assert result["value"] == pytest.approx(500000 * expected_retention, rel=1e-6)

    def test_negative_cost_raises(self):
        """Negative current_cost should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            replacement_cost(current_cost=-100)

    def test_invalid_cost_type_raises(self):
        """Non-numeric current_cost should raise ValueError."""
        with pytest.raises(ValueError, match="must be a number"):
            replacement_cost(current_cost="not_a_number")

    def test_returns_required_keys(self):
        """Result dict should contain all required keys."""
        result = replacement_cost(current_cost=100)
        expected_keys = (
            "value", "method", "formula_reference", "gross_cost",
            "total_obsolescence_pct", "steps", "assumptions",
        )
        for key in expected_keys:
            assert key in result
