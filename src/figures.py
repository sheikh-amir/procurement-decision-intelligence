"""Render static figures for documentation from a completed pipeline run.

Usage:
    python -m src.figures --in data/sample_run --out docs/img --label "Synthetic sample data"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

INK = "#1f2933"
ACCENT = "#0b6ea8"
WARN = "#b3541e"
GRID = "#d8dee4"


def _style(ax) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK, labelsize=9)


def decision_frontier(in_dir: Path, out_dir: Path, label: str) -> Path:
    frontier = pd.read_csv(in_dir / "threshold_decision_frontier.csv")
    decision = json.loads((in_dir / "management_decision.json").read_text())
    rec = decision.get("recommended_threshold", {})
    workload = decision.get("workload_risk", {})
    capacity = workload.get("capacity_hours", 40)

    fig, ax1 = plt.subplots(figsize=(8, 4.1), dpi=100)
    ax1.plot(
        frontier["score_threshold"],
        frontier["review_hours"],
        color=ACCENT,
        linewidth=2.2,
        label="Weekly review hours required",
    )
    ax1.axhline(capacity, color=WARN, linestyle="--", linewidth=1.5, label=f"Analyst capacity ({capacity:.0f} h)")
    ax1.set_xlabel("Priority-score threshold", color=INK, fontsize=10)
    ax1.set_ylabel("Review hours", color=INK, fontsize=10)
    _style(ax1)

    ax2 = ax1.twinx()
    ax2.plot(
        frontier["score_threshold"],
        frontier["proxy_risk_coverage_pct"],
        color=INK,
        linewidth=1.6,
        alpha=0.55,
        label="Proxy-risk coverage (%)",
    )
    ax2.set_ylabel("Proxy-risk coverage (%)", color=INK, fontsize=10)
    ax2.spines[["top"]].set_visible(False)
    ax2.tick_params(colors=INK, labelsize=9)

    if rec:
        ax1.axvline(rec["score_threshold"], color=ACCENT, alpha=0.35, linewidth=8)
        ax1.annotate(
            f"Recommended: {rec['score_threshold']:.0f}\n{int(rec['alerts'])} alerts",
            xy=(rec["score_threshold"], capacity),
            xytext=(8, 24),
            textcoords="offset points",
            fontsize=9,
            color=INK,
            weight="bold",
        )

    handles = ax1.get_legend_handles_labels()[0] + ax2.get_legend_handles_labels()[0]
    labels = ax1.get_legend_handles_labels()[1] + ax2.get_legend_handles_labels()[1]
    ax1.legend(handles, labels, loc="upper right", frameon=False, fontsize=9)

    ax1.set_title(
        "Threshold decision frontier: coverage vs analyst capacity",
        color=INK,
        fontsize=12,
        weight="bold",
        loc="left",
        pad=14,
    )
    fig.text(0.008, 0.008, label, fontsize=8, color="#7a8590")
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "decision_frontier.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def band_distribution(in_dir: Path, out_dir: Path, label: str) -> Path:
    ranked = pd.read_csv(in_dir / "processed_ranked_exceptions.csv")
    order = ["Low", "Moderate", "High", "Critical"]
    counts = ranked["priority_band"].value_counts().reindex(order).fillna(0)

    fig, ax = plt.subplots(figsize=(6.0, 3.4), dpi=100)
    bars = ax.bar(order, counts.values, color=[GRID, "#8fb8cf", ACCENT, WARN], width=0.62)
    for bar, value in zip(bars, counts.values):
        ax.annotate(
            f"{int(value):,}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color=INK,
        )
    ax.set_ylabel("Transactions", color=INK, fontsize=10)
    ax.set_title("Priority-band distribution", color=INK, fontsize=12, weight="bold", loc="left", pad=12)
    _style(ax)
    fig.text(0.008, 0.008, label, fontsize=8, color="#7a8590")
    fig.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "priority_bands.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Render documentation figures")
    parser.add_argument("--in", dest="in_dir", default="data", help="pipeline output directory")
    parser.add_argument("--out", dest="out_dir", default="docs/img", help="figure output directory")
    parser.add_argument(
        "--label",
        default="Generated from pipeline output",
        help="provenance caption stamped onto each figure",
    )
    args = parser.parse_args()

    in_dir, out_dir = Path(args.in_dir), Path(args.out_dir)
    for path in (
        decision_frontier(in_dir, out_dir, args.label),
        band_distribution(in_dir, out_dir, args.label),
    ):
        print(f"wrote {path}")


if __name__ == "__main__":
    _cli()
