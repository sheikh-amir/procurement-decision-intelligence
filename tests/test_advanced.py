import pandas as pd

from src.engine import add_features, score
from src.optimizer import monte_carlo_backlog, recommend_threshold, threshold_frontier
from src.quality import quality_report


def rich_fixture():
    rows = []
    oid = 1
    for month in range(1, 9):
        for agency in ["Agency A", "Agency B", "Agency C"]:
            for vendor_idx in range(1, 6):
                for t in range(3):
                    rows.append(
                        {
                            "OBJECTID": oid,
                            "AGENCY": agency,
                            "TRANSACTION_DATE": pd.Timestamp(2025, month, 5 + t),
                            "TRANSACTION_AMOUNT": 100 + vendor_idx * 25 + month * 7,
                            "VENDOR_NAME": f"Vendor {vendor_idx}",
                            "VENDOR_STATE_PROVINCE": "DC",
                            "MCC_DESCRIPTION": "Office" if vendor_idx < 5 else "Technology",
                        }
                    )
                    oid += 1
    # Inject a concentrated spend spike and duplicate pair.
    rows[-1]["TRANSACTION_AMOUNT"] = 40_000.0
    rows[-2]["TRANSACTION_AMOUNT"] = 7_777.0
    rows[-3]["TRANSACTION_AMOUNT"] = 7_777.0
    rows[-2]["VENDOR_NAME"] = "Vendor X"
    rows[-3]["VENDOR_NAME"] = "Vendor X"
    rows[-2]["TRANSACTION_DATE"] = rows[-3]["TRANSACTION_DATE"] + pd.Timedelta(days=1)
    return pd.DataFrame(rows)


def test_advanced_features_are_bounded():
    featured = add_features(rich_fixture())
    for col in [
        "vendor_concentration",
        "vendor_cross_agency_reach",
        "temporal_spend_spike",
        "new_vendor_for_agency",
        "unsupervised",
    ]:
        assert featured[col].between(0, 1).all(), col


def test_explainability_and_evidence_diversity_exist():
    ranked = score(add_features(rich_fixture()))
    assert ranked["top_score_contributors"].str.len().gt(0).all()
    assert ranked["signal_family_count"].ge(0).all()
    assert ranked["evidence_confidence"].between(0, 1).all()


def test_threshold_optimizer_respects_capacity_when_feasible():
    ranked = score(add_features(rich_fixture()))
    rec = recommend_threshold(ranked, weekly_review_hours=5, review_minutes=12, min_multi_family_rate_pct=0)
    assert rec["review_hours"] <= 5
    frontier = threshold_frontier(ranked, review_minutes=12)
    assert frontier["alerts"].is_monotonic_decreasing
    assert frontier["proxy_risk_coverage_pct"].is_monotonic_decreasing


def test_monte_carlo_is_reproducible_and_capacity_sensitive():
    a = monte_carlo_backlog(100, analysts=1, hours_per_analyst=10, seed=7)
    b = monte_carlo_backlog(100, analysts=1, hours_per_analyst=10, seed=7)
    c = monte_carlo_backlog(100, analysts=5, hours_per_analyst=40, seed=7)
    assert a == b
    assert c["backlog_probability_pct"] <= a["backlog_probability_pct"]


def test_quality_report_flags_duplicate_ids():
    df = rich_fixture().head(10).copy()
    df.loc[df.index[-1], "OBJECTID"] = df.loc[df.index[0], "OBJECTID"]
    report = quality_report(df)
    row = report[report["metric"] == "duplicate_objectid_rate"].iloc[0]
    assert row["status"] == "FAIL"


def test_weight_sensitivity_is_reproducible_and_bounded():
    from src.sensitivity import weight_sensitivity

    ranked = score(add_features(rich_fixture()))
    a = weight_sensitivity(ranked, top_n=20, simulations=20, seed=99)
    b = weight_sensitivity(ranked, top_n=20, simulations=20, seed=99)
    assert a == b
    assert 0 <= a["min_top_queue_jaccard"] <= a["mean_top_queue_jaccard"] <= 1
