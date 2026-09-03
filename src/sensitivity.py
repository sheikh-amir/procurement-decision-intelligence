"""Model-risk sensitivity analysis for governed score weights."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import WEIGHTS


def weight_sensitivity(
    scored: pd.DataFrame,
    top_n: int = 100,
    simulations: int = 75,
    concentration: float = 180.0,
    seed: int = 42,
) -> dict:
    """Stress-test queue stability under plausible perturbations of business weights.

    Weights are sampled from a Dirichlet distribution centered on the governed
    baseline weights. The output measures overlap with the baseline top-N queue.
    This is a model-risk diagnostic, not statistical confidence in misconduct.
    """
    if scored.empty:
        return {
            "top_n": 0,
            "simulations": simulations,
            "mean_top_queue_jaccard": 1.0,
            "p10_top_queue_jaccard": 1.0,
            "min_top_queue_jaccard": 1.0,
        }

    signals = list(WEIGHTS)
    n = min(top_n, len(scored))
    X = scored[signals].fillna(0).clip(0, 1).to_numpy(dtype=float)
    baseline_w = np.array([WEIGHTS[s] for s in signals], dtype=float)
    baseline_w = baseline_w / baseline_w.sum()
    baseline_scores = X @ baseline_w
    base_idx = set(np.argpartition(baseline_scores, -n)[-n:].tolist())

    alpha = np.maximum(baseline_w * concentration, 0.1)
    rng = np.random.default_rng(seed)
    overlaps = []
    for _ in range(simulations):
        w = rng.dirichlet(alpha)
        sim_scores = X @ w
        sim_idx = set(np.argpartition(sim_scores, -n)[-n:].tolist())
        union = len(base_idx | sim_idx)
        overlaps.append(len(base_idx & sim_idx) / union if union else 1.0)

    arr = np.asarray(overlaps)
    return {
        "top_n": int(n),
        "simulations": int(simulations),
        "mean_top_queue_jaccard": round(float(arr.mean()), 4),
        "p10_top_queue_jaccard": round(float(np.quantile(arr, 0.10)), 4),
        "min_top_queue_jaccard": round(float(arr.min()), 4),
        "interpretation": "Higher overlap means the top queue is less sensitive to reasonable weight changes.",
    }
