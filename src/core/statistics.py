"""Statistical functions for valuation analysis.

Implements Monte Carlo simulation and decision tree analysis
from Chapter 6 and Appendix B of the Ascent Partners textbook.

All functions return structured dicts with:
    - value: The primary result
    - method: The calculation method used
    - formula_reference: Reference to the methodology
    - steps: Step-by-step calculation breakdown
    - assumptions: List of assumptions made during calculation
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable
from typing import Any, Literal, cast

from pydantic import BaseModel, Field, field_validator


class DistributionInput(BaseModel):
    """Validated input distribution for Monte Carlo simulation."""

    name: str = Field(min_length=1)
    distribution: Literal["normal", "uniform", "triangular"]
    params: dict[str, float]

    @field_validator("params")
    @classmethod
    def validate_params(cls, v: dict[str, float], info) -> dict[str, float]:
        dist = info.data.get("distribution")
        if dist == "normal":
            if "mean" not in v or "std" not in v:
                raise ValueError("Normal distribution requires 'mean' and 'std' params")
            if v["std"] <= 0:
                raise ValueError("Normal distribution 'std' must be positive")
        elif dist == "uniform":
            if "low" not in v or "high" not in v:
                raise ValueError("Uniform distribution requires 'low' and 'high' params")
            if v["low"] >= v["high"]:
                raise ValueError("Uniform 'low' must be less than 'high'")
        elif dist == "triangular":
            if "low" not in v or "high" not in v or "mode" not in v:
                raise ValueError("Triangular distribution requires 'low', 'high', and 'mode' params")
            if not (v["low"] <= v["mode"] <= v["high"]):
                raise ValueError("Triangular: low <= mode <= high required")
        return v


class TreeNode(BaseModel):
    """Validated node in a decision tree."""

    id: str = Field(min_length=1)
    type: Literal["decision", "chance", "terminal"]
    label: str = Field(min_length=1)
    value: float = 0.0


class TreeEdge(BaseModel):
    """Validated edge in a decision tree."""

    from_node: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    probability: float = 0.0
    cost: float = 0.0

    @field_validator("probability")
    @classmethod
    def validate_probability(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("Probability must be between 0 and 1")
        return v


class DecisionTreeInput(BaseModel):
    """Validated decision tree input."""

    nodes: list[TreeNode]
    edges: list[TreeEdge]

    @field_validator("nodes")
    @classmethod
    def validate_nodes(cls, v: list[TreeNode]) -> list[TreeNode]:
        if not v:
            raise ValueError("Decision tree must have at least one node")
        node_ids = {node.id for node in v}
        if len(node_ids) != len(v):
            raise ValueError("All node IDs must be unique")
        return v

    @field_validator("edges")
    @classmethod
    def validate_edges(cls, v: list[TreeEdge], info) -> list[TreeEdge]:
        if not v:
            raise ValueError("Decision tree must have at least one edge")
        node_ids = {node.id for node in info.data.get("nodes", [])}
        for edge in v:
            if edge.from_node not in node_ids:
                raise ValueError(f"Edge references non-existent node: {edge.from_node}")
            if edge.to not in node_ids:
                raise ValueError(f"Edge references non-existent node: {edge.to}")
        return v


def monte_carlo_valuation(
    valuation_fn: Callable[..., float],
    input_distributions: list[dict[str, Any]],
    iterations: int = 10000,
    seed: int | None = None,
) -> dict[str, Any]:
    """Perform Monte Carlo simulation for valuation uncertainty analysis.

    Runs the valuation function multiple times with randomly sampled inputs
    from specified distributions to produce a probability distribution of
    valuation outcomes.

    Parameters:
        valuation_fn: Function that takes named parameters and returns a float value
        input_distributions: List of dicts with keys:
            - name: Parameter name passed to valuation_fn
            - distribution: "normal", "uniform", or "triangular"
            - params: Distribution-specific parameters
                - normal: {"mean": float, "std": float}
                - uniform: {"low": float, "high": float}
                - triangular: {"low": float, "high": float, "mode": float}
        iterations: Number of simulation runs (default 10000)
        seed: Random seed for reproducibility (default None)

    Returns:
        Dict with keys:
            - mean: Mean of simulated valuations
            - median: Median of simulated valuations
            - std: Standard deviation
            - percentile_5: 5th percentile
            - percentile_25: 25th percentile
            - percentile_75: 75th percentile
            - percentile_95: 95th percentile
            - min: Minimum value
            - max: Maximum value
            - method: "Monte Carlo Simulation"
            - formula_reference: Reference description
            - iterations: Number of iterations performed
            - seed: Random seed used
            - steps: Description of the simulation
            - assumptions: List of assumptions

    Raises:
        ValueError: If input_distributions is empty or iterations < 1

    Book Reference:
        Chapter 6, Section 6.2 — Monte Carlo Simulation for Valuation
        Appendix B — Statistical Methods in Valuation
    """
    if not input_distributions:
        raise ValueError("input_distributions must contain at least one distribution")
    if iterations < 1:
        raise ValueError("iterations must be at least 1")

    validated_dists = [DistributionInput(**d) for d in input_distributions]

    if seed is not None:
        random.seed(seed)

    results: list[float] = []

    for _ in range(iterations):
        inputs = {}
        for dist in validated_dists:
            if dist.distribution == "normal":
                inputs[dist.name] = random.gauss(dist.params["mean"], dist.params["std"])
            elif dist.distribution == "uniform":
                inputs[dist.name] = random.uniform(dist.params["low"], dist.params["high"])
            elif dist.distribution == "triangular":
                inputs[dist.name] = _random_triangular(
                    dist.params["low"], dist.params["high"], dist.params["mode"],
                )

        try:
            result = valuation_fn(**inputs)
            results.append(result)
        except (TypeError, ValueError) as e:
            raise ValueError(f"valuation_fn failed with sampled inputs: {e}") from e

    results.sort()
    n = len(results)

    mean = sum(results) / n
    variance = sum((x - mean) ** 2 for x in results) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(variance)

    def percentile(p: float) -> float:
        idx = int(p / 100 * (n - 1))
        return results[idx]

    distribution_descriptions = []
    for dist in validated_dists:
        if dist.distribution == "normal":
            distribution_descriptions.append(
                f"{dist.name} ~ N({dist.params['mean']}, {dist.params['std']})"
            )
        elif dist.distribution == "uniform":
            distribution_descriptions.append(
                f"{dist.name} ~ U({dist.params['low']}, {dist.params['high']})"
            )
        elif dist.distribution == "triangular":
            distribution_descriptions.append(
                f"{dist.name} ~ Triangular({dist.params['low']}, {dist.params['mode']}, {dist.params['high']})"
            )

    return {
        "mean": round(mean, 2),
        "median": round(percentile(50), 2),
        "std": round(std, 2),
        "percentile_5": round(percentile(5), 2),
        "percentile_25": round(percentile(25), 2),
        "percentile_75": round(percentile(75), 2),
        "percentile_95": round(percentile(95), 2),
        "min": round(results[0], 2),
        "max": round(results[-1], 2),
        "method": "Monte Carlo Simulation",
        "formula_reference": "Monte Carlo: Sample from input distributions, compute valuation, aggregate statistics",
        "iterations": iterations,
        "seed": seed,
        "steps": [
            f"Number of iterations: {iterations}",
            f"Input distributions: {', '.join(distribution_descriptions)}",
            f"Random seed: {seed if seed is not None else 'None (non-deterministic)'}",
            f"Mean result: ${mean:,.2f}",
            f"Standard deviation: ${std:,.2f}",
            f"5th-95th percentile range: ${percentile(5):,.2f} - ${percentile(95):,.2f}",
        ],
        "assumptions": [
            "Input distributions accurately represent parameter uncertainty",
            "Input parameters are independent (no correlation modeled)",
            "valuation_fn correctly computes the valuation for given inputs",
            f"{iterations} iterations provide sufficient convergence",
        ],
    }


def _random_triangular(low: float, high: float, mode: float) -> float:
    """Generate a random number from a triangular distribution.

    Uses inverse transform sampling.
    """
    u = random.random()
    c = (mode - low) / (high - low)

    if u < c:
        return low + math.sqrt(u * (high - low) * (mode - low))
    else:
        return high - math.sqrt((1 - u) * (high - low) * (high - mode))


def decision_tree_valuation(
    tree: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate a decision tree to compute expected values at each node.

    The tree consists of three node types:
    - decision: A choice point where the optimal branch is selected (max value)
    - chance: A probabilistic branch where expected value is computed
    - terminal: An endpoint with a fixed value

    Parameters:
        tree: Dict with keys:
            - nodes: List of node dicts with keys: id, type, label, value
            - edges: List of edge dicts with keys: from, to, probability, cost

    Returns:
        Dict with keys:
            - expected_value: Expected value at the root node
            - node_values: Dict mapping node ID to expected value
            - optimal_path: List of node IDs representing the optimal path
            - method: "Decision Tree Analysis"
            - formula_reference: Reference description
            - steps: Step-by-step evaluation
            - assumptions: List of assumptions

    Raises:
        ValueError: If tree structure is invalid

    Book Reference:
        Chapter 6, Section 6.3 — Decision Tree Analysis for Valuation
        Used for valuing assets with contingent outcomes (e.g., R&D projects, litigation)
    """
    validated = DecisionTreeInput(**tree)

    nodes = {node.id: node for node in validated.nodes}
    edges_from: dict[str, list[TreeEdge]] = {}
    for edge in validated.edges:
        if edge.from_node not in edges_from:
            edges_from[edge.from_node] = []
        edges_from[edge.from_node].append(edge)

    node_values: dict[str, float] = {}
    evaluation_steps: list[str] = []

    def evaluate(node_id: str) -> float:
        node = nodes[node_id]

        if node.type == "terminal":
            node_values[node_id] = node.value
            evaluation_steps.append(f"Node '{node.label}' (terminal): value = ${node.value:,.2f}")
            return node.value

        if node_id not in edges_from or not edges_from[node_id]:
            node_values[node_id] = node.value
            evaluation_steps.append(f"Node '{node.label}' (leaf): value = ${node.value:,.2f}")
            return node.value

        if node.type == "decision":
            branch_values = []
            for edge in edges_from[node_id]:
                child_value = evaluate(edge.to)
                net_value = child_value - edge.cost
                branch_values.append((edge.to, net_value, edge))

            best = max(branch_values, key=lambda x: x[1])
            node_values[node_id] = best[1]
            evaluation_steps.append(
                f"Node '{node.label}' (decision): choose branch to '{nodes[best[0]].label}' "
                f"(value = ${best[1]:,.2f})"
            )
            return best[1]

        elif node.type == "chance":
            total_prob = sum(edge.probability for edge in edges_from[node_id])
            if not math.isclose(total_prob, 1.0, abs_tol=1e-6):
                raise ValueError(
                    f"Probabilities for chance node '{node.label}' sum to {total_prob:.4f}, expected 1.0"
                )

            expected = 0.0
            for edge in edges_from[node_id]:
                child_value = evaluate(edge.to)
                net_value = child_value - edge.cost
                contribution = net_value * edge.probability
                expected += contribution
                evaluation_steps.append(
                    f"  Branch to '{nodes[edge.to].label}': "
                    f"P={edge.probability:.2%}, value=${net_value:,.2f}, "
                    f"contribution=${contribution:,.2f}"
                )

            node_values[node_id] = expected
            evaluation_steps.append(
                f"Node '{node.label}' (chance): expected value = ${expected:,.2f}"
            )
            return expected

        else:
            raise ValueError(f"Unknown node type: {node.type}")

    root_id = validated.nodes[0].id
    root_value = evaluate(root_id)

    optimal_path = _find_optimal_path(root_id, nodes, edges_from, node_values)

    return {
        "expected_value": round(root_value, 2),
        "node_values": {k: round(v, 2) for k, v in node_values.items()},
        "optimal_path": optimal_path,
        "method": "Decision Tree Analysis",
        "formula_reference": "Backward induction: EV(chance) = sum(P_i * V_i), EV(decision) = max(branches)",
        "steps": evaluation_steps,
        "assumptions": [
            "All probabilities at chance nodes sum to 1.0",
            "Decision nodes select the branch with maximum expected value",
            "Values are risk-neutral (no risk adjustment beyond discounting)",
            "Tree is acyclic (no loops)",
        ],
    }


