"""Monte Carlo simulation for valuation under uncertainty.

Re-exports monte_carlo_valuation from src.core.statistics and adds
monte_carlo_sensitivity for sensitivity analysis on valuation functions.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def monte_carlo_sensitivity(
    valuation_fn: Callable[[dict], float],
    base_params: dict,
    distributions: dict,
    iterations: int = 10000,
    seed: int | None = None,
) -> dict:
    """Run Monte Carlo sensitivity analysis on a valuation function.

    Unlike monte_carlo_valuation which simulates all inputs, this function
    varies only the specified parameters (distributions) while keeping others
    at their base values.

    Args:
        valuation_fn: Callable that takes a dict of parameter names to values.
        base_params: Base/default values for all parameters.
        distributions: Dict mapping parameter names to distribution specs.
            Each spec: {"distribution": str, "params": dict}.
            Supported: "normal", "uniform", "triangular", "lognormal".
        iterations: Number of simulation iterations (1000-100000).
        seed: Random seed for reproducibility.

    Returns:
        Dict with value (mean), method, formula_reference, steps, assumptions,
        statistics, and sensitivity_ranking of parameters by impact.
    """
    if iterations < 1000:
        raise ValueError("iterations must be >= 1000")
    if iterations > 100000:
        raise ValueError("iterations must be <= 100000")
    if not distributions:
        raise ValueError("distributions must not be empty")

    rng = np.random.default_rng(seed)

    samples: dict[str, np.ndarray] = {}
    for name, dist_spec in distributions.items():
        dist = dist_spec["distribution"]
        params = dist_spec["params"]

        if dist == "normal":
            samples[name] = rng.normal(loc=params["mean"], scale=params["std"], size=iterations)
        elif dist == "uniform":
            samples[name] = rng.uniform(low=params["low"], high=params["high"], size=iterations)
        elif dist == "triangular":
            samples[name] = rng.triangular(
                left=params["low"], mode=params["mode"],
                right=params["high"], size=iterations,
            )
        elif dist == "lognormal":
            samples[name] = rng.lognormal(mean=params["mean"], sigma=params["sigma"], size=iterations)
        else:
            raise ValueError(f"Unsupported distribution: {dist}")

    results = np.zeros(iterations)
    for i in range(iterations):
        params = dict(base_params)
        for name in samples:
            params[name] = float(samples[name][i])
        result = valuation_fn(params)
        val = result.value if hasattr(result, "value") else result
        results[i] = float(val)

    mean_val = float(np.mean(results))
    std_val = float(np.std(results))
    p5 = float(np.percentile(results, 5))
    p50 = float(np.percentile(results, 50))
    p95 = float(np.percentile(results, 95))

    sensitivity_ranking: list[dict[str, float | str | None]] = []
    for name in samples:
        corr = float(np.corrcoef(samples[name], results)[0, 1])
        sensitivity_ranking.append({
            "parameter": name,
            "correlation": round(corr, 4),
            "abs_correlation": round(abs(corr), 4),
            "base_value": base_params.get(name),
            "simulated_mean": round(float(np.mean(samples[name])), 4),
            "simulated_std": round(float(np.std(samples[name])), 4),
        })

    sensitivity_ranking.sort(key=lambda x: x["abs_correlation"], reverse=True)  # type: ignore[arg-type,return-value]

    return {
        "value": round(mean_val, 2),
        "method": "Monte Carlo Sensitivity Analysis",
        "formula_reference": "Ch 2.4, Appendix A.11, A.15",
        "steps": [
            {"step": 1, "description": f"Monte Carlo sensitivity analysis with {iterations} iterations"},
            {"step": 2, "description": f"Varying {len(distributions)} parameters"},
            {"step": 3, "description": "Mean valuation result", "value": round(mean_val, 2)},
        ],
        "assumptions": {
            "iterations": iterations,
            "seed": seed,
            "base_params": base_params,
            "distributions": distributions,
        },
        "statistics": {
            "mean": round(mean_val, 2),
            "std": round(std_val, 2),
            "median": round(p50, 2),
            "percentile_5": round(p5, 2),
            "percentile_50": round(p50, 2),
            "percentile_95": round(p95, 2),
            "confidence_interval_90": [round(p5, 2), round(p95, 2)],
            "min": round(float(np.min(results)), 2),
            "max": round(float(np.max(results)), 2),
        },
        "sensitivity_ranking": sensitivity_ranking,
    }
