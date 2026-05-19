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
from typing import Any, Callable, Literal

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
            f"valuation_fn correctly computes the valuation for given inputs",
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

        if node.type == "decision":
            best_edge = max(
                edges_from[current],
                key=lambda e: node_values.get(e.to, 0) - e.cost,
            )
            current = best_edge.to
            path.append(current)
        elif node.type == "chance":
            best_edge = max(
                edges_from[current],
                key=lambda e: node_values.get(e.to, 0) - e.cost,
            )
            current = best_edge.to
            path.append(current)
        else:
            break

    return path
