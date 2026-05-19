"""Tests for statistical functions: Monte Carlo simulation and decision tree analysis."""

import math
import pytest

from src.core.statistics import decision_tree_valuation, monte_carlo_valuation


class TestMonteCarloValuation:
    """Test monte_carlo_valuation function."""

    def _simple_valuation(self, revenue, discount_rate):
        """Simple perpetuity valuation: value = revenue / discount_rate."""
        return revenue / discount_rate

    def test_basic_monte_carlo(self):
        """Monte Carlo with normal distributions."""
        result = monte_carlo_valuation(
            valuation_fn=self._simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1_000_000, "std": 100_000}},
                {"name": "discount_rate", "distribution": "normal", "params": {"mean": 0.10, "std": 0.01}},
            ],
            iterations=1000,
            seed=42,
        )

        assert "mean" in result
        assert "median" in result
        assert "std" in result
        assert "percentile_5" in result
        assert "percentile_25" in result
        assert "percentile_75" in result
        assert "percentile_95" in result
        assert "min" in result
        assert "max" in result
        assert result["method"] == "Monte Carlo Simulation"
        assert result["iterations"] == 1000
        assert result["seed"] == 42

    def test_mean_near_expected(self):
        """Mean should be near the deterministic result."""
        result = monte_carlo_valuation(
            valuation_fn=self._simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1_000_000, "std": 10_000}},
                {"name": "discount_rate", "distribution": "normal", "params": {"mean": 0.10, "std": 0.001}},
            ],
            iterations=5000,
            seed=42,
        )
        expected = 1_000_000 / 0.10  # 10,000,000
        assert math.isclose(result["mean"], expected, rel_tol=0.05)

    def test_uniform_distribution(self):
        """Monte Carlo with uniform distributions."""
        result = monte_carlo_valuation(
            valuation_fn=self._simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "uniform", "params": {"low": 900_000, "high": 1_100_000}},
                {"name": "discount_rate", "distribution": "uniform", "params": {"low": 0.08, "high": 0.12}},
            ],
            iterations=1000,
            seed=42,
        )
        assert result["min"] < result["max"]

    def test_triangular_distribution(self):
        """Monte Carlo with triangular distributions."""
        result = monte_carlo_valuation(
            valuation_fn=self._simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "triangular", "params": {"low": 800_000, "high": 1_200_000, "mode": 1_000_000}},
                {"name": "discount_rate", "distribution": "triangular", "params": {"low": 0.08, "high": 0.12, "mode": 0.10}},
            ],
            iterations=1000,
            seed=42,
        )
        assert result["mean"] > 0

    def test_reproducible_with_seed(self):
        """Same seed should produce same results."""
        result1 = monte_carlo_valuation(
            valuation_fn=self._simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1_000_000, "std": 100_000}},
                {"name": "discount_rate", "distribution": "normal", "params": {"mean": 0.10, "std": 0.01}},
            ],
            iterations=500,
            seed=123,
        )
        result2 = monte_carlo_valuation(
            valuation_fn=self._simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1_000_000, "std": 100_000}},
                {"name": "discount_rate", "distribution": "normal", "params": {"mean": 0.10, "std": 0.01}},
            ],
            iterations=500,
            seed=123,
        )
        assert result1["mean"] == result2["mean"]
        assert result1["percentile_5"] == result2["percentile_5"]

    def test_percentiles_ordered(self):
        """Percentiles should be in ascending order."""
        result = monte_carlo_valuation(
            valuation_fn=self._simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1_000_000, "std": 100_000}},
                {"name": "discount_rate", "distribution": "normal", "params": {"mean": 0.10, "std": 0.01}},
            ],
            iterations=1000,
            seed=42,
        )
        assert result["percentile_5"] <= result["percentile_25"]
        assert result["percentile_25"] <= result["median"]
        assert result["median"] <= result["percentile_75"]
        assert result["percentile_75"] <= result["percentile_95"]

    def test_empty_distributions_raises(self):
        with pytest.raises(ValueError, match="at least one"):
            monte_carlo_valuation(
                valuation_fn=self._simple_valuation,
                input_distributions=[],
            )

    def test_zero_iterations_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            monte_carlo_valuation(
                valuation_fn=self._simple_valuation,
                input_distributions=[
                    {"name": "revenue", "distribution": "normal", "params": {"mean": 100, "std": 10}},
                ],
                iterations=0,
            )

    def test_invalid_distribution_params_raises(self):
        with pytest.raises(ValueError):
            monte_carlo_valuation(
                valuation_fn=self._simple_valuation,
                input_distributions=[
                    {"name": "revenue", "distribution": "normal", "params": {"mean": 100}},
                ],
            )

    def test_invalid_triangular_params_raises(self):
        with pytest.raises(ValueError, match="low <= mode"):
            monte_carlo_valuation(
                valuation_fn=self._simple_valuation,
                input_distributions=[
                    {"name": "x", "distribution": "triangular", "params": {"low": 10, "high": 20, "mode": 30}},
                ],
            )


