"""End-to-end governed analytical pipeline.

Two data modes:

    python -m src.pipeline                              # live DC Open Data API
    python -m src.pipeline --sample --out data/sample_run   # offline synthetic fixture

The sample mode exists so the pipeline can be executed and reviewed without
network access. Its output is clearly marked ``synthetic_sample`` so no result
produced offline can be mistaken for a finding about a real organisation.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .config import MODEL_VERSION
from .data import fetch_all_raw, normalize, save_raw
from .engine import add_features, agency_summary, capacity_simulation, score
from .optimizer import monte_carlo_backlog, recommend_threshold, threshold_frontier
from .quality import enforce_quality_gate, quality_report
from .sample import generate
from .sensitivity import weight_sensitivity


def load_raw(use_sample: bool, sample_size: int, seed: int) -> tuple[pd.DataFrame, str]:
    """Return the raw extract and the provenance label that travels with it."""
    if use_sample:
        return generate(n_transactions=sample_size, seed=seed), "synthetic_sample"
    return fetch_all_raw(), "live_dc_open_data"


def run(
    out_dir: Path,
    use_sample: bool = False,
    sample_size: int = 6000,
    seed: int = 7,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    raw, data_mode = load_raw(use_sample, sample_size, seed)
    save_raw(raw, out_dir / "raw_purchase_card.csv")

    dq = quality_report(raw)
    dq.to_csv(out_dir / "data_quality_report.csv", index=False)
    enforce_quality_gate(dq)

    clean = normalize(raw)
    ranked = score(add_features(clean))
    ranked.to_csv(out_dir / "processed_ranked_exceptions.csv", index=False)

    capacity_simulation(ranked).to_csv(out_dir / "control_capacity_simulation.csv", index=False)
    agency_summary(ranked).to_csv(out_dir / "agency_summary.csv", index=False)

    threshold_frontier(ranked).to_csv(out_dir / "threshold_decision_frontier.csv", index=False)
    recommendation = recommend_threshold(ranked)
    queue = ranked[ranked["priority_score"] >= recommendation["score_threshold"]]

    decision = {
        "model_version": MODEL_VERSION,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "recommended_threshold": recommendation,
        "workload_risk": monte_carlo_backlog(alerts=len(queue)),
        "weight_sensitivity": weight_sensitivity(ranked),
        "interpretation": "Screening/prioritization only; not evidence of misconduct.",
        "data_mode": data_mode,
    }
    (out_dir / "management_decision.json").write_text(json.dumps(decision, indent=2))

    _print_summary(ranked, decision)
    return decision


def _print_summary(ranked: pd.DataFrame, decision: dict) -> None:
    print(f"Data mode: {decision['data_mode']}")
    if decision["data_mode"] == "synthetic_sample":
        print("WARNING: synthetic fixture. Results are illustrative only.")
    print(f"Processed {len(ranked):,} transactions with model {decision['model_version']}")
    print(f"Recommended threshold under scenario capacity: {decision['recommended_threshold']['score_threshold']}")
    print(f"Estimated backlog probability: {decision['workload_risk']['backlog_probability_pct']}%")
    print("Top 10 prioritized exceptions:")
    print(
        ranked[
            [
                "AGENCY",
                "TRANSACTION_DATE",
                "VENDOR_NAME",
                "TRANSACTION_AMOUNT",
                "priority_score",
                "signal_family_count",
                "reasons",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the procurement decision-intelligence pipeline")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="use the offline synthetic fixture instead of the live DC Open Data API",
    )
    parser.add_argument("--out", dest="out_dir", default="data", help="output directory")
    parser.add_argument("--sample-size", type=int, default=6000, help="rows to generate in --sample mode")
    parser.add_argument("--seed", type=int, default=7, help="random seed for --sample mode")
    args = parser.parse_args()

    run(
        out_dir=Path(args.out_dir),
        use_sample=args.sample,
        sample_size=args.sample_size,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