def _find_optimal_path(
    node_id: str,
    nodes: dict[str, TreeNode],
    edges_from: dict[str, list[TreeEdge]],
    node_values: dict[str, float],
) -> list[str]:
    """Find the optimal path through the decision tree."""
    path = [node_id]
    current = node_id

    while current in edges_from and edges_from[current]:
        node = nodes[current]

        if node.type == "decision" or node.type == "chance":
            best_edge = max(
                edges_from[current],
                key=lambda e: node_values.get(e.to, 0) - e.cost,
            )
            current = best_edge.to
            path.append(current)
        else:
            break

    return path


def monte_carlo_with_correlation(
    valuation_fn: Callable[..., float],
    distributions: list[dict[str, Any]],
    correlation_matrix: list[list[float]],
    iterations: int = 10000,
    seed: int | None = None,
) -> dict[str, Any]:
    """Perform Monte Carlo simulation with correlated input variables.

    Uses Cholesky decomposition of the correlation matrix to generate correlated
    random variables from independent standard normal draws. This captures the
    realistic interdependencies between input parameters.

    Formula:
        Z_correlated = L * Z_independent
        where L = Cholesky decomposition of correlation matrix
        X_i = mu_i + sigma_i * Z_correlated_i

    Parameters:
        valuation_fn: Function that takes named parameters and returns a float value
        distributions: List of dicts with keys:
            - name: Parameter name passed to valuation_fn
            - distribution: "normal", "uniform", or "triangular"
            - params: Distribution-specific parameters
                - normal: {"mean": float, "std": float}
                - uniform: {"low": float, "high": float}
                - triangular: {"low": float, "high": float, "mode": float}
        correlation_matrix: NxN symmetric positive-definite matrix (list of lists)
        iterations: Number of simulation runs (default 10000)
        seed: Random seed for reproducibility (default None)

    Returns:
        Dict with keys:
            - mean: Mean of simulated valuations
            - median: Median of simulated valuations
            - std: Standard deviation
            - percentile_5: 5th percentile
            - percentile_25: 25th percentile
            - percentile_75: 75th percentile
            - percentile_95: 95th percentile
            - min: Minimum value
            - max: Maximum value
            - method: "Monte Carlo with Correlation"
            - formula_reference: Reference description
            - iterations: Number of iterations performed
            - seed: Random seed used
            - correlation_used: Whether correlation was applied
            - steps: Description of the simulation
            - assumptions: List of assumptions

    Raises:
        ValueError: If distributions is empty, correlation matrix is invalid, or iterations < 1

    Book Reference:
        Chapter 6, Section 6.2 — Monte Carlo with Correlated Inputs
        Iman & Conover (1982), "A Distribution-Free Approach to Inducing Rank Correlation"
    """
    if not distributions:
        raise ValueError("distributions must contain at least one distribution")
    if iterations < 1:
        raise ValueError("iterations must be at least 1")

    n_vars = len(distributions)
    if len(correlation_matrix) != n_vars:
        raise ValueError(
            f"Correlation matrix must be {n_vars}x{n_vars}, "
            f"got {len(correlation_matrix)} rows"
        )
    for i, row in enumerate(correlation_matrix):
        if len(row) != n_vars:
            raise ValueError(
                f"Correlation matrix row {i} has {len(row)} elements, expected {n_vars}"
            )

    validated_dists = [DistributionInput(**d) for d in distributions]

    if seed is not None:
        random.seed(seed)

    cholesky = _cholesky_decomposition(correlation_matrix)

    results: list[float] = []

    for _ in range(iterations):
        independent_normals = [random.gauss(0, 1) for _ in range(n_vars)]
        correlated_normals = _matrix_vector_multiply(cholesky, independent_normals)

        inputs = {}
        for i, dist in enumerate(validated_dists):
            z = correlated_normals[i]
            if dist.distribution == "normal":
                inputs[dist.name] = dist.params["mean"] + dist.params["std"] * z
            elif dist.distribution == "uniform":
                u = _norm_cdf(z)
                low = dist.params["low"]
                high = dist.params["high"]
                inputs[dist.name] = low + u * (high - low)
            elif dist.distribution == "triangular":
                u = _norm_cdf(z)
                inputs[dist.name] = _triangular_from_uniform(
                    dist.params["low"], dist.params["high"], dist.params["mode"], u,
                )

        try:
            result = valuation_fn(**inputs)
            results.append(result)
        except (TypeError, ValueError) as e:
            raise ValueError(f"valuation_fn failed with sampled inputs: {e}") from e

    results.sort()
    n = len(results)

    mean = sum(results) / n
    variance = sum((x - mean) ** 2 for x in results) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(variance)

    def percentile(p: float) -> float:
        idx = int(p / 100 * (n - 1))
        return results[idx]

    return {
        "mean": round(mean, 2),
        "median": round(percentile(50), 2),
        "std": round(std, 2),
        "percentile_5": round(percentile(5), 2),
        "percentile_25": round(percentile(25), 2),
        "percentile_75": round(percentile(75), 2),
        "percentile_95": round(percentile(95), 2),
        "min": round(results[0], 2),
        "max": round(results[-1], 2),
        "method": "Monte Carlo with Correlation",
        "formula_reference": "Monte Carlo with Cholesky decomposition for correlated inputs",
        "iterations": iterations,
        "seed": seed,
        "correlation_used": True,
        "steps": [
            f"Number of iterations: {iterations}",
            f"Number of input variables: {n_vars}",
            f"Correlation matrix: {n_vars}x{n_vars} (Cholesky decomposition applied)",
            f"Random seed: {seed if seed is not None else 'None (non-deterministic)'}",
            f"Mean result: ${mean:,.2f}",
            f"Standard deviation: ${std:,.2f}",
            f"5th-95th percentile range: ${percentile(5):,.2f} - ${percentile(95):,.2f}",
        ],
        "assumptions": [
            "Input distributions accurately represent parameter uncertainty",
            "Correlation matrix is positive-definite and correctly specified",
            "Correlations are modeled using Cholesky decomposition of normal variables",
            "valuation_fn correctly computes the valuation for given inputs",
            f"{iterations} iterations provide sufficient convergence",
        ],
    }


