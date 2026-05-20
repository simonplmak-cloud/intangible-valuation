"""Tests for Monte Carlo simulation (TASK-042)."""

import pytest

from intangible_valuation.advanced.monte_carlo import monte_carlo_sensitivity
from intangible_valuation.core.statistics import monte_carlo_valuation


def simple_valuation(revenue, margin):
    return revenue * margin


class TestMonteCarloValuation:
    def test_basic_simulation(self):
        result = monte_carlo_valuation(
            valuation_fn=simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1000, "std": 100}},
                {"name": "margin", "distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            ],
            iterations=5000,
            seed=42,
        )
        assert result["mean"] > 0
        assert result["method"] == "Monte Carlo Simulation"

    def test_statistics_present(self):
        result = monte_carlo_valuation(
            valuation_fn=simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1000, "std": 100}},
                {"name": "margin", "distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            ],
            iterations=5000,
            seed=42,
        )
        assert "mean" in result
        assert "std" in result
        assert "median" in result
        assert "percentile_5" in result
        assert "percentile_95" in result

    def test_reproducible_with_seed(self):
        r1 = monte_carlo_valuation(
            valuation_fn=simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1000, "std": 100}},
                {"name": "margin", "distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            ],
            iterations=5000,
            seed=42,
        )
        r2 = monte_carlo_valuation(
            valuation_fn=simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "normal", "params": {"mean": 1000, "std": 100}},
                {"name": "margin", "distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            ],
            iterations=5000,
            seed=42,
        )
        assert r1["mean"] == r2["mean"]

    def test_too_few_iterations_raises(self):
        with pytest.raises(ValueError):
            dists = [{"name": "x", "distribution": "normal", "params": {"mean": 0, "std": 1}}]
            monte_carlo_valuation(simple_valuation, dists, iterations=0)

    def test_empty_distributions_raises(self):
        with pytest.raises(ValueError, match="at least one distribution"):
            monte_carlo_valuation(simple_valuation, [], iterations=5000)

    def test_unsupported_distribution_raises(self):
        with pytest.raises(ValueError):
            monte_carlo_valuation(
                simple_valuation,
                [{"name": "x", "distribution": "exponential", "params": {"scale": 1}}],
                iterations=5000,
            )

    def test_triangular_distribution(self):
        result = monte_carlo_valuation(
            valuation_fn=simple_valuation,
            input_distributions=[
                {"name": "revenue", "distribution": "triangular", "params": {"low": 800, "mode": 1000, "high": 1200}},
                {"name": "margin", "distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            ],
            iterations=5000,
            seed=42,
        )
        assert result["mean"] > 0


def simple_valuation_dict(params):
    return params["revenue"] * params["margin"]


class TestMonteCarloSensitivity:
    def test_basic_sensitivity(self):
        result = monte_carlo_sensitivity(
            valuation_fn=simple_valuation_dict,
            base_params={"revenue": 1000, "margin": 0.2, "fixed_cost": 100},
            distributions={
                "revenue": {"distribution": "normal", "params": {"mean": 1000, "std": 100}},
                "margin": {"distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            },
            iterations=5000,
            seed=42,
        )
        assert result["value"] > 0
        assert "sensitivity_ranking" in result

    def test_sensitivity_ranking(self):
        result = monte_carlo_sensitivity(
            valuation_fn=simple_valuation_dict,
            base_params={"revenue": 1000, "margin": 0.2},
            distributions={
                "revenue": {"distribution": "normal", "params": {"mean": 1000, "std": 100}},
                "margin": {"distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            },
            iterations=5000,
            seed=42,
        )
        ranking = result["sensitivity_ranking"]
        assert len(ranking) == 2
        assert all("correlation" in r for r in ranking)
        assert all("parameter" in r for r in ranking)

    def test_ranking_sorted_by_abs_correlation(self):
        result = monte_carlo_sensitivity(
            valuation_fn=simple_valuation_dict,
            base_params={"revenue": 1000, "margin": 0.2},
            distributions={
                "revenue": {"distribution": "normal", "params": {"mean": 1000, "std": 100}},
                "margin": {"distribution": "uniform", "params": {"low": 0.1, "high": 0.3}},
            },
            iterations=5000,
            seed=42,
        )
        ranking = result["sensitivity_ranking"]
        assert ranking[0]["abs_correlation"] >= ranking[1]["abs_correlation"]

    def test_empty_distributions_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            monte_carlo_sensitivity(simple_valuation_dict, {"revenue": 1000}, {}, iterations=5000)

    def test_too_few_iterations_raises(self):
        with pytest.raises(ValueError, match=">= 1000"):
            monte_carlo_sensitivity(
                valuation_fn=simple_valuation_dict,
                base_params={"revenue": 1000},
                distributions={"revenue": {"distribution": "normal", "params": {"mean": 1000, "std": 100}}},
                iterations=500,
            )

    def test_unsupported_distribution_raises(self):
        with pytest.raises(ValueError, match="Unsupported distribution"):
            monte_carlo_sensitivity(
                valuation_fn=simple_valuation_dict,
                base_params={"revenue": 1000},
                distributions={"revenue": {"distribution": "exponential", "params": {"scale": 1}}},
                iterations=5000,
            )

    def test_reproducible_with_seed(self):
        r1 = monte_carlo_sensitivity(
            valuation_fn=simple_valuation_dict,
            base_params={"revenue": 1000, "margin": 0.2},
            distributions={
                "revenue": {"distribution": "normal", "params": {"mean": 1000, "std": 100}},
            },
            iterations=5000,
            seed=42,
        )
        r2 = monte_carlo_sensitivity(
            valuation_fn=simple_valuation_dict,
            base_params={"revenue": 1000, "margin": 0.2},
            distributions={
                "revenue": {"distribution": "normal", "params": {"mean": 1000, "std": 100}},
            },
            iterations=5000,
            seed=42,
        )
        assert r1["value"] == r2["value"]
