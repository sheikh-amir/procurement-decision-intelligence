"""Tests for the offline sample-data path."""
from __future__ import annotations

import pandas as pd

from src.data import normalize
from src.engine import add_features, score
from src.quality import enforce_quality_gate, quality_report
from src.sample import generate


def test_sample_matches_expected_schema():
    df = generate(n_transactions=400, seed=1)
    from src.config import EXPECTED_COLUMNS

    assert EXPECTED_COLUMNS.issubset(set(df.columns))
    assert df["OBJECTID"].is_unique


def test_sample_dates_normalize_to_plausible_range():
    """Guards the epoch-unit conversion between the generator and normalize()."""
    clean = normalize(generate(n_transactions=400, seed=1))
    assert clean["TRANSACTION_DATE"].min() >= pd.Timestamp("2020-01-01")
    assert clean["TRANSACTION_DATE"].max() <= pd.Timestamp("2035-01-01")


def test_sample_passes_quality_gate():
    enforce_quality_gate(quality_report(generate(n_transactions=400, seed=3)))


def test_sample_is_reproducible():
    a = generate(n_transactions=200, seed=11)
    b = generate(n_transactions=200, seed=11)
    pd.testing.assert_frame_equal(a, b)


def test_sample_run_produces_a_ranked_queue():
    ranked = score(add_features(normalize(generate(n_transactions=1200, seed=5))))
    assert len(ranked) > 0
    assert ranked["priority_score"].between(0, 100).all()
    # The injected structured patterns should surface above the noise floor.
    assert ranked["priority_score"].max() > ranked["priority_score"].median()


def test_sample_pipeline_writes_all_artifacts(tmp_path):
    """Guards the offline entry point documented in the README and sample-run notes."""
    from src.pipeline import run

    decision = run(out_dir=tmp_path, use_sample=True, sample_size=800, seed=5)

    expected = {
        "raw_purchase_card.csv",
        "data_quality_report.csv",
        "processed_ranked_exceptions.csv",
        "agency_summary.csv",
        "control_capacity_simulation.csv",
        "threshold_decision_frontier.csv",
        "management_decision.json",
    }
    assert expected == {p.name for p in tmp_path.iterdir()}
    # Offline output must always be self-identifying so it cannot be read as a real finding.
    assert decision["data_mode"] == "synthetic_sample"


def test_committed_sample_queue_is_reproducible(tmp_path):
    """The committed review queue must be regenerable from the committed code."""
    from pathlib import Path

    import pandas as pd

    from src.pipeline import run

    committed = Path("data/sample_run/recommended_review_queue.csv")
    if not committed.exists():  # pragma: no cover - repo layout guard
        return
    decision = run(out_dir=tmp_path, use_sample=True)
    threshold = decision["recommended_threshold"]["score_threshold"]
    fresh = pd.read_csv(tmp_path / "processed_ranked_exceptions.csv")
    fresh = fresh[fresh["priority_score"] >= threshold]
    fresh.to_csv(tmp_path / "queue.csv", index=False)
    assert (tmp_path / "queue.csv").read_bytes() == committed.read_bytes()