def sensitivity_tornado(
    function_name: str,
    base_params: dict[str, Any],
    parameter_ranges: dict[str, list[float]],
) -> dict[str, Any]:
    """Generate tornado diagram data for multi-parameter sensitivity analysis.

    Evaluates the impact of varying each parameter across its range while holding
    others at base values. Results are sorted by impact (largest to smallest),
    producing the classic tornado diagram ordering.

    Parameters:
        function_name: Name of the function to analyze (same as sensitivity_analysis)
        base_params: Base case parameter values for all parameters
        parameter_ranges: Dict mapping parameter names to lists of test values

    Returns:
        Dict with keys:
            - base_value: Value at base case parameters
            - tornado: List of {"parameter": str, "low_value": float, "high_value": float,
              "low_result": float, "high_result": float, "impact": float}
              sorted by impact (descending)
            - method: "Tornado Sensitivity Analysis"
            - formula_reference: Reference description
            - steps: Description of the analysis
            - assumptions: List of assumptions

    Raises:
        ValueError: If parameter_ranges is empty or function is unsupported

    Example:
        >>> result = sensitivity_tornado(
        ...     function_name="present_value",
        ...     base_params={"future_value": 1_000_000, "discount_rate": 0.10, "periods": 10},
        ...     parameter_ranges={
        ...         "discount_rate": [0.08, 0.10, 0.12],
        ...         "periods": [8, 10, 12],
        ...     },
        ... )

    Book Reference:
        Appendix A, Section A.3 — Tornado Diagram Sensitivity Analysis
        Used to identify the most impactful input variables on valuation
    """
    if not parameter_ranges:
        raise ValueError("parameter_ranges must contain at least one parameter")

    from src.utils.formulas import sensitivity_analysis

    base_value = _call_function(function_name, base_params)

    tornado_data = []

    for param_name, param_range in parameter_ranges.items():
        if len(param_range) < 2:
            raise ValueError(f"Parameter '{param_name}' range must have at least 2 values")

        sa_result = sensitivity_analysis(
            function_name=function_name,
            parameter_name=param_name,
            parameter_range=param_range,
            fixed_parameters={k: v for k, v in base_params.items() if k != param_name},
        )

        valid_results = [r for r in sa_result["results"] if r["result"] is not None]
        if not valid_results:
            continue

        low_result = valid_results[0]["result"]
        high_result = valid_results[-1]["result"]
        impact = abs(high_result - low_result)

        tornado_data.append({
            "parameter": param_name,
            "low_value": param_range[0],
            "high_value": param_range[-1],
            "low_result": round(low_result, 2),
            "high_result": round(high_result, 2),
            "impact": round(impact, 2),
        })

    tornado_data.sort(key=lambda x: x["impact"], reverse=True)

    return {
        "base_value": round(base_value, 2),
        "tornado": tornado_data,
        "method": "Tornado Sensitivity Analysis",
        "formula_reference": "One-at-a-time sensitivity analysis, sorted by impact magnitude",
        "steps": [
            f"Function: {function_name}",
            f"Base case value: ${base_value:,.2f}",
            f"Parameters analyzed: {list(parameter_ranges.keys())}",
            "Results sorted by impact (largest to smallest)",
        ],
        "assumptions": [
            "All other parameters held constant at base values",
            "Parameter ranges represent realistic bounds of uncertainty",
            "Linear interpolation between tested points is reasonable",
            "Impact is measured as absolute difference between high and low results",
        ],
    }