class TestDecisionTreeValuation:
    """Test decision_tree_valuation function."""

    def test_simple_chance_tree(self):
        """Simple chance node with two outcomes."""
        tree = {
            "nodes": [
                {"id": "root", "type": "chance", "label": "Market Outcome", "value": 0},
                {"id": "success", "type": "terminal", "label": "Success", "value": 1_000_000},
                {"id": "failure", "type": "terminal", "label": "Failure", "value": 0},
            ],
            "edges": [
                {"from": "root", "to": "success", "probability": 0.6, "cost": 0},
                {"from": "root", "to": "failure", "probability": 0.4, "cost": 0},
            ],
        }
        result = decision_tree_valuation(tree)
        assert math.isclose(result["expected_value"], 600_000, abs_tol=1)
        assert result["method"] == "Decision Tree Analysis"

    def test_decision_node(self):
        """Decision node chooses best branch."""
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "Invest?", "value": 0},
                {"id": "invest", "type": "terminal", "label": "Invest", "value": 500_000},
                {"id": "dont_invest", "type": "terminal", "label": "Don't Invest", "value": 0},
            ],
            "edges": [
                {"from": "root", "to": "invest", "probability": 1.0, "cost": 0},
                {"from": "root", "to": "dont_invest", "probability": 1.0, "cost": 0},
            ],
        }
        result = decision_tree_valuation(tree)
        assert math.isclose(result["expected_value"], 500_000, abs_tol=1)
        assert "invest" in result["optimal_path"]

    def test_multi_level_tree(self):
        """Multi-level tree with decision and chance nodes."""
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "Project Choice", "value": 0},
                {"id": "project_a", "type": "chance", "label": "Project A", "value": 0},
                {"id": "project_b", "type": "chance", "label": "Project B", "value": 0},
                {"id": "a_success", "type": "terminal", "label": "A Success", "value": 2_000_000},
                {"id": "a_fail", "type": "terminal", "label": "A Fail", "value": -500_000},
                {"id": "b_success", "type": "terminal", "label": "B Success", "value": 1_000_000},
                {"id": "b_fail", "type": "terminal", "label": "B Fail", "value": 0},
            ],
            "edges": [
                {"from": "root", "to": "project_a", "probability": 1.0, "cost": 0},
                {"from": "root", "to": "project_b", "probability": 1.0, "cost": 0},
                {"from": "project_a", "to": "a_success", "probability": 0.5, "cost": 0},
                {"from": "project_a", "to": "a_fail", "probability": 0.5, "cost": 0},
                {"from": "project_b", "to": "b_success", "probability": 0.8, "cost": 0},
                {"from": "project_b", "to": "b_fail", "probability": 0.2, "cost": 0},
            ],
        }
        result = decision_tree_valuation(tree)
        ev_a = 0.5 * 2_000_000 + 0.5 * (-500_000)  # 750,000
        ev_b = 0.8 * 1_000_000 + 0.2 * 0  # 800,000
        assert math.isclose(result["expected_value"], max(ev_a, ev_b), abs_tol=1)

    def test_tree_with_costs(self):
        """Tree edges with costs."""
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "Invest?", "value": 0},
                {"id": "invest", "type": "terminal", "label": "Invest", "value": 1_200_000},
                {"id": "wait", "type": "terminal", "label": "Wait", "value": 0},
            ],
            "edges": [
                {"from": "root", "to": "invest", "probability": 1.0, "cost": 1_000_000},
                {"from": "root", "to": "wait", "probability": 1.0, "cost": 0},
            ],
        }
        result = decision_tree_valuation(tree)
        assert math.isclose(result["expected_value"], 200_000, abs_tol=1)

    def test_probability_sum_not_one_raises(self):
        with pytest.raises(ValueError, match="sum to"):
            tree = {
                "nodes": [
                    {"id": "root", "type": "chance", "label": "Test", "value": 0},
                    {"id": "a", "type": "terminal", "label": "A", "value": 100},
                    {"id": "b", "type": "terminal", "label": "B", "value": 200},
                ],
                "edges": [
                    {"from": "root", "to": "a", "probability": 0.3, "cost": 0},
                    {"from": "root", "to": "b", "probability": 0.3, "cost": 0},
                ],
            }
            decision_tree_valuation(tree)

    def test_empty_nodes_raises(self):
        with pytest.raises(ValueError, match="at least one node"):
            decision_tree_valuation({"nodes": [], "edges": []})

    def test_empty_edges_raises(self):
        with pytest.raises(ValueError, match="at least one edge"):
            decision_tree_valuation({
                "nodes": [{"id": "root", "type": "terminal", "label": "Root", "value": 100}],
                "edges": [],
            })

    def test_duplicate_node_ids_raises(self):
        with pytest.raises(ValueError, match="unique"):
            decision_tree_valuation({
                "nodes": [
                    {"id": "a", "type": "terminal", "label": "A", "value": 100},
                    {"id": "a", "type": "terminal", "label": "A2", "value": 200},
                ],
                "edges": [],
            })

    def test_invalid_edge_reference_raises(self):
        with pytest.raises(ValueError, match="non-existent"):
            decision_tree_valuation({
                "nodes": [
                    {"id": "root", "type": "chance", "label": "Root", "value": 0},
                    {"id": "leaf", "type": "terminal", "label": "Leaf", "value": 100},
                ],
                "edges": [
                    {"from": "root", "to": "nonexistent", "probability": 1.0, "cost": 0},
                ],
            })

    def test_optimal_path_contains_root(self):
        """Optimal path should start from root node."""
        tree = {
            "nodes": [
                {"id": "root", "type": "decision", "label": "Root", "value": 0},
                {"id": "a", "type": "terminal", "label": "A", "value": 100},
                {"id": "b", "type": "terminal", "label": "B", "value": 200},
            ],
            "edges": [
                {"from": "root", "to": "a", "probability": 1.0, "cost": 0},
                {"from": "root", "to": "b", "probability": 1.0, "cost": 0},
            ],
        }
        result = decision_tree_valuation(tree)
        assert result["optimal_path"][0] == "root"
        assert "b" in result["optimal_path"]
