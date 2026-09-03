"""Management scenario optimization and workload risk simulation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import DEFAULT_REVIEW_MINUTES, DEFAULT_WEEKLY_REVIEW_HOURS


def threshold_frontier(
    scored: pd.DataFrame,
    thresholds=range(35, 96),
    review_minutes: float = DEFAULT_REVIEW_MINUTES,
) -> pd.DataFrame:
    """Build a Pareto-style decision frontier for score thresholds."""
    total_proxy_risk = max(float(scored["priority_score"].sum()), 1.0)
    rows = []
    for threshold in thresholds:
        q = scored[scored["priority_score"] >= threshold]
        proxy_risk = float(q["priority_score"].sum())
        rows.append(
            {
                "score_threshold": threshold,
                "alerts": len(q),
                "review_hours": round(len(q) * review_minutes / 60, 2),
                "proxy_risk_coverage_pct": round(100 * proxy_risk / total_proxy_risk, 2),
                "avg_selected_score": round(float(q["priority_score"].mean()), 2) if len(q) else 0.0,
                "multi_family_rate_pct": round(100 * float((q.get("signal_family_count", 0) >= 3).mean()), 2)
                if len(q)
                else 0.0,
            }
        )
    return pd.DataFrame(rows)


def recommend_threshold(
    scored: pd.DataFrame,
    weekly_review_hours: float = DEFAULT_WEEKLY_REVIEW_HOURS,
    review_minutes: float = DEFAULT_REVIEW_MINUTES,
    min_multi_family_rate_pct: float = 40.0,
) -> dict:
    """Recommend the lowest threshold satisfying capacity and evidence-diversity constraints."""
    frontier = threshold_frontier(scored, review_minutes=review_minutes)
    feasible = frontier[
        (frontier["review_hours"] <= weekly_review_hours)
        & (frontier["multi_family_rate_pct"] >= min_multi_family_rate_pct)
    ]
    if feasible.empty:
        feasible = frontier[frontier["review_hours"] <= weekly_review_hours]
    if feasible.empty:
        row = frontier.iloc[-1]
    else:
        # Lowest feasible threshold preserves the broadest proxy-risk coverage.
        row = feasible.sort_values("score_threshold").iloc[0]
    return row.to_dict()


def monte_carlo_backlog(
    alerts: int,
    analysts: int = 2,
    hours_per_analyst: float = 20,
    median_review_minutes: float = DEFAULT_REVIEW_MINUTES,
    simulations: int = 3000,
    seed: int = 42,
) -> dict:
    """Estimate probability that a queue exceeds weekly review capacity.

    Review times are sampled from a log-normal distribution to represent a long
    tail of complex cases rather than assuming every alert takes exactly 12 minutes.
    """
    if alerts <= 0:
        return {"backlog_probability_pct": 0.0, "p50_hours": 0.0, "p90_hours": 0.0, "capacity_hours": analysts * hours_per_analyst}

    rng = np.random.default_rng(seed)
    sigma = 0.55
    mu = np.log(max(median_review_minutes, 0.1))
    sampled_minutes = rng.lognormal(mean=mu, sigma=sigma, size=(simulations, alerts)).sum(axis=1)
    hours = sampled_minutes / 60
    capacity = analysts * hours_per_analyst
    return {
        "backlog_probability_pct": round(100 * float((hours > capacity).mean()), 2),
        "p50_hours": round(float(np.quantile(hours, 0.50)), 2),
        "p90_hours": round(float(np.quantile(hours, 0.90)), 2),
        "capacity_hours": round(float(capacity), 2),
    }