def scenario_analysis(
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate probability-weighted expected value across multiple scenarios.

    Each scenario defines a set of parameter values and an associated probability.
    The function evaluates the valuation for each scenario and computes the
    probability-weighted expected value.

    Parameters:
        scenarios: List of dicts with keys:
            - name: Scenario name (str)
            - probability: Probability of scenario (float, 0-1)
            - params: Dict of parameter values for the valuation function
            - function_name: Name of the valuation function to call

    Returns:
        Dict with keys:
            - expected_value: Probability-weighted expected value
            - scenarios: List of {"name": str, "probability": float, "value": float, "contribution": float}
            - method: "Scenario Analysis"
            - formula_reference: Reference description
            - steps: Step-by-step calculation
            - assumptions: List of assumptions

    Raises:
        ValueError: If scenarios list is empty, probabilities don't sum to 1, or params invalid

    Example:
        >>> result = scenario_analysis([
        ...     {
        ...         "name": "Base", "probability": 0.6,
        ...         "params": {"revenue": 1_000_000, "discount_rate": 0.10},
        ...         "function_name": "perpetuity_pv",
        ...     },
        ...     {
        ...         "name": "Upside", "probability": 0.2,
        ...         "params": {"revenue": 1_500_000, "discount_rate": 0.09},
        ...         "function_name": "perpetuity_pv",
        ...     },
        ...     {
        ...         "name": "Downside", "probability": 0.2,
        ...         "params": {"revenue": 700_000, "discount_rate": 0.12},
        ...         "function_name": "perpetuity_pv",
        ...     },
        ... ])

    Book Reference:
        Chapter 6, Section 6.3 — Scenario Analysis for Valuation
        Used for valuing assets with discrete outcome possibilities
    """
    if not scenarios:
        raise ValueError("scenarios list must contain at least one scenario")

    total_probability = sum(s["probability"] for s in scenarios)
    if not math.isclose(total_probability, 1.0, abs_tol=1e-6):
        raise ValueError(
            f"Scenario probabilities sum to {total_probability:.4f}, expected 1.0"
        )

    scenario_results = []
    expected_value = 0.0
    steps = []

    for scenario in scenarios:
        if "name" not in scenario:
            raise ValueError("Each scenario must have a 'name' key")
        if "probability" not in scenario:
            raise ValueError(f"Scenario '{scenario.get('name', 'unknown')}' must have a 'probability' key")
        if "params" not in scenario:
            raise ValueError(f"Scenario '{scenario['name']}' must have a 'params' key")
        if "function_name" not in scenario:
            raise ValueError(f"Scenario '{scenario['name']}' must have a 'function_name' key")

        prob = scenario["probability"]
        if prob < 0 or prob > 1:
            raise ValueError(f"Scenario '{scenario['name']}' probability must be between 0 and 1")

        value = _call_function(scenario["function_name"], scenario["params"])
        contribution = value * prob
        expected_value += contribution

        scenario_results.append({
            "name": scenario["name"],
            "probability": prob,
            "value": round(value, 2),
            "contribution": round(contribution, 2),
        })

        steps.append(
            f"Scenario '{scenario['name']}': P={prob:.2%}, "
            f"Value=${value:,.2f}, Contribution=${contribution:,.2f}"
        )

    steps.append(f"Expected Value = ${expected_value:,.2f}")

    return {
        "expected_value": round(expected_value, 2),
        "scenarios": scenario_results,
        "method": "Scenario Analysis",
        "formula_reference": "EV = sum(Probability_i * Value_i) for all scenarios",
        "steps": steps,
        "assumptions": [
            "Scenario probabilities are mutually exclusive and exhaustive",
            "Probabilities sum to 1.0 (100%)",
            "Each scenario's parameter set produces a valid valuation",
            "Expected value represents the risk-neutral valuation",
        ],
    }


def _call_function(function_name: str, params: dict[str, Any]) -> float:
    """Call a valuation function by name and return its numeric value."""
    function_map: dict[str, Callable] = {
        "present_value": _call_present_value,
        "future_value": _call_future_value,
        "annuity_pv": _call_annuity_pv,
        "perpetuity_pv": _call_perpetuity_pv,
        "growing_annuity_pv": _call_growing_annuity_pv,
        "terminal_value": _call_terminal_value,
        "build_up_discount_rate": _call_build_up,
        "capm_discount_rate": _call_capm,
        "wacc": _call_wacc,
    }

    if function_name not in function_map:
        raise ValueError(
            f"Unsupported function: {function_name}. "
            f"Supported: {', '.join(function_map.keys())}"
        )

    return cast(float, function_map[function_name](**params))


def _call_present_value(**kwargs: Any) -> float:
    from src.core.time_value import present_value
    return present_value(**kwargs).value


def _call_future_value(**kwargs: Any) -> float:
    from src.core.time_value import future_value
    return future_value(**kwargs).value


def _call_annuity_pv(**kwargs: Any) -> float:
    from src.core.time_value import annuity_pv
    return annuity_pv(**kwargs).value


def _call_perpetuity_pv(**kwargs: Any) -> float:
    from src.core.time_value import perpetuity_pv
    return perpetuity_pv(**kwargs).value


def _call_growing_annuity_pv(**kwargs: Any) -> float:
    from src.core.time_value import growing_annuity_pv
    return growing_annuity_pv(**kwargs).value


def _call_terminal_value(**kwargs: Any) -> float:
    from src.core.time_value import terminal_value
    return terminal_value(**kwargs).value


def _call_build_up(**kwargs: Any) -> float:
    from src.core.discount_rates import build_up_discount_rate
    return build_up_discount_rate(**kwargs).value


def _call_capm(**kwargs: Any) -> float:
    from src.core.discount_rates import capm_discount_rate
    return capm_discount_rate(**kwargs).value


def _call_wacc(**kwargs: Any) -> float:
    from src.core.discount_rates import wacc
    return wacc(**kwargs).value


def _cholesky_decomposition(matrix: list[list[float]]) -> list[list[float]]:
    """Compute the Cholesky decomposition of a positive-definite matrix.

    Returns lower triangular matrix L such that A = L * L^T.
    """
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1):
            s = sum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                val = matrix[i][i] - s
                if val <= 0:
                    raise ValueError(
                        "Correlation matrix is not positive-definite. "
                        "Ensure the matrix is symmetric and positive-definite."
                    )
                lower[i][j] = math.sqrt(val)
            else:
                if math.isclose(lower[j][j], 0.0, abs_tol=1e-12):
                    raise ValueError("Correlation matrix has zero diagonal element")
                lower[i][j] = (matrix[i][j] - s) / lower[j][j]

    return lower


def _matrix_vector_multiply(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Multiply a matrix by a vector."""
    n = len(matrix)
    result = []
    for i in range(n):
        val = sum(matrix[i][j] * vector[j] for j in range(len(vector)))
        result.append(val)
    return result


def _norm_cdf(x: float) -> float:
    """Approximation of the standard normal cumulative distribution function."""
    from src.core.discount_rates import _norm_cdf as _ncdf
    return _ncdf(x)


def _triangular_from_uniform(low: float, high: float, mode: float, u: float) -> float:
    """Generate triangular distribution value from uniform random variable."""
    c = (mode - low) / (high - low)
    if u < c:
        return low + math.sqrt(u * (high - low) * (mode - low))
    else:
        return high - math.sqrt((1 - u) * (high - low) * (high - mode))
